#!/usr/bin/env python3
"""Collect the daily activity that feeds the heatmap (README card + website).

Why this script is more than a scraper
--------------------------------------
GitHub's public contribution calendar only counts commits whose e-mail is linked
to the profile that owns the calendar. Work pushed with another identity (or by a
second account) never shows up, so the calendar can read "0 contributions" even
while a repository is busy. This script therefore merges two sources, per day,
taking the larger value (so nothing is double-counted):

  1. The contribution calendar of every account in ``contributions.accounts``
     (data/profile.json). GraphQL API when a token is available, otherwise the
     public HTML fragment.
  2. Commits in the profile owner's own public, non-fork repositories, whoever
     authored them (bots excluded), via the REST API.
     Disable with ``"include_repo_commits": false``.

If every source fails the existing data/contributions.json is left untouched,
so a flaky run never wipes the graph.

Environment
-----------
GITHUB_TOKEN / GH_TOKEN   optional but recommended (higher API limits). Inside
                          GitHub Actions ``secrets.GITHUB_TOKEN`` is enough.
GH_PROFILE_USER           overrides person.username from profile.json.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data" / "profile.json"
OUT = ROOT / "data" / "contributions.json"
API = "https://api.github.com"
UA = "Parsa-Emami-profile-readme/2.0 (+https://github.com/Parsa-Emami/Parsa-Emami)"
WINDOW_DAYS = 365  # today and the 364 days before it


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def warn(msg: str) -> None:
    print(f"::warning::{msg}", file=sys.stderr)


def token() -> str | None:
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or None


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "application/vnd.github+json"})
    if token():
        s.headers["Authorization"] = f"Bearer {token()}"
    return s


def window(today: dt.date | None = None) -> tuple[dt.date, dt.date]:
    end = today or dt.datetime.now(dt.timezone.utc).date()
    return end - dt.timedelta(days=WINDOW_DAYS - 1), end


# --------------------------------------------------------------------------- #
# source 1a: calendar via GraphQL
# --------------------------------------------------------------------------- #
GQL = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def calendar_graphql(s: requests.Session, login: str, start: dt.date, end: dt.date) -> dict[str, int]:
    r = s.post(
        f"{API}/graphql",
        json={"query": GQL, "variables": {
            "login": login,
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": f"{end.isoformat()}T23:59:59Z",
        }},
        timeout=40,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors") or not (payload.get("data") or {}).get("user"):
        raise RuntimeError(f"GraphQL error for {login}: {payload.get('errors') or 'user not found'}")
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {d["date"]: int(d["contributionCount"]) for w in weeks for d in w["contributionDays"]}


# --------------------------------------------------------------------------- #
# source 1b: calendar via the public HTML fragment
# --------------------------------------------------------------------------- #
_CELL = re.compile(r"<td\b[^>]*\bdata-date=\"(\d{4}-\d{2}-\d{2})\"[^>]*>", re.S)
_TIP = re.compile(r"<tool-tip\b[^>]*\bfor=\"([^\"]+)\"[^>]*>(.*?)</tool-tip>", re.S)
_ID = re.compile(r"\bid=\"([^\"]+)\"")
_LEVEL = re.compile(r"\bdata-level=\"(\d)\"")
_COUNT = re.compile(r"([\d,]+)\s+contributions?\b", re.I)
LEVEL_FALLBACK = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10}  # only used if a tooltip is missing


def parse_calendar_html(markup: str) -> dict[str, int]:
    """Parse https://github.com/users/<login>/contributions into {date: count}."""
    tips: dict[str, str] = {}
    for cell_id, text in _TIP.findall(markup):
        tips[cell_id] = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())

    days: dict[str, int] = {}
    for m in _CELL.finditer(markup):
        tag = m.group(0)
        date = m.group(1)
        idm = _ID.search(tag)
        text = tips.get(idm.group(1), "") if idm else ""
        if text:
            if re.search(r"\bno contributions?\b", text, re.I):
                count = 0
            else:
                c = _COUNT.search(text)
                count = int(c.group(1).replace(",", "")) if c else 0
        else:
            lv = _LEVEL.search(tag)
            count = LEVEL_FALLBACK.get(int(lv.group(1)), 0) if lv else 0
        days[date] = count
    if not days:
        raise RuntimeError("no contribution cells found (GitHub markup changed?)")
    return days


def calendar_html(s: requests.Session, login: str) -> dict[str, int]:
    r = s.get(f"https://github.com/users/{login}/contributions",
              headers={"Accept": "text/html"}, timeout=40)
    r.raise_for_status()
    return parse_calendar_html(r.text)


def calendar_for(s: requests.Session, login: str, start: dt.date, end: dt.date) -> dict[str, int]:
    if token():
        try:
            return calendar_graphql(s, login, start, end)
        except Exception as exc:  # fall through to HTML
            warn(f"GraphQL calendar failed for {login}: {exc}")
    return calendar_html(s, login)


# --------------------------------------------------------------------------- #
# source 2: commits in the owner's public repositories
# --------------------------------------------------------------------------- #
def _is_bot(item: dict) -> bool:
    author = item.get("author") or {}
    committer = item.get("committer") or {}
    names = [
        (author.get("login") or ""),
        (committer.get("login") or ""),
        ((item.get("commit") or {}).get("author") or {}).get("name") or "",
    ]
    return any(n.endswith("[bot]") or n == "github-actions" for n in names) or author.get("type") == "Bot"


def repo_commit_counts(s: requests.Session, owner: str, start: dt.date) -> dict[str, int]:
    counts: dict[str, int] = {}
    repos: list[dict] = []
    page = 1
    while page <= 5:
        r = s.get(f"{API}/users/{owner}/repos", params={"type": "owner", "per_page": 100, "page": page}, timeout=40)
        r.raise_for_status()
        chunk = r.json()
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1

    since = f"{start.isoformat()}T00:00:00Z"
    for repo in repos:
        if repo.get("fork") or repo.get("disabled"):
            continue
        name = repo["name"]
        for page in range(1, 11):  # up to 1000 commits per repo per year
            r = s.get(f"{API}/repos/{owner}/{name}/commits",
                      params={"since": since, "per_page": 100, "page": page}, timeout=40)
            if r.status_code == 409:  # empty repository
                break
            r.raise_for_status()
            items = r.json()
            for it in items:
                if _is_bot(it):
                    continue
                stamp = ((it.get("commit") or {}).get("author") or {}).get("date")
                if stamp:
                    day = stamp[:10]
                    counts[day] = counts.get(day, 0) + 1
            if len(items) < 100:
                break
    return counts


# --------------------------------------------------------------------------- #
# merge + statistics
# --------------------------------------------------------------------------- #
def merge(start: dt.date, end: dt.date, calendars: list[dict[str, int]], commits: dict[str, int]) -> list[dict]:
    days = []
    cur = start
    while cur <= end:
        iso = cur.isoformat()
        cal = sum(c.get(iso, 0) for c in calendars)
        days.append({"date": iso, "count": max(cal, commits.get(iso, 0))})
        cur += dt.timedelta(days=1)
    return days


def current_streak(days: list[dict], today: dt.date) -> int:
    if not days:
        return 0
    i = len(days) - 1
    if days[i]["date"] == today.isoformat() and days[i]["count"] == 0:
        i -= 1
    n = 0
    while i >= 0 and days[i]["count"] > 0:
        n += 1
        i -= 1
    return n


def longest_streak(days: list[dict]) -> int:
    best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    return best


def build_payload(username: str, days: list[dict], sources: dict, today: dt.date) -> dict:
    best = max(days, key=lambda x: x["count"]) if days else {"date": None, "count": 0}
    return {
        "username": username,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "range": {"start": days[0]["date"] if days else None, "end": days[-1]["date"] if days else None},
        "total_contributions": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "current_streak": current_streak(days, today),
        "longest_streak": longest_streak(days),
        "best_day": best,
        "sources": sources,
        "days": days,
    }


def load_settings() -> tuple[str, list[str], bool]:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    username = os.getenv("GH_PROFILE_USER") or profile["person"]["username"]
    cfg = profile.get("contributions", {})
    accounts = cfg.get("accounts") or [username]
    if username not in accounts:
        accounts = [username, *accounts]
    return username, accounts, bool(cfg.get("include_repo_commits", True))


def main() -> int:
    username, accounts, with_repos = load_settings()
    start, end = window()
    s = session()

    calendars: list[dict[str, int]] = []
    src: dict = {"calendar": {}, "repo_commits": None}
    failures = 0

    for login in accounts:
        try:
            cal = {d: c for d, c in calendar_for(s, login, start, end).items() if start.isoformat() <= d <= end.isoformat()}
            calendars.append(cal)
            src["calendar"][login] = sum(cal.values())
            print(f"calendar  {login:<16} {sum(cal.values()):>5} contributions")
        except Exception as exc:
            failures += 1
            warn(f"calendar for {login} failed: {exc}")

    commits: dict[str, int] = {}
    if with_repos:
        try:
            commits = repo_commit_counts(s, username, start)
            src["repo_commits"] = sum(commits.values())
            print(f"repo commits ({username}): {sum(commits.values())}")
        except Exception as exc:
            failures += 1
            warn(f"repository commit scan failed: {exc}")

    expected = len(accounts) + (1 if with_repos else 0)
    if failures >= expected:
        warn("every source failed - keeping the existing data/contributions.json")
        return 0

    days = merge(start, end, calendars, commits)
    payload = build_payload(username, days, src, end)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: total={payload['total_contributions']} "
          f"active_days={payload['active_days']} current={payload['current_streak']} longest={payload['longest_streak']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

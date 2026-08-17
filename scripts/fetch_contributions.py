#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
USERNAME = os.getenv("GH_PROFILE_USER", "Parsa-Emami")
URL = f"https://github.com/users/{USERNAME}/contributions"

def parse_count(text: str) -> int:
    text = " ".join(text.split())
    if re.search(r"\bno contributions?\b", text, flags=re.I):
        return 0
    m = re.search(r"([\d,]+)\s+contribution", text, flags=re.I)
    return int(m.group(1).replace(",", "")) if m else 0

def fetch_days():
    r = requests.get(
        URL,
        headers={
            "User-Agent": "Parsa-Emami-profile-readme/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=30,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day[data-date]")
    if not cells:
        raise RuntimeError("GitHub contribution cells were not found; their HTML may have changed.")

    days = []
    for cell in cells:
        date = cell.get("data-date")
        count = None

        raw = cell.get("data-count")
        if raw and str(raw).isdigit():
            count = int(raw)

        if count is None:
            tooltip = ""
            cell_id = cell.get("id")
            if cell_id:
                tip = soup.find("tool-tip", attrs={"for": cell_id})
                if tip:
                    tooltip = tip.get_text(" ", strip=True)

            if not tooltip:
                tooltip = cell.get("aria-label", "")

            count = parse_count(tooltip)

        days.append({"date": date, "count": count})

    # GitHub can include duplicate/transition cells around year boundaries.
    by_date = {}
    for day in days:
        by_date[day["date"]] = day["count"]

    return [{"date": d, "count": by_date[d]} for d in sorted(by_date)]

def current_streak(days):
    if not days:
        return 0
    i = len(days) - 1
    today = dt.date.today().isoformat()
    if days[i]["date"] == today and days[i]["count"] == 0:
        i -= 1
    n = 0
    while i >= 0 and days[i]["count"] > 0:
        n += 1
        i -= 1
    return n

def longest_streak(days):
    best = run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best

def build_payload(days):
    total = sum(x["count"] for x in days)
    active = sum(x["count"] > 0 for x in days)
    best = max(days, key=lambda x: x["count"]) if days else {"date": None, "count": 0}
    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "range": {
            "start": days[0]["date"] if days else None,
            "end": days[-1]["date"] if days else None,
        },
        "total_contributions": total,
        "active_days": active,
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(days),
        "best_day": best,
        "days": days,
    }

def main():
    payload = build_payload(fetch_days())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"wrote {OUT}: total={payload['total_contributions']}, "
        f"current={payload['current_streak']}, longest={payload['longest_streak']}"
    )

if __name__ == "__main__":
    main()

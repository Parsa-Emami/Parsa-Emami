"""Load data/profile.json and provide the small helpers every builder shares."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def load_profile() -> dict:
    return json.loads((DATA / "profile.json").read_text(encoding="utf-8"))


def load_contributions() -> dict:
    p = DATA / "contributions.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"total_contributions": 0, "days": [], "range": {"start": None, "end": None}}


def today() -> dt.date:
    """Build date (UTC). Override with BUILD_DATE=YYYY-MM-DD for reproducible builds."""
    forced = os.getenv("BUILD_DATE")
    if forced:
        return dt.date.fromisoformat(forced)
    return dt.datetime.now(dt.timezone.utc).date()


def build_id() -> str:
    sha = os.getenv("GITHUB_SHA", "")
    return sha[:7] if sha else "local"


# --------------------------------------------------------------------------- #
# dates
# --------------------------------------------------------------------------- #
def _ym(s: str) -> tuple[int, int]:
    parts = s.split("-")
    return int(parts[0]), int(parts[1]) if len(parts) > 1 else 1


def fmt_ym(s: str | None) -> str:
    """'2025-09' -> '09.2025' (same numeric style as chanhdai.com); '2025' -> '2025'."""
    if not s:
        return ""
    if "-" not in s:
        return s
    y, m = _ym(s)
    return f"{m:02d}.{y}"


def fmt_period(start: str, end: str | None) -> str:
    return f"{fmt_ym(start)}—{fmt_ym(end)}" if end else f"{fmt_ym(start)}—"


def duration(start: str, end: str | None, now: dt.date | None = None) -> str:
    """Inclusive month count rendered like '1y 1m' (both end months are counted)."""
    now = now or today()
    sy, sm = _ym(start)
    ey, em = _ym(end) if end else (now.year, now.month)
    months = (ey - sy) * 12 + (em - sm) + 1
    y, m = divmod(max(months, 1), 12)
    if y and m:
        return f"{y}y {m}m"
    return f"{y}y" if y else f"{m}m"


def fmt_day(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}.{m}.{y}"


# --------------------------------------------------------------------------- #
# inline markup: [label](url)
# --------------------------------------------------------------------------- #
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def tokens(text: str) -> list[tuple[str, str | None]]:
    """Split text into (text, href|None) tokens."""
    out: list[tuple[str, str | None]] = []
    pos = 0
    for m in _LINK.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], None))
        out.append((m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], None))
    return out


def plain(text: str) -> str:
    return _LINK.sub(lambda m: m.group(1), text)


def resolve(href: str, base: str) -> str:
    """Turn in-page anchors into absolute links (used outside the website)."""
    return base.rstrip("/") + "/" + href if href.startswith("#") else href


def to_html(text: str) -> str:
    parts = []
    for t, href in tokens(text):
        if href:
            ext = href.startswith("http")
            attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
            parts.append(f'<a href="{escape(href, quote=True)}"{attrs}>{escape(t)}</a>')
        else:
            parts.append(escape(t))
    return "".join(parts)


def to_md(text: str, base: str) -> str:
    return _LINK.sub(lambda m: f"[{m.group(1)}]({resolve(m.group(2), base)})", text)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def parts_text(parts: list[dict]) -> str:
    """Overview rows are lists of {t, href}; join to plain text."""
    return " ".join(p["t"] for p in parts)

#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT = 30
TITLE_H = 30
TOP = 22

BG_TOP = "#111722"
BG_BOTTOM = "#0a0e14"
FRAME = "#1f6feb"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def levels(days):
    nonzero = sorted(d["count"] for d in days if d["count"] > 0)
    if not nonzero:
        return lambda _: 0
    def q(p):
        i = min(len(nonzero)-1, round((len(nonzero)-1) * p))
        return nonzero[i]
    q1, q2, q3 = q(.25), q(.50), q(.75)
    def level(n):
        if n <= 0: return 0
        if n <= q1: return 1
        if n <= q2: return 2
        if n <= q3: return 3
        return 4
    return level

def make_grid(days):
    if not days:
        return []
    lookup = {d["date"]: d["count"] for d in days}
    first = dt.date.fromisoformat(days[0]["date"])
    last = dt.date.fromisoformat(days[-1]["date"])
    start = first - dt.timedelta(days=(first.weekday()+1) % 7)
    end = last + dt.timedelta(days=(6 - ((last.weekday()+1) % 7)))
    weeks = []
    cur = start
    while cur <= end:
        week = []
        for _ in range(7):
            iso = cur.isoformat()
            week.append((iso, lookup.get(iso)) if iso in lookup else None)
            cur += dt.timedelta(days=1)
        weeks.append(week)
    return weeks

def render(data):
    days = data["days"]
    level = levels(days)
    grid = make_grid(days)
    ncols = max(1, len(grid))
    art_w = ncols * STEP
    art_h = 7 * STEP
    W = PAD + LEFT + art_w + PAD
    stats_h = 92
    H = TITLE_H + TOP + art_h + stats_h + PAD
    grid_x = PAD + LEFT
    grid_y = TITLE_H + TOP

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        '<style>@keyframes c{0%{opacity:0;transform:translateY(-7px)}100%{opacity:1;transform:translateY(0)}}'
        '.cell{opacity:0;animation:c .38s cubic-bezier(.2,.8,.2,1) both}</style>',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/>'
        f'<stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity=".58"/>',
        f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{FRAME}" stroke-opacity=".35"/>',
    ]
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD+i*16}" cy="{TITLE_H/2}" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{W/2}" y="19" fill="{MUTED}" font-size="11" text-anchor="middle">'
        f'{html.escape(data["username"])}@github: ~/contributions --graph</text>'
    )

    # Month labels.
    seen = set()
    for ci, week in enumerate(grid):
        for cell in week:
            if not cell:
                continue
            date = dt.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen and date.day <= 7:
                seen.add(key)
                parts.append(
                    f'<text x="{grid_x + ci*STEP}" y="{TITLE_H+15}" fill="{MUTED}" font-size="9">{date.strftime("%b")}</text>'
                )
            break

    for ri, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        parts.append(
            f'<text x="{PAD}" y="{grid_y + ri*STEP + 9.5:.1f}" fill="{MUTED}" font-size="9">{name}</text>'
        )

    for ci, week in enumerate(grid):
        for ri, cell in enumerate(week):
            if not cell:
                continue
            date_s, count = cell
            lvl = level(count)
            delay = ci * .017 + ri * .040
            x = grid_x + ci * STEP
            y = grid_y + ri * STEP
            plural = "" if count == 1 else "s"
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_s}: {count} contribution{plural}</title></rect>'
            )

    legend_y = grid_y + art_h + 7
    legend_x = max(PAD + 110, W - PAD - 150)
    parts.append(f'<text x="{legend_x-8}" y="{legend_y+9}" fill="{MUTED}" font-size="9" text-anchor="end">Less</text>')
    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{legend_x+i*15}" y="{legend_y}" width="11" height="11" rx="2" fill="{color}"/>')
    parts.append(f'<text x="{legend_x+len(PALETTE)*15+3}" y="{legend_y+9}" fill="{MUTED}" font-size="9">More</text>')

    sep = legend_y + 27
    parts.append(f'<line x1="0" y1="{sep}" x2="{W}" y2="{sep}" stroke="{FRAME}" stroke-opacity=".24"/>')

    total = data.get("total_contributions", 0)
    current = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    best = data.get("best_day") or {"date": "-", "count": 0}
    rng = data.get("range") or {}
    y1 = sep + 25
    parts += [
        f'<text x="{PAD}" y="{y1}" fill="{GREEN}" font-size="13"><tspan font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>',
        f'<text x="{W-PAD}" y="{y1}" fill="{MUTED}" font-size="11" text-anchor="end">'
        f'{rng.get("start","-")} → {rng.get("end","-")}</text>',
        f'<text x="{PAD}" y="{y1+25}" fill="{MUTED}" font-size="12">current streak '
        f'<tspan fill="{ACCENT}" font-weight="700">{current} days</tspan>'
        f'<tspan> · longest </tspan><tspan fill="{ACCENT}" font-weight="700">{longest} days</tspan></text>',
        f'<text x="{W-PAD}" y="{y1+25}" fill="{MUTED}" font-size="11" text-anchor="end">best day '
        f'<tspan fill="{GOLD}" font-weight="700">{best.get("count",0)}</tspan> on {best.get("date","-")}</text>',
        '</svg>'
    ]
    return "".join(parts)

def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    OUT.write_text(render(data), encoding="utf-8")
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()

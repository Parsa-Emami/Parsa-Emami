#!/usr/bin/env python3
from __future__ import annotations

import html
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wordmark.svg"

W, H = 520, 420
PAD = 20
TITLE_H = 30

BG_TOP = "#111722"
BG_BOTTOM = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

glyphs = {
"P": ["###### ","#     #","#     #","###### ","#      ","#      ","#      "],
"A": ["  ###  "," #   # ","#     #","#######","#     #","#     #","#     #"],
"R": ["###### ","#     #","#     #","###### ","#   #  ","#    # ","#     #"],
"S": [" ##### ","#     #","#      "," ##### ","      #","#     #"," ##### "],
}

def banner(text="PARSA"):
    lines = [""] * 7
    for ch in text:
        g = glyphs[ch]
        for i in range(7):
            lines[i] += g[i] + " "
    return lines

lines = banner()
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
    '<defs>',
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/>'
    f'<stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
    '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
    '<feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    '</defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLE_H}" x2="{W}" y2="{TITLE_H}" stroke="{FRAME}"/>',
]
for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLE_H/2}" r="5" fill="{color}"/>')

parts += [
    f'<text x="{W/2}" y="19" fill="{MUTED}" font-size="11" text-anchor="middle">parsa@github:~$ ./identity.sh</text>',
    '<g filter="url(#glow)">'
]

x, y0 = 34, 78
font_size, line_h = 10.6, 18
for i, line in enumerate(lines):
    safe = html.escape(line)
    delay = 0.20 + i * 0.09
    parts.append(
        f'<text xml:space="preserve" x="{x}" y="{y0+i*line_h}" fill="{INK}" font-size="{font_size}" '
        f'opacity="0">{safe}<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".28s" fill="freeze"/></text>'
    )
parts.append('</g>')

metadata = [
    ("role", "Software Engineering / Architecture"),
    ("focus", "Security · Red Team Thinking · Applied AI"),
    ("build", "Production Systems · Automation · Developer Tools"),
    ("status", "building, breaking, proving"),
]
yy = 238
for i, (key, value) in enumerate(metadata):
    delay = 1.0 + i * 0.14
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur=".30s" fill="freeze"/>'
        f'<text x="{PAD+8}" y="{yy+i*31}" fill="{ACCENT}" font-size="12">{key:>7}</text>'
        f'<text x="{PAD+82}" y="{yy+i*31}" fill="{INK}" font-size="12">: {html.escape(value)}</text></g>'
    )

parts += [
    f'<line x1="{PAD}" y1="370" x2="{W-PAD}" y2="370" stroke="{FRAME}"/>',
    f'<text x="{PAD+8}" y="396" fill="{GREEN}" font-size="12">● online</text>',
    f'<text x="{W-PAD-8}" y="396" fill="{GOLD}" font-size="11" text-anchor="end">Parsa-Emami</text>',
    '</svg>'
]

OUT.write_text("".join(parts), encoding="utf-8")
print(f"wrote {OUT}")

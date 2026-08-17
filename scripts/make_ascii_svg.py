#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-prepped.png"
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "parsa-ascii.svg"

COLS = 92
ROWS = 50
CELL_W = 7.2
CELL_H = 13.2
PAD = 18
TITLE_H = 30
STATUS_H = 34

RAMP = " .`:-=+*#%@"
BG_TOP = "#111722"
BG_BOTTOM = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
ACCENT = "#22d3ee"

art_w = COLS * CELL_W
art_h = ROWS * CELL_H
W = art_w + PAD * 2
H = TITLE_H + art_h + STATUS_H + PAD

img = Image.open(src).convert("L")
img = ImageOps.fit(img, (COLS, ROWS), method=Image.Resampling.LANCZOS)
img = ImageEnhance.Contrast(img).enhance(1.06)

rows = []
for y in range(ROWS):
    line = []
    for x in range(COLS):
        lum = img.getpixel((x, y)) / 255.0
        lum = lum ** 1.15
        if lum >= 0.84:
            line.append(" ")
        else:
            idx = round((1.0 - lum) * (len(RAMP) - 1))
            idx = max(0, min(len(RAMP) - 1, idx))
            line.append(RAMP[idx])
    rows.append("".join(line))

static = os.getenv("STATIC") == "1"
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" '
    'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
    '<defs>',
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG_TOP}"/>'
    f'<stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
]
for row in range(ROWS):
    y = TITLE_H + 3 + row * CELL_H
    parts.append(
        f'<clipPath id="clip{row}"><rect x="{PAD}" y="{y:.1f}" width="0" height="{CELL_H:.1f}">'
        + ("" if static else f'<animate attributeName="width" from="0" to="{art_w:.1f}" begin="{row*0.085:.3f}s" dur="0.16s" fill="freeze"/>')
        + (f'<set attributeName="width" to="{art_w:.1f}"/>' if static else "")
        + '</rect></clipPath>'
    )
parts += [
    '</defs>',
    f'<rect width="{W:.0f}" height="{H:.0f}" rx="12" fill="url(#bg)"/>',
    f'<rect x=".5" y=".5" width="{W-1:.0f}" height="{H-1:.0f}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLE_H}" x2="{W:.0f}" y2="{TITLE_H}" stroke="{FRAME}"/>',
]
for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLE_H/2}" r="5" fill="{color}"/>')

parts.append(
    f'<text x="{W/2:.1f}" y="19" fill="{MUTED}" font-size="11" text-anchor="middle">'
    'parsa@github:~$ ./portrait.sh</text>'
)

font_size = CELL_H * 0.86
art_top = TITLE_H + 3
for row, line in enumerate(rows):
    y = art_top + row * CELL_H + CELL_H * 0.78
    safe = html.escape(line)
    parts.append(
        f'<g clip-path="url(#clip{row})"><text xml:space="preserve" x="{PAD}" y="{y:.1f}" '
        f'fill="{INK}" font-size="{font_size:.1f}" textLength="{art_w:.1f}" lengthAdjust="spacing">'
        f'{safe}</text></g>'
    )
    if not static:
        delay = row * 0.085
        parts.append(
            f'<rect y="{art_top + row*CELL_H + 1:.1f}" width="6" height="{CELL_H-2:.1f}" fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+art_w:.1f}" begin="{delay:.3f}s" dur=".16s" fill="freeze"/>'
            f'<set attributeName="opacity" to=".85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+0.16:.3f}s"/></rect>'
        )

sep_y = TITLE_H + art_h + 4
parts += [
    f'<line x1="0" y1="{sep_y:.1f}" x2="{W:.0f}" y2="{sep_y:.1f}" stroke="{FRAME}"/>',
    f'<text x="{PAD}" y="{sep_y+23:.1f}" fill="{MUTED}" font-size="12">parsa@github:~$ whoami '
    f'<tspan fill="{INK}">Parsa Emami</tspan></text>',
    f'<rect x="{PAD+246}" y="{sep_y+11:.1f}" width="8" height="14" fill="{ACCENT}">'
    '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.48;.5;1" dur="1s" repeatCount="indefinite"/>'
    '</rect>',
    '</svg>'
]

dst.write_text("".join(parts), encoding="utf-8")
print(f"wrote {dst}")

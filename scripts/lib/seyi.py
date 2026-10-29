from __future__ import annotations

from functools import lru_cache
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

BACKGROUND = '#10110f'
INK = '#f3f0e8'
ACCENT = '#d3ff52'
MUTED = '#9d9d94'
LABEL = '#5f625b'
BORDER = '#383a33'
FONTS = Path(__file__).resolve().parents[1] / 'fonts'
SYMBOLS = {
    '↗': 'M0 .7L.7 0M0 0H.7V.7',
    '↘': 'M0 0L.7 .7M0 .7H.7V0',
    '↓': 'M.35 0V.7M0 .35l.35 .35 .35 -.35',
    '⏤': 'M0 .35H.8',
}


@lru_cache(maxsize=2)
def font_data(weight):
    name = 'Medium' if weight == 500 else 'Regular'
    font = TTFont(FONTS / f'OpenSauce-{name}.woff2')
    return font, font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm


@lru_cache(maxsize=None)
def glyph_path(weight, name):
    _, glyphs, _, _ = font_data(weight)
    pen = SVGPathPen(glyphs)
    glyphs[name].draw(pen)
    return pen.getCommands()


def measure(text, size, weight=500, tracking=0):
    font, _, cmap, units = font_data(weight)
    return sum(size*.8 if ch in SYMBOLS else font['hmtx'][cmap[ord(ch)]][0] * size / units for ch in text) + max(0, len(text)-1) * tracking


class Drawing:
    def __init__(self, width=1348):
        self.width = width
        self.parts = []
        self.defs = []
        self.glyphs = {}

    def rect(self, x, y, w, h, fill='none', stroke=None, radius=0):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" fill="{fill}"' + (f' stroke="{stroke}"' if stroke else '') + '/>')

    def line(self, x, y, end, color=BORDER):
        self.parts.append(f'<path d="M{x:g} {y:g}H{end:g}" stroke="{color}" stroke-width=".7"/>')

    def text(self, x, y, text, size=16, weight=500, color=INK, tracking=0, anchor='start', outline=False):
        width = measure(text, size, weight, tracking)
        x -= width if anchor == 'end' else width/2 if anchor == 'middle' else 0
        font, _, cmap, units = font_data(weight)
        scale = size / units
        uses = []
        for ch in text:
            if ch in SYMBOLS:
                uses.append(f'<path d="{SYMBOLS[ch]}" transform="translate({x:.3f} {y-size*.7:g}) scale({size:g})" fill="none" stroke="{color}" stroke-width=".07"/>')
                x += size*.8+tracking
                continue
            name = cmap[ord(ch)]
            key = weight, name
            if key not in self.glyphs:
                gid = f'g{len(self.glyphs)}'
                self.glyphs[key] = gid
                self.defs.append(f'<path id="{gid}" d="{glyph_path(weight, name)}"/>')
            effect = f' stroke-width="{1/scale:.3f}"' if outline else ''
            uses.append(f'<use href="#{self.glyphs[key]}" transform="translate({x:.3f} {y:g}) scale({scale:.6f} {-scale:.6f})"{effect}/>')
            x += font['hmtx'][name][0] * scale + tracking
        paint = f'fill="none" stroke="{color}"' if outline else f'fill="{color}"'
        self.parts.append(f'<g {paint} data-label="{escape(text, quote=True)}">' + ''.join(uses) + '</g>')
        return width

    def label(self, x, y, text, size=6.62569, color=ACCENT, anchor='start'):
        return self.text(x, y, text, size, color=color, tracking=size*.13, anchor=anchor)

    def paragraph(self, x, y, text, width, size, line_height, color=INK, tracking=0, weight=500, anchor='start'):
        lines = []
        current = ''
        for word in text.split():
            candidate = f'{current} {word}'.strip()
            if current and measure(candidate, size, weight, tracking) > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        for number, line in enumerate(lines):
            self.text(x, y+number*line_height, line, size, weight, color, tracking, anchor)
        return y+len(lines)*line_height

    def pill(self, x, y, text, size=8, fill='none', color=INK, padding=12, height=25):
        width = measure(text, size) + padding*2
        self.rect(x, y, width, height, fill, BORDER if fill == 'none' else None, height/2)
        self.text(x+padding, y+height/2+size*.34, text, size, color=color)
        return width

    def svg(self, height, title, description):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height:g}" viewBox="0 0 {self.width} {height:g}" role="img" aria-labelledby="title desc">'
                f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
                f'<defs><clipPath id="frame"><rect width="{self.width}" height="{height:g}"/></clipPath>{"".join(self.defs)}</defs>'
                f'<g clip-path="url(#frame)"><rect width="{self.width}" height="{height:g}" fill="{BACKGROUND}"/>{"".join(self.parts)}</g></svg>\n')

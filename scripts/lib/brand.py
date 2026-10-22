from __future__ import annotations

import io
from functools import lru_cache
from html import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from . import fonts


@lru_cache(maxsize=None)
def font_data(weight: int, mono: bool):
    font = TTFont(io.BytesIO(fonts._instance(mono, weight)))
    return font, font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm


@lru_cache(maxsize=None)
def glyph_path(weight: int, mono: bool, name: str) -> str:
    _, glyphs, _, _ = font_data(weight, mono)
    pen = SVGPathPen(glyphs)
    glyphs[name].draw(pen)
    return pen.getCommands()


def measure(text: str, size: float, weight: int = 400, mono: bool = False, tracking: float = 0) -> float:
    font, _, cmap, units = font_data(weight, mono)
    return sum(font['hmtx'][cmap.get(ord(ch), '.notdef')][0] * size / units for ch in text) + max(0, len(text) - 1) * tracking


class Drawing:
    def __init__(self, theme: dict, width: int = 830):
        self.t = theme
        self.width = width
        self.parts = []
        self.defs = []
        self.glyphs = {}

    def rect(self, x, y, w, h, fill=None, stroke=None, radius=0, extra=''):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" fill="{fill or "none"}"' + (f' stroke="{stroke}"' if stroke else '') + extra + '/>')

    def line(self, x1, y1, x2, y2, color=None):
        self.parts.append(f'<path d="M{x1:g} {y1:g}H{x2:g}" stroke="{color or self.t["border"]}"/>' if y1 == y2 else f'<path d="M{x1:g} {y1:g}L{x2:g} {y2:g}" fill="none" stroke="{color or self.t["border"]}"/>')

    def circle(self, x, y, r, fill=None, stroke=None, extra=''):
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill or "none"}"' + (f' stroke="{stroke}"' if stroke else '') + extra + '/>')

    def text(self, x, y, text: str, size=16, weight=400, color=None, mono=False, tracking=0, anchor='start'):
        width = measure(text, size, weight, mono, tracking)
        x -= width if anchor == 'end' else width / 2 if anchor == 'middle' else 0
        font, _, cmap, units = font_data(weight, mono)
        scale = size / units
        uses = []
        for ch in text:
            name = cmap.get(ord(ch), '.notdef')
            key = (weight, mono, name)
            if key not in self.glyphs:
                gid = f'g{len(self.glyphs)}'
                self.glyphs[key] = gid
                self.defs.append(f'<path id="{gid}" d="{glyph_path(weight, mono, name)}"/>')
            uses.append(f'<use href="#{self.glyphs[key]}" transform="translate({x:.3f} {y:g}) scale({scale:.6f} {-scale:.6f})"/>')
            x += font['hmtx'][name][0] * scale + tracking
        self.parts.append(f'<g fill="{color or self.t["ink"]}" data-label="{escape(text, quote=True)}">' + ''.join(uses) + '</g>')
        return width

    def serif(self, x, y, text: str, size=40, color=None):
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-family="Georgia,Times New Roman,serif" font-style="italic" font-size="{size:g}" fill="{color or self.t["accent"]}">{escape(text)}</text>')

    def para(self, x, y, text: str, width, size=16, color=None, lh=25):
        lines = []
        line = ''
        for word in text.split():
            candidate = f'{line} {word}'.strip()
            if line and measure(candidate, size) > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        for i, line in enumerate(lines):
            self.text(x, y + i * lh, line, size, color=color)
        return y + len(lines) * lh

    def label(self, x, y, text, color=None):
        self.text(x, y, text, 11, color=color or self.t['subtle'], mono=True, tracking=.25)

    def arrow(self, x, y, size=20, color=None):
        self.parts.append(f'<path d="M{x:g} {y+size:g}l{size:g} {-size:g}m{-size:g} 0h{size:g}v{size:g}" stroke="{color or self.t["accent"]}" stroke-width="1.5" fill="none"/>')

    def contours(self, x, y):
        self.parts.append(f'<g stroke="{self.t["accent"]}" stroke-opacity=".11" fill="none">')
        for r in range(80, 1050, 30):
            self.parts.append(f'<ellipse cx="{x:g}" cy="{y:g}" rx="{r}" ry="{r*.76:g}"/>')
        self.parts.append('</g>')

    def svg(self, height, title, description):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" viewBox="0 0 {self.width} {height}" role="img" aria-labelledby="title desc">'
                f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>'
                f'<defs><clipPath id="frame"><rect width="{self.width}" height="{height}" rx="8"/></clipPath>{"".join(self.defs)}</defs>'
                f'<g clip-path="url(#frame)"><rect width="{self.width}" height="{height}" fill="{self.t["paper"]}"/>{"".join(self.parts)}</g></svg>\n')

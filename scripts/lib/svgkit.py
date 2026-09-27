"""A tiny SVG layout toolkit for the README cards.

Text is measured with the real Geist metrics so it can be wrapped inside the
image, and the exact glyphs used are embedded as base64 woff2 subsets.
"""
from __future__ import annotations

import base64
import io
from collections import defaultdict
from html import escape

from PIL import Image

from . import content as C
from . import fonts, icons

THEMES: dict[str, dict] = {
    "light": {
        "bg": "#ffffff", "fg": "#0a0a0a", "muted_fg": "#737373", "muted": "#f5f5f5", "border": "#e5e5e5",
        "hatch": "#0a0a0a", "hatch_op": 0.07, "ring": "#a3a3a3",
        "heat": ["#efefef", "#d4d4d4", "#a3a3a3", "#525252", "#0a0a0a"], "avatar": "avatar-light.webp",
    },
    "dark": {
        "bg": "#0a0a0a", "fg": "#fafafa", "muted_fg": "#a3a3a3", "muted": "#171717", "border": "#2a2a2a",
        "hatch": "#fafafa", "hatch_op": 0.08, "ring": "#525252",
        "heat": ["#1a1a1a", "#3a3a3a", "#6b6b6b", "#a8a8a8", "#fafafa"], "avatar": "avatar-dark.webp",
    },
}

W = 830           # card width (GitHub's README column is ~830px wide)
PAD = 28          # inner horizontal padding
HATCH_H = 14      # decorative hatch strip on top of every card
HEAD_H = 52       # title row height


def esc(s: str) -> str:
    return escape(s, quote=True)


def jpeg_data_uri(path, size: int, quality: int = 84) -> str:
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


class Doc:
    """A drawing surface. ``sub()`` creates child surfaces that share font tracking."""

    def __init__(self, theme: str, parent: "Doc | None" = None) -> None:
        self.tn = theme
        self.t = THEMES[theme]
        self.parts: list[str] = []
        self.used: dict[tuple[bool, int], set[str]] = parent.used if parent else defaultdict(set)
        self.defs: list[str] = parent.defs if parent else []
        self._uid = parent._uid if parent else [0]

    # ---- infrastructure --------------------------------------------------
    def uid(self, prefix: str) -> str:
        self._uid[0] += 1
        return f"{prefix}{self._uid[0]}"

    def sub(self) -> "Doc":
        return Doc(self.tn, self)

    def place(self, child: "Doc", x: float, y: float) -> None:
        self.parts.append(f'<g transform="translate({x:g} {y:g})">{"".join(child.parts)}</g>')

    # ---- primitives ------------------------------------------------------
    def rect(self, x, y, w, h, fill="none", stroke=None, rx=0, sw=1, extra="") -> None:
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}"{st}{extra}/>')

    def line(self, x1, y1, x2, y2, stroke=None, sw=1) -> None:
        stroke = stroke or self.t["border"]
        # crisp 1px lines: align to half pixels
        self.parts.append(f'<line x1="{x1:g}" y1="{y1 + .5:g}" x2="{x2:g}" y2="{y2 + .5:g}" stroke="{stroke}" stroke-width="{sw}"/>')

    def vline(self, x, y1, y2, stroke=None) -> None:
        stroke = stroke or self.t["border"]
        self.parts.append(f'<line x1="{x + .5:g}" y1="{y1:g}" x2="{x + .5:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="1"/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=1) -> None:
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.parts.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}"{st}/>')

    def hatch(self, x, y, w, h) -> None:
        pid = "hatch"
        if not any(f'id="{pid}"' in d for d in self.defs):
            self.defs.append(
                f'<pattern id="{pid}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<rect width="1" height="10" fill="{self.t["hatch"]}" fill-opacity="{self.t["hatch_op"]}"/></pattern>'
            )
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{pid})"/>')

    def icon(self, name: str, x, y, size=16, color=None, sw=2) -> None:
        color = color or self.t["muted_fg"]
        s = size / 24
        if name == "github":
            self.parts.append(f'<path transform="translate({x:g} {y:g}) scale({s:g})" fill="{color}" d="{icons.GITHUB_PATH}"/>')
            return
        self.parts.append(
            f'<g transform="translate({x:g} {y:g}) scale({s:g})" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{icons.stroke_icon(name)}</g>'
        )

    # ---- text ------------------------------------------------------------
    def _track(self, mono: bool, weight: int, s: str) -> None:
        self.used[(mono, weight)].update(s)

    def text(self, x, y, s: str, size=15, weight=400, fill=None, mono=False, anchor="start", cls="", extra="") -> float:
        """Draw one line. Returns its measured width."""
        fill = fill or self.t["fg"]
        self._track(mono, weight, s)
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        c = f' class="{"m" if mono else "s"}{" " + cls if cls else ""}"'
        self.parts.append(
            f'<text x="{x:g}" y="{y:g}"{c} font-size="{size:g}" font-weight="{weight}" fill="{fill}"{a}{extra}>{esc(s)}</text>'
        )
        return fonts.text_width(s, size, weight, mono)

    def spans(self, x, y, runs: list[tuple[str, str, int]], size=12, mono=True, anchor="start") -> None:
        """One text line made of (string, fill, weight) runs."""
        for s, _, wt in runs:
            self._track(mono, wt, s)
        body = "".join(f'<tspan fill="{f}" font-weight="{wt}">{esc(s)}</tspan>' for s, f, wt in runs)
        a = "" if anchor == "start" else f' text-anchor="{anchor}"'
        self.parts.append(f'<text x="{x:g}" y="{y:g}" class="{"m" if mono else "s"}" font-size="{size:g}" xml:space="preserve"{a}>{body}</text>')

    def para(self, x, y, text: str, max_w: float, size=14, weight=400, fill=None, lh=None, link_fill=None) -> float:
        """Wrapped paragraph with inline [links](url). ``y`` is the top; returns the bottom y."""
        fill = fill or self.t["fg"]
        link_fill = link_fill or self.t["fg"]
        lh = lh or round(size * 1.62)
        words: list[list[tuple[str, bool]]] = []
        cur: list[tuple[str, bool]] = []
        for tok, href in C.tokens(text):
            buf = ""
            for ch in tok:
                if ch == " ":
                    if buf:
                        cur.append((buf, bool(href)))
                        buf = ""
                    if cur:
                        words.append(cur)
                        cur = []
                else:
                    buf += ch
            if buf:
                cur.append((buf, bool(href)))
        if cur:
            words.append(cur)

        space = fonts.text_width(" ", size, weight)
        lines: list[list[list[tuple[str, bool]]]] = []
        line: list[list[tuple[str, bool]]] = []
        width = 0.0
        for w in words:
            ww = fonts.text_width("".join(c for c, _ in w), size, weight)
            if line and width + space + ww > max_w:
                lines.append(line)
                line, width = [], 0.0
            width += (space if line else 0) + ww
            line.append(w)
        if line:
            lines.append(line)

        for i, ln in enumerate(lines):
            base = y + i * lh + size * 1.05
            out = []
            for wi, w in enumerate(ln):
                if wi:
                    if ln[wi - 1][-1][1] and w[0][1]:   # space inside a multi-word link stays underlined
                        out.append(f'<tspan fill="{link_fill}" text-decoration="underline"> </tspan>')
                    else:
                        out.append(" ")
                for chunk, is_link in w:
                    self._track(False, weight, chunk)
                    if is_link:
                        out.append(f'<tspan fill="{link_fill}" text-decoration="underline">{esc(chunk)}</tspan>')
                    else:
                        out.append(esc(chunk))
            self._track(False, weight, " ")
            self.parts.append(
                f'<text x="{x:g}" y="{base:g}" class="s" font-size="{size:g}" font-weight="{weight}" fill="{fill}" xml:space="preserve">{"".join(out)}</text>'
            )
        return y + len(lines) * lh

    # ---- composite pieces --------------------------------------------------
    def chip(self, x, y, label: str, size=12, h=24, pad=9, rx=7, weight=400, fg=None) -> float:
        w = fonts.text_width(label, size, weight) + pad * 2
        self.rect(x + .5, y + .5, w - 1, h - 1, fill=self.t["muted"], stroke=self.t["border"], rx=rx)
        self.text(x + pad, y + h / 2 + size * 0.35, label, size, weight, fg or self.t["muted_fg"] if size < 13 else fg or self.t["fg"])
        return w

    def chips(self, x, y, labels: list[str], max_w: float, size=12, h=24, gap=6, pad=9, rx=7, fg=None) -> float:
        """Flow chips onto rows; returns the bottom y."""
        cx, cy = x, y
        for lb in labels:
            w = fonts.text_width(lb, size) + pad * 2
            if cx > x and cx + w > x + max_w:
                cx, cy = x, cy + h + gap
            self.chip(cx, cy, lb, size, h, pad, rx, fg=fg)
            cx += w + gap
        return cy + h

    def tag(self, x, y, label: str, size=11) -> float:
        w = fonts.text_width(label, size, 500, True) + 14
        self.rect(x + .5, y + .5, w - 1, 19, stroke=self.t["border"], rx=6)
        self.text(x + 7, y + 14, label, size, 500, self.t["muted_fg"], mono=True)
        return w

    def tile(self, x, y, size: int, label: str) -> None:
        self.rect(x + .5, y + .5, size - 1, size - 1, fill=self.t["muted"], stroke=self.t["border"], rx=size * 0.25)
        fs = 10.5 if len(label) <= 3 else 9
        self.text(x + size / 2, y + size / 2 + fs * 0.36, label, fs, 600, self.t["fg"], mono=True, anchor="middle")

    def icon_box(self, x, y, name: str, size=28) -> None:
        self.rect(x + .5, y + .5, size - 1, size - 1, fill=self.t["muted"], stroke=self.t["border"], rx=8)
        self.icon(name, x + (size - 16) / 2, y + (size - 16) / 2, 16, self.t["muted_fg"])


# --------------------------------------------------------------------------- #
# document assembly
# --------------------------------------------------------------------------- #
STYLE_BASE = (
    ".s{font-family:" + fonts.SANS_STACK.replace('"', "'") + "}"
    ".m{font-family:" + fonts.MONO_STACK.replace('"', "'") + "}"
)


def assemble(d: Doc, height: float, title: str, desc: str, width: float = W, css: str = "", frame: bool = True,
             head: tuple[str, int] | None = None) -> str:
    """Wrap a Doc into a complete SVG. ``head`` = (title, count|0) draws the card header."""
    t = d.t
    body = "".join(d.parts)
    if head:
        title_text, count = head
        # header drawn into a separate list so it sits above the hatch
        h = Doc(d.tn, d)
        h.text(PAD, HATCH_H + 34, title_text, 20, 600, t["fg"])
        if count:
            tw = fonts.text_width(title_text, 20, 600)
            h.text(PAD + tw + 8, HATCH_H + 34, f"({count})", 12, 400, t["muted_fg"], mono=True)
        h.line(0, HATCH_H + HEAD_H, width, HATCH_H + HEAD_H)
        body = "".join(h.parts) + body

    face = fonts.font_face_css(d.used)
    clip_id = "clip"
    defs = "".join(d.defs)
    if frame:
        defs += f'<clipPath id="{clip_id}"><rect width="{width:g}" height="{height:g}" rx="12"/></clipPath>'
        strip = ""
        if head:
            d2 = Doc(d.tn, d)
            d2.hatch(0, 0, width, HATCH_H)
            d2.line(0, HATCH_H, width, HATCH_H)
            strip = "".join(d2.parts)
            defs = "".join(d.defs)  # hatch pattern registered by d2
            defs += f'<clipPath id="{clip_id}"><rect width="{width:g}" height="{height:g}" rx="12"/></clipPath>'
        inner = (
            f'<g clip-path="url(#{clip_id})"><rect width="{width:g}" height="{height:g}" fill="{t["bg"]}"/>{strip}{body}</g>'
            f'<rect x=".5" y=".5" width="{width - 1:g}" height="{height - 1:g}" rx="11.5" fill="none" stroke="{t["border"]}"/>'
        )
    else:
        inner = body
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width:g}" height="{height:g}" '
        f'viewBox="0 0 {width:g} {height:g}" role="img" aria-labelledby="t d">'
        f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
        f'<defs>{defs}</defs><style>{face}{STYLE_BASE}{css}</style>{inner}</svg>\n'
    )

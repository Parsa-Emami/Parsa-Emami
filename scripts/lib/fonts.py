"""Font helpers: text measurement (for wrapping text inside SVG cards) and
Geist subsetting/embedding so the cards render identically on every device.

Geist is (c) The Geist Project Authors, SIL Open Font License 1.1
(see scripts/fonts/LICENSE-Geist-OFL.txt). Embedding subsets is permitted.
"""
from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import ImageFont

FONT_DIR = Path(__file__).resolve().parents[1] / "fonts"
SANS_TTF = FONT_DIR / "Geist-Variable.ttf"
MONO_TTF = FONT_DIR / "GeistMono-Variable.ttf"

SANS_STACK = "Geist, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO_STACK = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# Safety margin: fallback fonts (when embedding is blocked) are usually a bit wider.
SLACK = 1.015


@lru_cache(maxsize=None)
def _pil_font(mono: bool, weight: int, size: float) -> ImageFont.FreeTypeFont:
    path = MONO_TTF if mono else SANS_TTF
    f = ImageFont.truetype(str(path), size=size, layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_axes([weight])
    return f


def text_width(text: str, size: float, weight: int = 400, mono: bool = False) -> float:
    """Advance width in px of ``text`` (kerning applied, small safety slack added)."""
    if not text:
        return 0.0
    return _pil_font(mono, weight, round(size, 2)).getlength(text) * SLACK


def wrap_text(text: str, max_width: float, size: float, weight: int = 400, mono: bool = False) -> list[str]:
    """Greedy word wrap using real glyph metrics."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if cur and text_width(trial, size, weight, mono) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------- #
# Embedding
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=None)
def _instance(mono: bool, weight: int) -> bytes:
    """Static TTF bytes for one weight of the variable font."""
    font = TTFont(str(MONO_TTF if mono else SANS_TTF), recalcTimestamp=False)
    inst = instancer.instantiateVariableFont(font, {"wght": weight}, inplace=False)
    buf = io.BytesIO()
    inst.save(buf)
    return buf.getvalue()


def _subset_woff2(ttf_bytes: bytes, chars: str) -> bytes:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "tnum", "case", "zero"]
    opts.notdef_outline = True
    opts.name_IDs = [1, 2]
    opts.hinting = False
    font = TTFont(io.BytesIO(ttf_bytes), recalcTimestamp=False)
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(font)
    out = io.BytesIO()
    font.flavor = "woff2"
    font.save(out)
    return out.getvalue()


def font_face_css(used: dict[tuple[bool, int], set[str]]) -> str:
    """@font-face rules (base64 woff2 subsets) for exactly the glyphs used.

    ``used`` maps ``(is_mono, weight)`` -> set of characters.
    """
    rules = []
    for (mono, weight), chars in sorted(used.items()):
        if not chars:
            continue
        data = _subset_woff2(_instance(mono, weight), "".join(sorted(chars)))
        b64 = base64.b64encode(data).decode("ascii")
        fam = "Geist Mono" if mono else "Geist"
        rules.append(
            f"@font-face{{font-family:'{fam}';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
        )
    return "".join(rules)


# --------------------------------------------------------------------------- #
# Website fonts (variable, Latin subset)
# --------------------------------------------------------------------------- #
LATIN_UNICODES = (
    "U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,"
    "U+2010-2015,U+2018-201E,U+2020-2022,U+2026,U+2030,U+2032-2033,U+2039-203A,"
    "U+20AC,U+2122,U+2190-2199,U+21B5,U+2212,U+25B2,U+25CF,U+25CB"
)


def write_site_fonts(out_dir: Path) -> list[Path]:
    """Write variable Geist Sans + Mono woff2 (Latin subset) for the website."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for src, name in ((SANS_TTF, "Geist-Variable.woff2"), (MONO_TTF, "GeistMono-Variable.woff2")):
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.hinting = False
        opts.notdef_outline = True
        opts.name_IDs = [1, 2]
        font = TTFont(str(src), recalcTimestamp=False)
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=subset.parse_unicodes(LATIN_UNICODES))
        sub.subset(font)
        font.flavor = "woff2"
        dst = out_dir / name
        font.save(str(dst))
        written.append(dst)
    lic = FONT_DIR / "LICENSE-Geist-OFL.txt"
    (out_dir / "LICENSE-Geist-OFL.txt").write_text(lic.read_text(encoding="utf-8"), encoding="utf-8")
    return written

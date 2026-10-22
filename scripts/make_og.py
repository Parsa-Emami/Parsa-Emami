from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from lib import content as C, fonts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site' / 'assets' / 'img' / 'og.png'


def build(p=None):
    p = p or C.load_profile()
    t = p['design']['themes']['light']
    image = Image.new('RGB', (1200, 630), t['paper'])
    draw = ImageDraw.Draw(image)
    for r in range(100, 1700, 36):
        draw.ellipse((1400-r, 130-r*.76, 1400+r, 130+r*.76), outline=t['border'], width=1)
    draw.text((58, 50), p['hero']['eyebrow'], font=fonts._pil_font(True, 400, 17), fill=t['subtle'])
    font = fonts._pil_font(False, 600, 176)
    name = p['person']['name']
    draw.text((50, 125), name, font=font, fill=t['ink'], stroke_width=0)
    x = 50 + draw.textlength(name, font=font)
    draw.text((x-1, 125), '.', font=font, fill=t['accent'])
    draw.line((60, 345, 1140, 345), fill=t['ink'], width=2)
    draw.text((60, 389), p['hero']['title'], font=fonts._pil_font(False, 400, 54), fill=t['ink'])
    draw.text((60, 458), p['hero']['accent'], font=fonts._pil_font(False, 400, 54), fill=t['accent'])
    draw.text((60, 574), p['person']['role'], font=fonts._pil_font(False, 400, 22), fill=t['text'])
    draw.text((937, 574), 'parsaaemm.dev', font=fonts._pil_font(True, 400, 18), fill=t['subtle'])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT, optimize=True)
    return OUT


if __name__ == '__main__':
    print(build())

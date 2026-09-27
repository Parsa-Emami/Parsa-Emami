#!/usr/bin/env python3
"""Render site/assets/img/og.png (1200x630) - the link-preview image.

Optional tool, only needed when your name/tagline/photo changes:

    pip install playwright && playwright install chromium
    python scripts/make_og.py
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from lib import content as C
from lib import fonts
from lib.svgkit import jpeg_data_uri

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "assets" / "img" / "og.png"


def html(p: dict) -> str:
    per = p["person"]
    chars = set(per["name"] + per["role"] + per["flip"][0] + per["coordinates"] + "parsa-emami.github.io/Fig. 1.") 
    css = fonts.font_face_css({(False, 600): chars, (False, 400): chars, (True, 400): chars})
    avatar = jpeg_data_uri(ROOT / "assets" / "avatar" / "avatar-dark.webp", 480, 88)
    host = p["site"]["url"].replace("https://", "").rstrip("/")
    return f"""<!doctype html><meta charset="utf-8"><style>{css}
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;background:#0a0a0a;color:#fafafa;font-family:Geist,system-ui,sans-serif;position:relative;overflow:hidden}}
.hatch{{position:absolute;left:0;right:0;background:repeating-linear-gradient(315deg,rgba(250,250,250,.08) 0,rgba(250,250,250,.08) 1px,transparent 0,transparent 50%) 0 0/12px 12px}}
.col{{position:absolute;top:0;bottom:0;width:1px;background:#2a2a2a}}
.row{{position:absolute;left:0;right:0;height:1px;background:#2a2a2a}}
.avatar{{position:absolute;left:150px;top:196px;width:238px;height:238px;border-radius:50%;background:url({avatar}) center/cover;box-shadow:0 0 0 10px #0a0a0a,0 0 0 11px #3a3a3a}}
.name{{position:absolute;left:452px;top:190px;font-size:92px;font-weight:600;letter-spacing:-.04em;line-height:1}}
.role{{position:absolute;left:456px;top:302px;font-size:32px;color:#a3a3a3}}
.flip{{position:absolute;left:456px;top:366px;font:400 28px 'Geist Mono',monospace;color:#a3a3a3}}
.fig{{position:absolute;right:100px;top:100px;font:400 20px 'Geist Mono',monospace;color:#a3a3a3}}
.fig b{{font-weight:400;color:#fafafa}}
.host{{position:absolute;left:100px;bottom:96px;font:400 24px 'Geist Mono',monospace;color:#a3a3a3}}
</style>
<div class="hatch" style="top:0;height:80px"></div><div class="hatch" style="bottom:0;height:80px"></div>
<div class="row" style="top:80px"></div><div class="row" style="bottom:80px"></div>
<div class="col" style="left:80px"></div><div class="col" style="right:80px"></div>
<div class="avatar"></div>
<div class="name">{per['name']}</div><div class="role">{per['role']}</div><div class="flip">{per['flip'][0]}</div>
<div class="fig"><b>Fig. 1.</b> {per['coordinates']}</div><div class="host">{host}</div>"""


async def main() -> None:
    from playwright.async_api import async_playwright

    p = C.load_profile()
    tmp = ROOT / "site" / "assets" / "img" / "_og.html"
    tmp.write_text(html(p), encoding="utf-8")
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.goto(tmp.as_uri())
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=str(OUT))
        await b.close()
    tmp.unlink()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())

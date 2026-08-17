#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-photo.jpg"
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "source-prepped.png"

image = Image.open(src).convert("RGBA")

# Background removal is optional at runtime. If rembg is unavailable, the script
# still produces a useful high-contrast portrait.
try:
    from rembg import remove
    image = remove(image)
    print("background: removed with rembg")
except Exception as exc:
    print(f"background: keeping original ({type(exc).__name__})")

# Composite transparency on white.
white = Image.new("RGBA", image.size, (255, 255, 255, 255))
white.alpha_composite(image)
gray = white.convert("L")

# Local-ish enhancement using only Pillow primitives.
gray = ImageOps.autocontrast(gray, cutoff=1)
gray = ImageEnhance.Contrast(gray).enhance(1.30)
gray = ImageEnhance.Brightness(gray).enhance(1.08)
gray = gray.filter(ImageFilter.UnsharpMask(radius=1.8, percent=125, threshold=3))

# Lift bright pixels toward white so the ASCII background becomes sparse.
gray = gray.point(lambda p: 255 if p > 238 else min(255, int(p * 1.035 + 6)))

gray.save(dst)
print(f"wrote {dst} ({gray.width}x{gray.height})")

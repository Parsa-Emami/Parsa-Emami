#!/usr/bin/env python3
"""Build the two avatar variants used by the README cards and the website.

    light theme -> graphite pencil sketch on white paper
    dark  theme -> the real photo, gently graded

Usage (run once locally, needs `pip install -r scripts/requirements-local.txt`):

    python scripts/prep_avatar.py                    # uses assets/source/source-photo.jpg
    python scripts/prep_avatar.py my-photo.jpg --cx 1015 --cy 1215 --size 1500

--cx/--cy/--size describe the square crop in ORIGINAL photo pixels
(centre x, centre y, side length). Tweak them until the face is centred.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "avatar"
SIZE = 512


def crop_square(img: np.ndarray, cx: int, cy: int, size: int) -> np.ndarray:
    h, w = img.shape[:2]
    size = min(size, h, w)
    x0 = int(np.clip(cx - size // 2, 0, w - size))
    y0 = int(np.clip(cy - size // 2, 0, h - size))
    return img[y0:y0 + size, x0:x0 + size]


def grade(img: np.ndarray) -> np.ndarray:
    """Lift shadows a little (CLAHE on luminance) while keeping natural colour."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l2 = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(6, 6)).apply(l)
    l = cv2.addWeighted(l, 0.45, l2, 0.55, 0)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def sketch(img: np.ndarray) -> np.ndarray:
    """Clean pencil sketch: denoise -> colour-dodge lines -> faint graphite shading."""
    sm = img
    for _ in range(2):
        sm = cv2.bilateralFilter(sm, d=9, sigmaColor=55, sigmaSpace=9)
    g = cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(255 - g, (0, 0), sigmaX=10)
    dodge = cv2.divide(g, 255 - blur, scale=256).astype(np.float32) / 255
    lines = np.clip((dodge - 0.20) / (0.99 - 0.20), 0, 1) ** 1.25

    lum = cv2.GaussianBlur(g, (0, 0), 6).astype(np.float32) / 255
    lum = np.clip((lum - 0.10) / 0.55, 0, 1)
    shading = 1 - (1 - lum) * 0.16
    out = np.clip(lines * shading, 0, 1)
    return (out * 255).astype(np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?", default=str(ROOT / "assets" / "source" / "source-photo.jpg"))
    ap.add_argument("--cx", type=int, default=1015)
    ap.add_argument("--cy", type=int, default=1215)
    ap.add_argument("--size", type=int, default=1500)
    args = ap.parse_args()

    src = cv2.imread(args.source)
    if src is None:
        raise SystemExit(f"cannot read {args.source}")
    face = cv2.resize(crop_square(src, args.cx, args.cy, args.size), (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    graded = grade(face)

    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "avatar-dark.webp"), graded, [cv2.IMWRITE_WEBP_QUALITY, 86])
    cv2.imwrite(str(OUT / "avatar-light.webp"), sketch(graded), [cv2.IMWRITE_WEBP_QUALITY, 88])
    print(f"wrote {OUT / 'avatar-dark.webp'} and {OUT / 'avatar-light.webp'} ({SIZE}x{SIZE})")


if __name__ == "__main__":
    main()

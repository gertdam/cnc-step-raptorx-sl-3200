#!/usr/bin/env python3
"""
Image pipeline for the CNC-Step RaptorX-SL 3200/S20 sales page.

Takes the raw iPhone photos in ./images (1-5 MB each, messy names with spaces
and '#'), and produces clean web-optimized assets:

  assets/img/<clean>.jpg    full / lightbox  (long edge 1600px, q80)
  assets/thumb/<clean>.jpg  gallery thumbs   (long edge 600px,  q75)
  assets/hero/hero-1600.jpg + hero-900.jpg   (hero, for <img srcset>)
  og-image.jpg                               (1200x630 social card)

It also REDACTS the previous owner's PII (Benutzername / Adresse / Email) on the
KinetiC-NC license screenshot with a solid white box before that image is written
anywhere, so the raw original never needs to be published.

Run once locally:  python3 scripts/optimize-images.py
Requires: Pillow.  (Raw ./images stays git-ignored; only assets/ is published.)
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images"
IMG = ROOT / "assets" / "img"
THUMB = ROOT / "assets" / "thumb"
HERO = ROOT / "assets" / "hero"
for d in (IMG, THUMB, HERO):
    d.mkdir(parents=True, exist_ok=True)

# source filename -> clean kebab-case basename
MAPPING = {
    "cnc front.jpg": "cnc-front",
    "cnc front 2.jpg": "cnc-front-2",
    "cnc back.jpg": "cnc-back",
    "cnc top.jpg": "cnc-top",
    "cnc sn#.jpg": "cnc-serial",
    "cnc step sn#.jpg": "cnc-step-serial",
    "spindle 1.jpg": "spindle-1",
    "spindle 2 sn#.jpg": "spindle-serial",
    "controls cabinet.jpg": "controls-cabinet",
    "computer cabinet.jpg": "computer-cabinet",
    "kinetic controls box.jpg": "kinetic-controls-box",
    "operating-hours (minimal).jpg": "operating-hours",
    "toolling.jpg": "tooling",
    "more tooling.jpg": "tooling-more",
    "kinetic nc registration 1st owner.jpg": "kinetic-registration",
}

HERO_SRC = "cnc front.jpg"
PII_SRC = "kinetic nc registration 1st owner.jpg"

# PII redaction box as fractions of (width, height) of the upright image.
# Covers the Benutzername / Adresse / Email value column; stays above the
# "Uneingeschraenkte Vollversion" line and right of the field labels.
PII_BOX_FRAC = (0.345, 0.418, 0.945, 0.560)  # (left, top, right, bottom)


def load_upright(path: Path) -> Image.Image:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)  # bake in iPhone orientation
    return im.convert("RGB")


def redact(im: Image.Image) -> Image.Image:
    w, h = im.size
    l, t, r, b = PII_BOX_FRAC
    box = (int(l * w), int(t * h), int(r * w), int(b * h))
    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=(255, 255, 255))
    return im


def resize_long_edge(im: Image.Image, max_edge: int) -> Image.Image:
    out = im.copy()
    out.thumbnail((max_edge, max_edge), Image.LANCZOS)
    return out


def save_jpg(im: Image.Image, path: Path, quality: int):
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)


def cover_crop(im: Image.Image, tw: int, th: int) -> Image.Image:
    w, h = im.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale + 0.5), int(h * scale + 0.5)
    r = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return r.crop((x, y, x + tw, y + th))


def main():
    missing = [s for s in MAPPING if not (SRC / s).exists()]
    if missing:
        raise SystemExit(f"Missing source images: {missing}")

    for src_name, clean in MAPPING.items():
        im = load_upright(SRC / src_name)
        if src_name == PII_SRC:
            im = redact(im)
            print(f"  redacted PII on {src_name}")
        save_jpg(resize_long_edge(im, 1600), IMG / f"{clean}.jpg", 80)
        save_jpg(resize_long_edge(im, 600), THUMB / f"{clean}.jpg", 75)
        print(f"  {src_name:40s} -> {clean}.jpg")

    # Hero variants + OG card from the front shot
    hero = load_upright(SRC / HERO_SRC)
    save_jpg(resize_long_edge(hero, 1600), HERO / "hero-1600.jpg", 82)
    save_jpg(resize_long_edge(hero, 900), HERO / "hero-900.jpg", 82)
    save_jpg(cover_crop(hero, 1200, 630), ROOT / "og-image.jpg", 85)
    print("  hero-1600 / hero-900 / og-image.jpg written")
    print("Done.")


if __name__ == "__main__":
    main()

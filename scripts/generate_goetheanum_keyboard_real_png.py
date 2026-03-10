#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont


ROWS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "ß", "´"],
    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"],
    ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"],
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate real keyboard mapping preview from font glyphs.")
    p.add_argument(
        "--font",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1/Goetheanum-v1.2.1-Klar.otf"),
    )
    p.add_argument(
        "--out-png",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1/goetheanum-keyboard-real-mac-de.png"),
    )
    return p.parse_args()


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def key_mapping() -> dict[str, int]:
    return {
        "1": 0xE100,
        "2": 0xE101,
        "3": 0xE102,
        "4": 0xE103,
    }


def centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont, fill: str) -> None:
    l, t, r, b = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = l + (r - l - tw) // 2
    y = t + (b - t - th) // 2
    draw.text((x, y), text, font=font, fill=fill)


def main() -> None:
    args = parse_args()
    args.out_png.parent.mkdir(parents=True, exist_ok=True)

    tt = TTFont(str(args.font))
    cmap = tt.getBestCmap() or {}
    available = set(cmap.keys())
    tt.close()

    img = Image.new("RGB", (1280, 560), "#f4f7fb")
    d = ImageDraw.Draw(img)

    title = load_font(44, bold=True)
    sub = load_font(20, bold=False)
    label = load_font(18, bold=True)
    small = load_font(15, bold=False)
    icon_font = ImageFont.truetype(str(args.font), size=28)

    d.text((40, 28), "Goetheanum Keyboard (real glyph view, macOS DE)", font=title, fill="#1f3040")
    d.text((40, 84), "Nur bereits vorhandene Piktogramme werden als Symbol gezeigt.", font=sub, fill="#4d6174")

    key_w = 84
    key_h = 72
    gap = 10
    row_offsets = [0, 20, 40, 60]

    mapping = key_mapping()
    y0 = 130
    for ridx, row in enumerate(ROWS):
        y = y0 + ridx * (key_h + gap)
        x = 40 + row_offsets[ridx]
        for key in row:
            cp = mapping.get(key)
            active = cp in available if cp is not None else False
            fill = "#ffffff" if active else "#f9fbfd"
            border = "#9db3c7" if active else "#d4dee7"
            d.rounded_rectangle((x, y, x + key_w, y + key_h), radius=10, fill=fill, outline=border, width=2)
            d.text((x + 8, y + 6), key, font=label, fill="#203348")

            if cp is None:
                d.text((x + 8, y + 46), "frei", font=small, fill="#8aa0b2")
            elif active:
                centered_text(d, (x + 28, y + 18, x + key_w - 6, y + key_h - 10), chr(cp), icon_font, "#17304a")
                d.text((x + 8, y + 46), f"U+{cp:04X}", font=small, fill="#3f5870")
            else:
                d.text((x + 8, y + 46), f"U+{cp:04X} fehlt", font=small, fill="#8aa0b2")

            x += key_w + gap

    d.text((40, 510), "Aktuell im Font enthalten: 1=E100, 2=E101, 3=E102, 4=E103", font=sub, fill="#4d6174")

    img.save(args.out_png)
    print(args.out_png)


if __name__ == "__main__":
    main()

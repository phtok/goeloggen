#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROWS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "ß", "´"],
    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"],
    ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"],
]

LETTER_ORDER = list("qwertzuiopasdfghjklyxcvbnm")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Goetheanum keyboard mapping visual (PNG).")
    p.add_argument(
        "--out-png",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1/goetheanum-icons-keyboard-mac-de.png"),
    )
    return p.parse_args()


def mapping_lower() -> dict[str, int]:
    m: dict[str, int] = {"1": 0xE100, "2": 0xE101, "3": 0xE102, "4": 0xE103}
    for idx, key in enumerate(LETTER_ORDER):
        m[key] = 0xE200 + idx
    return m


def mapping_upper() -> dict[str, int]:
    m: dict[str, int] = {"1": 0xE100, "2": 0xE101, "3": 0xE102, "4": 0xE103}
    for idx, key in enumerate(LETTER_ORDER):
        m[key] = 0xE240 + idx
    return m


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_board(
    draw: ImageDraw.ImageDraw,
    title: str,
    x0: int,
    y0: int,
    mapping: dict[str, int],
    title_font: ImageFont.ImageFont,
    key_font: ImageFont.ImageFont,
    cp_font: ImageFont.ImageFont,
) -> None:
    key_w = 72
    key_h = 62
    gap = 8
    row_offsets = [0, 18, 36, 54]

    draw.text((x0, y0 - 34), title, fill="#1f3040", font=title_font)

    y = y0
    for ridx, row in enumerate(ROWS):
        x = x0 + row_offsets[ridx]
        for key in row:
            draw.rounded_rectangle(
                (x, y, x + key_w, y + key_h),
                radius=9,
                fill="#ffffff",
                outline="#cfd9e2",
                width=2,
            )
            draw.text((x + 10, y + 8), key, fill="#203348", font=key_font)
            cp = mapping.get(key.lower())
            if cp is not None:
                draw.text((x + 10, y + 36), f"U+{cp:04X}", fill="#3f5870", font=cp_font)
            x += key_w + gap
        y += key_h + gap


def main() -> None:
    args = parse_args()
    args.out_png.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (1980, 760), "#f4f7fb")
    draw = ImageDraw.Draw(img)

    title_font = font(44, bold=True)
    sub_font = font(20, bold=False)
    board_font = font(28, bold=True)
    key_font = font(20, bold=True)
    cp_font = font(16, bold=False)
    foot_font = font(18, bold=False)

    draw.text(
        (48, 34),
        "Goetheanum Icons Keyboard (macOS, DE) - Vorschlag",
        fill="#1f3040",
        font=title_font,
    )
    draw.text(
        (48, 90),
        "Logos auf 1-4. Piktos: a-z als Basis, Shift+a-z als Varianten. Eigene Eingabequelle 'Goetheanum Icons'.",
        fill="#4d6174",
        font=sub_font,
    )

    draw_board(draw, "Ebene 1: ohne Shift (Basis-Piktos)", 48, 150, mapping_lower(), board_font, key_font, cp_font)
    draw_board(draw, "Ebene 2: mit Shift (Variante/Fill)", 1020, 150, mapping_upper(), board_font, key_font, cp_font)

    draw.text(
        (48, 718),
        "Logo-Codes: 1=E100, 2=E101, 3=E102, 4=E103 | Piktos Basis: E200-E219 | Piktos Shift: E240-E259",
        fill="#4d6174",
        font=foot_font,
    )

    img.save(args.out_png)
    print(args.out_png)


if __name__ == "__main__":
    main()

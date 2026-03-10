#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROWS = [
    {
        "offset": 0,
        "keys": [18, 19, 20, 21, 23, 22, 26, 28, 25, 29, 27, 24],
        "lower": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "ß", "´"],
        "upper": ["!", '"', "§", "$", "%", "&", "/", "(", ")", "=", "?", "`"],
    },
    {
        "offset": 22,
        "keys": [12, 13, 14, 15, 17, 16, 32, 34, 31, 35, 33, 30],
        "lower": ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"],
        "upper": ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü", "*"],
    },
    {
        "offset": 44,
        "keys": [0, 1, 2, 3, 5, 4, 38, 40, 37, 39, 41, 42],
        "lower": ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"],
        "upper": ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "'"],
    },
    {
        "offset": 66,
        "keys": [10, 6, 7, 8, 9, 11, 45, 46, 43, 47, 44],
        "lower": ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"],
        "upper": [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_"],
    },
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate clean A4 keyboard overview PNGs for Goetheanum Icons.")
    p.add_argument("--font-icons", type=Path, required=True)
    p.add_argument("--font-title", type=Path, required=True)
    p.add_argument("--font-subtitle", type=Path, required=True)
    p.add_argument("--font-keys", type=Path, required=True)
    p.add_argument("--mapping-json", type=Path, required=True)
    p.add_argument("--out-lower", type=Path, required=True)
    p.add_argument("--out-upper", type=Path, required=True)
    return p.parse_args()


def centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont, fill: str) -> None:
    l, t, r, b = box
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    x = l + (r - l - tw) // 2 - bb[0]
    y = t + (b - t - th) // 2 - bb[1]
    draw.text((x, y), text, font=font, fill=fill)


def draw_glyph_fit(
    draw: ImageDraw.ImageDraw,
    glyph: str,
    icon_font_path: Path,
    box: tuple[int, int, int, int],
    max_size: int,
    min_size: int,
    fill: str,
) -> None:
    l, t, r, b = box
    bw = r - l
    bh = b - t
    cache: dict[int, ImageFont.ImageFont] = {}
    chosen = None
    for sz in range(max_size, min_size - 1, -2):
        f = cache.get(sz)
        if f is None:
            f = ImageFont.truetype(str(icon_font_path), size=sz)
            cache[sz] = f
        bb = draw.textbbox((0, 0), glyph, font=f)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        if tw <= bw and th <= bh:
            chosen = f
            break
    if chosen is None:
        chosen = ImageFont.truetype(str(icon_font_path), size=min_size)
    centered(draw, box, glyph, chosen, fill)


def draw_sheet(
    *,
    mapping_by_keycode: dict[int, dict[str, str]],
    icon_font_path: Path,
    title_font_path: Path,
    subtitle_font_path: Path,
    key_font_path: Path,
    key_mode: str,
    out_path: Path,
) -> None:
    # A4 landscape at 300 dpi.
    w, h = 3508, 2480
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    c_text = "#111111"
    c_sub = "#444444"
    c_border = "#2f2f2f"

    f_title = ImageFont.truetype(str(title_font_path), size=96)
    f_sub = ImageFont.truetype(str(subtitle_font_path), size=52)
    f_key = ImageFont.truetype(str(key_font_path), size=46)

    d.text((120, 95), "Goetheanum Icons Keyboard", font=f_title, fill=c_text)
    subtitle = "Kleinbuchstaben MacOS DE" if key_mode == "lower" else "Großbuchstaben MacOS DE"
    d.text((120, 205), subtitle, font=f_sub, fill=c_sub)

    margin_x = 120
    grid_y = 340
    key_w = 259
    key_h = 430
    gap_x = 14
    gap_y = 26

    for row_idx, row in enumerate(ROWS):
        labels = row[key_mode]
        x = margin_x + row["offset"] * 2
        y = grid_y + row_idx * (key_h + gap_y)
        for keycode, key_label in zip(row["keys"], labels):
            d.rounded_rectangle((x, y, x + key_w, y + key_h), radius=14, outline=c_border, width=2, fill="#FFFFFF")
            d.text((x + 14, y + 12), key_label, font=f_key, fill=c_text)

            icon = mapping_by_keycode.get(keycode)
            if icon is not None:
                glyph = icon.get("upper_glyph", icon["glyph"]) if key_mode == "upper" else icon["glyph"]
                cp_hex = icon.get("upper_codepoint", icon.get("codepoint", "")) if key_mode == "upper" else icon.get("codepoint", "")
                try:
                    cp = int(str(cp_hex).replace("U+", "0x"), 16)
                except ValueError:
                    cp = -1
                # Wide desktop logo (with text) needs a smaller min size to avoid clipping.
                if cp in {0xE100, 0xE140}:
                    max_sz = 120
                    min_sz = 20
                else:
                    max_sz = 180 if key_mode == "lower" else 162
                    min_sz = 44
                draw_glyph_fit(
                    d,
                    glyph,
                    icon_font_path,
                    (x + 16, y + 90, x + key_w - 16, y + key_h - 24),
                    max_size=max_sz,
                    min_size=min_sz,
                    fill=c_text,
                )
            x += key_w + gap_x

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def main() -> None:
    args = parse_args()
    data = json.loads(args.mapping_json.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    mapping_by_keycode: dict[int, dict[str, str]] = {int(r["keycode"]): r for r in rows}

    draw_sheet(
        mapping_by_keycode=mapping_by_keycode,
        icon_font_path=args.font_icons,
        title_font_path=args.font_title,
        subtitle_font_path=args.font_subtitle,
        key_font_path=args.font_keys,
        key_mode="lower",
        out_path=args.out_lower,
    )
    draw_sheet(
        mapping_by_keycode=mapping_by_keycode,
        icon_font_path=args.font_icons,
        title_font_path=args.font_title,
        subtitle_font_path=args.font_subtitle,
        key_font_path=args.font_keys,
        key_mode="upper",
        out_path=args.out_upper,
    )
    print(args.out_lower)
    print(args.out_upper)


if __name__ == "__main__":
    main()

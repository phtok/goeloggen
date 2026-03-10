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
    p = argparse.ArgumentParser(description="Generate didactic Goetheanum icon keyboard PNGs.")
    p.add_argument("--font", type=Path, required=True)
    p.add_argument("--mapping-json", type=Path, required=True)
    p.add_argument("--out-lower", type=Path, required=True)
    p.add_argument("--out-upper", type=Path, required=True)
    return p.parse_args()


def load_ui_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_label(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        test = f"{cur} {w}"
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines[:2]


def centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont, fill: str) -> None:
    l, t, r, b = box
    bb = draw.textbbox((0, 0), text, font=font)
    x = l + (r - l - (bb[2] - bb[0])) // 2
    y = t + (b - t - (bb[3] - bb[1])) // 2
    draw.text((x, y), text, font=font, fill=fill)


def draw_layout(
    out_path: Path,
    title: str,
    subtitle: str,
    row_key_label_mode: str,
    mapping_by_keycode: dict[int, dict[str, str]],
    icon_font: ImageFont.ImageFont,
    icon_font_wide: ImageFont.ImageFont,
    icon_count: int,
    show_long_labels: bool,
) -> None:
    img = Image.new("RGB", (2240, 1320), "#f4f7fb")
    d = ImageDraw.Draw(img)

    f_title = load_ui_font(58, bold=True)
    f_sub = load_ui_font(30, bold=False)
    f_key = load_ui_font(30, bold=True)
    f_code = load_ui_font(20, bold=False)
    f_label = load_ui_font(25, bold=True)
    f_small = load_ui_font(18, bold=False)

    d.text((52, 34), title, font=f_title, fill="#1f3040")
    d.text((52, 108), subtitle, font=f_sub, fill="#4d6174")

    key_w = 164
    key_h = 220
    gap = 12
    row_gap = 14
    y = 180

    for row in ROWS:
        x = 52 + row["offset"]
        labels = row[row_key_label_mode]
        for keycode, key_label in zip(row["keys"], labels):
            icon = mapping_by_keycode.get(keycode)
            active = icon is not None

            fill = "#ffffff" if active else "#edf3f8"
            border = "#9db3c7" if active else "#d4dee8"
            d.rounded_rectangle((x, y, x + key_w, y + key_h), radius=14, fill=fill, outline=border, width=2)
            d.text((x + 10, y + 8), key_label, font=f_key, fill="#203348")

            if active:
                glyph = icon.get("upper_glyph", icon["glyph"]) if row_key_label_mode == "upper" else icon["glyph"]
                cp_txt = icon.get("upper_codepoint", icon["codepoint"]) if row_key_label_mode == "upper" else icon["codepoint"]
                cp = int(cp_txt[2:], 16)
                use_icon_font = icon_font_wide if cp in {0xE103, 0xE143} else icon_font
                centered(d, (x + 8, y + 38, x + key_w - 8, y + 110), glyph, use_icon_font, "#17304a")
                code = icon["codepoint"]
                centered(d, (x + 6, y + 116, x + key_w - 6, y + 142), code, f_code, "#3f5870")
                label_lines = wrap_label(d, icon["label"], f_label, key_w - 14)
                y0 = y + 150
                for li, line in enumerate(label_lines):
                    centered(d, (x + 7, y0 + li * 28, x + key_w - 7, y0 + li * 28 + 24), line, f_label, "#29435f")
                if show_long_labels and row_key_label_mode == "upper":
                    # On uppercase proof we explicitly show the output behavior.
                    centered(
                        d,
                        (x + 6, y + 202, x + key_w - 6, y + 216),
                        "Output: Icon + Label",
                        f_small,
                        "#6c7f91",
                    )
            else:
                centered(d, (x + 8, y + 150, x + key_w - 8, y + 176), "frei", f_label, "#8aa0b2")

            x += key_w + gap
        y += key_h + row_gap

    footer = f"Belegte Tasten: {icon_count} | Reihenfolge: macOS DE | Quelle: Goetheanum Icons Mapping"
    d.text((52, 1274), footer, font=f_sub, fill="#4d6174")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def main() -> None:
    args = parse_args()
    data = json.loads(args.mapping_json.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    mapping_by_keycode: dict[int, dict[str, str]] = {int(r["keycode"]): r for r in rows}
    icon_font = ImageFont.truetype(str(args.font), size=78)
    icon_font_wide = ImageFont.truetype(str(args.font), size=30)

    draw_layout(
        args.out_lower,
        "Goetheanum Icons Keyboard – Ebene Kleinbuchstaben",
        "Didaktische Ansicht: ohne Shift, Icon-only",
        "lower",
        mapping_by_keycode,
        icon_font,
        icon_font_wide,
        len(rows),
        show_long_labels=False,
    )
    draw_layout(
        args.out_upper,
        "Goetheanum Icons Keyboard – Ebene Großbuchstaben",
        "Didaktische Ansicht: mit Shift, Icon + Label-Ausgabe",
        "upper",
        mapping_by_keycode,
        icon_font,
        icon_font_wide,
        len(rows),
        show_long_labels=True,
    )

    print(args.out_lower)
    print(args.out_upper)


if __name__ == "__main__":
    main()

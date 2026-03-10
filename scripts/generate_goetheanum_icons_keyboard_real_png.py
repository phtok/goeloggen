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
        "offset": 20,
        "keys": [12, 13, 14, 15, 17, 16, 32, 34, 31, 35, 33, 30],
        "lower": ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"],
        "upper": ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü", "*"],
    },
    {
        "offset": 40,
        "keys": [0, 1, 2, 3, 5, 4, 38, 40, 37, 39, 41, 42],
        "lower": ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"],
        "upper": ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "'"],
    },
    {
        "offset": 60,
        "keys": [10, 6, 7, 8, 9, 11, 45, 46, 43, 47, 44],
        "lower": ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"],
        "upper": [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_"],
    },
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate real key-to-icon keyboard proof (macOS DE).")
    p.add_argument(
        "--font",
        type=Path,
        default=Path("/Users/philipptok/goeloggen/output/goetheanum-icons/v0.2.0/Goetheanum-Icons-v0.2.0-Filled.otf"),
    )
    p.add_argument(
        "--mapping-json",
        type=Path,
        default=Path("/Users/philipptok/goeloggen/output/goetheanum-icons/v0.2.0/keyboard-mapping-v0.2.0.json"),
    )
    p.add_argument(
        "--out-png",
        type=Path,
        default=Path("/Users/philipptok/goeloggen/output/goetheanum-icons/v0.2.0/goetheanum-icons-keyboard-real-mac-de-v0.2.0.png"),
    )
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


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
) -> None:
    l, t, r, b = box
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    x = l + (r - l - tw) // 2
    y = t + (b - t - th) // 2
    draw.text((x, y), text, font=font, fill=fill)


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_w: int,
) -> str:
    if draw.textbbox((0, 0), text, font=font)[2] <= max_w:
        return text
    candidate = text
    while len(candidate) > 4:
        candidate = candidate[:-1]
        t = candidate.rstrip() + "…"
        if draw.textbbox((0, 0), t, font=font)[2] <= max_w:
            return t
    return text[:3] + "…"


def draw_board(
    draw: ImageDraw.ImageDraw,
    title: str,
    subtitle: str,
    x0: int,
    y0: int,
    row_key_label_mode: str,
    mapping_by_keycode: dict[int, dict[str, str]],
    available_codepoints: set[int] | None,
    fonts: dict[str, ImageFont.ImageFont],
) -> None:
    key_w = 96
    key_h = 96
    gap = 10
    row_gap = 10

    draw.text((x0, y0 - 42), title, font=fonts["board_title"], fill="#1f3040")
    draw.text((x0, y0 - 16), subtitle, font=fonts["sub"], fill="#4d6174")

    y = y0
    for row in ROWS:
        x = x0 + row["offset"]
        labels = row[row_key_label_mode]
        for keycode, key_label in zip(row["keys"], labels):
            icon = mapping_by_keycode.get(keycode)
            has_icon = icon is not None
            cp = int(icon["codepoint"][2:], 16) if icon else None
            cp_ok = (cp in available_codepoints) if (cp is not None and available_codepoints is not None) else True

            fill = "#ffffff" if has_icon else "#f6f9fc"
            border = "#9db3c7" if has_icon else "#d5dfe8"
            draw.rounded_rectangle(
                (x, y, x + key_w, y + key_h),
                radius=11,
                fill=fill,
                outline=border,
                width=2,
            )
            draw.text((x + 8, y + 7), key_label, font=fonts["key"], fill="#203348")

            if has_icon and cp_ok:
                glyph = icon.get("upper_glyph", icon["glyph"]) if row_key_label_mode == "upper" else icon["glyph"]
                use_font = fonts["icon_wide"] if cp in {0xE103, 0xE143} else fonts["icon"]
                centered_text(
                    draw,
                    (x + 8, y + 22, x + key_w - 8, y + 60),
                    glyph,
                    use_font,
                    "#17304a",
                )
                label = fit_text(draw, icon["label"], fonts["tiny"], key_w - 14)
                centered_text(
                    draw,
                    (x + 7, y + 62, x + key_w - 7, y + 80),
                    label,
                    fonts["tiny"],
                    "#3f5870",
                )
            elif has_icon:
                centered_text(
                    draw,
                    (x + 7, y + 30, x + key_w - 7, y + 66),
                    "fehlend",
                    fonts["tiny"],
                    "#9e4e4e",
                )
            else:
                centered_text(
                    draw,
                    (x + 7, y + 64, x + key_w - 7, y + 82),
                    "frei",
                    fonts["tiny"],
                    "#8aa0b2",
                )

            x += key_w + gap
        y += key_h + row_gap


def main() -> None:
    args = parse_args()
    args.out_png.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(args.mapping_json.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    mapping_by_keycode: dict[int, dict[str, str]] = {int(r["keycode"]): r for r in rows}
    cps = [int(r["codepoint"][2:], 16) for r in rows if "codepoint" in r]
    cp_min = min(cps) if cps else 0
    cp_max = max(cps) if cps else 0

    available: set[int] | None = None

    img = Image.new("RGB", (2360, 880), "#f4f7fb")
    d = ImageDraw.Draw(img)

    fonts = {
        "title": load_ui_font(58, bold=True),
        "sub": load_ui_font(28, bold=False),
        "board_title": load_ui_font(34, bold=True),
        "key": load_ui_font(27, bold=True),
        "tiny": load_ui_font(17, bold=False),
        "foot": load_ui_font(24, bold=False),
        "icon": ImageFont.truetype(str(args.font), size=40),
        "icon_wide": ImageFont.truetype(str(args.font), size=24),
    }

    d.text((50, 34), "Goetheanum Icons Keyboard (real glyph view, macOS DE)", font=fonts["title"], fill="#1f3040")
    d.text(
        (50, 104),
        "Links: ohne Shift (Icon-only). Rechts: mit Shift (Icon + Label-Ausgabe).",
        font=fonts["sub"],
        fill="#4d6174",
    )

    draw_board(
        d,
        "Ebene 1: ohne Shift",
        "Kleinbuchstaben -> Icon ohne Text",
        50,
        180,
        "lower",
        mapping_by_keycode,
        available,
        fonts,
    )
    draw_board(
        d,
        "Ebene 2: mit Shift",
        "Großbuchstaben -> Icon + Labeltext",
        1210,
        180,
        "upper",
        mapping_by_keycode,
        available,
        fonts,
    )

    d.text(
        (50, 836),
        f"Icons belegt: {len(rows)} | Bereich: U+{cp_min:04X}-U+{cp_max:04X} | Layout: {data.get('layout_name', 'Goetheanum Icons (DE)')}",
        font=fonts["foot"],
        fill="#4d6174",
    )

    img.save(args.out_png)
    print(args.out_png)


if __name__ == "__main__":
    main()

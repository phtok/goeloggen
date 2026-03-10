#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int, bold: bool = False):
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


def key(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, w: int = 88, h: int = 64, fill: str = "#ffffff"):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=10, fill=fill, outline="#9db3c7", width=2)
    f = load_font(28, bold=True)
    bbox = draw.textbbox((0, 0), label, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) // 2, y + (h - th) // 2 - 2), label, font=f, fill="#17304a")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out-png",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1/Goetheanum-Logos-Prefix-Anleitung.png"),
    )
    args = ap.parse_args()
    args.out_png.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (1500, 860), "#f4f7fb")
    d = ImageDraw.Draw(img)

    title = load_font(52, bold=True)
    h2 = load_font(34, bold=True)
    txt = load_font(26, bold=False)
    small = load_font(22, bold=False)
    logo_font = ImageFont.truetype(
        "/Users/philipptok/goeloggen/output/goetheanum-fonts/v1.2.1/Goetheanum-v1.2.1-Klar.otf", size=32
    )
    logo_font_wide = ImageFont.truetype(
        "/Users/philipptok/goeloggen/output/goetheanum-fonts/v1.2.1/Goetheanum-v1.2.1-Klar.otf", size=18
    )

    d.text((56, 44), "Goetheanum Logos eingeben (Mac)", font=title, fill="#1f3040")
    d.text((56, 118), "Einfachste Anleitung fuer Laien", font=txt, fill="#4d6174")

    d.text((56, 196), "Schritt 1: Prefix druecken", font=h2, fill="#1f3040")
    d.text((56, 244), "Druecke gleichzeitig Option + Shift + -", font=txt, fill="#2f4458")
    key(d, 70, 292, "OPT")
    key(d, 176, 292, "SHIFT")
    key(d, 282, 292, "-")

    d.text((56, 418), "Schritt 2: direkt danach die Logo-Taste", font=h2, fill="#1f3040")
    d.text((56, 466), "1 = Icon   2 = Point   3 = Square   4 = Desktop", font=txt, fill="#2f4458")

    x = 70
    for i, cp in enumerate([0xE100, 0xE101, 0xE102, 0xE103], start=1):
        key(d, x, 516, str(i), w=120, h=88, fill="#ffffff")
        d.text((x + 10, 612), f"U+E10{i-1}", font=small, fill="#4d6174")
        use_font = logo_font_wide if cp == 0xE103 else logo_font
        d.text((x + 66, 540), chr(cp), font=use_font, fill="#17304a", anchor="mm")
        x += 148

    d.rounded_rectangle((56, 710, 1444, 812), radius=12, fill="#e9f0f7", outline="#c8d8e6", width=2)
    d.text(
        (78, 740),
        "Wenn nichts erscheint: Font 'Goetheanum' aktivieren und Eingabequelle 'Goetheanum Logos Prefix (DE)' auswaehlen.",
        font=small,
        fill="#2f4458",
    )

    img.save(args.out_png)
    print(args.out_png)


if __name__ == "__main__":
    main()

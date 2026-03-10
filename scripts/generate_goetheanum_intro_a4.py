#!/usr/bin/env python3
from __future__ import annotations

import argparse
import textwrap
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate A4 intro sheet for Goetheanum font family.")
    p.add_argument("--font-leise", type=Path, required=True)
    p.add_argument("--font-klar", type=Path, required=True)
    p.add_argument("--font-laut", type=Path, required=True)
    p.add_argument("--font-variabel", type=Path, required=True)
    p.add_argument("--font-icons", type=Path, required=True)
    p.add_argument("--version", default="1.3.4")
    p.add_argument("--out-png", type=Path, required=True)
    p.add_argument("--out-pdf", type=Path, required=True)
    return p.parse_args()


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    font: ImageFont.FreeTypeFont,
    fill: str = "#1B1B1B",
    line_gap: int = 8,
) -> int:
    x0, y0, x1, y1 = box
    y = y0
    max_width = x1 - x0
    words = text.split()
    line = ""
    lines: list[str] = []
    for w in words:
        probe = f"{line} {w}".strip()
        bb = draw.textbbox((0, 0), probe, font=font)
        if (bb[2] - bb[0]) <= max_width:
            line = probe
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    for ln in lines:
        bb = draw.textbbox((0, 0), ln, font=font)
        h = bb[3] - bb[1]
        if y + h > y1:
            break
        draw.text((x0, y), ln, font=font, fill=fill)
        y += h + line_gap
    return y


def main() -> None:
    args = parse_args()

    # A4 portrait at 300dpi
    w, h = 2480, 3508
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    c_main = "#111111"
    c_sub = "#4A4A4A"
    c_rule = "#D3D3D3"
    c_box = "#F8F8F8"

    f_title = load_font(args.font_laut, 128)
    f_subtitle = load_font(args.font_leise, 54)
    f_h2 = load_font(args.font_laut, 52)
    f_label = load_font(args.font_klar, 42)
    f_body = load_font(args.font_klar, 34)
    f_small = load_font(args.font_leise, 28)
    f_sample_leise = load_font(args.font_leise, 68)
    f_sample_klar = load_font(args.font_klar, 68)
    f_sample_laut = load_font(args.font_laut, 68)
    f_sample_var = load_font(args.font_variabel, 68)
    f_icon = load_font(args.font_icons, 70)

    margin = 140
    y = 120

    d.text((margin, y), "Goetheanum Schriften", font=f_title, fill=c_main)
    y += 150
    d.text((margin, y), "Einfuhrung fuer neue Nutzer", font=f_subtitle, fill=c_sub)
    y += 80
    d.line((margin, y, w - margin, y), fill=c_rule, width=3)
    y += 40

    d.text((margin, y), "Die fuenf Schnitte", font=f_h2, fill=c_main)
    y += 74

    sample_left = margin
    sample_right = w - margin
    row_h = 190

    rows = [
        ("Leise", "ruhiger Ton, Introzeilen, Zwischenueberschriften, feine Hinweise", "Leise: «Goetheanum Kultur und Dialog»", f_sample_leise),
        ("Klar", "Standard fuer Lauftext und Alltag, beste Lesbarkeit", "Klar: «Goetheanum Kommunikation im Alltag»", f_sample_klar),
        ("Laut", "starker Akzent, Headlines, Calls-to-action, Signaletik", "Laut: «Goetheanum Programm Heute»", f_sample_laut),
        ("Variabel", "flexibel fuer digitale Layouts, hier als stabiler Standardschnitt", "Variabel: «Goetheanum flexibel einsetzen»", f_sample_var),
    ]

    for name, desc, sample, sample_font in rows:
        d.rounded_rectangle((sample_left, y, sample_right, y + row_h), radius=18, outline=c_rule, width=2, fill="#FFFFFF")
        d.text((sample_left + 24, y + 22), name, font=f_label, fill=c_main)
        draw_wrapped(d, desc, (sample_left + 260, y + 28, sample_right - 26, y + 86), f_small, fill=c_sub, line_gap=4)
        d.text((sample_left + 24, y + 98), sample, font=sample_font, fill=c_main)
        y += row_h + 18

    # Icons block
    d.rounded_rectangle((sample_left, y, sample_right, y + 250), radius=18, outline=c_rule, width=2, fill="#FFFFFF")
    d.text((sample_left + 24, y + 20), "Icons", font=f_label, fill=c_main)
    draw_wrapped(
        d,
        "Nur fuer Piktogramme und Logos. Direktbelegung: 1 Logo, 2 Point, 3 Square, 4 Icon. "
        "Kleinbuchstaben sind icon-only, Grossbuchstaben enthalten icon+label.",
        (sample_left + 260, y + 26, sample_right - 24, y + 110),
        f_small,
        fill=c_sub,
        line_gap=4,
    )
    d.text((sample_left + 24, y + 138), "1234   qwertuiop   asdfghjkl", font=f_icon, fill=c_main)
    y += 274

    d.text((margin, y), "Schnelle Einsatzregeln", font=f_h2, fill=c_main)
    y += 70
    rules = [
        "Leise nicht fuer Fliesstext-Mengen, sondern als Gegenstimme und Rhythmusgeber.",
        "Klar ist der Standard in Sekretariat, Korrespondenz, Dokumenten und Formularen.",
        "Laut gezielt einsetzen: Titel, Navigation, Schilder, Hervorhebungen.",
        "Variabel fuer konsistente Anwendungen ohne Stilwechsel.",
        "Icons immer mit Genuegend Abstand setzen (mindestens ein Leerzeichen).",
    ]
    for rule in rules:
        d.text((margin + 10, y), "•", font=f_body, fill=c_main)
        draw_wrapped(d, rule, (margin + 42, y + 2, w - margin, y + 72), f_body, fill=c_main, line_gap=4)
        y += 62

    y += 20
    d.line((margin, y, w - margin, y), fill=c_rule, width=3)
    y += 30

    # Integrated beipackzettel
    d.rounded_rectangle((margin, y, w - margin, y + 300), radius=18, outline=c_rule, width=2, fill=c_box)
    d.text((margin + 24, y + 20), "Beipackzettel", font=f_label, fill=c_main)
    today = date.today().isoformat()
    beipack = (
        f"Goetheanum Schriften Version {args.version}.\n"
        f"Erstellt am {today} durch die Goetheanum Kommunikation,\n"
        "basierend auf der Schrift Titillium aus Urbino.\n"
        "Piktogramme und Icons u.a. von Severin Geissler und Philipp Tok."
    )
    by = y + 86
    for line in beipack.splitlines():
        d.text((margin + 24, by), line, font=f_body, fill=c_main)
        by += 50

    args.out_png.parent.mkdir(parents=True, exist_ok=True)
    args.out_pdf.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out_png)
    img.convert("RGB").save(args.out_pdf, "PDF", resolution=300.0)

    print(args.out_png)
    print(args.out_pdf)


if __name__ == "__main__":
    main()

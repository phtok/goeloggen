#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROWS = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "ß", "´"],
    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"],
    ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"],
]

LETTER_ORDER = list("qwertzuiopasdfghjklyxcvbnm")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Goetheanum keyboard mapping visual (SVG).")
    p.add_argument(
        "--out-svg",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1/goetheanum-icons-keyboard-mac-de.svg"),
    )
    return p.parse_args()


def cp_label(cp: int | None) -> str:
    if cp is None:
        return ""
    return f"U+{cp:04X}"


def mapping_lower() -> dict[str, int]:
    m: dict[str, int] = {
        "1": 0xE100,
        "2": 0xE101,
        "3": 0xE102,
        "4": 0xE103,
    }
    for idx, key in enumerate(LETTER_ORDER):
        m[key] = 0xE200 + idx
    return m


def mapping_upper() -> dict[str, int]:
    m: dict[str, int] = {
        "1": 0xE100,
        "2": 0xE101,
        "3": 0xE102,
        "4": 0xE103,
    }
    for idx, key in enumerate(LETTER_ORDER):
        m[key] = 0xE240 + idx
    return m


def draw_board(title: str, x0: int, y0: int, mapping: dict[str, int]) -> str:
    key_w = 72
    key_h = 62
    gap = 8
    row_offsets = [0, 18, 36, 54]
    out: list[str] = []
    out.append(f'<text x="{x0}" y="{y0 - 18}" class="board-title">{title}</text>')
    y = y0
    for ridx, row in enumerate(ROWS):
        x = x0 + row_offsets[ridx]
        for key in row:
            cp = mapping.get(key.lower())
            out.append(
                f'<rect x="{x}" y="{y}" width="{key_w}" height="{key_h}" rx="9" ry="9" class="key" />'
            )
            out.append(f'<text x="{x + 10}" y="{y + 20}" class="klabel">{key}</text>')
            if cp is not None:
                out.append(f'<text x="{x + 10}" y="{y + 46}" class="cp">{cp_label(cp)}</text>')
            x += key_w + gap
        y += key_h + gap
    return "\n".join(out)


def main() -> None:
    args = parse_args()
    args.out_svg.parent.mkdir(parents=True, exist_ok=True)

    lower = mapping_lower()
    upper = mapping_upper()

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1980" height="760" viewBox="0 0 1980 760">
  <style>
    .bg {{ fill: #f4f7fb; }}
    .title {{ font: 700 40px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #1f3040; }}
    .sub {{ font: 500 18px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #4d6174; }}
    .board-title {{ font: 700 24px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #1f3040; }}
    .key {{ fill: #ffffff; stroke: #cfd9e2; stroke-width: 2; }}
    .klabel {{ font: 700 17px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #203348; }}
    .cp {{ font: 500 15px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #3f5870; letter-spacing: 0.5px; }}
    .foot {{ font: 500 16px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #4d6174; }}
  </style>
  <rect class="bg" x="0" y="0" width="1980" height="760"/>
  <text x="48" y="60" class="title">Goetheanum Icons Keyboard (macOS, DE) - Vorschlag</text>
  <text x="48" y="92" class="sub">Logos auf 1-4. Piktos: a-z als Basis, Shift+a-z als Varianten. Eigene Eingabequelle 'Goetheanum Icons'.</text>
  {draw_board("Ebene 1: ohne Shift (Basis-Piktos)", 48, 150, lower)}
  {draw_board("Ebene 2: mit Shift (Variante/Fill)", 1020, 150, upper)}
  <text x="48" y="720" class="foot">Logo-Codes: 1=E100, 2=E101, 3=E102, 4=E103 | Piktos Basis: E200-E219 | Piktos Shift: E240-E259</text>
</svg>
"""
    args.out_svg.write_text(svg, encoding="utf-8")
    print(args.out_svg)


if __name__ == "__main__":
    main()

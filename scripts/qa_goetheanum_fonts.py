#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


CHECK_CODEPOINTS = [
    ("«", 0x00AB, "guillemotleft"),
    ("‹", 0x2039, "guilsinglleft"),
    ("›", 0x203A, "guilsinglright"),
    ("»", 0x00BB, "guillemotright"),
    ("Ä", 0x00C4, "Adieresis"),
    ("Ö", 0x00D6, "Odieresis"),
    ("Ü", 0x00DC, "Udieresis"),
    ("ä", 0x00E4, "adieresis"),
    ("ö", 0x00F6, "odieresis"),
    ("ü", 0x00FC, "udieresis"),
]

CHECK_GUILLEMETS = CHECK_CODEPOINTS[:4]
CHECK_UMLAUTS_UPPER = CHECK_CODEPOINTS[4:7]
CHECK_UMLAUTS_LOWER = CHECK_CODEPOINTS[7:]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--font-dir", type=Path, default=Path("output/goetheanum-fonts"))
    p.add_argument("--out-dir", type=Path, default=Path("output/goetheanum-fonts/qa"))
    return p.parse_args()


def collect_fonts(font_dir: Path) -> list[Path]:
    wanted_tokens = [
        "Leise",
        "Klar",
        "Laut",
        "Variable",
    ]
    out = []
    for token in wanted_tokens:
        matches = sorted(font_dir.glob(f"*{token}*.otf"))
        if not matches:
            raise FileNotFoundError(f"Missing font token '{token}' in {font_dir}")
        out.append(matches[-1])
    return out


def write_report(font_paths: list[Path], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# Goetheanum Font QA Report")
    lines.append("")
    for p in font_paths:
        f = TTFont(p)
        cmap = f.getBestCmap() or {}
        lines.append(f"## {p.name}")
        lines.append("")
        lines.append(f"- Tables: `{', '.join(sorted(f.keys()))}`")
        lines.append(f"- `OS/2.usWeightClass`: `{f['OS/2'].usWeightClass}`")
        n = f["name"]
        get = lambda nid: str(n.getName(nid, 3, 1, 0x409) or n.getName(nid, 1, 0, 0) or "")
        lines.append(f"- Name 1 (Family): `{get(1)}`")
        lines.append(f"- Name 2 (Style): `{get(2)}`")
        lines.append(f"- Name 4 (Full): `{get(4)}`")
        lines.append(f"- Name 6 (PostScript): `{get(6)}`")
        lines.append("")
        lines.append("| Glyph | Codepoint | Mapped Glyph Name |")
        lines.append("|---|---:|---|")
        for glyph_char, cp, _expected in CHECK_CODEPOINTS:
            mapped = cmap.get(cp, "MISSING")
            lines.append(f"| {glyph_char} | `U+{cp:04X}` | `{mapped}` |")
        lines.append("")
        f.close()
    out_md.write_text("\n".join(lines), encoding="utf-8")


def _glyph_path_data(font: TTFont, glyph_name: str) -> str:
    glyph_set = font.getGlyphSet()
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    return pen.getCommands()


def write_svg_proof(font_paths: list[Path], out_svg: Path, title: str, check_items: list[tuple[str, int, str]]) -> None:
    cell_w = 220
    cell_h = 220
    left_pad = 220
    top_pad = 90
    cols = len(check_items)
    rows = len(font_paths)
    width = left_pad + cols * cell_w + 40
    height = top_pad + rows * cell_h + 40
    scale = 0.12
    baseline = 150

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="#fbfaf6"/>')
    parts.append('<style><![CDATA[')
    parts.append('.title{font:700 22px serif;fill:#1b2c3a;}')
    parts.append('.fontlabel{font:600 15px sans-serif;fill:#22384a;}')
    parts.append('.glabel{font:500 13px sans-serif;fill:#4a5c6e;}')
    parts.append('.box{fill:none;stroke:#d9dee4;stroke-width:1;}')
    parts.append('.glyph{fill:#112538;}')
    parts.append(']]></style>')
    parts.append(f'<text x="24" y="38" class="title">{title}</text>')

    for col_idx, (glyph_char, cp, _exp) in enumerate(check_items):
        x = left_pad + col_idx * cell_w + 12
        parts.append(f'<text x="{x}" y="68" class="glabel">{glyph_char} U+{cp:04X}</text>')

    for row_idx, fp in enumerate(font_paths):
        font = TTFont(fp)
        cmap = font.getBestCmap() or {}
        row_y = top_pad + row_idx * cell_h
        parts.append(f'<text x="24" y="{row_y + 110}" class="fontlabel">{fp.name}</text>')
        for col_idx, (_glyph_char, cp, _exp) in enumerate(check_items):
            x = left_pad + col_idx * cell_w
            y = row_y
            parts.append(f'<rect class="box" x="{x}" y="{y}" width="{cell_w}" height="{cell_h}"/>')
            gname = cmap.get(cp)
            if not gname:
                continue
            d = _glyph_path_data(font, gname)
            if not d:
                continue
            tx = x + 56
            ty = y + baseline
            parts.append(
                f'<g transform="translate({tx},{ty}) scale({scale}, {-scale})"><path class="glyph" d="{d}"/></g>'
            )
        font.close()

    parts.append("</svg>")
    out_svg.write_text("\n".join(parts), encoding="utf-8")


def write_html_specimen(out_html: Path) -> None:
    html = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Goetheanum Schriftprobe</title>
  <style>
    @font-face { font-family: "Goetheanum"; src: url("../Goetheanum-Leise.otf") format("opentype"); font-weight: 280; font-style: normal; }
    @font-face { font-family: "Goetheanum"; src: url("../Goetheanum-Klar.otf") format("opentype"); font-weight: 450; font-style: normal; }
    @font-face { font-family: "Goetheanum"; src: url("../Goetheanum-Laut.otf") format("opentype"); font-weight: 600; font-style: normal; }
    body { margin: 24px; font-family: sans-serif; background: #f7f6f2; color: #1f2e3a; }
    .block { margin-bottom: 24px; padding: 16px; border: 1px solid #d8dde3; background: #fff; }
    .label { font: 600 13px/1.2 sans-serif; color: #4e5f72; margin-bottom: 10px; }
    .line { font-family: "Goetheanum", sans-serif; font-size: 40px; line-height: 1.2; }
    .l { font-weight: 280; }
    .k { font-weight: 450; }
    .u { font-weight: 600; }
  </style>
</head>
<body>
  <div class="block"><div class="label">Leise (280)</div><div class="line l">« ‹ Ä Ö Ü ä ö ü › »</div></div>
  <div class="block"><div class="label">Klar (450)</div><div class="line k">« ‹ Ä Ö Ü ä ö ü › »</div></div>
  <div class="block"><div class="label">Laut (600)</div><div class="line u">« ‹ Ä Ö Ü ä ö ü › »</div></div>
  <div class="block"><div class="label">Lauftext-Test</div><div class="line k" style="font-size:28px">Goetheanum «Sekretariat» – Überblick über Öffnungszeiten, Größe, Lösung, Führung.</div></div>
</body>
</html>
"""
    out_html.write_text(html, encoding="utf-8")


def write_q_proof(font_paths: list[Path], out_svg: Path) -> None:
    cell_w = 380
    cell_h = 240
    left_pad = 220
    top_pad = 90
    width = left_pad + cell_w + 40
    height = top_pad + len(font_paths) * cell_h + 40

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="#fbfaf6"/>')
    parts.append('<style><![CDATA[')
    parts.append('.title{font:700 22px serif;fill:#1b2c3a;}')
    parts.append('.fontlabel{font:600 15px sans-serif;fill:#22384a;}')
    parts.append('.glabel{font:500 13px sans-serif;fill:#4a5c6e;}')
    parts.append('.box{fill:none;stroke:#d9dee4;stroke-width:1;}')
    parts.append('.glyph{fill:#112538;}')
    parts.append(']]></style>')
    parts.append('<text x="24" y="38" class="title">Goetheanum QA: Großes Q</text>')
    parts.append(f'<text x="{left_pad + 12}" y="68" class="glabel">Q U+0051</text>')

    for row_idx, fp in enumerate(font_paths):
        f = TTFont(fp)
        gs = f.getGlyphSet()
        cmap = f.getBestCmap() or {}
        gname = cmap.get(0x0051, "Q")
        pen = SVGPathPen(gs)
        gs[gname].draw(pen)
        d = pen.getCommands()
        y = top_pad + row_idx * cell_h
        parts.append(f'<text x="24" y="{y + 120}" class="fontlabel">{fp.name}</text>')
        parts.append(f'<rect class="box" x="{left_pad}" y="{y}" width="{cell_w}" height="{cell_h}"/>')
        parts.append(
            f'<g transform="translate({left_pad + 100},{y + 170}) scale(0.18,-0.18)"><path class="glyph" d="{d}"/></g>'
        )
        f.close()

    parts.append("</svg>")
    out_svg.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fonts = collect_fonts(args.font_dir)

    write_report(fonts, args.out_dir / "qa-report.md")
    write_svg_proof(
        fonts,
        args.out_dir / "qa-glyph-proof-guillemets.svg",
        "Goetheanum QA: Guillemets",
        CHECK_GUILLEMETS,
    )
    write_svg_proof(
        fonts,
        args.out_dir / "qa-glyph-proof-umlauts.svg",
        "Goetheanum QA: Umlaute (Großbuchstaben)",
        CHECK_UMLAUTS_UPPER,
    )
    write_svg_proof(
        fonts,
        args.out_dir / "qa-glyph-proof-umlauts-lower.svg",
        "Goetheanum QA: Umlaute (Kleinbuchstaben)",
        CHECK_UMLAUTS_LOWER,
    )
    write_q_proof(fonts, args.out_dir / "qa-glyph-proof-Q.svg")
    write_html_specimen(args.out_dir / "specimen.html")

    print("Wrote:")
    print(args.out_dir / "qa-report.md")
    print(args.out_dir / "qa-glyph-proof-guillemets.svg")
    print(args.out_dir / "qa-glyph-proof-umlauts.svg")
    print(args.out_dir / "qa-glyph-proof-umlauts-lower.svg")
    print(args.out_dir / "qa-glyph-proof-Q.svg")
    print(args.out_dir / "specimen.html")


if __name__ == "__main__":
    main()

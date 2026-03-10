#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import RecordingPen
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


@dataclass
class FontRef:
    label: str
    font: TTFont


class OutlineTextDrawer:
    def __init__(self) -> None:
        self.path_cache: Dict[Tuple[int, str], list] = {}
        self.cmap_cache: Dict[int, dict[int, str]] = {}

    def _glyph_name(self, font: TTFont, cp: int) -> str:
        key = id(font)
        cmap = self.cmap_cache.get(key)
        if cmap is None:
            cmap = font.getBestCmap() or {}
            self.cmap_cache[key] = cmap
        return cmap.get(cp, ".notdef")

    def _glyph_ops(self, font: TTFont, glyph_name: str):
        key = (id(font), glyph_name)
        if key in self.path_cache:
            return self.path_cache[key]
        rec = RecordingPen()
        font.getGlyphSet()[glyph_name].draw(rec)
        self.path_cache[key] = rec.value
        return rec.value

    def draw_text(
        self,
        c: canvas.Canvas,
        font: TTFont,
        text: str,
        x: float,
        y: float,
        size: float,
        fill_color: str = "#10263A",
        tracking: float = 0.0,
    ) -> float:
        scale = size / font["head"].unitsPerEm
        hmtx = font["hmtx"].metrics
        cur_x = x
        c.setFillColor(HexColor(fill_color))
        for ch in text:
            cp = ord(ch)
            if ch == "\n":
                continue
            gname = self._glyph_name(font, cp)
            if gname not in hmtx:
                gname = ".notdef"
            adv, _lsb = hmtx.get(gname, (font["head"].unitsPerEm * 0.5, 0))
            ops = self._glyph_ops(font, gname)
            if ops:
                path = c.beginPath()
                for op, args in ops:
                    if op == "moveTo":
                        path.moveTo(args[0][0], args[0][1])
                    elif op == "lineTo":
                        path.lineTo(args[0][0], args[0][1])
                    elif op == "curveTo":
                        path.curveTo(
                            args[0][0], args[0][1],
                            args[1][0], args[1][1],
                            args[2][0], args[2][1],
                        )
                    elif op == "closePath":
                        path.close()
                c.saveState()
                c.translate(cur_x, y)
                c.scale(scale, scale)
                c.drawPath(path, fill=1, stroke=0)
                c.restoreState()
            cur_x += adv * scale + tracking
        return cur_x - x


def find_font_by_token(font_dir: Path, token: str) -> Path:
    matches = sorted(font_dir.glob(f"*{token}*.otf"))
    if not matches:
        raise FileNotFoundError(f"Missing font matching token '{token}' in {font_dir}")
    return matches[-1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Goetheanum context PDF proof.")
    p.add_argument("--font-dir", type=Path, required=True)
    p.add_argument("--out-pdf", type=Path, default=Path("output/pdf/goetheanum-context-proof.pdf"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    args.out_pdf.parent.mkdir(parents=True, exist_ok=True)

    leise_p = find_font_by_token(args.font_dir, "Leise")
    klar_p = find_font_by_token(args.font_dir, "Klar")
    laut_p = find_font_by_token(args.font_dir, "Laut")
    var_p = find_font_by_token(args.font_dir, "Variable")

    leise = TTFont(leise_p)
    klar = TTFont(klar_p)
    laut = TTFont(laut_p)
    vf = TTFont(var_p)
    var_280 = instantiateVariableFont(vf, {"wght": 280.0}, inplace=False, optimize=True)
    var_450 = instantiateVariableFont(vf, {"wght": 450.0}, inplace=False, optimize=True)
    var_600 = instantiateVariableFont(vf, {"wght": 600.0}, inplace=False, optimize=True)

    samples = [
        FontRef("Leise (static 280)", leise),
        FontRef("Klar (static 450)", klar),
        FontRef("Laut (static 600)", laut),
        FontRef("Variable @280", var_280),
        FontRef("Variable @450", var_450),
        FontRef("Variable @600", var_600),
    ]

    sentence_a = "«GoetheQanum Tester»"
    sentence_b = "‹GoetheQanum Tester›"
    sentence_c = "«Übergröße öffnet Ökonomie»"
    icon_line_small = "PUA-Icons: " + "".join(chr(cp) for cp in [0xE100, 0xE101, 0xE102])
    icon_line_desktop = "PUA-Desktop: " + chr(0xE103)

    c = canvas.Canvas(str(args.out_pdf), pagesize=A4)
    w, h = A4
    drawer = OutlineTextDrawer()

    c.setTitle("Goetheanum Kontext-Proof")
    c.setAuthor("Codex")
    c.setFillColor(HexColor("#1F3040"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(48, h - 40, "Goetheanum Kontext-Proof (mit Guillemets)")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#4D6174"))
    source_label = str(args.font_dir)
    marker = "/output/"
    if marker in source_label:
        source_label = source_label[source_label.index(marker) + 1 :]
    elif len(source_label) > 48:
        source_label = f".../{args.font_dir.name}"
    c.drawString(48, h - 58, f"Quelle: {source_label}")
    c.drawString(48, h - 72, "Beispielsaetze: doppelte U+00AB/U+00BB und einfache U+2039/U+203A")

    y = h - 182
    for ref in samples:
        c.setFillColor(HexColor("#4D6174"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(48, y + 52, ref.label)
        drawer.draw_text(c, ref.font, sentence_a, 220, y + 45, 26)
        drawer.draw_text(c, ref.font, sentence_b, 220, y + 14, 26)
        drawer.draw_text(c, ref.font, sentence_c, 220, y - 14, 22)
        y -= 98
        if y < 120:
            break

    c.setFillColor(HexColor("#4D6174"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(48, 120, "Icon-Glyphs (PUA E100-E103)")
    drawer.draw_text(c, klar, icon_line_small, 220, 112, 24, tracking=5)
    drawer.draw_text(c, klar, icon_line_desktop, 220, 88, 14, tracking=2)

    c.showPage()
    c.save()

    for f in [leise, klar, laut, vf, var_280, var_450, var_600]:
        f.close()

    print(args.out_pdf)


if __name__ == "__main__":
    main()

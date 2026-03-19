#!/usr/bin/env python3
from __future__ import annotations

import argparse
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


@dataclass
class FontEntry:
    role: str
    path: Path
    font: TTFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit Goetheanum output fonts.")
    p.add_argument("--font-dir", type=Path, default=Path("output/goetheanum-fonts"))
    p.add_argument("--source-regular", type=Path, required=True)
    p.add_argument("--report", type=Path, default=Path("output/goetheanum-fonts/qa/full-audit.md"))
    return p.parse_args()


def find_font(font_dir: Path, token: str) -> Path:
    matches = sorted(font_dir.glob(f"*{token}*.otf"))
    if not matches:
        raise FileNotFoundError(f"No font file matching *{token}*.otf in {font_dir}")
    return matches[-1]


def load_fonts(font_dir: Path) -> list[FontEntry]:
    roles = [
        ("leise", "Leise"),
        ("klar", "Klar"),
        ("laut", "Laut"),
        ("variable", "Variable"),
    ]
    out: list[FontEntry] = []
    for role, token in roles:
        p = find_font(font_dir, token)
        out.append(FontEntry(role=role, path=p, font=TTFont(p)))
    return out


def glyph_drawable(font: TTFont, glyph_name: str) -> bool:
    try:
        rec = RecordingPen()
        font.getGlyphSet()[glyph_name].draw(rec)
        return True
    except Exception:
        return False


def glyph_svg_path(font: TTFont, glyph_name: str) -> str:
    pen = SVGPathPen(font.getGlyphSet())
    font.getGlyphSet()[glyph_name].draw(pen)
    return pen.getCommands() or ""


def significant_codepoints(cmap: dict[int, str]) -> set[int]:
    keep: set[int] = set()
    for cp in cmap.keys():
        cat = unicodedata.category(chr(cp))
        if cat.startswith(("L", "N", "P", "S")):
            keep.add(cp)
    return keep


def main() -> None:
    args = parse_args()
    fonts = load_fonts(args.font_dir)
    src_regular = TTFont(args.source_regular)

    lines: list[str] = []
    lines.append("# Goetheanum Full Glyph Audit")
    lines.append("")
    lines.append(f"- Font directory: `{args.font_dir}`")
    lines.append(f"- Source regular: `{args.source_regular}`")
    lines.append("")

    src_cmap = src_regular.getBestCmap() or {}
    src_sig = significant_codepoints(src_cmap)
    lines.append(f"- Source regular codepoints: `{len(src_cmap)}` (significant: `{len(src_sig)}`)")
    lines.append("")

    cmaps: dict[str, dict[int, str]] = {}
    for e in fonts:
        cmap = e.font.getBestCmap() or {}
        cmaps[e.role] = cmap
        lines.append(f"## {e.path.name}")
        lines.append(f"- Role: `{e.role}`")
        lines.append(f"- Codepoints in cmap: `{len(cmap)}`")
        lines.append(f"- Num glyphs (`maxp`): `{e.font['maxp'].numGlyphs}`")
        lines.append(f"- Tables: `{', '.join(sorted(e.font.keys()))}`")
        lines.append("")

    # Coverage checks vs source regular.
    for role in ("leise", "klar", "laut", "variable"):
        missing = sorted(src_sig - set(cmaps[role].keys()))
        lines.append(f"### Coverage vs Source: {role}")
        lines.append(f"- Missing significant codepoints: `{len(missing)}`")
        if missing:
            preview = ", ".join(f"U+{cp:04X}" for cp in missing[:30])
            lines.append(f"- Preview missing: `{preview}`")
        lines.append("")

    # Cross-font cmap consistency.
    base = set(cmaps["klar"].keys())
    for role in ("leise", "laut", "variable"):
        extra = sorted(set(cmaps[role].keys()) - base)
        miss = sorted(base - set(cmaps[role].keys()))
        lines.append(f"### CMap Consistency Klar vs {role}")
        lines.append(f"- Extra in {role}: `{len(extra)}`")
        lines.append(f"- Missing in {role}: `{len(miss)}`")
        lines.append("")

    # Broken drawable glyphs and suspicious widths.
    lines.append("## Structural Checks")
    for e in fonts:
        cmap = cmaps[e.role]
        broken: list[str] = []
        suspicious_width: list[str] = []
        upm = e.font["head"].unitsPerEm
        for cp, gname in cmap.items():
            if not glyph_drawable(e.font, gname):
                broken.append(f"U+{cp:04X}:{gname}")
            adv = e.font["hmtx"].metrics.get(gname, (None, None))[0]
            if adv is None:
                suspicious_width.append(f"U+{cp:04X}:{gname}:missing_hmtx")
                continue
            if cp != 0x0020 and adv <= 0:
                suspicious_width.append(f"U+{cp:04X}:{gname}:nonpositive({adv})")
            if adv > upm * 3:
                suspicious_width.append(f"U+{cp:04X}:{gname}:huge({adv})")
        lines.append(f"### {e.role}")
        lines.append(f"- Broken drawable mapped glyphs: `{len(broken)}`")
        if broken:
            lines.append(f"- Examples: `{', '.join(broken[:20])}`")
        lines.append(f"- Suspicious advance widths: `{len(suspicious_width)}`")
        if suspicious_width:
            lines.append(f"- Examples: `{', '.join(suspicious_width[:20])}`")
        lines.append("")

    # Weight consistency heuristic on basic Latin letters+digits.
    lines.append("## Weight Consistency Heuristic (Leise/Klar/Laut)")
    letter_digit = [
        cp
        for cp in range(0x20, 0x7F)
        if cp in cmaps["leise"] and cp in cmaps["klar"] and cp in cmaps["laut"]
        and unicodedata.category(chr(cp)).startswith(("L", "N"))
    ]
    identical_across_weights: list[str] = []
    for cp in letter_digit:
        paths = []
        for role in ("leise", "klar", "laut"):
            gname = cmaps[role][cp]
            paths.append(glyph_svg_path(next(e.font for e in fonts if e.role == role), gname))
        if paths[0] == paths[1] == paths[2]:
            identical_across_weights.append(f"U+{cp:04X}:{chr(cp)}")
    lines.append(f"- Basic Latin letters/digits checked: `{len(letter_digit)}`")
    lines.append(f"- Identical outlines across all 3 weights: `{len(identical_across_weights)}`")
    if identical_across_weights:
        lines.append(f"- Identical list: `{', '.join(identical_across_weights[:80])}`")
    lines.append("")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")
    print(args.report)

    for e in fonts:
        e.font.close()
    src_regular.close()


if __name__ == "__main__":
    main()

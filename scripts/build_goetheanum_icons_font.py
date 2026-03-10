#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from fontTools import subset
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Goetheanum Icons OTF from repaired SVGs.")
    p.add_argument("--template-font", type=Path, required=True)
    p.add_argument("--svg-dir", type=Path, required=True)
    p.add_argument("--out-font", type=Path, required=True)
    p.add_argument("--version", default="0.1.0")
    p.add_argument("--family", default="Goetheanum Icons")
    p.add_argument("--style", default="Filled")
    p.add_argument("--codepoint-start", type=lambda s: int(s, 0), default=0xE200)
    p.add_argument("--mapping-csv", type=Path, required=True)
    p.add_argument("--mapping-md", type=Path, required=True)
    p.add_argument(
        "--keep-existing-unicodes",
        action="store_true",
        help="Keep Unicode codepoints already present in the template font when subsetting.",
    )
    return p.parse_args()


def set_name_fields(
    font: TTFont,
    family: str,
    subfamily: str,
    full: str,
    postscript: str,
    version: str,
) -> None:
    name = font["name"]
    version_string = f"Version {version}"
    unique_id = f"{version};GOEA;{postscript}"
    for platform, enc, lang in ((3, 1, 0x409), (1, 0, 0)):
        name.setName(family, 1, platform, enc, lang)
        name.setName(subfamily, 2, platform, enc, lang)
        name.setName(unique_id, 3, platform, enc, lang)
        name.setName(full, 4, platform, enc, lang)
        name.setName(version_string, 5, platform, enc, lang)
        name.setName(postscript, 6, platform, enc, lang)
        name.setName(family, 16, platform, enc, lang)
        name.setName(subfamily, 17, platform, enc, lang)


def set_regular_metadata(font: TTFont) -> None:
    os2 = font["OS/2"]
    os2.usWeightClass = 400
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    os2.fsSelection |= 1 << 6
    os2.usFirstCharIndex = 32
    os2.usLastCharIndex = 0xE2FF

    head = font["head"]
    head.macStyle &= ~0b11
    font["post"].italicAngle = 0


def subset_to_unicodes(font: TTFont, unicodes: list[int]) -> None:
    opts = subset.Options()
    # Keep hint data untouched to avoid CFF Private-dict assumptions during pruning.
    opts.hinting = True
    opts.retain_gids = False
    opts.notdef_outline = True
    opts.layout_features = []
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.name_languages = ["*"]
    opts.drop_tables = []
    s = subset.Subsetter(options=opts)
    s.populate(unicodes=unicodes)
    s.subset(font)


def svg_path_data(svg_path: Path) -> list[str]:
    import xml.etree.ElementTree as ET

    root = ET.parse(svg_path).getroot()
    ds: list[str] = []
    for el in root.iter():
        if el.tag.split("}")[-1] != "path":
            continue
        d = (el.attrib.get("d") or "").strip()
        if d:
            ds.append(d)
    return ds


def make_charstring_from_svg(font: TTFont, svg_path: Path) -> tuple[object, int]:
    ds = svg_path_data(svg_path)
    if not ds:
        raise ValueError(f"No path data in {svg_path}")
    rec = RecordingPen()
    for d in ds:
        parse_path(d, rec)

    # Repaired SVGs are normalized to viewBox 0..1000 in y-down coordinates.
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    rec.replay(TransformPen(pen, (1, 0, 0, -1, 0, 1000)))

    top = font["CFF "].cff.topDictIndex[0]
    private = getattr(top, "Private", None)
    if private is None and hasattr(top, "FDArray") and len(top.FDArray):
        private = top.FDArray[0].Private
    gsubrs = getattr(top, "GlobalSubrs", None)
    cs = pen.getCharString(private=private, globalSubrs=gsubrs, optimize=False)
    return cs, 1000


def upsert_cff_glyph(font: TTFont, glyph_name: str, charstring: object, advance: int, codepoint: int) -> None:
    top = font["CFF "].cff.topDictIndex[0]
    cs_obj = top.CharStrings
    order = font.getGlyphOrder()
    hmtx = font["hmtx"].metrics

    if glyph_name in cs_obj.charStrings:
        idx = cs_obj.charStrings[glyph_name]
        if isinstance(idx, int):
            cs_obj.charStringsIndex[idx] = charstring
        else:
            cs_obj[glyph_name] = charstring
    else:
        idx = len(cs_obj.charStringsIndex)
        cs_obj.charStringsIndex.append(charstring)
        cs_obj.charStrings[glyph_name] = idx
        order.append(glyph_name)

    font.setGlyphOrder(order)
    top.charset = order
    if hasattr(top, "FDSelect") and hasattr(top.FDSelect, "gidArray"):
        gid_array = top.FDSelect.gidArray
        if len(gid_array) < len(order):
            gid_array.extend([0] * (len(order) - len(gid_array)))
    hmtx[glyph_name] = (advance, hmtx.get(glyph_name, (0, 0))[1])
    font["hhea"].numberOfHMetrics = len(hmtx)
    font["maxp"].numGlyphs = len(order)

    for st in font["cmap"].tables:
        if st.isUnicode():
            st.cmap[codepoint] = glyph_name


def main() -> None:
    args = parse_args()
    args.out_font.parent.mkdir(parents=True, exist_ok=True)
    args.mapping_csv.parent.mkdir(parents=True, exist_ok=True)
    args.mapping_md.parent.mkdir(parents=True, exist_ok=True)

    font = TTFont(args.template_font)
    existing_unicodes = sorted(
        {
            cp
            for st in font["cmap"].tables
            if st.isUnicode()
            for cp in st.cmap.keys()
        }
    )
    set_name_fields(
        font,
        args.family,
        args.style,
        f"{args.family} {args.style}",
        f"{args.family.replace(' ', '')}-{args.style}",
        args.version,
    )
    set_regular_metadata(font)

    files = sorted(args.svg_dir.glob("*.svg"))
    if not files:
        raise SystemExit(f"No SVG files in {args.svg_dir}")

    rows: list[tuple[int, str, str]] = []
    existing_cids = [
        int(m.group(1))
        for g in font.getGlyphOrder()
        for m in [re.match(r"^cid(\d+)$", g)]
        if m
    ]
    next_cid = (max(existing_cids) + 1) if existing_cids else 1
    cp = args.codepoint_start
    codepoints: list[int] = []
    for svg in files:
        gname = f"cid{next_cid:05d}"
        next_cid += 1
        charstring, advance = make_charstring_from_svg(font, svg)
        upsert_cff_glyph(font, gname, charstring, advance, cp)
        rows.append((cp, gname, svg.name))
        codepoints.append(cp)
        cp += 1

    # Keep only icons (+space) for the icon font artifact.
    keep_unicodes = [0x20, *codepoints]
    if args.keep_existing_unicodes:
        keep_unicodes = sorted(set(keep_unicodes) | set(existing_unicodes))
    subset_to_unicodes(font, keep_unicodes)

    font.save(args.out_font)
    font.close()

    with args.mapping_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codepoint", "glyph_name", "source_svg"])
        for codepoint, gname, src in rows:
            w.writerow([f"U+{codepoint:04X}", gname, src])

    lines = [
        f"# {args.family} {args.style} v{args.version}",
        "",
        f"- Output font: `{args.out_font}`",
        f"- Source SVG dir: `{args.svg_dir}`",
        f"- Glyph count: `{len(rows)}`",
        f"- Codepoint range: `U+{rows[0][0]:04X}` - `U+{rows[-1][0]:04X}`",
        "",
        "| Codepoint | Glyph | Source |",
        "|---|---|---|",
    ]
    for codepoint, gname, src in rows:
        lines.append(f"| `U+{codepoint:04X}` | `{gname}` | `{src}` |")
    args.mapping_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(args.out_font)
    print(args.mapping_csv)
    print(args.mapping_md)


if __name__ == "__main__":
    main()

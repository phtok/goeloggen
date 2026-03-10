#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools import subset
from fontTools.svgLib.path import parse_path
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, SourceDescriptor
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.cffLib.CFF2ToCFF import convertCFF2ToCFF
from fontTools.varLib import build as varlib_build
from fontTools.varLib import interpolatable
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance


MASTER_WEIGHTS = [
    ("thin", 250),
    ("light", 300),
    ("regular", 400),
    ("semibold", 600),
    ("bold", 700),
]

TARGETS = [
    ("Leise", 280),
    ("Klar", 450),
    ("Laut", 600),
]

GLYPH_CHECKS = {
    "guillemotleft": 0x00AB,
    "guillemotright": 0x00BB,
    "guilsinglleft": 0x2039,
    "guilsinglright": 0x203A,
    "Adieresis": 0x00C4,
    "Odieresis": 0x00D6,
    "Udieresis": 0x00DC,
    "adieresis": 0x00E4,
    "odieresis": 0x00F6,
    "udieresis": 0x00FC,
    "goe_icon_de": 0xE100,
    "goe_point_de": 0xE101,
    "goe_square_de": 0xE102,
    "goe_desktop_de": 0xE103,
}

ICON_SPECS = [
    ("goe_icon_de", 0xE100),
    ("goe_point_de", 0xE101),
    ("goe_square_de", 0xE102),
    ("goe_desktop_de", 0xE103),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Goetheanum static + variable fonts.")
    p.add_argument("--thin", required=True, type=Path)
    p.add_argument("--light", required=True, type=Path)
    p.add_argument("--regular", required=True, type=Path)
    p.add_argument("--semibold", required=True, type=Path)
    p.add_argument("--bold", required=True, type=Path)
    p.add_argument("--family", default="Goetheanum")
    p.add_argument("--version", default="1.1.0")
    p.add_argument("--icon-svg", type=Path, default=None, help="Simple Goetheanum icon SVG")
    p.add_argument("--point-svg", type=Path, default=None, help="Point Goetheanum icon SVG")
    p.add_argument("--square-svg", type=Path, default=None, help="Square Goetheanum icon SVG")
    p.add_argument("--desktop-svg", type=Path, default=None, help="Full desktop Goetheanum logo SVG")
    p.add_argument("--outdir", type=Path, default=Path("output/goetheanum-fonts"))
    p.add_argument("--workdir", type=Path, default=Path("tmp/goetheanum-font-build/work"))
    return p.parse_args()


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


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


def set_weight_metadata(font: TTFont, weight: int, regular_flag: bool) -> None:
    os2 = font["OS/2"]
    os2.usWeightClass = int(weight)
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    if regular_flag:
        os2.fsSelection |= 1 << 6

    head = font["head"]
    head.macStyle &= ~0b11
    post = font["post"]
    post.italicAngle = 0


def copy_sources(args: argparse.Namespace, source_dir: Path) -> dict[str, Path]:
    src_map = {
        "thin": args.thin,
        "light": args.light,
        "regular": args.regular,
        "semibold": args.semibold,
        "bold": args.bold,
    }
    copied: dict[str, Path] = {}
    for key, src in src_map.items():
        if not src.exists():
            raise FileNotFoundError(f"Missing source font: {src}")
        dst = source_dir / f"{key}.otf"
        shutil.copy2(src, dst)
        copied[key] = dst
    return copied


def make_nohint_fonts(source_paths: dict[str, Path], out_dir: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for key, src in source_paths.items():
        font = TTFont(src)
        glyphs = font.getGlyphOrder()

        opts = subset.Options()
        opts.hinting = False
        opts.retain_gids = True
        opts.notdef_outline = True
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.name_legacy = True
        opts.name_languages = ["*"]
        opts.drop_tables = []

        s = subset.Subsetter(options=opts)
        s.populate(glyphs=glyphs)
        s.subset(font)

        dst = out_dir / f"{key}.otf"
        font.save(dst)
        font.close()
        out[key] = dst
    return out


def incompatible_glyphs(fonts: list[TTFont], names: list[str]) -> set[str]:
    problems = interpolatable.test([f.getGlyphSet() for f in fonts], names=names)
    return set(problems.keys())


def copy_outline_from_default(default_font: TTFont, target_font: TTFont, glyph_name: str) -> None:
    src_glyph_set = default_font.getGlyphSet()
    if glyph_name not in src_glyph_set:
        return

    dst_top = target_font["CFF "].cff.topDictIndex[0]
    dst_charstrings = dst_top.CharStrings
    if glyph_name not in dst_charstrings:
        return

    rec = RecordingPen()
    src_glyph_set[glyph_name].draw(rec)
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    rec.replay(pen)
    cs = pen.getCharString(private=dst_top.Private, globalSubrs=dst_top.GlobalSubrs, optimize=True)
    dst_charstrings[glyph_name] = cs


def _set_cff_glyph_from_recording(font: TTFont, glyph_name: str, ops: list[tuple[str, tuple]]) -> None:
    if "CFF " not in font:
        return
    top = font["CFF "].cff.topDictIndex[0]
    if glyph_name not in top.CharStrings:
        return
    rec = RecordingPen()
    rec.value = list(ops)
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    rec.replay(pen)
    cs = pen.getCharString(private=top.Private, globalSubrs=top.GlobalSubrs, optimize=False)
    top.CharStrings[glyph_name] = cs


def normalize_q_node_structure(font: TTFont) -> None:
    glyph_set = font.getGlyphSet()
    if "Q" not in glyph_set:
        return
    rec = RecordingPen()
    glyph_set["Q"].draw(rec)
    ops = list(rec.value)

    # Thin/Light masters have one extra line segment in contour 0; we add a
    # zero-length line segment to 19-op masters to keep interpolation-compatible
    # node structure while preserving contour shape.
    if len(ops) != 19:
        return
    if not (
        len(ops) > 5
        and ops[2][0] == "lineTo"
        and ops[3][0] == "lineTo"
        and ops[4][0] == "lineTo"
        and ops[5][0] == "curveTo"
    ):
        return

    duplicate_point = ops[4][1][0]
    new_ops = ops[:5] + [("lineTo", (duplicate_point,))] + ops[5:]
    _set_cff_glyph_from_recording(font, "Q", new_ops)


def repair_single_guillemets(font: TTFont) -> None:
    if "CFF " not in font:
        return
    top = font["CFF "].cff.topDictIndex[0]
    charstrings = top.CharStrings
    if "guilsinglleft" not in charstrings or "guilsinglright" not in charstrings:
        return

    glyph_set = font.getGlyphSet()
    rec = RecordingPen()
    glyph_set["guilsinglleft"].draw(rec)

    width = font["hmtx"].metrics.get("guilsinglleft", (0, 0))[0]
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    transform = TransformPen(pen, (-1, 0, 0, 1, width, 0))
    rec.replay(transform)
    cs = pen.getCharString(private=top.Private, globalSubrs=top.GlobalSubrs, optimize=False)
    charstrings["guilsinglright"] = cs
    if "guilsinglright" in font["hmtx"].metrics:
        font["hmtx"].metrics["guilsinglright"] = (width, font["hmtx"].metrics["guilsinglright"][1])


def repair_double_guillemets(font: TTFont) -> None:
    if "CFF " not in font:
        return
    top = font["CFF "].cff.topDictIndex[0]
    charstrings = top.CharStrings
    if "guilsinglleft" not in charstrings:
        return
    if "guillemotleft" not in charstrings or "guillemotright" not in charstrings:
        return

    glyph_set = font.getGlyphSet()
    rec_single = RecordingPen()
    glyph_set["guilsinglleft"].draw(rec_single)
    ops_single = list(rec_single.value)
    if not ops_single:
        return

    hmtx = font["hmtx"].metrics
    single_adv = hmtx.get("guilsinglleft", (0, 0))[0]
    if single_adv <= 0:
        return

    bpen = BoundsPen(glyph_set)
    glyph_set["guilsinglleft"].draw(bpen)
    if not bpen.bounds:
        return
    xmin, _ymin, xmax, _ymax = bpen.bounds
    right_sb = single_adv - xmax

    # Build guillemotleft from two single-left chevrons with controlled overlap.
    shift = int(round(single_adv * 0.74))
    rec_double_left = RecordingPen()
    rec_single.replay(rec_double_left)
    rec_single.replay(TransformPen(rec_double_left, (1, 0, 0, 1, shift, 0)))
    _set_cff_glyph_from_recording(font, "guillemotleft", list(rec_double_left.value))

    double_adv = int(round((xmax + shift) + right_sb))
    old_lsb_left = hmtx.get("guillemotleft", (0, 0))[1]
    hmtx["guillemotleft"] = (double_adv, old_lsb_left)

    # guillemotright is mirrored from guillemotleft for baseline/height symmetry.
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    rec_double_left.replay(TransformPen(pen, (-1, 0, 0, 1, double_adv, 0)))
    cs = pen.getCharString(private=top.Private, globalSubrs=top.GlobalSubrs, optimize=False)
    charstrings["guillemotright"] = cs
    old_lsb_right = hmtx.get("guillemotright", (0, 0))[1]
    hmtx["guillemotright"] = (double_adv, old_lsb_right)


def repair_fraction_metrics(font: TTFont, ref_advance: int, ref_lsb: int) -> None:
    cmap = font.getBestCmap() or {}
    frac = cmap.get(0x2044)
    if not frac:
        return
    adv, lsb = font["hmtx"].metrics.get(frac, (None, None))
    if adv is None:
        return
    upm = font["head"].unitsPerEm
    if adv <= 0 or adv > upm * 3:
        font["hmtx"].metrics[frac] = (ref_advance, ref_lsb if ref_lsb is not None else lsb)


def _svg_paths(svg_path: Path) -> tuple[tuple[float, float, float, float], list[str]]:
    root = ET.parse(svg_path).getroot()
    view_box = root.attrib.get("viewBox")
    if not view_box:
        raise ValueError(f"SVG missing viewBox: {svg_path}")
    vals = [float(x) for x in view_box.replace(",", " ").split()]
    if len(vals) != 4:
        raise ValueError(f"Unexpected viewBox format in {svg_path}: {view_box}")
    paths = []
    for el in root.iter():
        if el.tag.split("}")[-1] == "path" and "d" in el.attrib:
            paths.append(el.attrib["d"])
    if not paths:
        raise ValueError(f"No path elements found in {svg_path}")
    return (vals[0], vals[1], vals[2], vals[3]), paths


def _make_cff_charstring_from_svg(font: TTFont, svg_path: Path) -> tuple[object, int]:
    (minx, miny, vbw, vbh), path_defs = _svg_paths(svg_path)
    rec = RecordingPen()
    for d in path_defs:
        parse_path(d, rec)
    upm = font["head"].unitsPerEm
    scale = upm / vbh
    transform = (scale, 0, 0, -scale, -minx * scale, (vbh + miny) * scale)
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    rec.replay(TransformPen(pen, transform))
    top = font["CFF "].cff.topDictIndex[0]
    cs = pen.getCharString(private=top.Private, globalSubrs=top.GlobalSubrs, optimize=False)
    advance = int(round(vbw * scale))
    return cs, advance


def _upsert_cff_glyph(font: TTFont, glyph_name: str, charstring: object, advance: int, codepoint: int) -> None:
    top = font["CFF "].cff.topDictIndex[0]
    cs_obj = top.CharStrings
    order = font.getGlyphOrder()
    hmtx = font["hmtx"].metrics

    if glyph_name in cs_obj.charStrings:
        idx = cs_obj.charStrings[glyph_name]
        if isinstance(idx, int):
            cs_obj.charStringsIndex[idx] = charstring
        else:
            # Defensive fallback in case table is decompiled to objects.
            cs_obj[glyph_name] = charstring
        if glyph_name not in order:
            order.append(glyph_name)
    else:
        idx = len(cs_obj.charStringsIndex)
        cs_obj.charStringsIndex.append(charstring)
        cs_obj.charStrings[glyph_name] = idx
        if glyph_name not in order:
            order.append(glyph_name)

    font.setGlyphOrder(order)
    top.charset = order
    hmtx[glyph_name] = (advance, hmtx.get(glyph_name, (0, 0))[1])
    font["hhea"].numberOfHMetrics = len(hmtx)
    font["maxp"].numGlyphs = len(order)

    for st in font["cmap"].tables:
        if st.isUnicode():
            st.cmap[codepoint] = glyph_name


def inject_logo_icons(fonts: list[TTFont], icon_files: dict[str, Path]) -> None:
    for font in fonts:
        for glyph_name, codepoint in ICON_SPECS:
            svg_path = icon_files.get(glyph_name)
            if svg_path is None:
                continue
            charstring, advance = _make_cff_charstring_from_svg(font, svg_path)
            _upsert_cff_glyph(font, glyph_name, charstring, advance, codepoint)


def harmonize_incompatible_glyphs(
    master_paths: dict[str, Path],
    harmonized_dir: Path,
    icon_files: dict[str, Path] | None = None,
) -> dict[str, Path]:
    ordered_keys = [k for k, _ in MASTER_WEIGHTS]
    fonts = [TTFont(master_paths[k]) for k in ordered_keys]
    names = ordered_keys[:]

    default_idx = ordered_keys.index("regular")
    default_font = fonts[default_idx]
    default_cmap = default_font.getBestCmap() or {}
    default_fraction = default_cmap.get(0x2044)
    ref_adv, ref_lsb = (13, -160)
    if default_fraction and default_fraction in default_font["hmtx"].metrics:
        ref_adv, ref_lsb = default_font["hmtx"].metrics[default_fraction]

    for font in fonts:
        repair_single_guillemets(font)
        repair_double_guillemets(font)
        normalize_q_node_structure(font)
        repair_fraction_metrics(font, ref_adv, ref_lsb)

    skip_copy = {"guilsinglleft", "guilsinglright", "guillemotleft", "guillemotright"}
    bad = incompatible_glyphs(fonts, names)
    for glyph_name in sorted(bad):
        if glyph_name in skip_copy:
            continue
        for i, font in enumerate(fonts):
            if i == default_idx:
                continue
            copy_outline_from_default(default_font, font, glyph_name)

    recheck = incompatible_glyphs(fonts, names)
    if recheck:
        # One extra pass with the refreshed incompatibility list.
        for glyph_name in sorted(recheck):
            if glyph_name in skip_copy:
                continue
            for i, font in enumerate(fonts):
                if i == default_idx:
                    continue
                copy_outline_from_default(default_font, font, glyph_name)
        recheck = incompatible_glyphs(fonts, names)
        if recheck:
            glyph_list = ", ".join(sorted(recheck))
            raise RuntimeError(f"Still incompatible after harmonization: {glyph_list}")

    # Ensure right single guillemet is always the mirrored left shape per master.
    for font in fonts:
        repair_single_guillemets(font)

    if icon_files:
        inject_logo_icons(fonts, icon_files)

    out: dict[str, Path] = {}
    for key, font in zip(ordered_keys, fonts):
        dst = harmonized_dir / f"{key}.otf"
        font.save(dst)
        font.close()
        out[key] = dst
    return out


def build_variable_font(
    harmonized_paths: dict[str, Path],
    family: str,
    version: str,
    out_dir: Path,
) -> Path:
    ds = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name = "Weight"
    axis.tag = "wght"
    axis.minimum = 250
    axis.maximum = 700
    axis.default = 400
    axis.map = [(250, 250), (300, 300), (400, 400), (600, 600), (700, 700)]
    ds.addAxis(axis)

    for key, wght in MASTER_WEIGHTS:
        src = SourceDescriptor()
        src.path = str(harmonized_paths[key].resolve())
        src.name = key
        src.familyName = family
        src.styleName = key.capitalize()
        src.location = {"Weight": wght}
        src.copyInfo = True
        src.copyFeatures = True
        src.copyLib = True
        ds.addSource(src)

    designspace_path = out_dir / "goetheanum.designspace"
    ds.write(designspace_path)

    vf, _, _ = varlib_build(str(designspace_path), optimize=True)
    set_name_fields(
        vf,
        family,
        "Variable",
        f"{family} Variable",
        f"{family}-Variable",
        version,
    )
    set_weight_metadata(vf, 400, regular_flag=True)

    if "fvar" in vf:
        axis_obj = vf["fvar"].axes[0]
        axis_obj.axisNameID = vf["name"].addName("Weight")
        axis_obj.minValue = 250
        axis_obj.defaultValue = 400
        axis_obj.maxValue = 700
        vf["fvar"].instances = []
        for style, wght in TARGETS:
            sub_id = vf["name"].addName(style)
            ps_id = vf["name"].addName(f"{family}-{style}")
            inst = NamedInstance()
            inst.subfamilyNameID = sub_id
            inst.postscriptNameID = ps_id
            inst.coordinates = {"wght": float(wght)}
            vf["fvar"].instances.append(inst)

    version_tag = version.replace(" ", "_")
    vf_path = out_dir / f"{family}-v{version_tag}-Variable.otf"
    vf.save(vf_path)
    vf.close()
    return vf_path


def build_static_instances(vf_path: Path, family: str, version: str, out_dir: Path) -> list[Path]:
    out_files: list[Path] = []
    for style, wght in TARGETS:
        vf = TTFont(vf_path)
        static = instantiateVariableFont(vf, {"wght": float(wght)}, inplace=False, optimize=True)
        vf.close()
        if "fvar" in static:
            del static["fvar"]
        if "STAT" in static:
            del static["STAT"]
        if "avar" in static:
            del static["avar"]
        if "MVAR" in static:
            del static["MVAR"]
        if "HVAR" in static:
            del static["HVAR"]

        if "CFF2" in static:
            convertCFF2ToCFF(static, updatePostTable=True)
        static.recalcBBoxes = False

        set_name_fields(
            static,
            family,
            style,
            f"{family} {style}",
            f"{family}-{style}",
            version,
        )
        set_weight_metadata(static, wght, regular_flag=(style == "Klar"))

        version_tag = version.replace(" ", "_")
        out_path = out_dir / f"{family}-v{version_tag}-{style}.otf"
        static.save(out_path)
        static.close()
        out_files.append(out_path)
    return out_files


def glyph_report(paths: list[Path]) -> None:
    for p in paths:
        f = TTFont(p)
        cmap = f.getBestCmap() or {}
        print(f"\n== {p.name} ==")
        for label, cp in GLYPH_CHECKS.items():
            glyph = cmap.get(cp)
            print(f"{label:16} U+{cp:04X} -> {glyph if glyph else 'MISSING'}")
        f.close()


def main() -> None:
    args = parse_args()
    ensure_clean_dir(args.workdir)
    version_tag = args.version.replace(" ", "_")
    version_outdir = args.outdir / f"v{version_tag}"
    version_outdir.mkdir(parents=True, exist_ok=True)

    source_dir = args.workdir / "sources"
    nohint_dir = args.workdir / "nohint"
    harmonized_dir = args.workdir / "harmonized"
    source_dir.mkdir(parents=True, exist_ok=True)
    nohint_dir.mkdir(parents=True, exist_ok=True)
    harmonized_dir.mkdir(parents=True, exist_ok=True)

    copied = copy_sources(args, source_dir)
    icon_files = {
        "goe_icon_de": args.icon_svg,
        "goe_point_de": args.point_svg,
        "goe_square_de": args.square_svg,
        "goe_desktop_de": args.desktop_svg,
    }
    if any(v is not None for v in icon_files.values()):
        for key, path in icon_files.items():
            if path is None:
                raise ValueError(f"Missing SVG path for {key}. Provide all four icon SVG arguments.")
            if not path.exists():
                raise FileNotFoundError(f"Missing icon SVG: {path}")
    nohint = make_nohint_fonts(copied, nohint_dir)
    harmonized = harmonize_incompatible_glyphs(
        nohint,
        harmonized_dir,
        icon_files=icon_files if all(v is not None for v in icon_files.values()) else None,
    )

    vf_path = build_variable_font(harmonized, args.family, args.version, version_outdir)
    static_paths = build_static_instances(vf_path, args.family, args.version, version_outdir)

    print("Built variable font:", vf_path)
    print("Built static fonts:")
    for p in static_paths:
        print(" -", p)

    glyph_report([vf_path, *static_paths])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, SourceDescriptor
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib import build as varlib_build


NAME_IDS = (1, 2, 3, 4, 5, 6, 16, 17, 21, 22)
STYLE_WEIGHTS = {
    "Leise": 280,
    "Klar": 450,
    "Laut": 600,
    "Variabel": 400,
    "Icons": 400,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create Goetheanum v1.4.0 release package.")
    p.add_argument("--version", default="1.4.22")
    p.add_argument("--icons-version", default="0.3.14")
    p.add_argument("--created-date", default=date.today().isoformat())
    p.add_argument(
        "--src-text-dir",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.3.4/install-offiziell"),
    )
    p.add_argument(
        "--src-icons-font",
        type=Path,
        default=None,
    )
    p.add_argument(
        "--src-digit-reference",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1"),
    )
    p.add_argument(
        "--icons-out-dir",
        type=Path,
        default=None,
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
    )
    p.add_argument("--icon-min-advance", type=int, default=1250)
    p.add_argument("--icon-extra-rsb", type=int, default=120)
    p.add_argument("--space-width", type=int, default=360)
    p.add_argument(
        "--c-text-override-svg",
        type=Path,
        default=Path("assets/icons/goetheanum-icons/v0.2.6/src-repaired/nursing_upload_clean.svg"),
        help="Optional cleaned SVG to override C key text glyph (U+E251).",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow deleting existing output directories. Default is safe mode (no overwrite).",
    )
    return p.parse_args()


def set_name_fields(font: TTFont, family: str, style: str, version: str) -> None:
    postscript = f"{family.replace(' ', '')}-{style.replace(' ', '')}"
    full = f"{family} {style}"
    version_string = f"Version {version}"
    unique_id = f"{version};GOEA;{postscript}"

    name = font["name"]
    platforms = {(rec.platformID, rec.platEncID, rec.langID) for rec in name.names}
    platforms |= {(3, 1, 0x409), (1, 0, 0)}

    values = {
        1: family,
        2: style,
        3: unique_id,
        4: full,
        5: version_string,
        6: postscript,
        16: family,
        17: style,
        21: family,
        22: style,
    }
    for pid, eid, lid in sorted(platforms):
        for nid in NAME_IDS:
            name.setName(values[nid], nid, pid, eid, lid)

    if "CFF " in font:
        top = font["CFF "].cff.topDictIndex[0]
        top.FamilyName = family
        top.FullName = full
        top.FontName = postscript
        top.Weight = style


def clear_variable_tables(font: TTFont) -> None:
    for tag in ("fvar", "STAT", "avar", "MVAR", "HVAR"):
        if tag in font:
            del font[tag]


def set_static_metadata(font: TTFont, weight: int) -> None:
    os2 = font["OS/2"]
    os2.usWeightClass = int(weight)
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    os2.fsSelection |= 1 << 6
    font["head"].macStyle &= ~0b11
    font["post"].italicAngle = 0.0


def remove_logo_codepoints(font: TTFont) -> None:
    cps = {0xE100, 0xE101, 0xE102, 0xE103, 0xE140, 0xE141, 0xE142, 0xE143}
    for st in font["cmap"].tables:
        if st.isUnicode():
            for cp in list(st.cmap.keys()):
                if cp in cps:
                    del st.cmap[cp]


def remove_goetheanum_icon_variant_codepoints(font: TTFont) -> None:
    # Remove legacy Goetheanum Icon variant (single building mark) from distribution.
    cps = {0xE103, 0xE143}
    for st in font["cmap"].tables:
        if st.isUnicode():
            for cp in list(st.cmap.keys()):
                if cp in cps:
                    del st.cmap[cp]


def _glyph_name_for_cp(font: TTFont, cp: int) -> str | None:
    cmap = font.getBestCmap() or {}
    return cmap.get(cp)


def _set_cff_glyph_from_ops(font: TTFont, glyph_name: str, ops: list[tuple[str, tuple]]) -> None:
    if "CFF " not in font:
        return
    top = font["CFF "].cff.topDictIndex[0]
    if glyph_name not in top.CharStrings:
        return
    private = getattr(top, "Private", None)
    if private is None and hasattr(top, "FDArray") and len(top.FDArray):
        private = top.FDArray[0].Private
    gsubrs = getattr(top, "GlobalSubrs", None)
    rec = RecordingPen()
    rec.value = list(ops)
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=False)
    rec.replay(pen)
    cs = pen.getCharString(private=private, globalSubrs=gsubrs, optimize=False)
    top.CharStrings[glyph_name] = cs


def _set_cff2_glyph_from_ops(font: TTFont, glyph_name: str, ops: list[tuple[str, tuple]]) -> None:
    if "CFF2" not in font:
        return
    top = font["CFF2"].cff.topDictIndex[0]
    if glyph_name not in top.CharStrings:
        return
    private = None
    if hasattr(top, "FDArray") and len(top.FDArray):
        private = top.FDArray[0].Private
    gsubrs = getattr(top, "GlobalSubrs", None)
    rec = RecordingPen()
    rec.value = list(ops)
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=True)
    rec.replay(pen)
    cs = pen.getCharString(private=private, globalSubrs=gsubrs, optimize=False)
    top.CharStrings[glyph_name] = cs


def _transform_ops(ops: list[tuple[str, tuple]], matrix: tuple[float, float, float, float, float, float]) -> list[tuple[str, tuple]]:
    rec = RecordingPen()
    rec.value = list(ops)
    out = RecordingPen()
    rec.replay(TransformPen(out, matrix))
    return list(out.value)


def _glyph_bounds_from_ops(font: TTFont, ops: list[tuple[str, tuple]]) -> tuple[float, float, float, float] | None:
    glyph_set = font.getGlyphSet()
    rec = RecordingPen()
    rec.value = list(ops)
    bpen = BoundsPen(glyph_set)
    rec.replay(bpen)
    return bpen.bounds


def _split_recording_into_contours(ops: list[tuple[str, tuple]]) -> list[list[tuple[str, tuple]]]:
    contours: list[list[tuple[str, tuple]]] = []
    current: list[tuple[str, tuple]] = []
    for op, args in ops:
        if op == "moveTo":
            if current:
                contours.append(current)
            current = [(op, args)]
            continue
        if not current:
            current = []
        current.append((op, args))
        if op in ("closePath", "endPath"):
            contours.append(current)
            current = []
    if current:
        contours.append(current)
    return contours


def _contour_bounds(glyph_set, contour_ops: list[tuple[str, tuple]]) -> tuple[float, float, float, float] | None:
    rec = RecordingPen()
    rec.value = list(contour_ops)
    bpen = BoundsPen(glyph_set)
    rec.replay(bpen)
    return bpen.bounds


def strip_wc_letters_from_icon_only_glyphs(font: TTFont) -> None:
    # Remove top-right WC letter contours only from the icon-only layer (y/x/c/v).
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    thresholds: dict[int, tuple[float, float]] = {
        0xE219: (430, 700),  # wc_gents
        0xE21A: (430, 700),  # wc_ladies
        0xE21B: (650, 620),  # wc_no_gents
        0xE21C: (430, 700),  # wc_wheelchair
    }
    for cp, (xmin_min, ymin_min) in thresholds.items():
        glyph_name = cmap.get(cp)
        if not glyph_name:
            continue
        rec = RecordingPen()
        glyph_set[glyph_name].draw(rec)
        contours = _split_recording_into_contours(list(rec.value))
        if not contours:
            continue
        filtered: list[tuple[str, tuple]] = []
        removed_any = False
        for contour in contours:
            bounds = _contour_bounds(glyph_set, contour)
            if bounds and bounds[0] >= xmin_min and bounds[1] >= ymin_min:
                removed_any = True
                continue
            filtered.extend(contour)
        if removed_any:
            _set_cff_glyph_from_ops(font, glyph_name, filtered)


def strip_compass_letters_from_icon_only_glyphs(font: TTFont) -> None:
    # Keep original compass needles/circles, remove only directional letter contours
    # from icon-only compass glyphs (F/G/H/J layer).
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    rules: dict[int, tuple[str, float, float]] = {
        # vertical compasses: remove top/bottom letter contours
        0xE203: ("y", 230, 770),  # N up
        0xE206: ("y", 230, 770),  # S up
        # horizontal compasses: remove left/right letter contours
        0xE204: ("x", 220, 780),  # N-S
        0xE205: ("x", 220, 780),  # S-N
    }
    for cp, (axis, lo, hi) in rules.items():
        glyph_name = cmap.get(cp)
        if not glyph_name:
            continue
        rec = RecordingPen()
        glyph_set[glyph_name].draw(rec)
        contours = _split_recording_into_contours(list(rec.value))
        if not contours:
            continue
        filtered: list[tuple[str, tuple]] = []
        removed_any = False
        for contour in contours:
            bounds = _contour_bounds(glyph_set, contour)
            if not bounds:
                filtered.extend(contour)
                continue
            xmin, ymin, xmax, ymax = bounds
            if axis == "y" and (ymax <= lo or ymin >= hi):
                removed_any = True
                continue
            if axis == "x" and (xmax <= lo or xmin >= hi):
                removed_any = True
                continue
            filtered.extend(contour)
        if removed_any:
            _set_cff_glyph_from_ops(font, glyph_name, filtered)


def _collect_svg_paths(svg_path: Path) -> list[str]:
    root = ET.parse(svg_path).getroot()
    ds: list[str] = []
    for el in root.iter():
        if el.tag.split("}")[-1] != "path":
            continue
        d = (el.attrib.get("d") or "").strip()
        if d:
            ds.append(d)
    return ds


def _normalize_svg_paths_to_1000(path_ds: list[str], pad: float = 90.0) -> list[tuple[str, tuple]]:
    rec = RecordingPen()
    for d in path_ds:
        parse_path(d, rec)
    ops = list(rec.value)
    bpen = BoundsPen(None)
    rec.replay(bpen)
    bounds = bpen.bounds
    if not bounds:
        return ops
    xmin, ymin, xmax, ymax = bounds
    bw = xmax - xmin
    bh = ymax - ymin
    if bw <= 0 or bh <= 0:
        return ops
    inner = 1000.0 - (2.0 * pad)
    s = min(inner / bw, inner / bh)
    tx = (1000.0 - bw * s) * 0.5 - xmin * s
    ty = (1000.0 - bh * s) * 0.5 - ymin * s
    return _transform_ops(ops, (s, 0, 0, s, tx, ty))


def override_glyph_from_svg(font: TTFont, cp: int, svg_path: Path, pad: float = 90.0) -> None:
    if not svg_path.exists():
        return
    glyph_name = _glyph_name_for_cp(font, cp)
    if not glyph_name:
        return
    path_ds = _collect_svg_paths(svg_path)
    if not path_ds:
        return
    normalized = _normalize_svg_paths_to_1000(path_ds, pad=pad)
    # Source SVG is y-down; CFF glyphs use y-up.
    ops = _transform_ops(normalized, (1, 0, 0, -1, 0, 1000))
    _set_cff_glyph_from_ops(font, glyph_name, ops)


def _union_bounds(bounds_list: list[tuple[float, float, float, float]]) -> tuple[float, float, float, float] | None:
    if not bounds_list:
        return None
    xmin = min(b[0] for b in bounds_list)
    ymin = min(b[1] for b in bounds_list)
    xmax = max(b[2] for b in bounds_list)
    ymax = max(b[3] for b in bounds_list)
    return (xmin, ymin, xmax, ymax)


def replace_nursing_text_icon_from_upload(font: TTFont, cp: int, svg_path: Path) -> None:
    # Keep existing text contours in glyph cp, replace the full top symbol with cleaned upload icon.
    if not svg_path.exists():
        return
    glyph_name = _glyph_name_for_cp(font, cp)
    if not glyph_name:
        return
    glyph_set = font.getGlyphSet()
    rec = RecordingPen()
    glyph_set[glyph_name].draw(rec)
    contours = _split_recording_into_contours(list(rec.value))
    if not contours:
        return

    text_contours: list[list[tuple[str, tuple]]] = []
    icon_bounds_parts: list[tuple[float, float, float, float]] = []
    for contour in contours:
        b = _contour_bounds(glyph_set, contour)
        if not b:
            continue
        # Existing glyph layout: icon in upper block, labels in lower block.
        if b[1] >= 560:
            icon_bounds_parts.append(b)
        elif b[3] <= 520:
            text_contours.append(contour)
    target_bounds = _union_bounds(icon_bounds_parts)
    if not target_bounds:
        return

    root = ET.parse(svg_path).getroot()
    vb = (root.attrib.get("viewBox") or "").replace(",", " ").split()
    view_h = 1000.0
    if len(vb) == 4:
        try:
            view_h = float(vb[3])
        except Exception:
            view_h = 1000.0

    candidates: list[tuple[float, tuple[float, float, float, float], list[tuple[str, tuple]]]] = []
    for el in root.iter():
        if el.tag.split("}")[-1] != "path":
            continue
        d = (el.attrib.get("d") or "").strip()
        if not d:
            continue
        rec_d = RecordingPen()
        try:
            parse_path(d, rec_d)
        except Exception:
            continue
        bp = BoundsPen(None)
        rec_d.replay(bp)
        b = bp.bounds
        if not b:
            continue
        w = b[2] - b[0]
        h = b[3] - b[1]
        area = max(0.0, w * h)
        if area <= 0:
            continue
        candidates.append((area, b, list(rec_d.value)))
    if not candidates:
        return

    # In upload files, the symbol sits in the top area; the labels are lower.
    # Keep all significant top paths (body + head), not only the largest one.
    top_limit = max(160.0, view_h * 0.42)
    top_candidates = [c for c in candidates if c[1][3] <= top_limit]
    pool = top_candidates or candidates
    max_area = max(c[0] for c in pool)
    chosen = [c for c in pool if c[0] >= (max_area * 0.25)]
    if not chosen:
        chosen = [max(pool, key=lambda x: x[0])]
    if not chosen:
        return

    icon_ops: list[tuple[str, tuple]] = []
    for _area, _b, ops in sorted(chosen, key=lambda x: (x[1][1], -x[0])):
        icon_ops.extend(ops)
    # Convert source y-down to y-up using source viewBox height.
    icon_ops = _transform_ops(icon_ops, (1, 0, 0, -1, 0, view_h))

    # If cleaned SVG still contains only one partial contour, fall back to the
    # canonical non-text nursing icon to preserve head+body geometry.
    if len(_split_recording_into_contours(icon_ops)) < 2:
        source_icon_cp = 0xE211
        source_glyph_name = _glyph_name_for_cp(font, source_icon_cp)
        if source_glyph_name:
            rec_src = RecordingPen()
            glyph_set[source_glyph_name].draw(rec_src)
            icon_ops = list(rec_src.value)
    icon_bounds = _glyph_bounds_from_ops(font, icon_ops)
    if not icon_bounds:
        return

    txmin, tymin, txmax, tymax = target_bounds
    tw = txmax - txmin
    th = tymax - tymin
    sxmin, symin, sxmax, symax = icon_bounds
    sw = sxmax - sxmin
    sh = symax - symin
    if sw <= 0 or sh <= 0 or tw <= 0 or th <= 0:
        return

    scale = min(tw / sw, th / sh) * 0.98
    s_cx = (sxmin + sxmax) * 0.5
    s_cy = (symin + symax) * 0.5
    t_cx = (txmin + txmax) * 0.5
    t_cy = (tymin + tymax) * 0.5
    e = t_cx - scale * s_cx
    f = t_cy - scale * s_cy
    icon_ops = _transform_ops(icon_ops, (scale, 0, 0, scale, e, f))

    merged: list[tuple[str, tuple]] = []
    merged.extend(icon_ops)
    for c in text_contours:
        merged.extend(c)
    _set_cff_glyph_from_ops(font, glyph_name, merged)


def tighten_nursing_text_metrics(font: TTFont, cp: int, target_adv: int = 980) -> None:
    glyph_name = _glyph_name_for_cp(font, cp)
    if not glyph_name:
        return
    hmtx = font["hmtx"].metrics
    if glyph_name not in hmtx:
        return
    _adv, lsb = hmtx[glyph_name]
    hmtx[glyph_name] = (int(target_adv), int(lsb))


def _build_charstring_from_ops(font: TTFont, ops: list[tuple[str, tuple]], *, cff2: bool) -> object:
    if cff2:
        top = font["CFF2"].cff.topDictIndex[0]
        private = None
        if hasattr(top, "FDArray") and len(top.FDArray):
            private = top.FDArray[0].Private
        gsubrs = getattr(top, "GlobalSubrs", None)
    else:
        top = font["CFF "].cff.topDictIndex[0]
        private = getattr(top, "Private", None)
        if private is None and hasattr(top, "FDArray") and len(top.FDArray):
            private = top.FDArray[0].Private
        gsubrs = getattr(top, "GlobalSubrs", None)
    rec = RecordingPen()
    rec.value = list(ops)
    pen = T2CharStringPen(width=None, glyphSet=None, CFF2=cff2)
    rec.replay(pen)
    return pen.getCharString(private=private, globalSubrs=gsubrs, optimize=False)


def _ensure_unique_glyph_name(font: TTFont, base: str) -> str:
    names = set(font.getGlyphOrder())
    if base not in names:
        return base
    i = 1
    while f"{base}.{i}" in names:
        i += 1
    return f"{base}.{i}"


def _append_or_replace_ops_glyph(font: TTFont, glyph_name: str, ops: list[tuple[str, tuple]], adv: int, lsb: int) -> str:
    order = font.getGlyphOrder()
    exists = glyph_name in order
    if not exists:
        glyph_name = _ensure_unique_glyph_name(font, glyph_name)
        order.append(glyph_name)
        font.setGlyphOrder(order)
        font["hmtx"].metrics[glyph_name] = (int(adv), int(lsb))
    else:
        font["hmtx"].metrics[glyph_name] = (int(adv), int(lsb))

    if "CFF " in font:
        top = font["CFF "].cff.topDictIndex[0]
        cs = top.CharStrings
        built = _build_charstring_from_ops(font, ops, cff2=False)
        if glyph_name in cs.charStrings:
            idx = cs.charStrings[glyph_name]
            cs.charStringsIndex.items[idx] = built
        else:
            top.charset.append(glyph_name)
            cs.charStrings[glyph_name] = len(cs.charStringsIndex.items)
            cs.charStringsIndex.items.append(built)

    if "CFF2" in font:
        top2 = font["CFF2"].cff.topDictIndex[0]
        cs2 = top2.CharStrings
        built2 = _build_charstring_from_ops(font, ops, cff2=True)
        if glyph_name in cs2.charStrings:
            idx2 = cs2.charStrings[glyph_name]
            cs2.charStringsIndex.items[idx2] = built2
        else:
            top2.charset.append(glyph_name)
            cs2.charStrings[glyph_name] = len(cs2.charStringsIndex.items)
            cs2.charStringsIndex.items.append(built2)
    return glyph_name


def _map_codepoint_to_glyph(font: TTFont, cp: int, glyph_name: str) -> None:
    for st in font["cmap"].tables:
        if st.isUnicode():
            st.cmap[cp] = glyph_name


def make_alt_arrow_variants(font: TTFont) -> None:
    # Build rotated/mirrored arrow variants for Option layer:
    # short/long arrows (4x each) + bent arrow (4x) + mirrored bent arrow (4x).
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics
    specs = [
        (0xE260, 0xE200, 0, False),
        (0xE261, 0xE200, -90, False),
        (0xE262, 0xE200, 180, False),
        (0xE263, 0xE200, 90, False),
        (0xE264, 0xE201, 0, False),
        (0xE265, 0xE201, -90, False),
        (0xE266, 0xE201, 180, False),
        (0xE267, 0xE201, 90, False),
        (0xE268, 0xE202, 0, False),
        (0xE269, 0xE202, -90, False),
        (0xE26A, 0xE202, 180, False),
        (0xE26B, 0xE202, 90, False),
        # Mirrored set must come from the bent arrow source, not a symmetric straight arrow.
        (0xE26C, 0xE200, 0, True),
        (0xE26D, 0xE200, -90, True),
        (0xE26E, 0xE200, 180, True),
        (0xE26F, 0xE200, 90, True),
    ]
    for dst_cp, src_cp, deg, mirror in specs:
        src_name = cmap.get(src_cp)
        if not src_name:
            continue
        rec = RecordingPen()
        glyph_set[src_name].draw(rec)
        ops = list(rec.value)
        if not ops:
            continue
        bounds = _glyph_bounds_from_ops(font, ops)
        if not bounds:
            continue
        xmin, ymin, xmax, ymax = bounds
        cx = (xmin + xmax) / 2.0
        cy = (ymin + ymax) / 2.0
        transformed = list(ops)
        if mirror:
            transformed = _transform_ops(transformed, (-1, 0, 0, 1, 2.0 * cx, 0))
        if deg:
            rad = math.radians(deg)
            c = math.cos(rad)
            s = math.sin(rad)
            e = cx - c * cx + s * cy
            f = cy - s * cx - c * cy
            transformed = _transform_ops(transformed, (c, s, -s, c, e, f))
        adv, lsb = hmtx.get(src_name, (1000, 0))
        dst_name = _append_or_replace_ops_glyph(font, f"cid{dst_cp:05d}", transformed, adv, lsb)
        _map_codepoint_to_glyph(font, dst_cp, dst_name)


def repair_single_double_guillemets_cff(font: TTFont, side_margin: int = 20, pair_overlap: float = 0.72) -> None:
    if "CFF " not in font:
        return

    cmap = font.getBestCmap() or {}
    g_single_left = cmap.get(0x2039)
    g_single_right = cmap.get(0x203A)
    g_double_left = cmap.get(0x00AB)
    g_double_right = cmap.get(0x00BB)
    if not g_single_left or not g_single_right or not g_double_left or not g_double_right:
        return

    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics

    rec_left_src = RecordingPen()
    glyph_set[g_single_left].draw(rec_left_src)
    ops_left_src = list(rec_left_src.value)
    if not ops_left_src:
        return

    bpen = BoundsPen(glyph_set)
    glyph_set[g_single_left].draw(bpen)
    if not bpen.bounds:
        return
    xmin, _ymin, xmax, _ymax = bpen.bounds
    stem_width = xmax - xmin
    new_adv = int(round(stem_width + side_margin * 2))
    dx = side_margin - xmin

    ops_left = _transform_ops(ops_left_src, (1, 0, 0, 1, dx, 0))
    _set_cff_glyph_from_ops(font, g_single_left, ops_left)
    hmtx[g_single_left] = (new_adv, int(side_margin))

    ops_right = _transform_ops(ops_left, (-1, 0, 0, 1, new_adv, 0))
    _set_cff_glyph_from_ops(font, g_single_right, ops_right)
    hmtx[g_single_right] = (new_adv, int(side_margin))

    shift = int(round(new_adv * pair_overlap))
    rec_double_left = RecordingPen()
    rec_single = RecordingPen()
    rec_single.value = list(ops_left)
    rec_single.replay(rec_double_left)
    rec_single.replay(TransformPen(rec_double_left, (1, 0, 0, 1, shift, 0)))
    ops_double_left = list(rec_double_left.value)

    _set_cff_glyph_from_ops(font, g_double_left, ops_double_left)
    double_adv = new_adv + shift
    hmtx[g_double_left] = (double_adv, int(side_margin))

    ops_double_right = _transform_ops(ops_double_left, (-1, 0, 0, 1, double_adv, 0))
    _set_cff_glyph_from_ops(font, g_double_right, ops_double_right)
    hmtx[g_double_right] = (double_adv, int(side_margin))


def shift_guillemets_right_cff(font: TTFont, single_dx: int = 0, double_dx: int = 0) -> None:
    if "CFF " not in font:
        return
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    for cp, dx in ((0x2039, single_dx), (0x203A, single_dx), (0x00AB, double_dx), (0x00BB, double_dx)):
        if dx == 0:
            continue
        g = cmap.get(cp)
        if not g:
            continue
        rec = RecordingPen()
        glyph_set[g].draw(rec)
        ops = list(rec.value)
        if not ops:
            continue
        _set_cff_glyph_from_ops(font, g, _transform_ops(ops, (1, 0, 0, 1, dx, 0)))


def repair_single_double_guillemets_cff2(font: TTFont, side_margin: int = 19, pair_overlap: float = 0.72) -> None:
    if "CFF2" not in font:
        return

    cmap = font.getBestCmap() or {}
    g_single_left = cmap.get(0x2039)
    g_single_right = cmap.get(0x203A)
    g_double_left = cmap.get(0x00AB)
    g_double_right = cmap.get(0x00BB)
    if not g_single_left or not g_single_right or not g_double_left or not g_double_right:
        return

    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics

    rec_left_src = RecordingPen()
    glyph_set[g_single_left].draw(rec_left_src)
    ops_left_src = list(rec_left_src.value)
    if not ops_left_src:
        return

    bpen = BoundsPen(glyph_set)
    glyph_set[g_single_left].draw(bpen)
    if not bpen.bounds:
        return
    xmin, _ymin, xmax, _ymax = bpen.bounds
    stem_width = xmax - xmin
    new_adv = int(round(stem_width + side_margin * 2))
    dx = side_margin - xmin

    ops_left = _transform_ops(ops_left_src, (1, 0, 0, 1, dx, 0))
    _set_cff2_glyph_from_ops(font, g_single_left, ops_left)
    hmtx[g_single_left] = (new_adv, int(side_margin))

    ops_right = _transform_ops(ops_left, (-1, 0, 0, 1, new_adv, 0))
    _set_cff2_glyph_from_ops(font, g_single_right, ops_right)
    hmtx[g_single_right] = (new_adv, int(side_margin))

    shift = int(round(new_adv * pair_overlap))
    rec_double_left = RecordingPen()
    rec_single = RecordingPen()
    rec_single.value = list(ops_left)
    rec_single.replay(rec_double_left)
    rec_single.replay(TransformPen(rec_double_left, (1, 0, 0, 1, shift, 0)))
    ops_double_left = list(rec_double_left.value)

    _set_cff2_glyph_from_ops(font, g_double_left, ops_double_left)
    double_adv = new_adv + shift
    hmtx[g_double_left] = (double_adv, int(side_margin))

    ops_double_right = _transform_ops(ops_double_left, (-1, 0, 0, 1, double_adv, 0))
    _set_cff2_glyph_from_ops(font, g_double_right, ops_double_right)
    hmtx[g_double_right] = (double_adv, int(side_margin))


def shift_guillemets_right_cff2(font: TTFont, single_dx: int = 0, double_dx: int = 0) -> None:
    if "CFF2" not in font:
        return
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    for cp, dx in ((0x2039, single_dx), (0x203A, single_dx), (0x00AB, double_dx), (0x00BB, double_dx)):
        if dx == 0:
            continue
        g = cmap.get(cp)
        if not g:
            continue
        rec = RecordingPen()
        glyph_set[g].draw(rec)
        ops = list(rec.value)
        if not ops:
            continue
        _set_cff2_glyph_from_ops(font, g, _transform_ops(ops, (1, 0, 0, 1, dx, 0)))


def widen_guillemets_by_advance_only(font: TTFont, single_add: int = 22, double_add: int = 24) -> None:
    cmap = font.getBestCmap() or {}
    hmtx = font["hmtx"].metrics
    single_glyphs = [cmap.get(0x2039), cmap.get(0x203A)]
    double_glyphs = [cmap.get(0x00AB), cmap.get(0x00BB)]

    single_advs = [hmtx[g][0] for g in single_glyphs if g and g in hmtx]
    if single_advs:
        target_single = int(max(single_advs) + single_add)
        for g in single_glyphs:
            if g and g in hmtx:
                _adv, lsb = hmtx[g]
                hmtx[g] = (target_single, int(lsb))

    double_advs = [hmtx[g][0] for g in double_glyphs if g and g in hmtx]
    if double_advs:
        target_double = int(max(double_advs) + double_add)
        for g in double_glyphs:
            if g and g in hmtx:
                _adv, lsb = hmtx[g]
                hmtx[g] = (target_double, int(lsb))


def rebalance_simple_guillemet_spacing_cff(
    font: TTFont,
    single_open_reduce: int = 10,
    single_close_increase: int = 8,
    double_open_reduce: int = 8,
    double_close_increase: int = 6,
) -> None:
    if "CFF " not in font:
        return

    cmap = font.getBestCmap() or {}
    hmtx = font["hmtx"].metrics
    glyph_set = font.getGlyphSet()

    def reduce_open(cp: int, amount: int) -> None:
        if amount <= 0:
            return
        g = cmap.get(cp)
        if not g or g not in hmtx:
            return
        rec = RecordingPen()
        glyph_set[g].draw(rec)
        bounds = _glyph_bounds_from_ops(font, list(rec.value))
        if not bounds:
            return
        xmin, _ymin, xmax, _ymax = bounds
        adv, lsb = hmtx[g]
        min_adv = int(math.ceil(xmax + max(6, lsb)))
        hmtx[g] = (max(min_adv, adv - amount), int(lsb))

    def increase_close(cp: int, amount: int, use_cff2: bool = False) -> None:
        if amount <= 0:
            return
        g = cmap.get(cp)
        if not g or g not in hmtx:
            return
        rec = RecordingPen()
        glyph_set[g].draw(rec)
        ops = list(rec.value)
        if not ops:
            return
        shifted = _transform_ops(ops, (1, 0, 0, 1, amount, 0))
        _set_cff_glyph_from_ops(font, g, shifted)
        adv, lsb = hmtx[g]
        hmtx[g] = (adv + amount, int(lsb + amount))

    reduce_open(0x2039, single_open_reduce)
    increase_close(0x203A, single_close_increase)
    reduce_open(0x00AB, double_open_reduce)
    increase_close(0x00BB, double_close_increase)


def rebalance_simple_guillemet_spacing_cff2(
    font: TTFont,
    single_open_reduce: int = 10,
    single_close_increase: int = 8,
    double_open_reduce: int = 8,
    double_close_increase: int = 6,
) -> None:
    if "CFF2" not in font:
        return

    cmap = font.getBestCmap() or {}
    hmtx = font["hmtx"].metrics
    glyph_set = font.getGlyphSet()

    def reduce_open(cp: int, amount: int) -> None:
        if amount <= 0:
            return
        g = cmap.get(cp)
        if not g or g not in hmtx:
            return
        rec = RecordingPen()
        glyph_set[g].draw(rec)
        bounds = _glyph_bounds_from_ops(font, list(rec.value))
        if not bounds:
            return
        xmin, _ymin, xmax, _ymax = bounds
        adv, lsb = hmtx[g]
        min_adv = int(math.ceil(xmax + max(6, lsb)))
        hmtx[g] = (max(min_adv, adv - amount), int(lsb))

    def increase_close(cp: int, amount: int) -> None:
        if amount <= 0:
            return
        g = cmap.get(cp)
        if not g or g not in hmtx:
            return
        rec = RecordingPen()
        glyph_set[g].draw(rec)
        ops = list(rec.value)
        if not ops:
            return
        shifted = _transform_ops(ops, (1, 0, 0, 1, amount, 0))
        _set_cff2_glyph_from_ops(font, g, shifted)
        adv, lsb = hmtx[g]
        hmtx[g] = (adv + amount, int(lsb + amount))

    reduce_open(0x2039, single_open_reduce)
    increase_close(0x203A, single_close_increase)
    reduce_open(0x00AB, double_open_reduce)
    increase_close(0x00BB, double_close_increase)


def neutralize_guillemet_kerning(font: TTFont) -> None:
    if "GPOS" not in font:
        return
    cmap = font.getBestCmap() or {}
    gl = cmap.get(0x2039)
    gr = cmap.get(0x203A)
    if not gl or not gr:
        return
    targets = {gl, gr}

    gpos = font["GPOS"].table
    if not gpos.LookupList:
        return

    for lookup in gpos.LookupList.Lookup:
        if lookup.LookupType != 2:
            continue
        for sub in lookup.SubTable:
            if sub.Format == 1:
                cov = list(sub.Coverage.glyphs)
                for idx, first in enumerate(cov):
                    ps = sub.PairSet[idx]
                    if first in targets:
                        ps.PairValueRecord = []
                        continue
                    ps.PairValueRecord = [r for r in ps.PairValueRecord if r.SecondGlyph not in targets]
            elif sub.Format == 2:
                class1_defs = sub.ClassDef1.classDefs if sub.ClassDef1 else {}
                class2_defs = sub.ClassDef2.classDefs if sub.ClassDef2 else {}
                class1_targets = {class1_defs.get(gl, 0), class1_defs.get(gr, 0)}
                class2_targets = {class2_defs.get(gl, 0), class2_defs.get(gr, 0)}

                for c1 in class1_targets:
                    if 0 <= c1 < len(sub.Class1Record):
                        row = sub.Class1Record[c1].Class2Record
                        for c2 in range(len(row)):
                            row[c2].Value1 = None
                            row[c2].Value2 = None

                for row in sub.Class1Record:
                    for c2 in class2_targets:
                        if 0 <= c2 < len(row.Class2Record):
                            row.Class2Record[c2].Value1 = None
                            row.Class2Record[c2].Value2 = None


def repair_text_digits_from_reference(font: TTFont, ref_font_path: Path) -> None:
    if not ref_font_path.exists():
        return
    ref = TTFont(ref_font_path)
    ref_cmap = ref.getBestCmap() or {}
    ref.close()
    fallback_digits = {
        0x31: "one",
        0x32: "two",
        0x33: "three",
        0x34: "four",
    }
    glyph_order = set(font.getGlyphOrder())
    for cp in (0x31, 0x32, 0x33, 0x34):
        g = ref_cmap.get(cp)
        if not g or g not in glyph_order:
            g = fallback_digits.get(cp)
        if not g or g not in glyph_order:
            continue
        for st in font["cmap"].tables:
            if st.isUnicode():
                st.cmap[cp] = g


def parse_cp(value: str) -> int:
    return int(value.replace("U+", "0x"), 16)


def apply_icons_ascii_mapping(font: TTFont, mapping_json: Path) -> None:
    data = json.loads(mapping_json.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    cmap = font.getBestCmap() or {}

    def glyph_for_cp(cp: int) -> str | None:
        return cmap.get(cp)

    default_lower = glyph_for_cp(0xE101)
    default_upper = glyph_for_cp(0xE141) or default_lower

    for row in rows:
        lower_key = row.get("lower_key", "")
        upper_key = row.get("upper_key", "")
        cp = parse_cp(row["codepoint"])
        ucp = parse_cp(row["upper_codepoint"])
        lower_glyph = glyph_for_cp(cp)
        upper_glyph = glyph_for_cp(ucp)
        if lower_key and len(lower_key) == 1 and lower_glyph:
            for st in font["cmap"].tables:
                if st.isUnicode():
                    st.cmap[ord(lower_key)] = lower_glyph
        if upper_key and len(upper_key) == 1 and upper_glyph:
            for st in font["cmap"].tables:
                if st.isUnicode():
                    st.cmap[ord(upper_key)] = upper_glyph

    for ch in "abcdefghijklmnopqrstuvwxyz":
        if default_lower:
            for st in font["cmap"].tables:
                if st.isUnicode() and ord(ch) not in st.cmap:
                    st.cmap[ord(ch)] = default_lower
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if default_upper:
            for st in font["cmap"].tables:
                if st.isUnicode() and ord(ch) not in st.cmap:
                    st.cmap[ord(ch)] = default_upper


def patch_icons_spacing(font: TTFont, min_advance: int, extra_rsb: int, space_width: int) -> None:
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics

    glyphs = set(cmap.values())
    for g in sorted(glyphs):
        if g == "space" or g not in hmtx:
            continue
        adv, lsb = hmtx[g]
        bpen = BoundsPen(glyph_set)
        glyph_set[g].draw(bpen)
        if bpen.bounds:
            xmax = bpen.bounds[2]
            adv_target = int(math.ceil(xmax + extra_rsb))
            adv_new = max(adv, adv_target, min_advance)
        else:
            adv_new = max(adv, min_advance)
        hmtx[g] = (adv_new, max(0, lsb))

    if "space" in hmtx:
        _, lsb = hmtx["space"]
        hmtx["space"] = (space_width, lsb)
    font["hhea"].numberOfHMetrics = len(hmtx)


def remove_icon_layout_tables(font: TTFont) -> None:
    for tag in ("GPOS", "GSUB", "kern", "morx", "kerx"):
        if tag in font:
            del font[tag]


def adjust_variable_instances(font: TTFont, family: str) -> None:
    if "fvar" not in font:
        return
    name = font["name"]
    instances: list[NamedInstance] = []
    for style, wght in (("Leise", 280.0), ("Klar", 450.0), ("Laut", 600.0)):
        sub_id = name.addName(style)
        ps_id = name.addName(f"{family.replace(' ', '')}-{style}")
        inst = NamedInstance()
        inst.subfamilyNameID = sub_id
        inst.postscriptNameID = ps_id
        inst.coordinates = {"wght": wght}
        instances.append(inst)
    font["fvar"].instances = instances


def build_variable_from_static_masters(
    out_font: Path,
    leise: Path,
    klar: Path,
    laut: Path,
    family: str,
) -> None:
    tmp = out_font.parent / "_var_build_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    ds_path = tmp / "goetheanum-variable.designspace"

    ds = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name = "Weight"
    axis.tag = "wght"
    axis.minimum = 280
    axis.maximum = 600
    axis.default = 450
    axis.map = [(280, 280), (450, 450), (600, 600)]
    ds.addAxis(axis)

    for style, src, weight in (
        ("Leise", leise, 280),
        ("Klar", klar, 450),
        ("Laut", laut, 600),
    ):
        s = SourceDescriptor()
        s.path = str(src.resolve())
        s.name = style
        s.familyName = family
        s.styleName = style
        s.location = {"Weight": weight}
        if style == "Klar":
            s.copyLib = True
            s.copyInfo = True
            s.copyGroups = True
            s.copyFeatures = True
        ds.addSource(s)

    ds.write(ds_path)
    vf, _, _ = varlib_build(str(ds_path))
    vf.save(out_font)
    shutil.rmtree(tmp)


def write_woff(src_otf: Path, out_woff: Path) -> None:
    font = TTFont(src_otf)
    font.flavor = "woff"
    out_woff.parent.mkdir(parents=True, exist_ok=True)
    font.save(out_woff)
    font.close()


def maybe_write_woff2(src_otf: Path, out_woff2: Path) -> bool:
    try:
        import brotli  # noqa: F401
    except Exception:
        return False
    font = TTFont(src_otf)
    font.flavor = "woff2"
    out_woff2.parent.mkdir(parents=True, exist_ok=True)
    font.save(out_woff2)
    font.close()
    return True


def zip_dir(src_dir: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for f in sorted(src_dir.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(src_dir.parent))


def resolve_src_icons_font(explicit: Path | None, icons_version: str) -> Path:
    if explicit is not None:
        return explicit
    wanted = Path(f"output/goetheanum-icons/v{icons_version}/Goetheanum-Icons-v{icons_version}-Filled.otf")
    if wanted.exists():
        return wanted
    available = sorted(Path("output/goetheanum-icons").glob("v*/Goetheanum-Icons-v*-Filled.otf"))
    if available:
        return available[-1]
    raise FileNotFoundError("No icon source font found. Pass --src-icons-font explicitly.")


def run_keylayout_generator(version: str, out_dir: Path) -> tuple[Path, Path]:
    subprocess.check_call(
        [
            sys.executable,
            "scripts/generate_goetheanum_icons_keylayout.py",
            "--version",
            version,
            "--out-dir",
            str(out_dir),
            "--upper-mode",
            "labeled-glyph",
        ]
    )
    return (
        out_dir / "Goetheanum-Icons-DE.keylayout",
        out_dir / f"keyboard-mapping-v{version}.json",
    )


def run_user_pdf(
    out_pdf: Path,
    font_leise: Path,
    font_klar: Path,
    font_laut: Path,
    font_variabel: Path,
    font_icons: Path,
    mapping_json: Path,
    version: str,
    created_date: str,
) -> None:
    swift_script = Path("scripts/generate_goetheanum_user_pdf.swift")
    swift_bin = Path("tmp/goetheanum_user_pdf_bin")
    swift_bin.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["HOME"] = str((Path.cwd() / "tmp" / "home").resolve())
    Path(env["HOME"]).mkdir(parents=True, exist_ok=True)

    subprocess.check_call(["swiftc", str(swift_script), "-o", str(swift_bin)], env=env)
    subprocess.check_call(
        [
            str(swift_bin),
            "--font-leise",
            str(font_leise),
            "--font-klar",
            str(font_klar),
            "--font-laut",
            str(font_laut),
            "--font-variable",
            str(font_variabel),
            "--font-icons",
            str(font_icons),
            "--mapping-json",
            str(mapping_json),
            "--version",
            version,
            "--created-date",
            created_date,
            "--out-pdf",
            str(out_pdf),
        ],
        env=env,
    )


def main() -> None:
    args = parse_args()
    if args.out_dir is None:
        args.out_dir = Path(f"output/goetheanum-fonts/v{args.version}")
    if args.icons_out_dir is None:
        args.icons_out_dir = Path(f"output/goetheanum-icons/v{args.icons_version}")
    src_icons_font = resolve_src_icons_font(args.src_icons_font, args.icons_version)
    src_icons_font_runtime = src_icons_font

    if args.out_dir.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing out-dir: {args.out_dir}. "
                "Use a new version/path or pass --overwrite."
            )
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.icons_out_dir.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing icons-out-dir: {args.icons_out_dir}. "
                "Use a new version/path or pass --overwrite."
            )
        # Keep source icon font available when input and output directory are identical.
        if src_icons_font.exists() and args.icons_out_dir in src_icons_font.resolve().parents:
            tmp_src = Path("tmp") / src_icons_font.name
            tmp_src.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_icons_font, tmp_src)
            src_icons_font_runtime = tmp_src
        shutil.rmtree(args.icons_out_dir)
    args.icons_out_dir.mkdir(parents=True, exist_ok=True)

    keylayout_path, mapping_json = run_keylayout_generator(args.icons_version, args.icons_out_dir)

    off_root = args.out_dir / f"Goetheanum-Schriften-v{args.version}"
    opt_root = args.out_dir / f"Goetheanum-Schriften-v{args.version}-Optional-Input"
    off_fonts = off_root / "Fonts"
    off_variable = off_root / "Variable"
    off_woff = off_root / "Webfonts" / "woff"
    off_woff2 = off_root / "Webfonts" / "woff2"
    opt_root.mkdir(parents=True, exist_ok=True)
    off_fonts.mkdir(parents=True, exist_ok=True)
    off_variable.mkdir(parents=True, exist_ok=True)
    off_woff.mkdir(parents=True, exist_ok=True)

    src_leise = args.src_text_dir / "Goetheanum-v1.3.4-Leise.otf"
    src_klar = args.src_text_dir / "Goetheanum-v1.3.4-Klar.otf"
    src_laut = args.src_text_dir / "Goetheanum-v1.3.4-Laut.otf"

    out_leise = off_fonts / f"Goetheanum-Schrift-v{args.version}-Leise.otf"
    out_klar = off_fonts / f"Goetheanum-Schrift-v{args.version}-Klar.otf"
    out_laut = off_fonts / f"Goetheanum-Schrift-v{args.version}-Laut.otf"
    out_variabel = off_variable / f"Goetheanum-Variabel-v{args.version}.otf"
    out_icons = off_fonts / f"Goetheanum-Icons-v{args.icons_version}.otf"

    refs = {
        "Leise": args.src_digit_reference / "Goetheanum-v1.2.1-Leise.otf",
        "Klar": args.src_digit_reference / "Goetheanum-v1.2.1-Klar.otf",
        "Laut": args.src_digit_reference / "Goetheanum-v1.2.1-Laut.otf",
    }

    # Base sidebearing air + asymmetrical fine-tuning:
    # opening ‹/« slightly tighter to following letters, closing ›/» with more lead-in.
    guillemet_margins = {"Leise": 92, "Klar": 94, "Laut": 96}
    for style, src, ref, dst in (
        ("Leise", src_leise, refs["Leise"], out_leise),
        ("Klar", src_klar, refs["Klar"], out_klar),
        ("Laut", src_laut, refs["Laut"], out_laut),
    ):
        font = TTFont(src)
        remove_logo_codepoints(font)
        repair_text_digits_from_reference(font, ref)
        repair_single_double_guillemets_cff(font, side_margin=guillemet_margins[style], pair_overlap=0.72)
        rebalance_simple_guillemet_spacing_cff(
            font,
            single_open_reduce=10,
            single_close_increase=8,
            double_open_reduce=8,
            double_close_increase=6,
        )
        neutralize_guillemet_kerning(font)
        clear_variable_tables(font)
        set_name_fields(font, "Goetheanum Schrift", style, args.version)
        set_static_metadata(font, STYLE_WEIGHTS[style])
        font.save(dst)
        font.close()

    # Build variable from the already repaired static masters so guillemets
    # stay symmetric and interpolate consistently across weights.
    build_variable_from_static_masters(
        out_font=out_variabel,
        leise=out_leise,
        klar=out_klar,
        laut=out_laut,
        family="Goetheanum Variabel",
    )
    variabel = TTFont(out_variabel)
    # Keep variable guillemets from static masters unchanged.
    # Rewriting CFF2 outlines here can cause inconsistent/empty glyphs in UI previews.
    neutralize_guillemet_kerning(variabel)
    set_name_fields(variabel, "Goetheanum Variabel", "Variabel", args.version)
    set_static_metadata(variabel, STYLE_WEIGHTS["Variabel"])
    adjust_variable_instances(variabel, "Goetheanum Variabel")
    variabel.save(out_variabel)
    variabel.close()

    icons = TTFont(src_icons_font_runtime)
    replace_nursing_text_icon_from_upload(icons, 0xE251, args.c_text_override_svg)
    strip_wc_letters_from_icon_only_glyphs(icons)
    strip_compass_letters_from_icon_only_glyphs(icons)
    make_alt_arrow_variants(icons)
    apply_icons_ascii_mapping(icons, mapping_json)
    remove_goetheanum_icon_variant_codepoints(icons)
    patch_icons_spacing(icons, args.icon_min_advance, args.icon_extra_rsb, args.space_width)
    tighten_nursing_text_metrics(icons, 0xE251, target_adv=980)
    remove_icon_layout_tables(icons)
    clear_variable_tables(icons)
    set_name_fields(icons, "Goetheanum Icons", "Icons", args.icons_version)
    set_static_metadata(icons, STYLE_WEIGHTS["Icons"])
    icons.save(out_icons)
    icons.close()
    shutil.copy2(out_icons, args.icons_out_dir / f"Goetheanum-Icons-v{args.icons_version}-Filled.otf")

    created_any_woff2 = False
    for f in (out_leise, out_klar, out_laut, out_variabel, out_icons):
        write_woff(f, off_woff / (f.stem + ".woff"))
        created_any_woff2 = maybe_write_woff2(f, off_woff2 / (f.stem + ".woff2")) or created_any_woff2

    if not created_any_woff2 and off_woff2.exists():
        shutil.rmtree(off_woff2)

    beipack_pdf = off_root / "Beipackzettel-Goetheanum-Schriften.pdf"
    run_user_pdf(
        out_pdf=beipack_pdf,
        font_leise=out_leise,
        font_klar=out_klar,
        font_laut=out_laut,
        font_variabel=out_variabel,
        font_icons=out_icons,
        mapping_json=mapping_json,
        version=args.version,
        created_date=args.created_date,
    )

    shutil.copy2(keylayout_path, opt_root / keylayout_path.name)

    off_zip = args.out_dir / f"Goetheanum-Schriften-v{args.version}.zip"
    opt_zip = args.out_dir / f"Goetheanum-Schriften-v{args.version}-Optional-Input.zip"
    zip_dir(off_root, off_zip)
    zip_dir(opt_root, opt_zip)

    print(out_leise)
    print(out_klar)
    print(out_laut)
    print(out_variabel)
    print(out_icons)
    print(beipack_pdf)
    print(off_zip)
    print(opt_zip)
    if not created_any_woff2:
        print("NOTE: WOFF2 not created (brotli module unavailable).", file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path


@dataclass
class SvgAudit:
    source_name: str
    repaired_name: str
    path_count: int
    has_stroke: bool
    has_non_path_shapes: bool
    dropped_white_paths: int
    viewbox: str
    bbox: tuple[float, float, float, float] | None
    aspect_ratio: float | None
    notes: list[str]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QA + normalize Goetheanum icon SVGs for font production.")
    p.add_argument("--src-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--pad", type=float, default=90.0, help="Padding in normalized 1000-unit box")
    return p.parse_args()


def style_dict(style: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in style.split(";"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def parse_css_styles(root: ET.Element) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for el in root.iter():
        if el.tag.split("}")[-1] != "style":
            continue
        css = (el.text or "").strip()
        if not css:
            continue
        for m in re.finditer(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}", css):
            cls = m.group(1)
            out[cls] = style_dict(m.group(2))
    return out


def parse_color(value: str) -> tuple[int, int, int] | None:
    v = value.strip().lower()
    if not v:
        return None
    if v == "white":
        return (255, 255, 255)
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3:
            try:
                return tuple(int(ch * 2, 16) for ch in h)  # type: ignore[return-value]
            except ValueError:
                return None
        if len(h) == 6:
            try:
                return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
            except ValueError:
                return None
    m = re.match(r"rgb\(\s*([0-9]+)\s*[,\s]\s*([0-9]+)\s*[,\s]\s*([0-9]+)\s*\)", v)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def is_white_fill(value: str) -> bool:
    rgb = parse_color(value)
    if rgb is None:
        return False
    return rgb[0] >= 245 and rgb[1] >= 245 and rgb[2] >= 245


def slugify(name: str) -> str:
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    n = n.lower()
    n = re.sub(r"[^a-z0-9]+", "_", n).strip("_")
    n = re.sub(r"_+", "_", n)
    if not n:
        n = "icon"
    return n


def collect_paths(svg_path: Path) -> tuple[str, list[str], bool, bool, int]:
    root = ET.parse(svg_path).getroot()
    css = parse_css_styles(root)
    viewbox = root.attrib.get("viewBox", "")
    path_ds: list[str] = []
    has_stroke = False
    has_non_path_shapes = False
    dropped_white_paths = 0

    def merged_style(el: ET.Element) -> dict[str, str]:
        style = style_dict(el.attrib.get("style", ""))
        class_style: dict[str, str] = {}
        for cls in el.attrib.get("class", "").split():
            if cls in css:
                class_style.update(css[cls])
        out = dict(class_style)
        out.update(style)
        for k, v in el.attrib.items():
            if k in {"fill", "stroke", "stroke-width", "opacity"}:
                out[k] = v
        return out

    def parse_points(points: str) -> list[tuple[float, float]]:
        vals = re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", points)
        nums = [float(v) for v in vals]
        return [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]

    def shape_to_path(el: ET.Element, tag: str) -> str:
        if tag == "rect":
            x = float(el.attrib.get("x", "0"))
            y = float(el.attrib.get("y", "0"))
            w = float(el.attrib.get("width", "0"))
            h = float(el.attrib.get("height", "0"))
            if w <= 0 or h <= 0:
                return ""
            return f"M{x} {y}H{x+w}V{y+h}H{x}Z"
        if tag == "circle":
            cx = float(el.attrib.get("cx", "0"))
            cy = float(el.attrib.get("cy", "0"))
            r = float(el.attrib.get("r", "0"))
            if r <= 0:
                return ""
            return f"M{cx-r} {cy}A{r} {r} 0 1 0 {cx+r} {cy}A{r} {r} 0 1 0 {cx-r} {cy}Z"
        if tag == "ellipse":
            cx = float(el.attrib.get("cx", "0"))
            cy = float(el.attrib.get("cy", "0"))
            rx = float(el.attrib.get("rx", "0"))
            ry = float(el.attrib.get("ry", "0"))
            if rx <= 0 or ry <= 0:
                return ""
            return f"M{cx-rx} {cy}A{rx} {ry} 0 1 0 {cx+rx} {cy}A{rx} {ry} 0 1 0 {cx-rx} {cy}Z"
        if tag == "line":
            x1 = float(el.attrib.get("x1", "0"))
            y1 = float(el.attrib.get("y1", "0"))
            x2 = float(el.attrib.get("x2", "0"))
            y2 = float(el.attrib.get("y2", "0"))
            return f"M{x1} {y1}L{x2} {y2}"
        if tag in {"polygon", "polyline"}:
            pts = parse_points(el.attrib.get("points", ""))
            if len(pts) < 2:
                return ""
            cmd = f"M{pts[0][0]} {pts[0][1]}"
            for x, y in pts[1:]:
                cmd += f"L{x} {y}"
            if tag == "polygon":
                cmd += "Z"
            return cmd
        return ""

    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag in {"rect", "circle", "ellipse", "polygon", "polyline", "line"}:
            has_non_path_shapes = True
        if tag not in {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}:
            continue
        d = el.attrib.get("d", "").strip() if tag == "path" else shape_to_path(el, tag)
        if not d:
            continue
        style = merged_style(el)
        fill = style.get("fill", "")
        if fill and fill.lower() != "none" and is_white_fill(fill):
            dropped_white_paths += 1
            continue

        stroke = style.get("stroke", "none")
        if stroke and stroke.lower() != "none":
            has_stroke = True

        # If shape has neither fill nor explicit black path intent, only stroke information
        # would be available (not expanded to outlines in this script). Keep path geometry for
        # existing path elements (for audit visibility), but skip non-path stroke-only shapes.
        if tag != "path" and ((not fill) or fill.lower() == "none"):
            continue
        path_ds.append(d)

    return viewbox, path_ds, has_stroke, has_non_path_shapes, dropped_white_paths


def normalize_to_1000(path_ds: list[str], pad: float) -> tuple[str, tuple[float, float, float, float]]:
    rec = RecordingPen()
    seen: set[str] = set()
    for d in path_ds:
        if d in seen:
            continue
        seen.add(d)
        parse_path(d, rec)

    bpen = BoundsPen(None)
    rec.replay(bpen)
    if not bpen.bounds:
        raise ValueError("No drawable bounds found")
    xmin, ymin, xmax, ymax = bpen.bounds
    bw = xmax - xmin
    bh = ymax - ymin
    if bw <= 0 or bh <= 0:
        raise ValueError("Degenerate bounds")

    target = 1000.0
    inner = target - 2.0 * pad
    scale = min(inner / bw, inner / bh)
    draw_w = bw * scale
    draw_h = bh * scale
    x_off = (target - draw_w) / 2.0
    y_off = (target - draw_h) / 2.0

    # SVG output is y-down in 0..1000 viewBox.
    tx = x_off - xmin * scale
    ty = y_off - ymin * scale
    m = (scale, 0, 0, scale, tx, ty)

    spen = SVGPathPen(None)
    rec.replay(TransformPen(spen, m))
    d_norm = spen.getCommands()
    return d_norm, (xmin, ymin, xmax, ymax)


def write_repaired_svg(out_path: Path, d_norm: str, source_name: str) -> None:
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!-- source: {source_name} -->\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">\n'
        f'  <path d="{d_norm}" fill="#000000"/>\n'
        "</svg>\n"
    )
    out_path.write_text(svg, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    src_files = sorted(args.src_dir.glob("*.svg"))
    if not src_files:
        raise SystemExit(f"No SVG files in {args.src_dir}")

    audits: list[SvgAudit] = []
    slug_seen: dict[str, int] = {}

    for svg in src_files:
        viewbox, path_ds, has_stroke, has_non_path_shapes, dropped_white_paths = collect_paths(svg)
        notes: list[str] = []

        if has_stroke:
            notes.append("stroke_detected")
        if has_non_path_shapes:
            notes.append("non_path_shape_detected")
        if not path_ds:
            notes.append("no_path_data")
        if dropped_white_paths:
            notes.append(f"white_bg_removed:{dropped_white_paths}")

        base_slug = slugify(svg.stem)
        idx = slug_seen.get(base_slug, 0)
        slug_seen[base_slug] = idx + 1
        repaired_slug = f"{base_slug}_{idx+1}" if idx > 0 else base_slug
        repaired_name = f"{repaired_slug}.svg"
        repaired_path = args.out_dir / repaired_name

        bbox = None
        aspect = None
        if path_ds:
            d_norm, bbox = normalize_to_1000(path_ds, pad=args.pad)
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            aspect = bw / bh if bh else None
            write_repaired_svg(repaired_path, d_norm, svg.name)
        else:
            repaired_path.write_text("", encoding="utf-8")

        audits.append(
            SvgAudit(
                source_name=svg.name,
                repaired_name=repaired_name,
                path_count=len(path_ds),
                has_stroke=has_stroke,
                has_non_path_shapes=has_non_path_shapes,
                dropped_white_paths=dropped_white_paths,
                viewbox=viewbox or "(none)",
                bbox=bbox,
                aspect_ratio=aspect,
                notes=notes,
            )
        )

    lines = [
        "# Goetheanum Icons SVG QA + Repair",
        "",
        f"- Source dir: `{args.src_dir}`",
        f"- Repaired dir: `{args.out_dir}`",
        f"- Source files: `{len(src_files)}`",
        f"- Padding normalized box: `{args.pad}`",
        "",
        "| Source | Repaired | Paths | White Dropped | Stroke | Non-Path | ViewBox | BBox | Aspect | Notes |",
        "|---|---|---:|---:|:---:|:---:|---|---|---:|---|",
    ]
    for a in audits:
        bbox = (
            f"({a.bbox[0]:.2f}, {a.bbox[1]:.2f}, {a.bbox[2]:.2f}, {a.bbox[3]:.2f})"
            if a.bbox
            else "-"
        )
        aspect = f"{a.aspect_ratio:.3f}" if a.aspect_ratio is not None else "-"
        notes = ", ".join(a.notes) if a.notes else "ok"
        lines.append(
            f"| `{a.source_name}` | `{a.repaired_name}` | {a.path_count} | {a.dropped_white_paths} | "
            f"{'yes' if a.has_stroke else 'no'} | {'yes' if a.has_non_path_shapes else 'no'} | "
            f"`{a.viewbox}` | `{bbox}` | {aspect} | {notes} |"
        )
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.report)


if __name__ == "__main__":
    main()

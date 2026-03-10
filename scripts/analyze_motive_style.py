#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
import statistics
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

SVG_NS = "{http://www.w3.org/2000/svg}"
NUM_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
CMD_OR_NUM_RE = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")

STOP_TOKENS = {
    "zeichnung", "fragment", "web", "main", "tok", "rt", "all", "svg", "image",
    "wie", "das", "der", "die", "und", "mit", "von", "im", "am", "auf", "zu", "f", "b"
}

CMD_GROUPS = ["M", "L", "C", "Q", "A", "H", "V", "S", "T", "Z"]
GRID_N = 5
ANGLE_BINS = 12
ALLOWED_SHORT_TOKENS = {"ki"}
NOISE_TOKEN_RE = re.compile(r"^(?:g\d{4}|p\d+[a-z]*|rt\d*|all\d*|tok\d*|main|web|svg|fragment|zeichnung|image|\d+)$")
ISSUE_SUFFIX_RE = re.compile(r"^[a-z]{1,2}\d*$")


@dataclass
class Entry:
    year: str
    issue: str
    date: str
    svg: str
    entry_id: str


@dataclass
class Feature:
    entry: Entry
    motif_key: str
    motif_tokens: List[str]
    view_w: float
    view_h: float
    elem_count: int
    path_count: int
    command_count: int
    curve_ratio: float
    close_ratio: float
    fill_ratio: float
    stroke_ratio: float
    avg_stroke_width_norm: float
    max_stroke_width_norm: float
    occupancy_ratio: float
    bbox_aspect: float
    length_norm: float
    point_count: int
    cmd_hist: Dict[str, float]
    grid_hist: List[float]
    angle_hist: List[float]
    style_label: str
    layout_label: str
    complexity_label: str


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def parse_float(value: Optional[str], default: float = 0.0) -> float:
    if value is None:
        return default
    m = NUM_RE.search(str(value))
    if not m:
        return default
    try:
        return float(m.group())
    except Exception:
        return default


def parse_style_attr(style: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for chunk in (style or "").split(";"):
        if ":" not in chunk:
            continue
        k, v = chunk.split(":", 1)
        out[k.strip().lower()] = v.strip()
    return out


def element_paint(elem: ET.Element) -> Tuple[bool, bool, float]:
    style = parse_style_attr(elem.attrib.get("style", ""))

    fill = elem.attrib.get("fill", style.get("fill", None))
    fill_opacity = parse_float(elem.attrib.get("fill-opacity", style.get("fill-opacity", "1")), 1.0)
    has_fill = fill_opacity > 0 and (fill is None or str(fill).strip().lower() != "none")

    stroke = elem.attrib.get("stroke", style.get("stroke", None))
    stroke_opacity = parse_float(elem.attrib.get("stroke-opacity", style.get("stroke-opacity", "1")), 1.0)
    has_stroke = stroke is not None and stroke_opacity > 0 and str(stroke).strip().lower() != "none"

    sw_raw = elem.attrib.get("stroke-width", style.get("stroke-width", "1"))
    stroke_width = parse_float(sw_raw, 1.0)
    if not has_stroke:
        stroke_width = 0.0

    return has_fill, has_stroke, stroke_width


def parse_viewbox(root: ET.Element) -> Tuple[float, float]:
    vb = root.attrib.get("viewBox")
    if vb:
        nums = NUM_RE.findall(vb)
        if len(nums) == 4:
            w = float(nums[2])
            h = float(nums[3])
            if w > 0 and h > 0:
                return w, h

    w = parse_float(root.attrib.get("width"), 100.0)
    h = parse_float(root.attrib.get("height"), 100.0)
    if w <= 0:
        w = 100.0
    if h <= 0:
        h = 100.0
    return w, h


def bbox_from_points(points: List[Tuple[float, float]]) -> Optional[Tuple[float, float, float, float]]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def merge_bbox(base: Optional[Tuple[float, float, float, float]], nxt: Optional[Tuple[float, float, float, float]]):
    if nxt is None:
        return base
    if base is None:
        return nxt
    return (
        min(base[0], nxt[0]),
        min(base[1], nxt[1]),
        max(base[2], nxt[2]),
        max(base[3], nxt[3]),
    )


def cmd_letter_hist(tokens: List[str]) -> Counter:
    c = Counter()
    for t in tokens:
        if len(t) == 1 and t.isalpha():
            c[t.upper()] += 1
    return c


def dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def parse_path_geometry(d: str) -> Tuple[List[Tuple[float, float]], float, Counter, int, int, int]:
    tokens = CMD_OR_NUM_RE.findall(d or "")
    if not tokens:
        return [], 0.0, Counter(), 0, 0, 0

    hist = cmd_letter_hist(tokens)

    i = 0
    cmd = None
    x = y = 0.0
    sx = sy = 0.0
    points: List[Tuple[float, float]] = []
    total_len = 0.0
    cmd_count = 0
    curve_count = 0
    close_count = 0

    def read_num() -> float:
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    while i < len(tokens):
        t = tokens[i]
        if len(t) == 1 and t.isalpha():
            cmd = t
            i += 1
            cmd_count += 1
        elif cmd is None:
            i += 1
            continue

        if cmd is None:
            continue

        up = cmd.upper()
        rel = cmd.islower()

        if up == "M":
            if i + 1 >= len(tokens):
                break
            x0, y0 = read_num(), read_num()
            if rel:
                x0 += x
                y0 += y
            x, y = x0, y0
            sx, sy = x, y
            points.append((x, y))
            while i + 1 < len(tokens) and not tokens[i].isalpha():
                x1, y1 = read_num(), read_num()
                if rel:
                    x1 += x
                    y1 += y
                total_len += dist((x, y), (x1, y1))
                x, y = x1, y1
                points.append((x, y))

        elif up == "L":
            while i + 1 < len(tokens) and not tokens[i].isalpha():
                x1, y1 = read_num(), read_num()
                if rel:
                    x1 += x
                    y1 += y
                total_len += dist((x, y), (x1, y1))
                x, y = x1, y1
                points.append((x, y))

        elif up == "H":
            while i < len(tokens) and not tokens[i].isalpha():
                x1 = read_num()
                if rel:
                    x1 += x
                total_len += abs(x1 - x)
                x = x1
                points.append((x, y))

        elif up == "V":
            while i < len(tokens) and not tokens[i].isalpha():
                y1 = read_num()
                if rel:
                    y1 += y
                total_len += abs(y1 - y)
                y = y1
                points.append((x, y))

        elif up == "C":
            curve_count += 1
            while i + 5 < len(tokens) and not tokens[i].isalpha():
                x1, y1 = read_num(), read_num()
                x2, y2 = read_num(), read_num()
                x3, y3 = read_num(), read_num()
                if rel:
                    x1 += x; y1 += y
                    x2 += x; y2 += y
                    x3 += x; y3 += y
                total_len += dist((x, y), (x1, y1)) + dist((x1, y1), (x2, y2)) + dist((x2, y2), (x3, y3))
                x, y = x3, y3
                points.extend([(x1, y1), (x2, y2), (x3, y3)])

        elif up == "S":
            curve_count += 1
            while i + 3 < len(tokens) and not tokens[i].isalpha():
                x2, y2 = read_num(), read_num()
                x3, y3 = read_num(), read_num()
                if rel:
                    x2 += x; y2 += y
                    x3 += x; y3 += y
                total_len += dist((x, y), (x2, y2)) + dist((x2, y2), (x3, y3))
                x, y = x3, y3
                points.extend([(x2, y2), (x3, y3)])

        elif up == "Q":
            curve_count += 1
            while i + 3 < len(tokens) and not tokens[i].isalpha():
                x1, y1 = read_num(), read_num()
                x2, y2 = read_num(), read_num()
                if rel:
                    x1 += x; y1 += y
                    x2 += x; y2 += y
                total_len += dist((x, y), (x1, y1)) + dist((x1, y1), (x2, y2))
                x, y = x2, y2
                points.extend([(x1, y1), (x2, y2)])

        elif up == "T":
            curve_count += 1
            while i + 1 < len(tokens) and not tokens[i].isalpha():
                x1, y1 = read_num(), read_num()
                if rel:
                    x1 += x; y1 += y
                total_len += dist((x, y), (x1, y1))
                x, y = x1, y1
                points.append((x, y))

        elif up == "A":
            curve_count += 1
            while i + 6 < len(tokens) and not tokens[i].isalpha():
                _rx, _ry = read_num(), read_num()
                _rot = read_num()
                _laf = read_num()
                _sf = read_num()
                x1, y1 = read_num(), read_num()
                if rel:
                    x1 += x; y1 += y
                total_len += dist((x, y), (x1, y1))
                x, y = x1, y1
                points.append((x, y))

        elif up == "Z":
            close_count += 1
            total_len += dist((x, y), (sx, sy))
            x, y = sx, sy
            points.append((x, y))

        else:
            # unknown command or malformed path
            while i < len(tokens) and not tokens[i].isalpha():
                i += 1

    return points, total_len, hist, cmd_count, curve_count, close_count


def points_from_shape(elem: ET.Element) -> List[Tuple[float, float]]:
    tag = strip_ns(elem.tag)
    pts: List[Tuple[float, float]] = []

    if tag in {"polyline", "polygon"}:
        nums = [float(x) for x in NUM_RE.findall(elem.attrib.get("points", ""))]
        for i in range(0, len(nums) - 1, 2):
            pts.append((nums[i], nums[i + 1]))

    elif tag == "line":
        x1 = parse_float(elem.attrib.get("x1"))
        y1 = parse_float(elem.attrib.get("y1"))
        x2 = parse_float(elem.attrib.get("x2"))
        y2 = parse_float(elem.attrib.get("y2"))
        pts.extend([(x1, y1), (x2, y2)])

    elif tag == "rect":
        x = parse_float(elem.attrib.get("x"))
        y = parse_float(elem.attrib.get("y"))
        w = parse_float(elem.attrib.get("width"))
        h = parse_float(elem.attrib.get("height"))
        pts.extend([(x, y), (x + w, y + h)])

    elif tag == "circle":
        cx = parse_float(elem.attrib.get("cx"))
        cy = parse_float(elem.attrib.get("cy"))
        r = parse_float(elem.attrib.get("r"))
        pts.extend([(cx - r, cy - r), (cx + r, cy + r)])

    elif tag == "ellipse":
        cx = parse_float(elem.attrib.get("cx"))
        cy = parse_float(elem.attrib.get("cy"))
        rx = parse_float(elem.attrib.get("rx"))
        ry = parse_float(elem.attrib.get("ry"))
        pts.extend([(cx - rx, cy - ry), (cx + rx, cy + ry)])

    return pts


def issue_sort(issue: str) -> int:
    m = re.search(r"\d+", issue or "")
    return int(m.group()) if m else 9999


def clean_token(tok: str) -> str:
    t = tok.strip().lower()
    t = t.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    t = re.sub(r"[^a-z0-9]+", "", t)
    return t


def token_is_noise(c: str) -> bool:
    if not c:
        return True
    if c in STOP_TOKENS:
        return True
    if NOISE_TOKEN_RE.fullmatch(c):
        return True
    if ISSUE_SUFFIX_RE.fullmatch(c) and c not in ALLOWED_SHORT_TOKENS:
        return True
    if len(c) <= 1:
        return True
    if len(c) <= 2 and c not in ALLOWED_SHORT_TOKENS:
        return True
    return False


def add_angle_hist(points: List[Tuple[float, float]], bins: List[float]):
    if len(points) < 2:
        return
    n = len(bins)
    for a, b in zip(points, points[1:]):
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        seg_len = math.hypot(dx, dy)
        if seg_len <= 1e-9:
            continue
        ang01 = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
        idx = min(n - 1, int(ang01 * n))
        bins[idx] += seg_len


def normalized_grid_hist(points: List[Tuple[float, float]], bbox: Tuple[float, float, float, float], n: int = GRID_N) -> List[float]:
    hist = [0.0] * (n * n)
    if not points:
        return hist
    x0, y0, x1, y1 = bbox
    bw = max(1e-9, x1 - x0)
    bh = max(1e-9, y1 - y0)
    for x, y in points:
        ux = (x - x0) / bw
        uy = (y - y0) / bh
        ux = 0.0 if ux < 0 else (0.999999 if ux >= 1 else ux)
        uy = 0.0 if uy < 0 else (0.999999 if uy >= 1 else uy)
        ix = int(ux * n)
        iy = int(uy * n)
        hist[iy * n + ix] += 1.0
    total = sum(hist)
    if total > 0:
        hist = [v / total for v in hist]
    return hist


def motif_tokens_from_name(svg_path: str, entry_id: str) -> List[str]:
    stem = Path(svg_path).stem
    stem = re.sub(r"^G\d{4}_\d{1,2}(?:[-_]\d{1,2})?[A-Za-z]*_?", "", stem)
    raw = re.split(r"[_\-]+", stem)

    out: List[str] = []
    for r in raw:
        c = clean_token(r)
        if token_is_noise(c):
            continue
        out.append(c)

    return out


def style_label(fill_ratio: float, stroke_ratio: float, sw_norm: float, curve_ratio: float, occ: float, cmd_count: int, path_count: int, close_ratio: float, length_norm: float) -> str:
    if stroke_ratio >= 0.45:
        if sw_norm >= 0.012:
            return "Breite Feder/Pinselspur"
        return "Linienbetonte Federzeichnung"
    if cmd_count >= 260 or length_norm >= 12:
        return "Dicht-ornamentale Federfigur"
    if occ <= 0.45:
        return "Luftige Zeichenfigur"
    if close_ratio >= 0.55 and path_count <= 2 and occ >= 0.72:
        return "Kompakte Flaechenfigur"
    if curve_ratio >= 0.95:
        return "Fliessende Kurvenfigur"
    if fill_ratio >= 0.8 and stroke_ratio <= 0.1:
        return "Reduzierte Silhouettenfigur"
    return "Gemischte Federfigur"


def layout_label(aspect: float, occ: float) -> str:
    if occ < 0.22:
        density = "viel Leerraum"
    elif occ < 0.5:
        density = "ausgewogene Flaeche"
    else:
        density = "dichte Flaeche"

    if aspect < 0.8:
        orient = "vertikal"
    elif aspect > 1.25:
        orient = "horizontal"
    else:
        orient = "kompakt"

    return f"{orient}, {density}"


def complexity_label(cmd_count: int, length_norm: float) -> str:
    if cmd_count >= 120 or length_norm >= 35:
        return "hoch"
    if cmd_count >= 45 or length_norm >= 14:
        return "mittel"
    return "niedrig"


def analyze_svg(entry: Entry, abs_svg: Path) -> Feature:
    tree = ET.parse(abs_svg)
    root = tree.getroot()

    vw, vh = parse_viewbox(root)
    min_dim = max(1.0, min(vw, vh))
    area = max(1.0, vw * vh)

    elem_count = 0
    path_count = 0
    total_cmd = 0
    total_curve = 0
    total_close = 0
    total_len = 0.0

    fill_elems = 0
    stroke_elems = 0
    stroke_widths: List[float] = []

    global_bbox: Optional[Tuple[float, float, float, float]] = None
    cmd_hist_abs = Counter()
    all_points: List[Tuple[float, float]] = []
    angle_hist_abs = [0.0] * ANGLE_BINS

    drawable_tags = {"path", "polygon", "polyline", "line", "rect", "circle", "ellipse"}

    for elem in root.iter():
        tag = strip_ns(elem.tag)
        if tag not in drawable_tags:
            continue

        elem_count += 1
        has_fill, has_stroke, sw = element_paint(elem)
        if has_fill:
            fill_elems += 1
        if has_stroke:
            stroke_elems += 1
            stroke_widths.append(sw)

        if tag == "path":
            path_count += 1
            pts, plen, hist, cmd_count, curve_count, close_count = parse_path_geometry(elem.attrib.get("d", ""))
            total_len += plen
            total_cmd += cmd_count
            total_curve += curve_count
            total_close += close_count
            cmd_hist_abs.update(hist)
            if pts:
                all_points.extend(pts)
                add_angle_hist(pts, angle_hist_abs)
            global_bbox = merge_bbox(global_bbox, bbox_from_points(pts))
        else:
            pts = points_from_shape(elem)
            if pts:
                all_points.extend(pts)
                add_angle_hist(pts, angle_hist_abs)
            global_bbox = merge_bbox(global_bbox, bbox_from_points(pts))
            # rough contributions for non-paths
            if tag in {"line", "polyline", "polygon"}:
                total_cmd += 1

    if global_bbox is None:
        global_bbox = (0.0, 0.0, 0.0, 0.0)

    bw = max(0.0, global_bbox[2] - global_bbox[0])
    bh = max(0.0, global_bbox[3] - global_bbox[1])
    bbox_area = max(0.0, bw * bh)

    fill_ratio = fill_elems / max(1, elem_count)
    stroke_ratio = stroke_elems / max(1, elem_count)
    avg_sw = statistics.mean(stroke_widths) if stroke_widths else 0.0
    max_sw = max(stroke_widths) if stroke_widths else 0.0
    avg_sw_norm = avg_sw / min_dim
    max_sw_norm = max_sw / min_dim
    curve_ratio = total_curve / max(1, total_cmd)
    close_ratio = total_close / max(1, path_count)
    occupancy = min(1.0, bbox_area / area)
    bbox_aspect = bw / bh if bh > 0 else 1.0
    length_norm = total_len / math.sqrt(area)
    point_count = len(all_points)

    hist_total = sum(cmd_hist_abs.values())
    cmd_hist_norm = {}
    for k in CMD_GROUPS:
        cmd_hist_norm[k] = (cmd_hist_abs.get(k, 0) / hist_total) if hist_total else 0.0

    angle_total = sum(angle_hist_abs)
    angle_hist_norm = [v / angle_total for v in angle_hist_abs] if angle_total > 0 else [0.0] * ANGLE_BINS
    grid_hist = normalized_grid_hist(all_points, global_bbox, n=GRID_N)

    tokens = motif_tokens_from_name(entry.svg, entry.entry_id)
    motif_key = tokens[0] if tokens else ""

    s_label = style_label(fill_ratio, stroke_ratio, avg_sw_norm, curve_ratio, occupancy, total_cmd, path_count, close_ratio, length_norm)
    l_label = layout_label(bbox_aspect, occupancy)
    c_label = complexity_label(total_cmd, length_norm)

    return Feature(
        entry=entry,
        motif_key=motif_key,
        motif_tokens=tokens,
        view_w=vw,
        view_h=vh,
        elem_count=elem_count,
        path_count=path_count,
        command_count=total_cmd,
        curve_ratio=curve_ratio,
        close_ratio=close_ratio,
        fill_ratio=fill_ratio,
        stroke_ratio=stroke_ratio,
        avg_stroke_width_norm=avg_sw_norm,
        max_stroke_width_norm=max_sw_norm,
        occupancy_ratio=occupancy,
        bbox_aspect=bbox_aspect,
        length_norm=length_norm,
        point_count=point_count,
        cmd_hist=cmd_hist_norm,
        grid_hist=grid_hist,
        angle_hist=angle_hist_norm,
        style_label=s_label,
        layout_label=l_label,
        complexity_label=c_label,
    )


def feature_distance(a: Feature, b: Feature) -> float:
    # weighted distance 0..~1
    cmd = sum(abs(a.cmd_hist.get(k, 0.0) - b.cmd_hist.get(k, 0.0)) for k in CMD_GROUPS) * 0.5
    grid = sum(abs(x - y) for x, y in zip(a.grid_hist, b.grid_hist)) * 0.5
    angle = sum(abs(x - y) for x, y in zip(a.angle_hist, b.angle_hist)) * 0.5
    d = 0.0
    d += 0.22 * grid
    d += 0.16 * angle
    d += 0.18 * cmd
    d += 0.10 * abs(a.curve_ratio - b.curve_ratio)
    d += 0.08 * abs(a.close_ratio - b.close_ratio)
    d += 0.07 * min(1.0, abs(a.command_count - b.command_count) / 650.0)
    d += 0.06 * min(1.0, abs(a.path_count - b.path_count) / 12.0)
    d += 0.06 * min(1.0, abs(a.occupancy_ratio - b.occupancy_ratio) * 2.0)
    d += 0.04 * min(1.0, abs(math.log((a.bbox_aspect + 1e-6) / (b.bbox_aspect + 1e-6))) / 1.2)
    d += 0.03 * min(1.0, abs(a.length_norm - b.length_norm) / 28.0)
    return d


def compute_knn(features: List[Feature], k: int = 10) -> List[List[Tuple[float, int]]]:
    n = len(features)
    rows: List[List[Tuple[float, int]]] = [[] for _ in range(n)]
    for i in range(n):
        fi = features[i]
        for j in range(i + 1, n):
            d = feature_distance(fi, features[j])
            rows[i].append((d, j))
            rows[j].append((d, i))
    for i in range(n):
        rows[i].sort(key=lambda t: (t[0], t[1]))
        if k > 0:
            rows[i] = rows[i][:k]
    return rows


def connected_components(features: List[Feature], knn: List[List[Tuple[float, int]]], max_dist: float = 0.085, mutual_topk: int = 4) -> List[List[int]]:
    n = len(features)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    top_sets = []
    for neighbors in knn:
        ids = {idx for _, idx in neighbors[:mutual_topk]}
        top_sets.append(ids)

    for i, neighbors in enumerate(knn):
        for d, j in neighbors[:mutual_topk]:
            if d > max_dist:
                continue
            if i in top_sets[j]:
                union(i, j)

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    comps = sorted(groups.values(), key=lambda g: (-len(g), min(g)))
    return comps


def quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    q = 0.0 if q < 0 else (1.0 if q > 1 else q)
    xs = sorted(values)
    idx = int(round(q * (len(xs) - 1)))
    return xs[idx]


def related_motif_pairs_from_knn(features: List[Feature], motif_groups: Dict[str, List[int]], knn: List[List[Tuple[float, int]]], topk: int = 6, max_dist: float = 0.16, min_votes: int = 3) -> List[Tuple[str, str, float, int, float]]:
    valid_motifs = {k for k, idxs in motif_groups.items() if len(idxs) >= 3}
    if not valid_motifs:
        return []

    idx_to_motif: Dict[int, str] = {}
    for i, ft in enumerate(features):
        if ft.motif_key in valid_motifs:
            idx_to_motif[i] = ft.motif_key

    pair_votes: Dict[Tuple[str, str], int] = defaultdict(int)
    pair_dist_sum: Dict[Tuple[str, str], float] = defaultdict(float)

    for i, neighbors in enumerate(knn):
        a = idx_to_motif.get(i)
        if not a:
            continue
        for d, j in neighbors[:topk]:
            if d > max_dist:
                continue
            b = idx_to_motif.get(j)
            if not b or a == b:
                continue
            key = (a, b) if a < b else (b, a)
            pair_votes[key] += 1
            pair_dist_sum[key] += d

    out: List[Tuple[str, str, float, int, float]] = []
    for (a, b), votes in pair_votes.items():
        if votes < min_votes:
            continue
        size_a = len(motif_groups[a])
        size_b = len(motif_groups[b])
        support = votes / max(1.0, min(size_a, size_b) * topk)
        avg_d = pair_dist_sum[(a, b)] / votes
        out.append((a, b, support, votes, avg_d))

    out.sort(key=lambda t: (-t[2], -t[3], t[4], t[0], t[1]))
    return out


def load_entries(csv_path: Path) -> List[Entry]:
    entries: List[Entry] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            e = Entry(
                year=(row.get("jahr") or "").strip(),
                issue=(row.get("heft") or "").strip(),
                date=(row.get("erscheinung") or "").strip(),
                svg=(row.get("svg") or "").strip(),
                entry_id=(row.get("id") or "").strip(),
            )
            if not e.year or not e.svg or not e.entry_id:
                continue
            entries.append(e)

    entries.sort(key=lambda e: (e.year, issue_sort(e.issue), e.issue, e.entry_id))
    return entries


def cluster_label(cluster: List[Feature]) -> str:
    motif_counter = Counter(f.motif_key for f in cluster if f.motif_key)
    if motif_counter:
        top, c = motif_counter.most_common(1)[0]
        if c >= max(2, int(0.35 * len(cluster))):
            return f"motiv:{top}"
    styles = Counter(f.style_label for f in cluster)
    top_style = styles.most_common(1)[0][0] if styles else "gemischt"
    return f"stil:{top_style}"


def centroid(fs: List[Feature]) -> Dict[str, float]:
    if not fs:
        return {}
    keys = ["curve_ratio", "close_ratio", "fill_ratio", "stroke_ratio", "avg_stroke_width_norm", "occupancy_ratio", "bbox_aspect", "length_norm"]
    out = {}
    for k in keys:
        out[k] = statistics.mean(getattr(f, k) for f in fs)
    for cmd in CMD_GROUPS:
        out[f"cmd_{cmd}"] = statistics.mean(f.cmd_hist.get(cmd, 0.0) for f in fs)
    return out


def centroid_dist(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 1.0
    cmd = sum(abs(a.get(f"cmd_{k}", 0.0) - b.get(f"cmd_{k}", 0.0)) for k in CMD_GROUPS) * 0.5
    d = 0.0
    d += 0.30 * cmd
    d += 0.15 * abs(a["curve_ratio"] - b["curve_ratio"])
    d += 0.12 * abs(a["fill_ratio"] - b["fill_ratio"])
    d += 0.10 * abs(a["stroke_ratio"] - b["stroke_ratio"])
    d += 0.13 * min(1.0, abs(a["avg_stroke_width_norm"] - b["avg_stroke_width_norm"]) * 120)
    d += 0.10 * min(1.0, abs(a["occupancy_ratio"] - b["occupancy_ratio"]) * 2)
    d += 0.05 * min(1.0, abs(math.log((a["bbox_aspect"] + 1e-6) / (b["bbox_aspect"] + 1e-6))) / 1.2)
    d += 0.05 * min(1.0, abs(a["length_norm"] - b["length_norm"]) / 28)
    return d


def short_code(f: Feature) -> str:
    y2 = f.entry.year[-2:] if len(f.entry.year) >= 2 else f.entry.year
    issue = re.sub(r"\s+", "", f.entry.issue)
    issue = issue or "?"
    return f"J{y2}H{issue}"


def ensure_local_assets(base: Path, out_dir: Path, features: List[Feature]) -> Path:
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    seen = set()
    for f in features:
        rel = f.entry.svg.strip().lstrip("/")
        if not rel or rel in seen:
            continue
        seen.add(rel)

        src = base / rel
        if not src.exists() or not src.is_file():
            continue

        dst = assets_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists() and dst.is_file() and (not dst.is_symlink()) and dst.stat().st_size > 0:
            continue

        if dst.exists() or dst.is_symlink():
            dst.unlink()
        shutil.copy2(src, dst)

    return assets_dir


def build_html(out_path: Path, features: List[Feature], clusters: List[List[int]], motif_groups: Dict[str, List[int]], related_pairs: List[Tuple[str, str, float, int, float]], generated: str):
    # compact gallery for manual review of motif relations
    by_idx = {i: f for i, f in enumerate(features)}

    cluster_blocks = []
    for rank, idxs in enumerate(clusters, 1):
        if len(idxs) < 3:
            continue
        fs = [by_idx[i] for i in idxs]
        label = cluster_label(fs)
        cards = []
        for f in fs[:36]:
            local_svg = f"assets/{f.entry.svg}"
            cards.append(
                f'<a class="card" href="{local_svg}" target="_blank" rel="noopener">'
                f'<img src="{local_svg}" loading="lazy" alt="{f.entry.entry_id}">'
                f'<div class="meta"><strong>{short_code(f)}</strong><span>{f.entry.year} · {f.entry.issue}</span><span>{f.motif_key or "—"}</span></div></a>'
            )
        block = (
            f'<section class="box"><h3>Cluster {rank} · {label} · {len(fs)} Zeichnungen</h3>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )
        cluster_blocks.append(block)
        if len(cluster_blocks) >= 24:
            break

    motif_blocks = []
    for motif, idxs in sorted(motif_groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(idxs) < 2:
            continue
        fs = [by_idx[i] for i in idxs]
        cards = []
        for f in fs[:24]:
            local_svg = f"assets/{f.entry.svg}"
            cards.append(
                f'<a class="card small" href="{local_svg}" target="_blank" rel="noopener">'
                f'<img src="{local_svg}" loading="lazy" alt="{f.entry.entry_id}">'
                f'<div class="meta"><strong>{short_code(f)}</strong><span>{f.entry.year}</span></div></a>'
            )
        motif_blocks.append(
            f'<section class="box"><h3>Motiv "{motif}" · {len(fs)} Zeichnungen</h3><div class="grid">{"".join(cards)}</div></section>'
        )
        if len(motif_blocks) >= 18:
            break

    rel_rows = []
    for a, b, support, votes, avg_d in related_pairs[:40]:
        rel_rows.append(f"<tr><td>{a}</td><td>{b}</td><td>{support:.2f}</td><td>{votes}</td><td>{avg_d:.3f}</td></tr>")

    html = f"""<!doctype html>
<html lang=\"de\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>Motiv- & Stilanalyse</title>
<style>
body{{font-family: 'Avenir Next', 'Segoe UI', sans-serif; margin:18px; background:#f5f3ee; color:#1d1a16;}}
h1{{font-size:28px; margin:0 0 8px;}}
.meta{{color:#6b6255; font-size:13px; margin:0 0 14px;}}
section{{margin:0 0 16px;}}
.box{{border:1px solid #d8cfbf; background:#fffefb; border-radius:12px; padding:10px; box-shadow:0 4px 10px rgba(0,0,0,.04);}}
.box h3{{margin:0 0 8px; font-size:15px;}}
.grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(120px,1fr)); gap:8px;}}
.card{{display:grid; gap:6px; border:1px solid #e3dbc9; border-radius:10px; padding:6px; background:#fff; text-decoration:none; color:inherit;}}
.card.small{{grid-template-rows:auto auto;}}
.card img{{width:100%; height:88px; object-fit:contain; background:#f8f4ea; border-radius:6px;}}
.card .meta{{font-size:11px; margin:0; display:grid; gap:1px; color:#5d564b;}}
.card .meta strong{{font-size:12px; color:#1d473f;}}
table{{width:100%; border-collapse:collapse; background:#fff; border:1px solid #ddd2c0; border-radius:8px; overflow:hidden;}}
th,td{{padding:7px 8px; border-bottom:1px solid #eee4d2; font-size:13px; text-align:left;}}
th{{background:#f9f4e8;}}
</style></head><body>
<h1>Motiv- & Stilanalyse (SVG-basiert)</h1>
<p class=\"meta\">Erzeugt am {generated} · Zeichnungen: {len(features)} · Cluster: {len(clusters)}</p>
<section class=\"box\"><h3>Verwandte Motive (KNN-Support)</h3><table><thead><tr><th>Motiv A</th><th>Motiv B</th><th>Support</th><th>Votes</th><th>Ø Distanz</th></tr></thead><tbody>{''.join(rel_rows)}</tbody></table></section>
<section><h2>Stil-Cluster (visuelle Aehnlichkeit)</h2>{''.join(cluster_blocks) or '<div class="box">Keine Cluster mit mindestens 3 Eintraegen gefunden.</div>'}</section>
<section><h2>Motiv-Familien</h2>{''.join(motif_blocks) or '<div class="box">Keine Motiv-Familien mit mindestens 2 Eintraegen gefunden.</div>'}</section>
</body></html>"""

    out_path.write_text(html, encoding="utf-8")


def run(repo_root: Path):
    base = repo_root / "ausgabe_zeichnungen" / "alle_jahrgaenge"
    csv_path = base / "total_verzeichnis.csv"
    out_dir = base / "analyse_motive_stil"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = load_entries(csv_path)

    features: List[Feature] = []
    missing = []
    for e in entries:
        abs_svg = base / e.svg
        if not abs_svg.exists():
            missing.append(e.svg)
            continue
        try:
            features.append(analyze_svg(e, abs_svg))
        except Exception as ex:
            missing.append(f"{e.svg} :: {ex}")

    # pairwise nearest neighbors (entry-level visual features)
    knn = compute_knn(features, k=10)
    nn_dists = [neighbors[0][0] for neighbors in knn if neighbors]
    nn_p50 = quantile(nn_dists, 0.50)
    cluster_max_dist = min(0.11, max(0.07, nn_p50 * 0.9))
    clusters = connected_components(features, knn, max_dist=cluster_max_dist, mutual_topk=3)

    # motif groups
    motif_groups: Dict[str, List[int]] = defaultdict(list)
    for i, f in enumerate(features):
        if f.motif_key:
            motif_groups[f.motif_key].append(i)

    related_pairs: List[Tuple[str, str, float, int, float]] = related_motif_pairs_from_knn(
        features, motif_groups, knn, topk=6, max_dist=max(0.12, cluster_max_dist * 1.5), min_votes=3
    )

    # per-entry nearest neighbors
    nn_rows: List[Tuple[str, str, float]] = []
    for i, fi in enumerate(features):
        for d, j in knn[i][:5]:
            nn_rows.append((fi.entry.entry_id, features[j].entry.entry_id, d))

    # write feature table
    feat_csv = out_dir / "entry_features.csv"
    with feat_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "id", "jahr", "heft", "datum", "svg", "motiv_key", "motiv_tokens", "style_label", "layout_label", "complexity",
            "elem_count", "path_count", "point_count", "command_count", "curve_ratio", "close_ratio", "fill_ratio", "stroke_ratio",
            "avg_stroke_width_norm", "max_stroke_width_norm", "occupancy_ratio", "bbox_aspect", "length_norm"
        ])
        for ft in features:
            w.writerow([
                ft.entry.entry_id, ft.entry.year, ft.entry.issue, ft.entry.date, ft.entry.svg, ft.motif_key,
                "|".join(ft.motif_tokens), ft.style_label, ft.layout_label, ft.complexity_label,
                ft.elem_count, ft.path_count, ft.point_count, ft.command_count,
                f"{ft.curve_ratio:.4f}", f"{ft.close_ratio:.4f}", f"{ft.fill_ratio:.4f}", f"{ft.stroke_ratio:.4f}",
                f"{ft.avg_stroke_width_norm:.6f}", f"{ft.max_stroke_width_norm:.6f}", f"{ft.occupancy_ratio:.4f}",
                f"{ft.bbox_aspect:.4f}", f"{ft.length_norm:.4f}"
            ])

    # style summary
    style_counter = Counter(ft.style_label for ft in features)
    layout_counter = Counter(ft.layout_label for ft in features)
    complexity_counter = Counter(ft.complexity_label for ft in features)

    style_csv = out_dir / "style_summary.csv"
    with style_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kategorie", "label", "anzahl"])
        for k, v in style_counter.most_common():
            w.writerow(["style", k, v])
        for k, v in layout_counter.most_common():
            w.writerow(["layout", k, v])
        for k, v in complexity_counter.most_common():
            w.writerow(["komplexitaet", k, v])

    motif_csv = out_dir / "motif_families.csv"
    with motif_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["motiv", "anzahl", "jahre", "style_mix", "beispiele"])
        for motif, idxs in sorted(motif_groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            if len(idxs) < 2:
                continue
            fs = [features[i] for i in idxs]
            years = sorted({x.entry.year for x in fs})
            styles = Counter(x.style_label for x in fs)
            top_styles = ", ".join(f"{k}({v})" for k, v in styles.most_common(3))
            examples = ", ".join(x.entry.entry_id for x in fs[:6])
            w.writerow([motif, len(idxs), "|".join(years), top_styles, examples])

    rel_csv = out_dir / "related_motif_pairs.csv"
    with rel_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["motiv_a", "motiv_b", "support", "votes", "avg_distanz", "count_a", "count_b"])
        for a, b, support, votes, avg_d in related_pairs:
            w.writerow([a, b, f"{support:.4f}", votes, f"{avg_d:.4f}", len(motif_groups[a]), len(motif_groups[b])])

    nn_csv = out_dir / "nearest_neighbors.csv"
    with nn_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "aehnlich_id", "distanz"])
        for row in nn_rows:
            w.writerow([row[0], row[1], f"{row[2]:.4f}"])

    # cluster table
    cluster_csv = out_dir / "style_clusters.csv"
    with cluster_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cluster_id", "label", "size", "motif_mix", "style_mix", "entries"])
        cidx = 1
        for idxs in clusters:
            if len(idxs) < 3:
                continue
            fs = [features[i] for i in idxs]
            motif_mix = Counter(x.motif_key for x in fs if x.motif_key)
            style_mix = Counter(x.style_label for x in fs)
            motif_txt = ", ".join(f"{k}({v})" for k, v in motif_mix.most_common(5)) if motif_mix else "-"
            style_txt = ", ".join(f"{k}({v})" for k, v in style_mix.most_common(4))
            entries_txt = "|".join(x.entry.entry_id for x in fs)
            w.writerow([cidx, cluster_label(fs), len(fs), motif_txt, style_txt, entries_txt])
            cidx += 1

    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_md = out_dir / "bericht_motive_stil.md"
    with report_md.open("w", encoding="utf-8") as f:
        f.write("# Motiv- und Stilanalyse der Zeichnungen\n\n")
        f.write(f"Erzeugt: {generated}\\\n")
        f.write(f"Grundlage: `total_verzeichnis.csv`\\\n")
        f.write(f"Analysierte Zeichnungen: {len(features)}\n\n")

        f.write("## Wichtigste Motivfamilien (nach Häufigkeit)\n\n")
        for motif, idxs in sorted(motif_groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:20]:
            if len(idxs) < 2:
                continue
            fs = [features[i] for i in idxs]
            years = ", ".join(sorted({x.entry.year for x in fs}))
            styles = Counter(x.style_label for x in fs)
            st = ", ".join(f"{k} ({v})" for k, v in styles.most_common(3))
            ex = ", ".join(x.entry.entry_id for x in fs[:4])
            f.write(f"- **{motif}**: {len(fs)} Zeichnungen · Jahre: {years} · Stil: {st} · Beispiele: `{ex}`\n")

        f.write("\n## Verwandte Motive (stilistische Nähe der Familien)\n\n")
        if related_pairs:
            for a, b, support, votes, avg_d in related_pairs[:40]:
                f.write(
                    f"- `{a}` ↔ `{b}` · Support: {support:.2f} (Votes: {votes}) · "
                    f"Ø Distanz: {avg_d:.3f} · Größen: {len(motif_groups[a])}/{len(motif_groups[b])}\n"
                )
        else:
            f.write("- Keine Paarungen unter dem aktuellen Distanzschwellenwert gefunden.\n")

        f.write("\n## Stilgruppen\n\n")
        for label, count in style_counter.most_common():
            f.write(f"- {label}: {count}\n")

        f.write("\n## Layout-/Flächenaufteilung\n\n")
        for label, count in layout_counter.most_common():
            f.write(f"- {label}: {count}\n")

        f.write("\n## Komplexitätsverteilung\n\n")
        for label, count in complexity_counter.most_common():
            f.write(f"- {label}: {count}\n")

        f.write("\n## Größte visuelle Cluster (motivnahe Gruppen, mind. 3)\n\n")
        shown = 0
        for idxs in clusters:
            if len(idxs) < 3:
                continue
            fs = [features[i] for i in idxs]
            shown += 1
            motif_mix = Counter(x.motif_key for x in fs if x.motif_key)
            style_mix = Counter(x.style_label for x in fs)
            f.write(f"- Cluster {shown} ({len(fs)}): {cluster_label(fs)} · ")
            if motif_mix:
                f.write("Motive: " + ", ".join(f"{k}({v})" for k, v in motif_mix.most_common(4)) + " · ")
            f.write("Stile: " + ", ".join(f"{k}({v})" for k, v in style_mix.most_common(3)) + "\n")
            if shown >= 20:
                break

        if missing:
            f.write("\n## Nicht ausgewertet / Fehler\n\n")
            for m in missing[:80]:
                f.write(f"- {m}\n")

    # html overview
    html_out = out_dir / "analyse_uebersicht.html"
    ensure_local_assets(base, out_dir, features)
    build_html(html_out, features, clusters, motif_groups, related_pairs, generated)

    info = {
        "generated_at": generated,
        "entries_total": len(entries),
        "entries_analyzed": len(features),
        "missing_or_error": len(missing),
        "motif_families": len(motif_groups),
        "motif_families_ge2": sum(1 for idxs in motif_groups.values() if len(idxs) >= 2),
        "related_motif_pairs": len(related_pairs),
        "style_clusters_total": len(clusters),
        "style_clusters_ge3": sum(1 for c in clusters if len(c) >= 3),
        "cluster_max_dist": round(cluster_max_dist, 4),
    }
    (out_dir / "analysis_meta.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"Output directory: {out_dir}")


def main():
    repo_root = Path(__file__).resolve().parents[1]
    run(repo_root)


if __name__ == "__main__":
    main()

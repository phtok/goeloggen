#!/usr/bin/env python3
import argparse
import csv
import html
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def normalize_dashes(value: str) -> str:
    return value.replace("–", "-").replace("—", "-")


def extract_issue_label(value: str) -> str:
    normalized = normalize_dashes(value).replace("_", "-")
    m = re.search(r"(?<!\d)(\d{1,2})-(\d{1,2})(?!\d)", normalized)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r"(?<!\d)(\d{1,2})(?!\d)", normalized)
    if m:
        return m.group(1)
    return normalized


def short_year(year: str) -> str:
    return year[-2:] if len(year) >= 2 else year


def compact_issue(issue: str) -> str:
    return extract_issue_label(issue).replace(" ", "")


def issue_sort_key(issue: str) -> int:
    m = re.search(r"\d+", issue or "")
    return int(m.group(0)) if m else 9999


def occurrence_suffix(idx: int) -> str:
    if idx <= 0:
        return ""
    letters = "abcdefghijklmnopqrstuvwxyz"
    if idx - 1 < len(letters):
        return letters[idx - 1]
    return f"_{idx}"


def sanitize_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._:-]+", "_", value.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "entry"


def canonical_id(row: dict, fallback_index: int) -> str:
    svg = (row.get("svg") or "").strip()
    datei = (row.get("datei") or "").strip()
    page = (row.get("seite") or "").strip()
    hint = (row.get("hinweis") or "").strip().lower()

    if svg:
        stem = Path(svg).stem
    elif datei:
        stem = Path(datei).stem
    else:
        stem = f"entry_{fallback_index}"

    rid = sanitize_id(stem)
    if page and f"-p{page}" not in rid:
        rid = f"{rid}-p{sanitize_id(page)}"
    if "tok-scan" in hint and "tok" not in rid:
        rid = f"{rid}-tok"
    return sanitize_id(rid)


def read_rows(csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if "id" not in fieldnames:
        fieldnames.append("id")
    if "status" not in fieldnames:
        fieldnames.append("status")
        for row in rows:
            row["status"] = "keep"
    seen_ids = defaultdict(int)
    for i, row in enumerate(rows, 1):
        rid = (row.get("id") or "").strip()
        if (not rid) or re.fullmatch(r"row-\d+", rid):
            rid = canonical_id(row, i)
        rid = sanitize_id(rid)
        if seen_ids[rid] > 0:
            rid = f"{rid}-{seen_ids[rid] + 1}"
        seen_ids[rid] += 1
        row["id"] = rid
        row["status"] = (row.get("status") or "keep").strip().lower() or "keep"
    return fieldnames, rows


def write_rows(csv_path: Path, fieldnames, rows):
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def is_keep(row) -> bool:
    return (row.get("status") or "keep").strip().lower() not in {"drop", "delete", "excluded"}


def parse_ids_file(ids_file: Path):
    if not ids_file.exists():
        raise FileNotFoundError(ids_file)
    return {
        line.strip()
        for line in ids_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def keep_from_file(output_root: Path, ids_file: Path, drop_others: bool):
    ids = parse_ids_file(ids_file)
    if drop_others and not ids:
        raise ValueError("IDs file is empty; refusing to drop all entries.")

    changed = 0
    matched = set()
    year_dirs = sorted([p for p in output_root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name)])
    for yd in year_dirs:
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        fieldnames, rows = read_rows(csv_path)
        local_changed = 0
        for r in rows:
            rid = r.get("id", "")
            old = (r.get("status") or "keep").strip().lower() or "keep"
            new_status = old

            if rid in ids:
                new_status = "keep"
                matched.add(rid)
            elif drop_others:
                new_status = "drop"

            if new_status != old:
                r["status"] = new_status
                local_changed += 1

        if local_changed:
            changed += local_changed
            write_rows(csv_path, fieldnames, rows)

    missing = sorted(ids - matched)
    print(f"Updated rows: {changed} (drop_others={drop_others})")
    print(f"Keep IDs matched: {len(matched)}/{len(ids)}")
    if missing:
        print(f"Keep IDs not found: {len(missing)}")
        for mid in missing[:30]:
            print(f"  {mid}")
        if len(missing) > 30:
            print("  ...")

    apply_root(output_root, delete_dropped=False, purge_csv=False)


def parse_jh_label(label: str):
    m = re.fullmatch(r"(?i)J(\d{2})H(\d{1,2})[a-z_0-9-]*", label.strip())
    if not m:
        raise ValueError(f"Invalid JH label: {label} (expected like J14H47)")
    year = 2000 + int(m.group(1))
    issue = int(m.group(2))
    return year, issue


def drop_before_jh(output_root: Path, label: str):
    target_year, target_issue = parse_jh_label(label)
    changed = 0
    year_dirs = sorted([p for p in output_root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name)])

    for yd in year_dirs:
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        fieldnames, rows = read_rows(csv_path)
        local_changed = 0
        for r in rows:
            raw_year = (r.get("jahr") or yd.name).strip()
            try:
                y = int(raw_year)
            except ValueError:
                y = int(yd.name)
            issue = issue_sort_key(r.get("heft", ""))
            if (y < target_year) or (y == target_year and issue < target_issue):
                old = (r.get("status") or "keep").strip().lower() or "keep"
                if old != "drop":
                    r["status"] = "drop"
                    local_changed += 1
        if local_changed:
            changed += local_changed
            write_rows(csv_path, fieldnames, rows)

    print(f"Marked as drop before {label.upper()}: {changed}")
    apply_root(output_root, delete_dropped=False, purge_csv=False)


def render_year_index(year: str, rows_keep):
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = []
    for r in rows_keep:
        parts.append(
            "<tr>"
            f"<td>{html.escape(r.get('jahr',''))}</td>"
            f"<td>{html.escape(r.get('heft',''))}</td>"
            f"<td>{html.escape(r.get('erscheinung',''))}</td>"
            f"<td>{html.escape(r.get('seite',''))}</td>"
            f"<td>{html.escape(r.get('titel',''))}</td>"
            f"<td class=\"drawing-cell\"><img src=\"{html.escape(r.get('svg',''))}\" alt=\"{html.escape(r.get('datei',''))}\" loading=\"lazy\"></td>"
            f"<td><code>{html.escape(r.get('datei',''))}</code><br><small>{html.escape(r.get('hinweis',''))}<br>ID: {html.escape(r.get('id',''))}</small></td>"
            "</tr>"
        )
    rows_html = "".join(parts)
    return f"""<!doctype html>
<html lang=\"de\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Verzeichnis Zeichnungen (kuratiert, {html.escape(year)})</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 28px; color: #1f2937; }}
    h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
    p.meta {{ margin: 0 0 20px 0; color: #6b7280; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 12px; vertical-align: top; }}
    th {{ background: #f9fafb; text-align: left; }}
    td.drawing-cell {{ min-width: 280px; }}
    img {{ width: 220px; height: auto; display: block; background: #fff; border: 1px solid #e5e7eb; padding: 16px; }}
    code {{ font-size: 12px; }}
    small {{ color: #6b7280; }}
  </style>
</head>
<body>
  <h1>Verzeichnis Zeichnungen (kuratiert, {html.escape(year)})</h1>
  <p class=\"meta\">Erzeugt am {generated} · Treffer: {len(rows_keep)}</p>
  <table>
    <thead>
      <tr>
        <th>Jahr</th><th>Heft</th><th>Erscheinung</th><th>Seite</th><th>Titel</th><th>Zeichnung (SVG)</th><th>Quelle</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</body>
</html>
"""


def render_year_overview(year: str, rows_keep):
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    seen = defaultdict(int)
    cards = []
    for r in rows_keep:
        issue = compact_issue(r.get("heft", ""))
        key = f"{year}|{issue}"
        occ = seen[key]
        seen[key] += 1
        tiny = f"J{short_year(year)}H{issue}{occurrence_suffix(occ)}"
        cards.append(
            f"<article class=\"card\"><img src=\"{html.escape(r.get('svg',''))}\" alt=\"{html.escape(r.get('datei',''))}\" loading=\"lazy\"><div class=\"tiny\">{html.escape(tiny)}</div></article>"
        )
    cards_html = "".join(cards)
    return f"""<!doctype html>
<html lang=\"de\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Jahresübersicht {html.escape(year)} (kuratiert)</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 28px; color: #1f2937; }}
    h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
    p.meta {{ margin: 0 0 22px 0; color: #6b7280; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 18px; }}
    .card {{ border: 1px solid #e5e7eb; background: #fff; padding: 12px 12px 10px; }}
    .card img {{ width: 100%; height: 140px; object-fit: contain; display: block; background: #fff; }}
    .tiny {{ margin-top: 8px; font-size: 11px; color: #6b7280; letter-spacing: 0.02em; }}
  </style>
</head>
<body>
  <h1>Jahresübersicht {html.escape(year)} (kuratiert)</h1>
  <p class=\"meta\">Erzeugt am {generated} · Zeichnungen: {len(rows_keep)}</p>
  <section class=\"grid\">{cards_html}</section>
</body>
</html>
"""


def rebuild_year(year_dir: Path):
    csv_path = year_dir / "verzeichnis.csv"
    fieldnames, rows = read_rows(csv_path)
    write_rows(csv_path, fieldnames, rows)
    rows_keep = [r for r in rows if is_keep(r)]
    year = year_dir.name

    (year_dir / "index_curated.html").write_text(render_year_index(year, rows_keep), encoding="utf-8")
    (year_dir / f"jahr_{year}_uebersicht_curated.html").write_text(render_year_overview(year, rows_keep), encoding="utf-8")


def list_entries(year_dir: Path, show_all: bool):
    _, rows = read_rows(year_dir / "verzeichnis.csv")
    for r in rows:
        if not show_all and not is_keep(r):
            continue
        print(
            f"{r.get('id','')}\t{r.get('status','keep')}\tJ{r.get('jahr','')} H{r.get('heft','')} S{r.get('seite','')}\t{r.get('datei','')}\t{r.get('svg','')}"
        )


def set_status(year_dir: Path, ids, status: str):
    csv_path = year_dir / "verzeichnis.csv"
    fieldnames, rows = read_rows(csv_path)
    target = set(ids)
    changed = 0
    for r in rows:
        if r.get("id") in target:
            r["status"] = status
            changed += 1
    write_rows(csv_path, fieldnames, rows)
    rebuild_year(year_dir)
    print(f"Updated {changed} entries to status={status}")


def delete_dropped_files(year_dir: Path, purge_csv: bool):
    csv_path = year_dir / "verzeichnis.csv"
    fieldnames, rows = read_rows(csv_path)
    keep_rows = []
    removed = 0
    for r in rows:
        if is_keep(r):
            keep_rows.append(r)
            continue
        svg_rel = r.get("svg", "")
        if svg_rel:
            target = year_dir / svg_rel
            if target.exists() and target.is_file():
                target.unlink()
                removed += 1
        if not purge_csv:
            keep_rows.append(r)

    if purge_csv:
        write_rows(csv_path, fieldnames, keep_rows)
    rebuild_year(year_dir)
    print(f"Deleted {removed} SVG files (purge_csv={purge_csv})")


def apply_root(output_root: Path, delete_dropped: bool, purge_csv: bool):
    year_dirs = sorted([p for p in output_root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name)])
    for yd in year_dirs:
        if (yd / "verzeichnis.csv").exists():
            if delete_dropped:
                delete_dropped_files(yd, purge_csv=purge_csv)
            else:
                rebuild_year(yd)

    total_script = Path("/Users/philipptok/goeloggen/scripts/generate_total_uebersicht.swift")
    env = os.environ.copy()
    env.setdefault("SWIFT_MODULECACHE_PATH", "/tmp/swift-module-cache")
    env.setdefault("CLANG_MODULE_CACHE_PATH", "/tmp/clang-module-cache")
    Path(env["SWIFT_MODULECACHE_PATH"]).mkdir(parents=True, exist_ok=True)
    Path(env["CLANG_MODULE_CACHE_PATH"]).mkdir(parents=True, exist_ok=True)
    subprocess.run(["swift", str(total_script), str(output_root)], check=True, env=env)


def drop_from_file(output_root: Path, ids_file: Path):
    ids = parse_ids_file(ids_file)
    if not ids:
        print("No IDs found in file.")
        return

    changed = 0
    matched = set()
    year_dirs = sorted([p for p in output_root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}", p.name)])
    for yd in year_dirs:
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        fieldnames, rows = read_rows(csv_path)
        local_changed = 0
        for r in rows:
            rid = r.get("id", "")
            if rid in ids:
                r["status"] = "drop"
                matched.add(rid)
                local_changed += 1
        if local_changed:
            changed += local_changed
            write_rows(csv_path, fieldnames, rows)

    missing = sorted(ids - matched)
    print(f"Marked as drop: {changed}")
    if missing:
        print(f"IDs not found: {len(missing)}")
        for mid in missing[:30]:
            print(f"  {mid}")
        if len(missing) > 30:
            print("  ...")

    apply_root(output_root, delete_dropped=False, purge_csv=False)


def main():
    parser = argparse.ArgumentParser(description="Curation helper for extracted SVG entries")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("year_dir")
    p_list.add_argument("--all", action="store_true")

    p_drop = sub.add_parser("drop")
    p_drop.add_argument("year_dir")
    p_drop.add_argument("ids", nargs="+")

    p_keep = sub.add_parser("keep")
    p_keep.add_argument("year_dir")
    p_keep.add_argument("ids", nargs="+")

    p_delete = sub.add_parser("delete-dropped")
    p_delete.add_argument("year_dir")
    p_delete.add_argument("--purge-csv", action="store_true")

    p_rebuild = sub.add_parser("rebuild")
    p_rebuild.add_argument("year_dir")

    p_apply = sub.add_parser("apply-root")
    p_apply.add_argument("output_root")
    p_apply.add_argument("--delete-dropped", action="store_true")
    p_apply.add_argument("--purge-csv", action="store_true")

    p_bulk = sub.add_parser("drop-from-file")
    p_bulk.add_argument("output_root")
    p_bulk.add_argument("ids_file")

    p_keep_file = sub.add_parser("keep-from-file")
    p_keep_file.add_argument("output_root")
    p_keep_file.add_argument("ids_file")
    p_keep_file.add_argument("--drop-others", action="store_true")

    p_keep_only = sub.add_parser("keep-only-from-file")
    p_keep_only.add_argument("output_root")
    p_keep_only.add_argument("ids_file")

    p_drop_before = sub.add_parser("drop-before-jh")
    p_drop_before.add_argument("output_root")
    p_drop_before.add_argument("label")

    args = parser.parse_args()

    if args.cmd == "list":
        list_entries(Path(args.year_dir), show_all=args.all)
    elif args.cmd == "drop":
        set_status(Path(args.year_dir), args.ids, status="drop")
    elif args.cmd == "keep":
        set_status(Path(args.year_dir), args.ids, status="keep")
    elif args.cmd == "delete-dropped":
        delete_dropped_files(Path(args.year_dir), purge_csv=args.purge_csv)
    elif args.cmd == "rebuild":
        rebuild_year(Path(args.year_dir))
    elif args.cmd == "apply-root":
        apply_root(Path(args.output_root), delete_dropped=args.delete_dropped, purge_csv=args.purge_csv)
    elif args.cmd == "drop-from-file":
        drop_from_file(Path(args.output_root), Path(args.ids_file))
    elif args.cmd == "keep-from-file":
        keep_from_file(Path(args.output_root), Path(args.ids_file), drop_others=args.drop_others)
    elif args.cmd == "keep-only-from-file":
        keep_from_file(Path(args.output_root), Path(args.ids_file), drop_others=True)
    elif args.cmd == "drop-before-jh":
        drop_before_jh(Path(args.output_root), args.label)


if __name__ == "__main__":
    main()

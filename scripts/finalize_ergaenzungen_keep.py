#!/usr/bin/env python3
import argparse
import csv
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

DROP_STATES = {"drop", "delete", "excluded"}
YEAR_RE = re.compile(r"^\d{4}$")


def is_keep(row: dict) -> bool:
    return (row.get("status") or "keep").strip().lower() not in DROP_STATES


def note_kind(row: dict) -> str:
    note = (row.get("hinweis") or "").split(";", 1)[0]
    if note.startswith("anchor:") or note.startswith("fallback:"):
        return "main"
    if note.startswith("all-pages-scan"):
        return "all"
    if note.startswith("tok-scan"):
        return "tok"
    if note.startswith("page3-right-top"):
        return "rt"
    return note or "other"


def row_key(row: dict, fallback_year: str) -> tuple:
    return (
        (row.get("jahr") or fallback_year).strip(),
        (row.get("heft") or "").strip(),
        (row.get("seite") or "").strip(),
        (row.get("datei") or "").strip(),
    )


def read_csv(csv_path: Path):
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []
    if "id" not in fieldnames:
        fieldnames.append("id")
        for i, r in enumerate(rows, 1):
            r["id"] = r.get("id") or f"row-{i}"
    if "status" not in fieldnames:
        fieldnames.append("status")
        for r in rows:
            r["status"] = "keep"
    return fieldnames, rows


def write_csv(csv_path: Path, fieldnames, rows):
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def all_year_dirs(root: Path):
    return [p for p in sorted(root.iterdir()) if p.is_dir() and YEAR_RE.fullmatch(p.name)]


def load_keep_ids(path: Path):
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def run_curate_apply(curate_script: Path, root: Path, delete_dropped: bool):
    cmd = ["python3", str(curate_script), "apply-root", str(root)]
    if delete_dropped:
        cmd.append("--delete-dropped")
    subprocess.run(cmd, check=True)


def apply_keep_only(add_root: Path, keep_ids: set):
    matched = 0
    changed = 0
    total = 0
    for yd in all_year_dirs(add_root):
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        fieldnames, rows = read_csv(csv_path)
        for r in rows:
            total += 1
            old = (r.get("status") or "keep").strip().lower() or "keep"
            rid = (r.get("id") or "").strip()
            new = "keep" if rid in keep_ids else "drop"
            if rid in keep_ids:
                matched += 1
            if new != old:
                r["status"] = new
                changed += 1
        write_csv(csv_path, fieldnames, rows)
    return {"matched": matched, "changed": changed, "total": total}


def build_main_keep_keys(main_root: Path):
    keys = set()
    for yd in all_year_dirs(main_root):
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        _, rows = read_csv(csv_path)
        for r in rows:
            if is_keep(r):
                keys.add(row_key(r, yd.name))
    return keys


def dedupe_page4_all_in_root(root: Path, external_main_keep_keys=None):
    if external_main_keep_keys is None:
        external_main_keep_keys = set()
    changed = 0
    dropped_dupes = 0
    promoted_main = 0
    collapsed_multi = 0

    for yd in all_year_dirs(root):
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        fieldnames, rows = read_csv(csv_path)

        by_key = defaultdict(list)
        for idx, r in enumerate(rows):
            if not is_keep(r):
                continue
            if note_kind(r) != "all":
                continue
            if (r.get("seite") or "").strip() != "4":
                continue
            by_key[row_key(r, yd.name)].append(idx)

        for key, idxs in by_key.items():
            # main candidate in additions for the same issue/page/file
            main_idxs = [
                i for i, r in enumerate(rows)
                if row_key(r, yd.name) == key and note_kind(r) == "main"
            ]
            in_external_main = key in external_main_keep_keys

            if in_external_main or main_idxs:
                for i in idxs:
                    if is_keep(rows[i]):
                        rows[i]["status"] = "drop"
                        changed += 1
                        dropped_dupes += 1
                if (not in_external_main) and main_idxs:
                    # Keep one main row if no equivalent in external main root.
                    main_i = main_idxs[0]
                    if not is_keep(rows[main_i]):
                        rows[main_i]["status"] = "keep"
                        changed += 1
                        promoted_main += 1
            else:
                # No main anywhere: keep only one all-page candidate.
                sorted_idxs = sorted(idxs, key=lambda i: (rows[i].get("id") or ""))
                for i in sorted_idxs[1:]:
                    if is_keep(rows[i]):
                        rows[i]["status"] = "drop"
                        changed += 1
                        collapsed_multi += 1

        write_csv(csv_path, fieldnames, rows)

    return {
        "changed": changed,
        "dropped_dupes": dropped_dupes,
        "promoted_main": promoted_main,
        "collapsed_multi": collapsed_multi,
    }


def ensure_unique_id(existing_ids: set, candidate: str) -> str:
    base = candidate or "entry"
    if base not in existing_ids:
        existing_ids.add(base)
        return base
    i = 2
    while True:
        c = f"{base}-{i}"
        if c not in existing_ids:
            existing_ids.add(c)
            return c
        i += 1


def ensure_unique_svg(images_dir: Path, rel_svg: str) -> str:
    path = Path(rel_svg)
    stem = path.stem
    ext = path.suffix or ".svg"
    candidate = images_dir / path.name
    if not candidate.exists():
        return f"images/{path.name}"
    i = 2
    while True:
        name = f"{stem}_add{i}{ext}"
        candidate = images_dir / name
        if not candidate.exists():
            return f"images/{name}"
        i += 1


def merge_additions_into_main(main_root: Path, add_root: Path):
    imported = 0
    skipped_existing = 0
    skipped_missing_file = 0

    # Preload main rows by year.
    main_data = {}
    for yd in all_year_dirs(main_root):
        csv_path = yd / "verzeichnis.csv"
        if csv_path.exists():
            fieldnames, rows = read_csv(csv_path)
        else:
            fieldnames, rows = (
                ["jahr", "heft", "erscheinung", "seite", "titel", "datei", "svg", "hinweis", "id", "status"],
                [],
            )
        main_data[yd.name] = {
            "dir": yd,
            "csv": csv_path,
            "fieldnames": fieldnames,
            "rows": rows,
        }

    # Ensure years existing in additions also exist in main_data.
    for yd in all_year_dirs(add_root):
        if yd.name not in main_data:
            target_year_dir = main_root / yd.name
            target_year_dir.mkdir(parents=True, exist_ok=True)
            main_data[yd.name] = {
                "dir": target_year_dir,
                "csv": target_year_dir / "verzeichnis.csv",
                "fieldnames": ["jahr", "heft", "erscheinung", "seite", "titel", "datei", "svg", "hinweis", "id", "status"],
                "rows": [],
            }

    # Build key index for existing main rows.
    main_key_index = defaultdict(list)
    main_id_set = defaultdict(set)
    for year, data in main_data.items():
        for idx, r in enumerate(data["rows"]):
            main_key_index[(year, row_key(r, year))].append(idx)
            main_id_set[year].add((r.get("id") or "").strip())

    for add_year_dir in all_year_dirs(add_root):
        year = add_year_dir.name
        add_csv = add_year_dir / "verzeichnis.csv"
        if not add_csv.exists():
            continue
        _, add_rows = read_csv(add_csv)

        target = main_data[year]
        target_images = target["dir"] / "images"
        target_images.mkdir(parents=True, exist_ok=True)

        for r in add_rows:
            if not is_keep(r):
                continue
            key = row_key(r, year)
            existing_idxs = main_key_index[(year, key)]
            if existing_idxs:
                if any(is_keep(target["rows"][i]) for i in existing_idxs):
                    skipped_existing += 1
                    continue
                # revive first existing row
                i = existing_idxs[0]
                target["rows"][i]["status"] = "keep"
                skipped_existing += 1
                continue

            src_svg_rel = (r.get("svg") or "").strip()
            src_svg_path = add_year_dir / src_svg_rel
            if not src_svg_rel or not src_svg_path.exists():
                skipped_missing_file += 1
                continue

            dst_svg_rel = ensure_unique_svg(target_images, src_svg_rel)
            dst_svg_path = target["dir"] / dst_svg_rel
            dst_svg_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_svg_path, dst_svg_path)

            new_row = dict(r)
            new_row["jahr"] = year
            new_row["svg"] = dst_svg_rel
            new_row["status"] = "keep"
            new_row["id"] = ensure_unique_id(main_id_set[year], (r.get("id") or "").strip())

            for fn in target["fieldnames"]:
                new_row.setdefault(fn, "")
            target["rows"].append(new_row)
            main_key_index[(year, key)].append(len(target["rows"]) - 1)
            imported += 1

    for year, data in main_data.items():
        write_csv(data["csv"], data["fieldnames"], data["rows"])

    return {
        "imported": imported,
        "skipped_existing": skipped_existing,
        "skipped_missing_file": skipped_missing_file,
    }


def drop_rows_present_in_main(add_root: Path, main_keep_keys: set):
    changed = 0
    for yd in all_year_dirs(add_root):
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        fieldnames, rows = read_csv(csv_path)
        local = 0
        for r in rows:
            if not is_keep(r):
                continue
            key = row_key(r, yd.name)
            if key in main_keep_keys:
                r["status"] = "drop"
                local += 1
        if local:
            changed += local
            write_csv(csv_path, fieldnames, rows)
    return {"changed": changed}


def main():
    ap = argparse.ArgumentParser(description="Finalize additions keep-list into main collection with page-4 dedupe and cleanup")
    ap.add_argument("main_root")
    ap.add_argument("add_root")
    ap.add_argument("keep_ids_file")
    ap.add_argument("--curate-script", default="/Users/philipptok/goeloggen/scripts/curate_entries.py")
    ap.add_argument("--cleanup-main", action="store_true")
    ap.add_argument("--cleanup-add", action="store_true")
    args = ap.parse_args()

    main_root = Path(args.main_root)
    add_root = Path(args.add_root)
    keep_ids_file = Path(args.keep_ids_file)
    curate_script = Path(args.curate_script)
    keep_ids = load_keep_ids(keep_ids_file)

    print(f"Keep IDs: {len(keep_ids)}")

    keep_res = apply_keep_only(add_root, keep_ids)
    print(f"Applied keep-only on additions: matched={keep_res['matched']}/{len(keep_ids)} changed={keep_res['changed']} total_rows={keep_res['total']}")

    main_keep_keys = build_main_keep_keys(main_root)
    dedupe_res = dedupe_page4_all_in_root(add_root, external_main_keep_keys=main_keep_keys)
    print(
        "Page4 dedupe in additions: "
        f"changed={dedupe_res['changed']} dropped_dupes={dedupe_res['dropped_dupes']} "
        f"promoted_main={dedupe_res['promoted_main']} collapsed_multi={dedupe_res['collapsed_multi']}"
    )

    # Rebuild additions before merge so IDs/status are normalized in HTML/CSV.
    run_curate_apply(curate_script, add_root, delete_dropped=False)

    merge_res = merge_additions_into_main(main_root, add_root)
    print(
        "Merged into main: "
        f"imported={merge_res['imported']} skipped_existing={merge_res['skipped_existing']} "
        f"skipped_missing_file={merge_res['skipped_missing_file']}"
    )

    dedupe_main_res = dedupe_page4_all_in_root(main_root)
    print(
        "Page4 dedupe in main: "
        f"changed={dedupe_main_res['changed']} dropped_dupes={dedupe_main_res['dropped_dupes']} "
        f"promoted_main={dedupe_main_res['promoted_main']} collapsed_multi={dedupe_main_res['collapsed_multi']}"
    )

    post_main_keep_keys = build_main_keep_keys(main_root)
    post_drop_res = drop_rows_present_in_main(add_root, post_main_keep_keys)
    print(f"Post-merge additions->main sync drops: changed={post_drop_res['changed']}")

    # Refresh roots and optionally cleanup dropped SVGs.
    run_curate_apply(curate_script, main_root, delete_dropped=args.cleanup_main)
    run_curate_apply(curate_script, add_root, delete_dropped=args.cleanup_add)

    print("Done.")


if __name__ == "__main__":
    main()

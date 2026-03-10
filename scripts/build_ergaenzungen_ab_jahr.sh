#!/usr/bin/env bash
set -euo pipefail

MIN_YEAR="${1:-2018}"
INPUT_ROOT="${2:-/Users/philipptok/goeloggen/hefte_pdf}"
BASE_ROOT="${3:-/Users/philipptok/goeloggen/ausgabe_zeichnungen/alle_jahrgaenge}"
OUT_ROOT="${4:-/Users/philipptok/goeloggen/ausgabe_zeichnungen/ergaenzungen_ab${MIN_YEAR}}"
EXTRACTOR="${5:-/Users/philipptok/goeloggen/scripts/extract_wochenschrift_zeichnungen.swift}"
TOTAL_SCRIPT="${6:-/Users/philipptok/goeloggen/scripts/generate_total_uebersicht.swift}"
CURATE_SCRIPT="${7:-/Users/philipptok/goeloggen/scripts/curate_entries.py}"
VORSORT_SCRIPT="${8:-/Users/philipptok/goeloggen/scripts/generate_vorsortierung.py}"

if ! [[ "$MIN_YEAR" =~ ^[0-9]{4}$ ]]; then
  echo "MIN_YEAR must be a 4-digit year, got: $MIN_YEAR"
  exit 1
fi

export SWIFT_MODULECACHE_PATH="${SWIFT_MODULECACHE_PATH:-/tmp/swift-module-cache}"
export CLANG_MODULE_CACHE_PATH="${CLANG_MODULE_CACHE_PATH:-/tmp/clang-module-cache}"
mkdir -p "$SWIFT_MODULECACHE_PATH" "$CLANG_MODULE_CACHE_PATH"
mkdir -p "$OUT_ROOT"

echo "Input root:  $INPUT_ROOT"
echo "Base root:   $BASE_ROOT"
echo "Output root: $OUT_ROOT"
echo "Min year:    $MIN_YEAR"

declare -a YEAR_DIRS
while IFS= read -r line; do
  YEAR_DIRS+=("$line")
done < <(
  find "$INPUT_ROOT" -type f -name '*.pdf' -print0 \
    | xargs -0 -n1 dirname \
    | sort -u \
    | while IFS= read -r d; do
        b="$(basename "$d")"
        if [[ "$b" =~ ^[0-9]{4}$ ]] && [[ "$b" -ge "$MIN_YEAR" ]]; then
          echo "$d"
        fi
      done \
    | sort -V
)

if [[ ${#YEAR_DIRS[@]} -eq 0 ]]; then
  echo "No year directories >= $MIN_YEAR with PDFs found."
  exit 1
fi

echo "Year directories: ${#YEAR_DIRS[@]}"

for d in "${YEAR_DIRS[@]}"; do
  year="$(basename "$d")"
  out="$OUT_ROOT/$year"
  count="$(find "$d" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
  echo "==> Year $year ($count PDFs, aggressive scan)"
  EXTRA_TOK_SCAN=1 EXTRA_PAGE3_RIGHT_SCAN=1 EXTRA_ALL_PAGES_SCAN=1 swift "$EXTRACTOR" "$d" "$out"
done

echo "==> Build raw total overview"
swift "$TOTAL_SCRIPT" "$OUT_ROOT"

echo "==> Filter out already-checked IDs from base root"
python3 - <<'PY' "$MIN_YEAR" "$BASE_ROOT" "$OUT_ROOT"
import csv
import re
import sys
from pathlib import Path

min_year = int(sys.argv[1])
base_root = Path(sys.argv[2])
out_root = Path(sys.argv[3])

year_re = re.compile(r"^\d{4}$")

def note_kind(note: str) -> str:
    prefix = (note or "").split(";", 1)[0]
    if prefix.startswith("anchor:") or prefix.startswith("fallback:"):
        return "main"
    if prefix.startswith("tok-scan"):
        return "tok-scan"
    if prefix.startswith("page3-right-top"):
        return "page3-right-top"
    if prefix.startswith("all-pages-scan"):
        return "all-pages-scan"
    return prefix or "other"

base_ids = set()
base_keys = set()
for yd in sorted(base_root.iterdir()):
    if not yd.is_dir() or not year_re.fullmatch(yd.name):
        continue
    if int(yd.name) < min_year:
        continue
    csv_path = yd / "verzeichnis.csv"
    if not csv_path.exists():
        continue
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rid = (row.get("id") or "").strip()
            if rid:
                base_ids.add(rid)
            key = (
                (row.get("jahr") or yd.name).strip(),
                (row.get("datei") or "").strip(),
                (row.get("seite") or "").strip(),
                note_kind(row.get("hinweis") or ""),
            )
            base_keys.add(key)

updated = 0
kept_new = 0
dropped_known = 0
for yd in sorted(out_root.iterdir()):
    if not yd.is_dir() or not year_re.fullmatch(yd.name):
        continue
    if int(yd.name) < min_year:
        continue
    csv_path = yd / "verzeichnis.csv"
    if not csv_path.exists():
        continue

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    if rows and "status" not in fieldnames:
        fieldnames.append("status")
        for r in rows:
            r["status"] = "keep"

    local_updated = 0
    for r in rows:
        rid = (r.get("id") or "").strip()
        old = (r.get("status") or "keep").strip().lower() or "keep"
        key = (
            (r.get("jahr") or yd.name).strip(),
            (r.get("datei") or "").strip(),
            (r.get("seite") or "").strip(),
            note_kind(r.get("hinweis") or ""),
        )
        if (rid and rid in base_ids) or (key in base_keys):
            new = "drop"
            dropped_known += 1
        else:
            new = "keep"
            kept_new += 1
        if new != old:
            r["status"] = new
            local_updated += 1
    if local_updated:
        updated += local_updated
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

print(f"Base IDs loaded: {len(base_ids)}")
print(f"Base keys loaded: {len(base_keys)}")
print(f"Rows updated: {updated}")
print(f"Known (dropped): {dropped_known}")
print(f"New candidates (kept): {kept_new}")
PY

echo "==> Build curated additions overviews"
python3 "$CURATE_SCRIPT" apply-root "$OUT_ROOT"

echo "==> Build vorsortiert overview"
python3 "$VORSORT_SCRIPT" "$BASE_ROOT" "$OUT_ROOT"

echo "Done."
echo "Open: $OUT_ROOT/total_uebersicht.html"
echo "Open: $OUT_ROOT/total_vorsortiert.html"

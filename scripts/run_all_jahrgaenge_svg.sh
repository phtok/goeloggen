#!/usr/bin/env bash
set -euo pipefail

INPUT_ROOT="${1:-/Users/philipptok/goeloggen/hefte_pdf}"
OUTPUT_ROOT="${2:-/Users/philipptok/goeloggen/ausgabe_zeichnungen/alle_jahrgaenge}"
EXTRACTOR="${3:-/Users/philipptok/goeloggen/scripts/extract_wochenschrift_zeichnungen.swift}"
TOTAL_SCRIPT="${4:-/Users/philipptok/goeloggen/scripts/generate_total_uebersicht.swift}"

export SWIFT_MODULECACHE_PATH="${SWIFT_MODULECACHE_PATH:-/tmp/swift-module-cache}"
export CLANG_MODULE_CACHE_PATH="${CLANG_MODULE_CACHE_PATH:-/tmp/clang-module-cache}"
mkdir -p "$SWIFT_MODULECACHE_PATH" "$CLANG_MODULE_CACHE_PATH"
mkdir -p "$OUTPUT_ROOT"

echo "Input root:  $INPUT_ROOT"
echo "Output root: $OUTPUT_ROOT"

declare -a YEAR_DIRS
while IFS= read -r line; do
  YEAR_DIRS+=("$line")
done < <(
  find "$INPUT_ROOT" -type f -name '*.pdf' -print0 \
    | xargs -0 -n1 dirname \
    | sort -u \
    | while IFS= read -r d; do
        b="$(basename "$d")"
        if [[ "$b" =~ ^[0-9]{4}$ ]]; then
          echo "$d"
        fi
      done \
    | sort -V
)

if [[ ${#YEAR_DIRS[@]} -eq 0 ]]; then
  echo "No year directories with PDFs found."
  exit 1
fi

echo "Year directories: ${#YEAR_DIRS[@]}"

for d in "${YEAR_DIRS[@]}"; do
  year="$(basename "$d")"
  out="$OUTPUT_ROOT/$year"
  count="$(find "$d" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
  extra_tok=0
  extra_p3_right=0
  extra_all_pages=0
  if [[ "$year" =~ ^20(12|13|14|15|16|17|18)$ ]]; then
    extra_tok=1
    extra_p3_right=1
    extra_all_pages=1
  fi
  echo "==> Year $year ($count PDFs, EXTRA_TOK_SCAN=$extra_tok, EXTRA_PAGE3_RIGHT_SCAN=$extra_p3_right, EXTRA_ALL_PAGES_SCAN=$extra_all_pages)"
  EXTRA_TOK_SCAN="$extra_tok" EXTRA_PAGE3_RIGHT_SCAN="$extra_p3_right" EXTRA_ALL_PAGES_SCAN="$extra_all_pages" swift "$EXTRACTOR" "$d" "$out"
done

echo "==> Building total overview"
swift "$TOTAL_SCRIPT" "$OUTPUT_ROOT"

echo "Done."

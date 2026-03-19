#!/usr/bin/env bash
set -euo pipefail

YEAR="${1:-}"
INPUT_ROOT="${2:-/Users/philipptok/goeloggen/hefte_pdf}"
OUTPUT_ROOT="${3:-/Users/philipptok/goeloggen/ausgabe_zeichnungen/alle_jahrgaenge}"
EXTRACTOR="${4:-/Users/philipptok/goeloggen/scripts/extract_wochenschrift_zeichnungen.swift}"
TOTAL_SCRIPT="${5:-/Users/philipptok/goeloggen/scripts/generate_total_uebersicht.swift}"

if [[ -z "$YEAR" ]]; then
  echo "Usage: $(basename "$0") <year> [input_root] [output_root] [extractor] [total_script]"
  exit 1
fi

YEAR_DIR="$INPUT_ROOT/$YEAR"
if [[ ! -d "$YEAR_DIR" ]]; then
  echo "Year directory not found: $YEAR_DIR"
  exit 1
fi

PDF_COUNT="$(find "$YEAR_DIR" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
if [[ "$PDF_COUNT" == "0" ]]; then
  echo "No PDFs found in: $YEAR_DIR"
  exit 1
fi

export SWIFT_MODULECACHE_PATH="${SWIFT_MODULECACHE_PATH:-/tmp/swift-module-cache}"
export CLANG_MODULE_CACHE_PATH="${CLANG_MODULE_CACHE_PATH:-/tmp/clang-module-cache}"
mkdir -p "$SWIFT_MODULECACHE_PATH" "$CLANG_MODULE_CACHE_PATH" "$OUTPUT_ROOT"

EXTRA_TOK=0
EXTRA_P3_RIGHT=0
EXTRA_ALL_PAGES=0
if [[ "$YEAR" =~ ^20(12|13|14|15|16|17|18)$ ]]; then
  EXTRA_TOK=1
  EXTRA_P3_RIGHT=1
  EXTRA_ALL_PAGES=1
fi

echo "==> Extract year $YEAR ($PDF_COUNT PDFs, EXTRA_TOK_SCAN=$EXTRA_TOK, EXTRA_PAGE3_RIGHT_SCAN=$EXTRA_P3_RIGHT, EXTRA_ALL_PAGES_SCAN=$EXTRA_ALL_PAGES)"
EXTRA_TOK_SCAN="$EXTRA_TOK" EXTRA_PAGE3_RIGHT_SCAN="$EXTRA_P3_RIGHT" EXTRA_ALL_PAGES_SCAN="$EXTRA_ALL_PAGES" swift "$EXTRACTOR" "$YEAR_DIR" "$OUTPUT_ROOT/$YEAR"

echo "==> Refresh total overview"
swift "$TOTAL_SCRIPT" "$OUTPUT_ROOT"

echo "Done."

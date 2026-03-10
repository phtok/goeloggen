#!/usr/bin/env bash
set -euo pipefail

INPUT_ROOT="${1:-/Users/philipptok/goeloggen/hefte_pdf}"
OUTPUT_DIR="${2:-/Users/philipptok/goeloggen/ausgabe_zeichnungen/tok_recherche}"
SWIFT_SCRIPT="${3:-/Users/philipptok/goeloggen/scripts/find_tok_texts.swift}"
FILTER_SCRIPT="${4:-/Users/philipptok/goeloggen/scripts/filter_tok_autorentexte.py}"

export SWIFT_MODULECACHE_PATH="${SWIFT_MODULECACHE_PATH:-/tmp/swift-module-cache}"
export CLANG_MODULE_CACHE_PATH="${CLANG_MODULE_CACHE_PATH:-/tmp/clang-module-cache}"
mkdir -p "$SWIFT_MODULECACHE_PATH" "$CLANG_MODULE_CACHE_PATH" "$OUTPUT_DIR"

echo "Input root:  $INPUT_ROOT"
echo "Output dir:  $OUTPUT_DIR"

swift "$SWIFT_SCRIPT" "$INPUT_ROOT" "$OUTPUT_DIR"

python3 "$FILTER_SCRIPT" \
  "$OUTPUT_DIR/tok_autorentexte.csv" \
  "$OUTPUT_DIR/tok_autorentexte_gefiltert.csv" \
  "$OUTPUT_DIR/tok_autorentexte_onepager_gefiltert.html"

echo "Done."
echo "Author onepager (raw):      $OUTPUT_DIR/tok_autorentexte_onepager.html"
echo "Author onepager (filtered): $OUTPUT_DIR/tok_autorentexte_onepager_gefiltert.html"
echo "Mentions onepager:          $OUTPUT_DIR/tok_erwaehnungen_onepager.html"

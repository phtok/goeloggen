#!/usr/bin/env python3
"""Erzeugt sprechende Abschnitts-Pfade als Weiterleitungs-Stubs.

Liest sektionen.json { "<sauberer-pfad>": "<zielseite>" } und schreibt je
<out>/<sauberer-pfad>/index.html, das RELATIV auf ../<zielseite> weiterleitet –
so funktioniert dieselbe Datei unter / (Custom-Domain) wie unter /goeloggen/
(github.io). Schlüssel mit $ (Kommentare) werden übersprungen.

Aufruf:  python3 tools/build_sections.py [ZIELORDNER]   (Default: _site)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_site")
MAP = json.load(open(os.path.join(ROOT, "sektionen.json"), encoding="utf-8"))

TEMPLATE = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Weiterleitung … {label}</title>
  <link rel="canonical" href="../{target}" />
  <meta http-equiv="refresh" content="0; url=../{target}" />
  <script>location.replace("../{target}" + location.search + location.hash)</script>
  <style>
    body {{ margin:0; min-height:100vh; display:grid; place-items:center;
      background:#36424f; color:#dbe0e4;
      font:400 16px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    a {{ color:#ebb565; }}
  </style>
</head>
<body>
  <p>Weiter zu {label} … <a href="../{target}">hier klicken</a>.</p>
</body>
</html>
"""

def main():
    n = 0
    for clean, target in MAP.items():
        if clean.startswith("$"):
            continue
        d = os.path.join(OUT, clean)
        os.makedirs(d, exist_ok=True)
        label = clean.replace("-", " ")
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(label=label, target=target))
        n += 1
    print(f"build_sections: {n} Abschnitts-Pfade nach {OUT} geschrieben.")

if __name__ == "__main__":
    main()

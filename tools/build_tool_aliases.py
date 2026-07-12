#!/usr/bin/env python3
"""Kurz-URLs je Werkzeug: legt im Publish-Ordner /<slug>/ als Weiterleitung
auf das Werkzeug unter apps/… an (aus tools.json, nur live/beta).

  werkzeuge.goetheanum.ch/signatur  ->  /apps/signatur-generator/

Relative Ziele (../…), damit die Aliasse auf der Custom-Domain (Root) UND
unter phtok.github.io/goeloggen/ funktionieren. Bestehende Dateien/Ordner
werden nie überschrieben (Kollisionen, z. B. logo-generator.html, gewinnen).
Aufruf: python3 tools/build_tool_aliases.py _site
"""
import json, sys, pathlib

STUB = """<!doctype html><html lang="de-CH"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={t}">
<script>location.replace("{t}"+location.search+location.hash)</script>
<title>Weiterleitung</title></head>
<body><p>Weiterleitung … <a href="{t}">hier klicken</a>.</p></body></html>
"""

def main(site: str) -> None:
    root = pathlib.Path(site)
    data = json.load(open("tools.json", encoding="utf-8"))
    tools = data["tools"] if isinstance(data, dict) else data
    for t in tools:
        slug, href, status = t.get("slug", ""), t.get("href", ""), t.get("status", "")
        if not slug or not href.startswith("apps/") or status not in ("live", "beta"):
            continue
        if (root / slug).exists() or (root / f"{slug}.html").exists():
            print(f"alias übersprungen (Kollision): /{slug}")
            continue
        # Kein Schrägstrich anhängen, wenn der Pfad eine Query/Anker trägt
        # (z. B. apps/qr-generator/?modus=kurzlink) – sonst bräche das Ziel.
        hrefn = href if (href.endswith("/") or "?" in href or "#" in href) else href + "/"
        target = "../" + hrefn
        d = root / slug
        d.mkdir(parents=True)
        (d / "index.html").write_text(STUB.format(t=target), encoding="utf-8")
        print(f"alias: /{slug}/ -> {href}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "_site")

#!/usr/bin/env python3
"""Kurz-URLs je Werkzeug: legt im Publish-Ordner /<slug>/ als Weiterleitung
auf das Werkzeug unter apps/… an (aus tools.json, nur live/beta).

  werkzeuge.goetheanum.ch/signatur  ->  /apps/signatur-generator/

Relative Ziele (../…), damit die Aliasse auf der Custom-Domain (Root) UND
unter phtok.github.io/goeloggen/ funktionieren. Ein bestehender ORDNER
/<slug>/ gewinnt und wird nie überschrieben (z. B. die Abschnitts-Pfade aus
sektionen.json). Eine gleichnamige Datei /<slug>.html ist dagegen KEINE
Kollision: sie liegt auf einem anderen Pfad und ist selbst nur eine
Weiterleitung auf dasselbe Ziel — beides darf nebeneinander stehen.

Der Alias ist ein Versprechen, kein Schmuck: die Teilen-Schaltfläche in
design-system/nav.js kopiert genau diese kurze Adresse. Darum prüft der Lauf
am Ende, dass jedes live/beta-Werkzeug unter apps/ seine /<slug>/ auch
wirklich hat, und bricht den Deploy sonst ab (statt einen toten Link
auszuliefern).

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
    erwartet = []
    for t in tools:
        slug, href, status = t.get("slug", ""), t.get("href", ""), t.get("status", "")
        if not slug or not href.startswith("apps/") or status not in ("live", "beta"):
            continue
        erwartet.append(slug)
        if (root / slug).is_dir():
            print(f"alias übersprungen (Ordner besteht schon): /{slug}/")
            continue
        # Kein Schrägstrich anhängen, wenn der Pfad eine Query/Anker trägt
        # (z. B. apps/qr-generator/?modus=kurzlink) – sonst bräche das Ziel.
        hrefn = href if (href.endswith("/") or "?" in href or "#" in href) else href + "/"
        target = "../" + hrefn
        d = root / slug
        d.mkdir(parents=True)
        (d / "index.html").write_text(STUB.format(t=target), encoding="utf-8")
        print(f"alias: /{slug}/ -> {href}")

    # Prüfung: jede kurze Adresse, die die Teilen-Schaltfläche kopieren kann,
    # muss auch ausgeliefert werden. Fehlt eine, ist der Deploy kaputt.
    fehlend = [s for s in erwartet if not (root / s / "index.html").is_file()]
    if fehlend:
        for s in fehlend:
            print(f"FEHLER: /{s}/ fehlt – die Teilen-Adresse wäre tot.", file=sys.stderr)
        sys.exit(1)
    print(f"alias-prüfung: {len(erwartet)} kurze Adressen vorhanden.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "_site")

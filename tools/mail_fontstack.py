#!/usr/bin/env python3
"""Font-Stapel der Mail-Editor-Mails härten (idempotent).

Die Mails sind MJML-Ausgabe; die MJML-Quelle liegt nicht im Repo. Die Wahrheit
sind darum die 24 Dateien in apps/mail-editor/mails/ und ihre 24 eingebetteten
Kopien (iframe srcdoc) in apps/mail-editor/index.html. Dieses Skript zieht
beide gleich:

1. @font-face: WOFF (Goetheanum) bzw. TTF (Source Sans 3 Regular) als zweite
   Quelle hinter WOFF2 – für Clients ohne WOFF2.
2. Outlook Windows: Conditional Comment im <head>, der alle Textrollen auf
   Arial setzt. Ohne ihn fällt Outlook bei unbekanntem Erst-Font auf
   Times New Roman.
3. color-scheme ‹light only›: Apple Mail und Outlook Mac zeigen die geprüfte
   helle Fassung statt einer automatischen Umfärbung.

Aufruf: python3 tools/mail_fontstack.py [--check]
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "apps/mail-editor"
BASE = "https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum"
MARKER = "<!-- fontstack:v1 -->"

ERSATZ = [
    (f"src: url('{BASE}/Webfonts/woff2/Goetheanum-Schrift-v2.9-Deutlich.woff2') format('woff2');",
     f"src: url('{BASE}/Webfonts/woff2/Goetheanum-Schrift-v2.9-Deutlich.woff2') format('woff2'), "
     f"url('{BASE}/Webfonts/woff/Goetheanum-Schrift-v2.9-Deutlich.woff') format('woff');"),
    (f"src: url('{BASE}/Fallback/SourceSans3-Regular.woff2') format('woff2');",
     f"src: url('{BASE}/Fallback/SourceSans3-Regular.woff2') format('woff2'), "
     f"url('{BASE}/Fallback/SourceSans3-Regular.ttf') format('truetype');"),
]

KOPF = f"""  {MARKER}
  <meta name="color-scheme" content="light only">
  <meta name="supported-color-schemes" content="light only">
  <style type="text/css">
    :root {{ color-scheme: light only; supported-color-schemes: light only; }}
  </style>
  <!--[if mso]>
  <style type="text/css">
    body, table, td, div, p, a, span, h1, h2, h3 {{ font-family: Arial, Helvetica, sans-serif !important; }}
  </style>
  <![endif]-->
</head>"""


def haerten(text: str, esc) -> str:
    for alt, neu in ERSATZ:
        text = text.replace(esc(alt), esc(neu))
    if esc(MARKER) not in text:
        n = text.count("</head>")
        text = text.replace("</head>", esc(KOPF[:-len("</head>")]) + "</head>")
        assert n, "kein </head> gefunden"
    return text


def roh(s):
    return s


def srcdoc(s):
    # srcdoc in index.html: & und " sind maskiert, < > nicht
    return html.escape(s, quote=True).replace("&lt;", "<").replace("&gt;", ">").replace("&#x27;", "'")


def main():
    check = "--check" in sys.argv
    geaendert = []
    ziele = [(p, lambda t: haerten(t, roh)) for p in sorted((APP / "mails").glob("mail_*.html"))]
    # index.html: nur die eingebetteten Mails (srcdoc), nicht den Kopf der Seite
    ziele.append((APP / "index.html",
                  lambda t: re.sub(r'srcdoc="([^"]*)"',
                                   lambda m: 'srcdoc="' + haerten(m.group(1), srcdoc) + '"', t)))
    for pfad, fn in ziele:
        alt = pfad.read_text(encoding="utf-8")
        neu = fn(alt)
        if neu != alt:
            geaendert.append(pfad.relative_to(ROOT))
            if not check:
                pfad.write_text(neu, encoding="utf-8")
    for p in geaendert:
        print(("veraltet: " if check else "gehärtet: ") + str(p))
    if check and geaendert:
        sys.exit(1)
    if not geaendert:
        print("alles aktuell")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Webfont-Adressen (Entscheid des Inhabers 25. 11. 2026): Unter jeder alten,
# versionierten Adresse in Webfonts/ (v2.7, v2.8 – in Mails und fremden
# Seiten verlinkt) liegt die aktuelle Fassung, dazu unversionierte Adressen,
# die immer die neueste Fassung liefern:
#   Webfonts/woff2/Goetheanum-Schrift-Klar.woff2, …-Kursiv-Klar.woff2 (seit 2.94),
#   …-Variabel.woff2, …-Icons, …-Pfeile
# Quelle sind die Dateien mit AKTUELL im Namen. Nach jedem Schrift-Bau laufen
# lassen; idempotent (reine Kopien).
# Aufruf:  python3 webfont_adressen.py
import os, re, shutil, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.normpath(os.path.join(HERE, "..", "..", "assets/fonts/goetheanum/Webfonts"))
AKTUELL = "v2.9"
CUTS = ("Leise", "Ruhig", "Klar", "Deutlich", "Laut")
# alte Adressen, die draussen verlinkt sind (je woff und woff2, wo vorhanden)
ALT = ["Goetheanum-Schrift-v2.7-Deutlich", "Goetheanum-Schrift-v2.7-Klar",
       "Goetheanum-Schrift-v2.8-Deutlich", "Goetheanum-Variabel-v2.7",
       "Goetheanum-Icons-v2.7", "Goetheanum-Pfeile-v2.7"]


def quelle(name):
    """Aktuelle Datei zu einem (alten oder unversionierten) Namen."""
    name = re.sub(r"-v2\.\d+", "", name)
    for fam in ("Goetheanum-Schrift-", "Goetheanum-Kursiv-"):
        if name.startswith(fam):
            return name.replace(fam, "%s%s-" % (fam, AKTUELL))
    return "%s-%s" % (name, AKTUELL)


def main():
    n = 0
    for flv in ("woff", "woff2"):
        ziele = ["Goetheanum-Schrift-%s" % c for c in CUTS] + \
                ["Goetheanum-Kursiv-Klar", "Goetheanum-Variabel", "Goetheanum-Icons",
                 "Goetheanum-Pfeile"]
        ziele += [a for a in ALT if os.path.exists(os.path.join(WF, flv, "%s.%s" % (a, flv)))]
        for z in ziele:
            src = os.path.join(WF, flv, "%s.%s" % (quelle(z), flv))
            dst = os.path.join(WF, flv, "%s.%s" % (z, flv))
            shutil.copyfile(src, dst); n += 1
            print("  %s/%s.%s ← %s" % (flv, z, flv, os.path.basename(src)))
    print("%d Adressen bespielt." % n)


if __name__ == "__main__":
    main()

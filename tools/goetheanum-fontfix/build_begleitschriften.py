#!/usr/bin/env python3
"""Begleitschriften für den Installer bauen (reproduzierbar, idempotent).

Erzeugt assets/fonts/goetheanum/Begleitschriften/:

- Source Sans 3, statisch, **unverändert** aus dem Adobe-Release 3.052R
  (Regular, It, Bold, BoldIt, Semibold, SemiboldIt). Entscheid Inhaber
  (31. 10. 2026): nicht umbenennen. Semibold ist bei Adobe schon eine eigene
  Office-Familie («Source Sans 3 Semibold», nameID 1), Regular/It/Bold/BoldIt
  bilden die Familie «Source Sans 3».
- Goetheanum Kyrillisch (Regular, Bold) aus Titillium Web [RUS by Daymarius]
  (Fallback/TitilliumRUS-Regular/-Bold.ttf).
- Goetheanum Arabisch (Regular, Bold) aus Cairo (Fallback/Cairo-Variable.ttf,
  statisch instanziiert bei wght 400/700, slnt 0).

Bei Kyrillisch und Arabisch wird nur die Namenstabelle in unser System
gebracht (Familie, Regular/Bold verbunden) und die OS/2-/head-Stilbits
gesetzt; Konturen, Metriken und GPOS/GSUB bleiben (die überlaufende alte
'kern'-Tabelle von Titillium RUS fällt weg, ihre Paare stehen im GPOS). Copyright (nameID 0) und
Lizenz (13/14) bleiben, die Herkunft steht in nameID 10. Beide Quellen: SIL
OFL 1.1, kein Reserved Font Name, fsType 0 (geprüft, Abbruch sonst).

Ausführen (aus der Repo-Wurzel oder hier):
    pip install fonttools
    python3 tools/goetheanum-fontfix/build_begleitschriften.py
Das Adobe-ZIP wird geladen und per SHA-256 geprüft; mit --adobe-zip <Datei>
eine lokale Kopie nehmen.
"""
import argparse
import hashlib
import io
import os
import shutil
import sys
import urllib.request
import zipfile

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
FALLBACK = os.path.join(FONTS, "Fallback")
ZIEL = os.path.join(FONTS, "Begleitschriften")

ADOBE_TAG = "3.052R"
ADOBE_URL = ("https://github.com/adobe-fonts/source-sans/releases/download/"
             "%s/TTF-source-sans-%s.zip" % (ADOBE_TAG, ADOBE_TAG))
ADOBE_SHA256 = "1b0dd1ec44b39f1dd98bbd153a1a3815f083639874ddee02c842bd601bad3d21"
ADOBE_LIZENZ_URL = ("https://raw.githubusercontent.com/adobe-fonts/source-sans/"
                    "%s/LICENSE.md" % ADOBE_TAG)
SOURCE_SANS = ["Regular", "It", "Bold", "BoldIt", "Semibold", "SemiboldIt"]

VERSION = "1.0"

# Familie, Quelle, Herkunftstext
ABLEITUNGEN = {
    "Kyrillisch": {
        "quelle": "Titillium Web [RUS by Daymarius]",
        "herkunft": (
            "Goetheanum Kyrillisch is a renamed version of Titillium Web "
            "[RUS by Daymarius] (Accademia di Belle Arti di Urbino; Cyrillic "
            "extension by Daymarius), adopted for the Goetheanum fonts. Outlines, "
            "metrics and features are unchanged. SIL Open Font License 1.1."),
    },
    "Arabisch": {
        "quelle": "Cairo",
        "herkunft": (
            "Goetheanum Arabisch is a renamed static instance of Cairo "
            "(The Cairo Project Authors, Mohamed Gaber; Latin based on Titillium "
            "Web), adopted for the Goetheanum fonts. Outlines, metrics and "
            "features are unchanged. SIL Open Font License 1.1."),
    },
}


def lade(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def pruefe_frei(font, datei):
    """OFL ohne Reserved Font Name und fsType 0, sonst Abbruch."""
    name = font["name"]
    lizenz = (name.getDebugName(13) or "") + (name.getDebugName(0) or "")
    if "Open Font License" not in lizenz:
        sys.exit("Keine OFL in %s" % datei)
    if "Reserved Font Name" in lizenz:
        sys.exit("Reserved Font Name in %s – umbenennen nicht erlaubt" % datei)
    if font["OS/2"].fsType != 0:
        sys.exit("fsType %d in %s" % (font["OS/2"].fsType, datei))


def benenne(font, familie, stil, version_alt):
    """Namenstabelle und Stilbits für Regular/Bold einer RIBBI-Familie."""
    fam = "Goetheanum " + familie
    ps = "Goetheanum%s-%s" % (familie, stil)
    name = font["name"]
    for nid in (1, 2, 3, 4, 5, 6, 10, 16, 17, 18, 21, 22, 25):
        name.removeNames(nameID=nid)
    werte = {
        1: fam,
        2: stil,
        3: "%s;GOET;%s" % (VERSION, ps),
        4: fam if stil == "Regular" else "%s %s" % (fam, stil),
        5: "Version %s; %s (Goetheanum %s)" % (VERSION, version_alt, familie),
        6: ps,
        10: ABLEITUNGEN[familie]["herkunft"],
    }
    for nid, wert in werte.items():
        name.setName(wert, nid, 3, 1, 0x409)
    # Mac-Einträge (Plattform 1) fallen weg; nur 0/13/14 & Co. bleiben dort.
    name.names = [r for r in name.names
                  if not (r.platformID == 1 and r.nameID in werte)]

    fett = stil == "Bold"
    os2 = font["OS/2"]
    os2.usWeightClass = 700 if fett else 400
    fs = os2.fsSelection & ~(0x01 | 0x20 | 0x40)       # italic, bold, regular weg
    os2.fsSelection = fs | (0x20 if fett else 0x40)
    font["head"].macStyle = 0x01 if fett else 0x00
    font["head"].fontRevision = float(VERSION)
    # DSIG/STAT veraltet nach Änderung; das alte 'kern' von Titillium RUS
    # Regular läuft über (Subtabelle > 64 KB) und steht vollständig im GPOS.
    for tab in ("DSIG", "STAT", "kern"):
        if tab in font:
            del font[tab]
    name.removeUnusedNames(font)


def baue_kyrillisch():
    for stil in ("Regular", "Bold"):
        datei = os.path.join(FALLBACK, "TitilliumRUS-%s.ttf" % stil)
        f = TTFont(datei, recalcTimestamp=False)
        pruefe_frei(f, datei)
        alt = (f["name"].getDebugName(5) or "").split(";")[0].strip()
        benenne(f, "Kyrillisch", stil, "%s %s" % (ABLEITUNGEN["Kyrillisch"]["quelle"], alt))
        ziel = os.path.join(ZIEL, "GoetheanumKyrillisch-%s.ttf" % stil)
        f.save(ziel)
        print("gebaut:", os.path.relpath(ziel, REPO))


def baue_arabisch():
    datei = os.path.join(FALLBACK, "Cairo-Variable.ttf")
    for stil, wght in (("Regular", 400), ("Bold", 700)):
        f = TTFont(datei, recalcTimestamp=False)
        pruefe_frei(f, datei)
        alt = (f["name"].getDebugName(5) or "").split(";")[0].strip()
        f = instancer.instantiateVariableFont(f, {"wght": wght, "slnt": 0})
        benenne(f, "Arabisch", stil, "%s %s" % (ABLEITUNGEN["Arabisch"]["quelle"], alt))
        ziel = os.path.join(ZIEL, "GoetheanumArabisch-%s.ttf" % stil)
        f.save(ziel)
        print("gebaut:", os.path.relpath(ziel, REPO))


def hole_source_sans(adobe_zip):
    daten = open(adobe_zip, "rb").read() if adobe_zip else lade(ADOBE_URL)
    if hashlib.sha256(daten).hexdigest() != ADOBE_SHA256:
        sys.exit("SHA-256 des Adobe-ZIP stimmt nicht – nichts geschrieben.")
    with zipfile.ZipFile(io.BytesIO(daten)) as z:
        for s in SOURCE_SANS:
            arc = "TTF/SourceSans3-%s.ttf" % s
            ziel = os.path.join(ZIEL, os.path.basename(arc))
            with open(ziel, "wb") as fh:
                fh.write(z.read(arc))
            print("kopiert:", os.path.relpath(ziel, REPO))
    lizenz = lade(ADOBE_LIZENZ_URL)
    with open(os.path.join(ZIEL, "LICENSE-SourceSans3.md"), "wb") as fh:
        fh.write(lizenz)


def schreibe_ofl():
    """OFL-Datei für Kyrillisch und Arabisch: Copyright der Quellen + Volltext."""
    ofl = open(os.path.join(FONTS, "OFL.txt"), encoding="utf-8").read()
    volltext = ofl[ofl.index("SIL OPEN FONT LICENSE Version 1.1"):]
    kopf = []
    for familie, datei in (("Kyrillisch", "TitilliumRUS-Regular.ttf"),
                           ("Arabisch", "Cairo-Variable.ttf")):
        f = TTFont(os.path.join(FALLBACK, datei))
        kopf.append("Goetheanum %s – Original Version: %s\n%s\n\n%s\n"
                    % (familie, ABLEITUNGEN[familie]["quelle"],
                       f["name"].getDebugName(0),
                       ABLEITUNGEN[familie]["herkunft"]))
    text = ("Goetheanum Kyrillisch und Goetheanum Arabisch sind umbenannte "
            "Fassungen (Modified Versions)\nunter der SIL Open Font License 1.1. "
            "Die Originale tragen keinen Reserved Font Name.\n\n"
            + "\n".join(kopf) + "\n" + "=" * 75 + "\n\n" + volltext)
    with open(os.path.join(ZIEL, "OFL-Kyrillisch-Arabisch.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adobe-zip", help="lokale TTF-source-sans-%s.zip" % ADOBE_TAG)
    args = ap.parse_args()
    os.makedirs(ZIEL, exist_ok=True)
    hole_source_sans(args.adobe_zip)
    baue_kyrillisch()
    baue_arabisch()
    schreibe_ofl()


if __name__ == "__main__":
    main()

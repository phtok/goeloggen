#!/usr/bin/env python3
"""Goetheanum Arabisch bauen: variable Schwesterdatei und fünf Office-Schnitte.

Quelle: assets/fonts/goetheanum/Fallback/Cairo-Variable.ttf (Cairo 3.130,
SIL OFL 1.1, kein Reserved Font Name, fsType 0 – geprüft, Abbruch sonst).

Schritte (Etappe A1, docs/befunde/schriftsysteme-3.0-2026-11-26.md):

1. Kursiv-Achse `slnt` bei 0 festsetzen, `wght` auf 200–705 mit neuem
   Standard 452 begrenzen (fontTools-Instancer, L4).
2. Achse auf die Hausachse heben: fvar 190–440–725 wie die Goetheanum
   Variabel; `avar` bildet jeden Hauswert auf das Cairo-Gewicht mit gleichem
   Alif-Stamm ab (STAMM unten, gemessen in
   docs/recherche_schriftsysteme-variable.md § Gewichtsabgleich). Die
   Abbildung ist die exakte Verkettung «Haus → Cairo-wght → Cairos eigenes
   avar», darum stückweise linear mit den Knicken beider Tabellen.
   gvar, HVAR, MVAR, GSUB/GPOS bleiben unberührt (normierter Raum gleich).
3. Sieben Named Instances mit Hausnamen, STAT neu.
4. Fünf statische Schnitte aus der variablen Datei, Office-Struktur wie das
   Haus (CLAUDE-REF.md § Schnitt-System): Familie «Goetheanum Arabisch» =
   Klar (Regular) + Laut (Fett) + Leise (Kursiv-Platz); Ruhig und Deutlich
   als eigene Familien.
5. Web: die variable Datei als woff2.

Ausgabe:
    assets/fonts/goetheanum/Begleitschriften/GoetheanumArabisch-Variabel.ttf
    assets/fonts/goetheanum/Begleitschriften/GoetheanumArabisch{Leise,Ruhig,Klar,Deutlich,Laut}.ttf
    assets/fonts/goetheanum/Webfonts/woff2/GoetheanumArabisch-Variabel.woff2

Konturen, Metriken (hhea 1303/−571) und Shaping (init/medi/fina/rlig,
mark/mkmk) bleiben Cairos. Reproduzierbar: zwei Läufe bytegleich.

    python3 tools/goetheanum-fontfix/build_arabisch.py
"""
import os
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
QUELLE = os.path.join(FONTS, "Fallback", "Cairo-Variable.ttf")
ZIEL = os.path.join(FONTS, "Begleitschriften")
WEB = os.path.join(FONTS, "Webfonts", "woff2")

VERSION = "2.0"
FAMILIE = "Goetheanum Arabisch"
PS = "GoetheanumArabisch"

# Hausachse (wie Goetheanum Variabel v2.9)
HAUS_MIN, HAUS_STD, HAUS_MAX = 190, 440, 725

# Hauswert → Cairo-wght mit gleichem Alif-Stamm (gemessen, s. Kopf)
STAMM = [(190, 200), (265, 302), (350, 358), (440, 452),
         (580, 636), (680, 683), (725, 705)]

INSTANZEN = [("Flüstern", "Fluestern", 190), ("Leise", "Leise", 265),
             ("Ruhig", "Ruhig", 350), ("Klar", "Klar", 440),
             ("Deutlich", "Deutlich", 580), ("Laut", "Laut", 680),
             ("Schreien", "Schreien", 725)]

# Office: (Schnitt, wght, Familie nameID 1, Stil nameID 2, fsSelection, macStyle)
OFFICE = [
    ("Klar", 440, FAMILIE, "Regular", 0x40, 0x00),
    ("Laut", 680, FAMILIE, "Bold", 0x20, 0x01),
    ("Leise", 265, FAMILIE, "Italic", 0x01, 0x02),
    ("Ruhig", 350, FAMILIE + " Ruhig", "Regular", 0x40, 0x00),
    ("Deutlich", 580, FAMILIE + " Deutlich", "Regular", 0x40, 0x00),
]

HERKUNFT = (
    "Goetheanum Arabisch is a modified version of Cairo (The Cairo Project "
    "Authors, Mohamed Gaber; Latin based on Titillium Web), adopted for the "
    "Goetheanum fonts. The slant axis is fixed at 0; the weight axis is "
    "remapped by avar to the Goetheanum axis (190-725) so that each Goetheanum "
    "weight matches its stem. Outlines, metrics and features are unchanged. "
    "SIL Open Font License 1.1.")


def pruefe_frei(font):
    name = font["name"]
    lizenz = (name.getDebugName(13) or "") + (name.getDebugName(0) or "")
    if "Open Font License" not in lizenz:
        sys.exit("Keine OFL in der Quelle")
    if "Reserved Font Name" in lizenz:
        sys.exit("Reserved Font Name in der Quelle – umbenennen nicht erlaubt")
    if font["OS/2"].fsType != 0:
        sys.exit("fsType %d in der Quelle" % font["OS/2"].fsType)


def linear(punkte, x):
    """Stückweise linear durch sortierte (x, y)-Paare."""
    for (x0, y0), (x1, y1) in zip(punkte, punkte[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def umkehr(punkte, y):
    return linear(sorted((b, a) for a, b in punkte), y)


def normiere(wert, lo, std, hi):
    if wert < std:
        return (wert - std) / (std - lo)
    return (wert - std) / (hi - std) if wert > std else 0.0


def entnormiere(n, lo, std, hi):
    return std + n * ((std - lo) if n < 0 else (hi - std))


def hausachse(font):
    """fvar auf die Hausachse, avar = Haus → Cairo-wght → Cairo-avar."""
    achse = font["fvar"].axes[0]
    c_lo, c_std, c_hi = achse.minValue, achse.defaultValue, achse.maxValue
    assert (achse.axisTag, c_lo, c_std, c_hi) == ("wght", 200, 452, 705)
    cairo_avar = sorted(font["avar"].segments["wght"].items())

    # Knicke: Hausstützpunkte und die Urbilder von Cairos avar-Knicken
    knicke = {h for h, _ in STAMM}
    for n, _ in cairo_avar:
        knicke.add(umkehr(STAMM, entnormiere(n, c_lo, c_std, c_hi)))
    segmente = {}
    for h in sorted(knicke):
        c = linear(STAMM, h)
        ziel = linear(cairo_avar, normiere(c, c_lo, c_std, c_hi))
        segmente[round(normiere(h, HAUS_MIN, HAUS_STD, HAUS_MAX), 6)] = round(ziel, 6)
    segmente[-1.0], segmente[0.0], segmente[1.0] = -1.0, 0.0, 1.0
    font["avar"].segments["wght"] = dict(sorted(segmente.items()))
    achse.minValue, achse.defaultValue, achse.maxValue = HAUS_MIN, HAUS_STD, HAUS_MAX


def setze(name, nid, wert):
    name.setName(wert, nid, 3, 1, 0x409)


def grundnamen(font, cairo_version):
    """Gemeinsame Einträge; alle Cairo-Namen ausser 0/8/9/11–14 fallen weg."""
    name = font["name"]
    name.names = [r for r in name.names
                  if r.platformID == 3 and r.nameID in (0, 8, 9, 11, 12, 13, 14)]
    setze(name, 5, "Version %s; Cairo %s (Goetheanum Arabisch)" % (VERSION, cairo_version))
    setze(name, 10, HERKUNFT)
    font["head"].fontRevision = float(VERSION)
    for tab in ("DSIG",):
        if tab in font:
            del font[tab]


def benenne_variabel(font):
    name = font["name"]
    fam = FAMILIE + " Variabel"
    setze(name, 1, fam)
    setze(name, 2, "Regular")
    setze(name, 3, "%s;GOET;%sVariabel" % (VERSION, PS))
    setze(name, 4, fam + " Klar")
    setze(name, 6, PS + "Variabel")
    setze(name, 16, fam)
    setze(name, 17, "Klar")
    setze(name, 25, PS + "Variabel")

    fvar = font["fvar"]
    fvar.axes[0].axisNameID = name.addName("Weight", platforms=((3, 1, 0x409),))
    fvar.instances = []
    for anzeige, ascii_, wert in INSTANZEN:
        inst = NamedInstance()
        inst.coordinates = {"wght": float(wert)}
        inst.subfamilyNameID = name.addName(anzeige, platforms=((3, 1, 0x409),))
        ps = PS + "Variabel" + ("" if ascii_ == "Klar" else "-" + ascii_)
        inst.postscriptNameID = name.addName(ps, platforms=((3, 1, 0x409),))
        fvar.instances.append(inst)

    werte = [{"value": w, "name": a, **({"flags": 0x2} if w == HAUS_STD else {})}
             for a, _, w in INSTANZEN]
    del font["STAT"]
    buildStatTable(font, [{"tag": "wght", "name": "Weight", "values": werte}],
                   elidedFallbackName="Klar", windowsNames=True, macNames=False)
    font["OS/2"].usWeightClass = HAUS_STD
    font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~0x61) | 0x40
    font["head"].macStyle = 0
    name.removeUnusedNames(font)


def benenne_statisch(font, schnitt, wght, fam, stil, fs, mac):
    name = font["name"]
    ps = PS + schnitt
    for nid in (16, 17, 25):
        name.removeNames(nameID=nid)
    setze(name, 1, fam)
    setze(name, 2, stil)
    setze(name, 3, "%s;GOET;%s" % (VERSION, ps))
    setze(name, 4, "%s %s" % (FAMILIE, schnitt))
    setze(name, 6, ps)
    if fam == FAMILIE:  # Trio: typografische Familie mit Hausnamen
        setze(name, 16, FAMILIE)
        setze(name, 17, schnitt)
    os2 = font["OS/2"]
    os2.usWeightClass = wght
    os2.fsSelection = (os2.fsSelection & ~0x61) | fs
    font["head"].macStyle = mac
    for tab in ("STAT", "fvar", "avar"):
        if tab in font:
            del font[tab]
    name.removeUnusedNames(font)


def baue_variabel():
    quelle = TTFont(QUELLE, recalcTimestamp=False)
    pruefe_frei(quelle)
    cairo_version = (quelle["name"].getDebugName(5) or "").split(";")[0].replace("Version ", "").strip()
    var = instancer.instantiateVariableFont(
        quelle, {"slnt": 0, "wght": (200, 452, 705)})
    hausachse(var)
    grundnamen(var, cairo_version)
    benenne_variabel(var)
    return var


def main():
    os.makedirs(ZIEL, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)
    var = baue_variabel()
    ziel = os.path.join(ZIEL, PS + "-Variabel.ttf")
    var.save(ziel)
    print("gebaut:", os.path.relpath(ziel, REPO))

    var = TTFont(ziel, recalcTimestamp=False)
    for schnitt, wght, fam, stil, fs, mac in OFFICE:
        st = instancer.instantiateVariableFont(var, {"wght": wght})
        benenne_statisch(st, schnitt, wght, fam, stil, fs, mac)
        datei = os.path.join(ZIEL, PS + schnitt + ".ttf")
        st.save(datei)
        print("gebaut:", os.path.relpath(datei, REPO))

    web = TTFont(ziel, recalcTimestamp=False)
    web.flavor = "woff2"
    datei = os.path.join(WEB, PS + "-Variabel.woff2")
    web.save(datei)
    print("gebaut:", os.path.relpath(datei, REPO))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Baut die ‹Office›-TTF aus den statischen OTF-Quellen: TrueType-Outlines
# (cu2qu). Seit dem Ende der Desktop-OTF-Auslieferung ist die Office-TTF das
# EINZIGE installierbare Paket und trägt die Familienstruktur selbst:
#   - Trio ‹Goetheanum Schrift›: Klar = Regular, Laut = Fett (Cmd+B),
#     Leise = Kursiv (Cmd+I) — Namen, Stilbits und echte Gewichte kommen
#     unverändert aus den Quell-OTF (440/680/265).
#   - Eigene Familien: Goetheanum Schrift Ruhig / Deutlich, Goetheanum Icons,
#     Goetheanum Pfeile — je ‹Regular›, im Namen wählbar.
# Eigene PostScript-/Unique-IDs. fsType = installierbar.
# TTF bettet PowerPoint zuverlässig ein (OTF/CFF nicht).
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
OUT = os.path.join(REPO, "assets/fonts/goetheanum/Office")

# Quelle  ->  (Modus, eindeutiger PostScript/ID-Stamm, flacher Familienname)
# ‹trio›  = RIBBI-Mitglied der Familie ‹Goetheanum Schrift› (Namen aus der Quelle)
# ‹flach› = eigene Regular-Familie, im Namen wählbar
JOBS = [
    ("Goetheanum-Schrift-v2.7-Leise.otf",    "trio",  "GoetheanumSchriftLeise",          None),
    ("Goetheanum-Schrift-v2.7-Ruhig.otf",    "flach", "GoetheanumSchriftRuhig",          "Goetheanum Schrift Ruhig"),
    ("Goetheanum-Schrift-v2.7-Klar.otf",     "trio",  "GoetheanumSchriftKlar",           None),
    ("Goetheanum-Schrift-v2.7-Deutlich.otf", "flach", "GoetheanumSchriftDeutlichOffice", "Goetheanum Schrift Deutlich"),
    ("Goetheanum-Schrift-v2.7-Laut.otf",     "trio",  "GoetheanumSchriftLaut",           None),
    ("Goetheanum-Icons-v2.7.otf",            "flach", "GoetheanumIconsOffice",           "Goetheanum Icons"),
    ("Goetheanum-Pfeile-v2.7.otf",           "flach", "GoetheanumPfeileOffice",          "Goetheanum Pfeile"),
]

# Design-Gewichte der flachen Schnitte (Schnitt-System v2.7; identisch zu
# STAT/Webfonts). Das Trio behält seine Gewichte direkt aus der Quell-OTF.
WEIGHTS = {"Ruhig": 350, "Deutlich": 580}

def otf_to_ttf(ft, max_err=1.0):
    glyphOrder = ft.getGlyphOrder(); gs = ft.getGlyphSet()
    glyf = newTable("glyf"); glyf.glyphOrder = glyphOrder; glyf.glyphs = {}
    for name in glyphOrder:
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, max_err, reverse_direction=True))
        glyf[name] = pen.glyph()
    ft["loca"] = newTable("loca")
    ft["glyf"] = glyf
    if "CFF " in ft: del ft["CFF "]
    if "VORG" in ft: del ft["VORG"]
    # maxp v1.0 mit aus dem glyf berechneten Höchstwerten
    # + hmtx-Vorbreite (lsb) aus dem echten xMin neu setzen: die OTF trägt teils
    # eine lsb ≠ xMin (Überhang z. B. bei Guillemets); TrueType richtet an der
    # lsb aus, sonst verschiebt sich die Glyphe. Vorschub (advance) bleibt.
    hmtx = ft["hmtx"]
    maxPoints = maxContours = maxComp = 0
    for name, g in glyf.glyphs.items():
        g.recalcBounds(glyf)
        xmin = g.xMin if g.numberOfContours != 0 else 0
        hmtx[name] = (hmtx[name][0], xmin)
        if g.isComposite():
            maxComp = max(maxComp, len(g.components))
        elif g.numberOfContours > 0:
            maxContours = max(maxContours, g.numberOfContours)
            maxPoints = max(maxPoints, len(g.coordinates))
    maxp = newTable("maxp"); maxp.tableVersion = 0x00010000
    maxp.numGlyphs = len(glyphOrder)
    maxp.maxPoints = maxPoints; maxp.maxContours = maxContours
    maxp.maxCompositePoints = 0; maxp.maxCompositeContours = 0
    maxp.maxZones = 1; maxp.maxTwilightPoints = 0; maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0; maxp.maxInstructionDefs = 0; maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0; maxp.maxComponentElements = maxComp
    maxp.maxComponentDepth = 1 if maxComp else 0
    ft["maxp"] = maxp
    ft["post"].formatType = 3.0           # TTF ohne Glyphennamen – für Office ok
    ft.sfntVersion = "\x00\x01\x00\x00"

def setname(ft, mode, ps, family):
    nm = ft["name"]
    def S(i, v):
        nm.setName(v, i, 3, 1, 0x409); nm.setName(v, i, 1, 0, 0)
    S(6, ps); S(3, "2.7;GOEA;" + ps)
    os2 = ft["OS/2"]
    os2.fsType = 0                                            # installierbar einbettbar
    if mode == "trio":
        # RIBBI-Namen (id 1/2/4/16/17/21/22), Stilbits (fsSelection/macStyle)
        # und echte Gewichte (Klar 440, Laut 680, Leise 265) bleiben unverändert
        # aus der Quell-OTF: die Office-TTF IST die Familie ‹Goetheanum Schrift›
        # — Laut = Fett (Cmd+B), Leise = Kursiv (Cmd+I).
        return
    head = ft["head"]
    nm.removeNames(nameID=16); nm.removeNames(nameID=17)   # keine Typo-Gruppierung → eigene Familie
    nm.removeNames(nameID=21); nm.removeNames(nameID=22)   # auch keine WWS-Gruppierung
    S(1, family); S(2, "Regular"); S(4, family)
    os2.fsSelection = (os2.fsSelection & ~0b100001) | 0x40   # nur REGULAR (Bold/Italic aus)
    # Echtes Design-Gewicht (wie STAT/Webfonts) statt pauschal 400 — pauschale
    # 400er machten die Schnitte für PowerPoint ununterscheidbar (Sperr-Effekt).
    os2.usWeightClass = WEIGHTS.get(family.split()[-1], 400)
    head.macStyle = 0

LIESMICH = """Goetheanum-Schriften fürs Office (Word, PowerPoint, Outlook)
==============================================================

WICHTIG — zuerst Altbestand entfernen:
Falls schon Goetheanum-Schriften installiert sind (auch die frueheren
Desktop-OTF), diese VOR der Installation entfernen — sonst geraten Alt
und Neu in Konflikt und Office zeigt gesperrte oder kuenstlich verformte
Schnitte.
  - Mac: Programm ‹Schriftsammlung› oeffnen, nach ‹Goetheanum› suchen,
    alle Treffer loeschen. Anleitung von Apple:
    https://support.apple.com/de-de/guide/font-book/fntb2bcb512d/mac
  - Windows: Einstellungen > Personalisierung > Schriftarten, nach
    ‹Goetheanum› suchen, deinstallieren.

Installieren:
  - Mac:     Doppelklick auf jede .ttf  ->  Installieren
  - Windows: Rechtsklick auf jede .ttf  ->  Installieren
Danach das Office-Programm neu starten.

Im Schrift-Menue heissen sie:
  Goetheanum Schrift            (= Klar. Laut ueber Fett/Cmd+B,
                                 Leise ueber Kursiv/Cmd+I)
  Goetheanum Schrift Ruhig
  Goetheanum Schrift Deutlich
  Goetheanum Icons  und  Goetheanum Pfeile

Fett und Kursiv zugleich gibt es nicht — die Kombination wuerde
kuenstlich verformt.

Der Beipackzettel (PDF) zeigt Zeichensatz, Funktionen und die Tastatur-
Belegung der Piktogramme.

WOFF/WOFF2 sind reine Web-Dateien und lassen sich NICHT installieren.
"""

def pack_zip():
    """Office-TTF-ZIP reproduzierbar: die TTF + Beipackzettel + LIESMICH."""
    import zipfile
    root = os.path.join(REPO, "assets/fonts/goetheanum")
    beipack = os.path.join(root, "Beipackzettel-Goetheanum-Schriften.pdf")
    out = os.path.join(root, "Goetheanum-Office-TTF.zip")
    members = sorted(glob.glob(os.path.join(OUT, "*.ttf")))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in members:
            zi = zipfile.ZipInfo(os.path.basename(p), date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(p, "rb") as fh: z.writestr(zi, fh.read())
        if os.path.isfile(beipack):
            zi = zipfile.ZipInfo("Beipackzettel-Goetheanum-Schriften.pdf", date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(beipack, "rb") as fh: z.writestr(zi, fh.read())
        z.writestr(zipfile.ZipInfo("LIESMICH.txt", date_time=(1980, 1, 1, 0, 0, 0)), LIESMICH)
    print("  Goetheanum-Office-TTF.zip (%d TTF + Beipackzettel + LIESMICH)" % len(members))

def main():
    os.makedirs(OUT, exist_ok=True)
    for src, mode, ps, family in JOBS:
        ft = TTFont(os.path.join(FONTS, src))
        otf_to_ttf(ft)
        setname(ft, mode, ps, family)
        out = os.path.join(OUT, ps.replace("Office", "") + ".ttf")
        ft.save(out)
        r = TTFont(out)                                       # Reload-Probe
        print("  %-30s -> %-28s glyf:%s ng:%d" % (
            src, os.path.basename(out), "glyf" in r, len(r.getGlyphOrder())))
    pack_zip()
    print("Office-TTF gebaut ->", OUT)

if __name__ == "__main__":
    main()

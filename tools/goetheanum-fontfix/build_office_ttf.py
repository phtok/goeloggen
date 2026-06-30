#!/usr/bin/env python3
# Baut die ‹Office›-TTF aus den statischen OTF-Schnitten: TrueType-Outlines
# (cu2qu) und FLACHE Familiennamen, exakt wie sie Office/PowerPoint-Vorlagen
# rufen — jeder Schnitt eine eigene Familie (Goetheanum Schrift Klar/Laut/Leise/
# Deutlich, Goetheanum Icons), alle ‹Regular›, im Namen wählbar. Eigene
# PostScript-/Unique-IDs, damit sie neben der konzeptuellen OTF (RIBBI-Familie
# ‹Goetheanum Schrift›) installiert sein können. fsType = installierbar.
# TTF bettet PowerPoint zuverlässig ein (OTF/CFF nicht).
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
OUT = os.path.join(REPO, "assets/fonts/goetheanum/Office")

# Quelle  ->  (sichtbarer Familienname, eindeutiger PostScript/ID-Stamm)
JOBS = [
    ("Goetheanum-Schrift-v2.6-Klar.otf",     "Goetheanum Schrift Klar",     "GoetheanumSchriftKlar"),
    ("Goetheanum-Schrift-v2.6-Laut.otf",     "Goetheanum Schrift Laut",     "GoetheanumSchriftLaut"),
    ("Goetheanum-Schrift-v2.6-Leise.otf",    "Goetheanum Schrift Leise",    "GoetheanumSchriftLeise"),
    ("Goetheanum-Schrift-v2.6-Deutlich.otf", "Goetheanum Schrift Deutlich", "GoetheanumSchriftDeutlichOffice"),
    ("Goetheanum-Icons-v2.6.otf",            "Goetheanum Icons",            "GoetheanumIconsOffice"),
]

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

def setname(ft, family, ps):
    nm = ft["name"]
    def S(i, v):
        nm.setName(v, i, 3, 1, 0x409); nm.setName(v, i, 1, 0, 0)
    nm.removeNames(nameID=16); nm.removeNames(nameID=17)   # keine Typo-Gruppierung → eigene Familie
    S(1, family); S(2, "Regular"); S(4, family); S(6, ps)
    S(3, "2.6;GOEA;" + ps)
    os2 = ft["OS/2"]; head = ft["head"]
    os2.fsSelection = (os2.fsSelection & ~0b100001) | 0x40   # nur REGULAR (Bold/Italic aus)
    os2.usWeightClass = 400
    os2.fsType = 0                                            # installierbar einbettbar
    head.macStyle = 0

LIESMICH = """Goetheanum-Schriften fürs Office (Word, PowerPoint, Outlook)
==============================================================

Installieren:
  - Mac:     Doppelklick auf jede .ttf  ->  Installieren
  - Windows: Rechtsklick auf jede .ttf  ->  Installieren
Danach das Office-Programm neu starten.

Im Schrift-Menue heissen sie:
  Goetheanum Schrift Klar / Laut / Leise / Deutlich  und  Goetheanum Icons

Der Beipackzettel (PDF) zeigt Zeichensatz, Funktionen und die Tastatur-
Belegung der Piktogramme.

WOFF/WOFF2 sind reine Web-Dateien und lassen sich NICHT installieren.
"""

def pack_zip():
    """Office-TTF-ZIP reproduzierbar: die fünf TTF + Beipackzettel + LIESMICH."""
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
    for src, family, ps in JOBS:
        ft = TTFont(os.path.join(FONTS, src))
        otf_to_ttf(ft)
        setname(ft, family, ps)
        out = os.path.join(OUT, ps.replace("Office", "") + ".ttf")
        ft.save(out)
        r = TTFont(out)                                       # Reload-Probe
        print("  %-30s -> %-28s glyf:%s ng:%d" % (
            src, os.path.basename(out), "glyf" in r, len(r.getGlyphOrder())))
    pack_zip()
    print("Office-TTF gebaut ->", OUT)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# PILOT: ein variabler Icon-Font mit echter wght-Achse aus fünf Piktogrammen.
# Beleg für ‹flexible Icons› – dieselbe Idee wie der Variable Font der Schrift,
# nur für Zeichen. Zwei Master pro Icon: der gezeichnete Umriss (leicht) und ein
# programmatisch verstärkter (fett, Punkt-für-Punkt entlang der Normalen nach
# aussen versetzt → punktkompatibel, also interpolierbar). varLib verwebt sie zur
# wght-Achse. Reproduzierbar; im Produktivfall kämen die Master aus gezeichneten
# Vorlagen (die Pfeile liegen z. B. schon in leicht+fett vor).
import os, sys, math, json, copy, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.subset import Subsetter
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from fontTools import varLib
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC  = os.path.join(REPO, "assets/fonts/goetheanum/Fonts/Goetheanum-Icons-v2.7.otf")
OUT  = os.path.join(REPO, "assets/fonts/goetheanum/Flex-Pilot")
DELTA = 52   # Verstärkung leicht -> fett in Font-Einheiten (UPM 1000)

# Icon-slug -> ASCII-Taste im Pilot-Font (bequem für die Demo)
PILOT = {"wlan":"w", "garderobe":"g", "pfeil-hoch":"u", "pfeil-rechts":"r", "fahrstuhl":"f"}

def contour_area(pts):
    a = 0.0; n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a / 2

def embolden_coords(coords, ends, delta):
    """Jeden Konturpunkt entlang der lokalen Normalen nach aussen versetzen –
    hält Punktzahl/Reihenfolge (interpolationskompatibel)."""
    out = [list(c) for c in coords]; start = 0
    for e in ends:
        idx = list(range(start, e + 1)); pts = [tuple(coords[i]) for i in idx]
        s = 1 if contour_area(pts) > 0 else -1; m = len(idx)
        for k in range(m):
            px, py = pts[(k - 1) % m]; nx, ny = pts[(k + 1) % m]
            tx, ty = nx - px, ny - py; L = math.hypot(tx, ty)
            if L < 1e-6: continue
            out[idx[k]] = [pts[k][0] + (ty / L) * delta * s,
                           pts[k][1] + (-tx / L) * delta * s]
        start = e + 1
    return out

def make_master(weight, delta):
    ft = TTFont(SRC)
    # auf die Pilot-Glyphen verkleinern + auf ASCII umlegen
    cmap = ft.getBestCmap(); man = json.load(open(
        os.path.join(REPO, "assets/fonts/goetheanum/Icons-Einzeldateien/icons.json")))
    slug2cp = {m["slug"]: int(m["codepoint"][2:], 16) for m in man}
    keep = {slug2cp[s] for s in PILOT}
    ss = Subsetter(); ss.populate(unicodes=list(keep)); ss.subset(ft)
    # glyf aus CFF (cu2qu)
    glyphOrder = ft.getGlyphOrder(); gs = ft.getGlyphSet()
    glyf = newTable("glyf"); glyf.glyphOrder = glyphOrder; glyf.glyphs = {}
    for name in glyphOrder:
        pen = TTGlyphPen(gs); gs[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=False))
        glyf[name] = pen.glyph()
    ft["glyf"] = glyf; ft["loca"] = newTable("loca")
    if "CFF " in ft: del ft["CFF "]
    if "VORG" in ft: del ft["VORG"]
    # optional verstärken
    if delta:
        for name in glyphOrder:
            g = glyf[name]
            if g.numberOfContours <= 0: continue
            g.coordinates = GlyphCoordinates(
                [tuple(map(round, p)) for p in
                 embolden_coords(g.coordinates, g.endPtsOfContours, delta)])
            g.recalcBounds(glyf)
    # PUA-Codepoints der Pilot-Icons auf ASCII-Tasten umlegen (Demo-freundlich)
    rename = {slug2cp[s]: ord(key) for s, key in PILOT.items()}
    for sub in ft["cmap"].tables:
        sub.cmap = {rename[cp]: gn for cp, gn in sub.cmap.items() if cp in rename}
    # maxp v1.0 mit vollständigen Feldern (glyf braucht sie)
    maxPoints = maxContours = 0
    for name in glyphOrder:
        g = glyf[name]
        if g.numberOfContours > 0:
            maxContours = max(maxContours, g.numberOfContours)
            maxPoints = max(maxPoints, len(g.coordinates))
    mp = newTable("maxp"); mp.tableVersion = 0x00010000
    mp.numGlyphs = len(glyphOrder); mp.maxPoints = maxPoints; mp.maxContours = maxContours
    mp.maxCompositePoints = 0; mp.maxCompositeContours = 0
    mp.maxZones = 1; mp.maxTwilightPoints = 0; mp.maxStorage = 0
    mp.maxFunctionDefs = 0; mp.maxInstructionDefs = 0; mp.maxStackElements = 0
    mp.maxSizeOfInstructions = 0; mp.maxComponentElements = 0; mp.maxComponentDepth = 0
    ft["maxp"] = mp
    ft["post"].formatType = 3.0
    ft["OS/2"].usWeightClass = weight
    ft.sfntVersion = "\x00\x01\x00\x00"
    return ft

def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    light = os.path.join(tmp, "light.ttf"); heavy = os.path.join(tmp, "heavy.ttf")
    make_master(300, 0).save(light)
    make_master(700, DELTA).save(heavy)
    # DesignSpace: eine wght-Achse
    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.tag = "wght"; ax.name = "Weight"
    ax.minimum = 300; ax.default = 300; ax.maximum = 700; ds.addAxis(ax)
    for path, w in ((light, 300), (heavy, 700)):
        s = SourceDescriptor(); s.path = path; s.location = {"Weight": w}; ds.addSource(s)
    for nm, w in (("Leicht", 300), ("Klar", 440), ("Laut", 680)):
        ins = InstanceDescriptor(); ins.styleName = nm; ins.location = {"Weight": w}
        ds.addInstance(ins)
    vf, _, _ = varLib.build(ds)
    # Benennung
    def S(i, v):
        vf["name"].setName(v, i, 3, 1, 0x409); vf["name"].setName(v, i, 1, 0, 0)
    S(1, "Goetheanum Icons Flex"); S(2, "Regular")
    S(4, "Goetheanum Icons Flex"); S(6, "GoetheanumIconsFlex")
    S(3, "2.7-pilot;GOEA;GoetheanumIconsFlex"); S(5, "Version 2.7 (Pilot)")
    otf = os.path.join(OUT, "Goetheanum-Icons-Flex-Pilot.ttf")
    vf.save(otf)
    vf.flavor = "woff2"; vf.save(os.path.join(OUT, "Goetheanum-Icons-Flex-Pilot.woff2"))
    print("Pilot gebaut:", otf)
    print("  Achse wght 300–700 · Glyphen:", ", ".join(f"{k}={v}" for k, v in PILOT.items()))

if __name__ == "__main__":
    main()

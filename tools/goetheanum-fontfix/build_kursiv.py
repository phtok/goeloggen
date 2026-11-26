#!/usr/bin/env python3
# Goetheanum Kursiv, Fassung 2.94 (26. 11. 2026). Entscheid des Inhabers vom
# 26. 11.; Bauplan und Befund: docs/befunde/kursive-probe-e1-2026-10-31.md
# (Abschnitte «Entscheid Form …», «Entscheid Bau», «Bau 2.94»).
#
# Baut aus den drei Kursiv-Mastern der Titillium Sans Pro (OFL):
#   - Variable/Goetheanum-Kursiv-Variabel-v2.9.otf   ‹Goetheanum Kursiv Variabel›,
#     wght 190–725, sieben Instanzen wie die aufrechte Variable (Flüstern …
#     Schreien), Standard Klar. Für Gestalter; eigene Datei, keine ital-Achse.
#   - Fonts/Goetheanum-Kursiv-v2.9-Klar.otf           Bauquelle (nicht im Paket)
#     für Office (build_office_ttf.py: eigene Familie ‹Goetheanum Kursiv›,
#     ⌘I bleibt Leise) und Web (Webfonts/…/Goetheanum-Kursiv-v2.9-Klar.woff2/.woff,
#     in tokens.css als ‹Goetheanum› mit font-style: italic).
#
# Quelle: https://github.com/chialab/titillium_pro, Commit 65ca1530. Der Klon
# ist fremder Inhalt: eigener Ordner, Skript mit `python3 -I`, Pfad als Argument:
#
#   git clone https://github.com/chialab/titillium_pro /tmp/tp
#   git -C /tmp/tp checkout 65ca1530fcc8ab4a864e4f3bc87672e5b8da821f
#   pip install fontmake ufo2ft ufoLib2 brotli skia-pathops
#   python3 -I tools/goetheanum-fontfix/build_kursiv.py /tmp/tp
#
# Schritte
#   1 Bold-Master vervollständigen (dem Bold-Italic-UFO fehlen 152 Glyphen):
#     a) reine Komponenten-Glyphen vom Regular;
#     b) aus der mitgelieferten BoldItalic.woff2 (aus demselben Master
#        kompiliert), wenn die Punkte zum Regular passen – auch wo der
#        Compiler Konturen umsortiert, Startpunkt oder Richtung gewechselt hat;
#     c) Ç: Punkte aus den Bold-Glyphen C und Cedille, an der woff2 eingepasst;
#        M.ss03 (Listenzeichen): Punkte aus der woff2, die flache Spitze der
#        Mitte (zwei Punkte im Regular, einer in der woff2) auf eine Spitze;
#     d) Jacute und Lslashcomb sind unerreichbar (kein Unicode, kein Feature,
#        keine Komponente): in allen Mastern entfernt.
#     Nichts wird mehr fortgeschrieben (die Probe schrieb 22 Glyphen aus Thin
#     und Regular fort, bis 108 Einheiten neben der echten Zeichnung).
#   2 Mischform (Inhaber 26. 11.): a mit Fuss als Grundform (ss01 der Pro),
#     l mit Bogen (Grundform der Pro). ss01 = a ohne Fuss, ss02 = gerades l.
#   3 Zeichen der Hausschrift, die der Pro fehlen: ‐ ‑ (U+2010/2011 = Divis),
#     ‒ (U+2012, Divis-lang auf Ziffernbreite), Wortverbinder U+2060, Ǻ ǻ.
#   4 Gewicht: Achse in Stammeinheiten (waagrechter Schnitt durch das I).
#     Ziel je Hausgewicht = senkrechter Stamm der aufrechten Hausschrift
#     geteilt durch cos 12°. Flüstern und Klar entstehen als Zwischenmaster
#     (Interpolation der echten Master); Schreien endet am Bold-Master
#     (Stamm 137 statt 141, 3 % leichter: eine Variable kann nicht über ihre
#     Master hinaus).
#   5 Vertikalmasse wie die Hausschnitte (typo 750/−250, lineGap 0,
#     USE_TYPO_METRICS); jedes Sprachsystem bekommt die Features von latn/dflt
#     (Quellfehler latn/DEU, siehe build_kursiv_probe.stilsets_alle_sprachen).
# Idempotent: feste Zeitstempel, gleicher Eingang ergibt gleiche Dateien.
import math, os, shutil, sys, tempfile, re, plistlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_kursiv_probe as P

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPointPen
from fontTools.pens.areaPen import AreaPen

REPO = P.REPO
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
VERSION, VMAJ, VMIN = "2.94", 2, 940
EPOCH = 3_847_219_200  # 26. 11. 2025 in Mac-Epoche, fest
FAMILY_VAR = "Goetheanum Kursiv Variabel"
FAMILY_STAT = "Goetheanum Kursiv"
OUT_VAR = os.path.join(ROOT, "Variable", "Goetheanum-Kursiv-Variabel-v2.9.otf")
OUT_STAT = os.path.join(ROOT, "Fonts", "Goetheanum-Kursiv-v2.9-Klar.otf")
OUT_WEB = os.path.join(ROOT, "Webfonts", "%s", "Goetheanum-Kursiv-v2.9-Klar.%s")
HAUS_VAR = os.path.join(ROOT, "Variable", "Goetheanum-Variabel-v2.9.otf")
# Gewichte wie die aufrechte Variable (fvar), Namen ASCII für PostScript
GEWICHTE = [("Flüstern", 190), ("Leise", 265), ("Ruhig", 350), ("Klar", 440),
            ("Deutlich", 580), ("Laut", 680), ("Schreien", 725)]
ASCII = {"Flüstern": "Fluestern"}
UNERREICHBAR = ["Jacute", "Lslashcomb"]


# ---------------------------------------------------------------- 1 Bold-Master
def _contours(rec):
    out, cur = [], None
    for op, a, k in rec:
        if op == "beginPath": cur = []
        elif op == "addPoint": cur.append((a[0], a[1]))
        elif op == "endPath": out.append(cur)
    return out


def _rec(glyph):
    r = RecordingPointPen(); glyph.drawPoints(r); return r.value


def _match_contours(ref, cand):
    """Ordnet die Konturen von cand denen von ref zu: gleiche Punktzahl und
    Punktarten, bis auf Reihenfolge, Startpunkt und Richtung. Liefert die
    umgestellten Konturen oder None."""
    used, out = set(), []
    for c in ref:
        kinds, best = [p[1] for p in c], None
        for j, d in enumerate(cand):
            if j in used or len(d) != len(c): continue
            for dd in (d, d[::-1]):
                for r in range(len(dd)):
                    rot = dd[r:] + dd[:r]
                    if [p[1] for p in rot] != kinds: continue
                    err = max(math.dist(p[0], q[0]) for p, q in zip(c, rot))
                    if best is None or err < best[0]: best = (err, j, rot)
        if best is None: return None
        used.add(best[1]); out.append(best[2])
    return out


def _draw(glyph, contours):
    pen = glyph.getPointPen()
    for c in contours:
        pen.beginPath()
        for xy, t in c: pen.addPoint(xy, segmentType=t)
        pen.endPath()


def _pts(g):
    return [(p.x, p.y) for c in g.contours for p in c.points]


def _offset(A, B):
    return Counter((round(a[0] - b[0]), round(a[1] - b[1])) for a in A for b in B).most_common(1)[0][0]


def bold_ccedilla(reg, bold, wgs, wpts):
    """Ç ist im Regular eine Kontur (C und Cedille verschmolzen, 51 Punkte),
    in der woff2 nach dem Entfernen der Überlappung 47. Jeder Punkt, der im
    Regular zu C oder zur Cedille gehört, nimmt den entsprechenden Punkt der
    Bold-Glyphe; die Lage der Cedille misst die woff2. Die sechs Punkte der
    Naht nehmen den nächsten woff2-Punkt."""
    g = "Ccedilla"; R = reg[g]; W = wpts
    plan = []
    for n in ("C", "cedilla"):
        plan.append((n, _offset(_pts(R), _pts(reg[n])), _offset(W, _pts(bold[n])),
                     _pts(reg[n]), _pts(bold[n])))
    out = []
    for c in R.contours:
        cc = []
        for p in c.points:
            hit = None
            for n, o_r, o_b, rp, bp in plan:
                key = (p.x - o_r[0], p.y - o_r[1])
                if key in rp:
                    bx, by = bp[rp.index(key)]; hit = (bx + o_b[0], by + o_b[1]); break
            if hit is None:
                # Naht: aus der Lage im Regular relativ zum C auf Bold übertragen,
                # dann auf den nächsten woff2-Punkt
                hit = min(W, key=lambda t: math.dist((p.x, p.y), t))
            cc.append((hit, p.type))
        out.append(cc)
    return out


def bold_m_ss03(reg, wcontours):
    """M.ss03: Regular 16 Punkte, woff2 15 – die flache Spitze der Mitte
    (zwei Punkte) ist in Bold eine Spitze. Beide Punkte gehen auf sie, 1
    Einheit auseinander."""
    R = reg["M.ss03"].contours[0].points
    W = [c for c in wcontours if len(c) == len(R) - 1][0]
    w = [xy for xy, t in W]
    out, j = [], 0
    # Reihenfolge wie im Regular; die zwei Spitzenpunkte stehen nebeneinander
    flat = [i for i in range(len(R) - 1) if R[i].y == R[i + 1].y and 0 < R[i].y < 100]
    i0 = flat[0]
    for i, p in enumerate(R):
        if i == i0: x, y = w[j]; out.append(((x - 1, y), p.type)); continue
        if i == i0 + 1: x, y = w[j]; out.append(((x + 1, y), p.type)); j += 1; continue
        out.append((w[j], p.type)); j += 1
    return [out]


def fill_bold(src, paths):
    import ufoLib2
    bold = paths["Bold"]; cp = os.path.join(bold, "glyphs", "contents.plist")
    contents = plistlib.load(open(cp, "rb"))
    missing = [g for g, f in contents.items() if not os.path.exists(os.path.join(bold, "glyphs", f))]
    for g in missing: del contents[g]
    plistlib.dump(contents, open(cp, "wb"))
    reg = ufoLib2.Font.open(paths["Regular"]); bf = ufoLib2.Font.open(bold)
    woff = TTFont(os.path.join(src, "Sans", "WEB", "TitilliumSansPro-BoldItalic.woff2"))
    wgs, wcmap, worder = woff.getGlyphSet(), woff.getBestCmap(), set(woff.getGlyphOrder())
    stat = Counter()
    for g in missing:
        r = reg[g]; ng = bf.newGlyph(g); ng.unicodes = list(r.unicodes)
        if g in UNERREICHBAR:
            del bf[g]; stat["unerreichbar"] += 1; continue
        if r.components and not r.contours:
            for c in r.components: ng.components.append(c)
            ng.width = r.width; stat["Komponenten"] += 1; continue
        wn = g if g in worder else (wcmap.get(r.unicodes[0]) if r.unicodes else None)
        wrec = _rec(wgs[wn]); wc = _contours(wrec)
        rc = _contours(_rec(r)) if not r.components else None
        m = _match_contours(rc, wc) if rc is not None else None
        if r.components:  # Kontur(en) + Komponente (Listenzeichen)
            if g == "M.ss03":
                _draw(ng, bold_m_ss03(reg, wc)); stat["woff2 angepasst"] += 1
            else:
                sys.exit("Bold-Master: %s hat Konturen und Komponenten, keine Regel" % g)
            for c in r.components: ng.components.append(c)
        elif m is not None:
            _draw(ng, m); stat["woff2"] += 1
        elif g == "Ccedilla":
            _draw(ng, bold_ccedilla(reg, bf, wgs, [xy for c in wc for xy, t in c]))
            stat["woff2 angepasst"] += 1
        else:
            sys.exit("Bold-Master: keine Regel für %s" % g)
        ng.width = woff["hmtx"][wn][0]
    bf.save(bold, overwrite=True)
    # unerreichbare Glyphen auch aus Thin und Regular
    for m_ in ("Thin", "Regular"):
        f = ufoLib2.Font.open(paths[m_])
        for g in UNERREICHBAR:
            if g in f: del f[g]
        f.save(paths[m_], overwrite=True)
    print("Bold-Master: %d fehlende Glyphen – %s" % (
        len(missing), ", ".join("%s %d" % kv for kv in sorted(stat.items()))))


def prepare(src, tmp):
    import ufoLib2
    ufo = os.path.join(src, "Sans", "UFO"); paths = {}
    for m, _ in P.MASTERS:
        d = os.path.join(tmp, "%s.ufo" % m)
        shutil.copytree(os.path.join(ufo, "Titillium Sans Pro-%s Italic.ufo" % m), d)
        lc = os.path.join(d, "layercontents.plist")
        if not os.path.isdir(os.path.join(d, "glyphs.public.background")):
            t = open(lc, encoding="utf-8").read()
            t = re.sub(r"\s*<array>\s*<string>public\.background</string>\s*"
                       r"<string>glyphs\.public\.background</string>\s*</array>", "", t)
            open(lc, "w", encoding="utf-8").write(t)
        paths[m] = d
    if not os.path.exists(os.path.join(paths["Bold"], "fontinfo.plist")):
        shutil.copy(os.path.join(paths["Regular"], "fontinfo.plist"), paths["Bold"])
    fill_bold(src, paths)
    return paths


# ------------------------------------------------------- 2 Mischform, 3 Zeichen
def swap_pairs(regular):
    block = re.search(r"feature ss01 \{(.*?)\} ss01;", regular.features.text, re.S)
    return [(b, a) for b, a in re.findall(r"sub (\S+) by (\S+);", block.group(1))
            if b in regular and a in regular]


def swap(font, pairs):
    for base, alt in pairs:
        a, b = font[base], font[alt]
        ca, cb = list(a.contours), list(b.contours)
        coa, cob = list(a.components), list(b.components)
        wa, wb, ana, anb = a.width, b.width, list(a.anchors), list(b.anchors)
        a.clearContours(); a.clearComponents(); b.clearContours(); b.clearComponents()
        for c in cb: a.appendContour(c)
        for c in ca: b.appendContour(c)
        for c in cob: a.components.append(c)
        for c in coa: b.components.append(c)
        a.width, b.width, a.anchors, b.anchors = wb, wa, anb, ana


def _bounds_where(font, g, ymin):
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(font)
    for c in font[g].contours:
        cb = BoundsPen(font); c.draw(cb)
        if cb.bounds and cb.bounds[1] >= ymin: c.draw(bp)
    return bp.bounds


def zeichen(font, angle):
    """Zeichen der Hausschrift, die der Pro fehlen (in jedem Master gleich
    gebaut, darum interpolierbar)."""
    from fontTools.pens.boundsPen import BoundsPen
    h = font["hyphen"]
    h.unicodes = sorted(set(h.unicodes) | {0x2010, 0x2011})
    # ‒ Ziffernstrich: Divis-lang (endash) auf die Breite der Null, mittig
    fd = font.newGlyph("figuredash"); fd.unicodes = [0x2012]
    fd.width = font["zero"].width
    fd.components.append(_comp("endash", (fd.width - font["endash"].width) / 2.0, 0))
    wj = font.newGlyph("uni2060"); wj.unicodes = [0x2060]; wj.width = 0
    t = math.tan(math.radians(abs(angle)))
    for neu, basis, akzent, ymin, u in (("Aringacute", "Aring", "acutecomb.case", 700, 0x1FA),
                                        ("aringacute", "aring", "acutecomb", 520, 0x1FB)):
        g = font.newGlyph(neu); g.unicodes = [u]; g.width = font[basis].width
        g.components.append(_comp(basis, 0, 0))
        ring = _bounds_where(font, basis, ymin)
        ab = BoundsPen(font); font[akzent].draw(ab); ab = ab.bounds
        dy = ring[3] + 20 - ab[1]
        # Mitte des Akzents über die Mitte des Rings, der Neigung nach versetzt
        dx = (ring[0] + ring[2]) / 2.0 - (ab[0] + ab[2]) / 2.0 + t * (
            (ab[1] + ab[3]) / 2.0 + dy - (ring[1] + ring[3]) / 2.0)
        g.components.append(_comp(akzent, dx, dy))


def _comp(base, dx, dy):
    from ufoLib2.objects import Component
    from fontTools.misc.transform import Transform
    return Component(baseGlyph=base, transformation=Transform(1, 0, 0, 1, round(dx), round(dy)))


# ------------------------------------------------------------------- 4 Gewicht
def haus_stamm(wght):
    """Senkrechter I-Stamm der aufrechten Hausschrift bei wght (Variable)."""
    from fontTools.varLib.instancer import instantiateVariableFont
    from fontTools.pens.boundsPen import BoundsPen
    f = instantiateVariableFont(TTFont(HAUS_VAR), {"wght": wght})
    gs = f.getGlyphSet(); g = gs[f.getBestCmap()[ord("I")]]
    a = AreaPen(gs); g.draw(a); b = BoundsPen(gs); g.draw(b)
    return abs(a.value) / (b.bounds[3] - b.bounds[1])


def ziele(angle, stems):
    c = math.cos(math.radians(abs(angle)))
    out = []
    for name, w in GEWICHTE:
        t = haus_stamm(w) / c
        out.append((name, w, t, min(t, stems["Bold"])))
    return out


# --------------------------------------------------------------- Namen, Masse
def set_info(font, family, style, weight, angle, ps):
    ref = TTFont(P.house("Klar")); os2, hh = ref["OS/2"], ref["hhea"]
    i = font.info
    i.familyName = family; i.styleName = style
    i.styleMapFamilyName = family; i.styleMapStyleName = "italic"
    i.openTypeNamePreferredFamilyName = family
    i.openTypeNamePreferredSubfamilyName = style
    i.postscriptFontName = ps
    i.postscriptFullName = "%s %s" % (family, style)
    i.openTypeNameUniqueID = "%s;GOEA;%s" % (VERSION, ps)
    i.versionMajor, i.versionMinor = VMAJ, VMIN
    i.openTypeNameVersion = "Version %s" % VERSION
    i.copyright = ("Copyright (c) 2024 The Titillium Pro Project Authors "
                   "(https://github.com/chialab/titillium_pro). Goetheanum-Bearbeitung 2026.")
    i.trademark = None
    i.openTypeNameManufacturer = "Goetheanum (Bearbeitung), Chialab (Titillium Pro)"
    i.openTypeNameDesigner = "Accademia di Belle Arti di Urbino; Antonio D'Elisiis (Titillium Pro)"
    i.openTypeNameDescription = ("Kursive der Goetheanum Schrift, aus Titillium Sans Pro "
                                 "Italic. Rolle: Werktitel im Fliesstext.")
    i.openTypeNameLicense = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeOS2WeightClass = weight
    i.italicAngle = angle
    i.unitsPerEm = 1000
    i.ascender, i.descender = os2.sTypoAscender, os2.sTypoDescender
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender = os2.sTypoAscender, os2.sTypoDescender
    i.openTypeOS2TypoLineGap = 0
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = os2.usWinAscent, os2.usWinDescent
    i.openTypeHheaAscender, i.openTypeHheaDescender = hh.ascent, hh.descent
    i.openTypeHheaLineGap = 0
    i.openTypeOS2Selection = [7]  # USE_TYPO_METRICS
    i.openTypeOS2VendorID = os2.achVendID
    i.openTypeHeadCreated = "2026/11/26 00:00:00"
    i.postscriptIsFixedPitch = False
    i.openTypeOS2Type = []
    feat = font.features.text
    feat = feat.replace('name "One story a";', 'name "a ohne Fuss";')
    feat = feat.replace('name "Straight l";', 'name "gerades l";')
    font.features.text = feat


def _fest(otf):
    otf["head"].created = otf["head"].modified = EPOCH
    otf.recalcTimestamp = False


def stat_table(otf, var):
    from fontTools.otlLib.builder import buildStatTable
    werte = [dict(value=w, name=n) for n, w in GEWICHTE] if var else [dict(value=440, name="Klar")]
    for v in werte:
        if v["value"] == 440: v["flags"] = 0x2  # elidierbar
    buildStatTable(otf, [
        dict(tag="wght", name="Weight", values=werte),
        dict(tag="ital", name="Italic", values=[dict(value=1, name="Kursiv")]),
    ], elidedFallbackName="Klar")


# --------------------------------------------------------------------- Bauen
def main():
    import ufoLib2, ufo2ft
    from fontmake.instantiator import Instantiator
    from fontTools.designspaceLib import (DesignSpaceDocument, AxisDescriptor,
                                          SourceDescriptor, InstanceDescriptor)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("Aufruf: python3 -I build_kursiv.py <Klon von chialab/titillium_pro>")
    src = os.path.abspath(args[0])
    with tempfile.TemporaryDirectory() as tmp:
        paths = prepare(src, tmp)
        fonts = {m: ufoLib2.Font.open(p) for m, p in paths.items()}
        pairs = swap_pairs(fonts["Regular"])
        angle = fonts["Regular"].info.italicAngle
        for m, f in fonts.items():
            swap(f, pairs); zeichen(f, angle)
        stems = {m: P.stem_ufo(fonts[m]) for m in fonts}
        tabelle = ziele(angle, stems)
        print("Neigung %.1f°, Master-Stämme: %s" % (
            angle, ", ".join("%s %.1f" % (m, stems[m]) for m, _ in P.MASTERS)))
        for n, w, t, d in tabelle:
            print("  %-9s %4d  Ziel %.1f%s" % (n, w, t, "" if t == d else "  → %.1f (Bold-Master)" % d))
        # Zwischenmaster Flüstern und Klar aus den drei echten Mastern
        ds3 = DesignSpaceDocument()
        ax = AxisDescriptor(); ax.tag, ax.name = "wght", "Weight"
        ax.minimum, ax.default, ax.maximum = stems["Thin"], stems["Regular"], stems["Bold"]
        ds3.addAxis(ax)
        for m, _ in P.MASTERS:
            s = SourceDescriptor(); s.font = fonts[m]; s.name = m; s.location = {"Weight": stems[m]}
            if m == "Regular": s.copyInfo = s.copyFeatures = s.copyGroups = s.copyLib = True
            ds3.addSource(s)
        zw = {n: d for n, w, t, d in tabelle if n in ("Flüstern", "Klar")}
        for n, d in zw.items():
            i = InstanceDescriptor(); i.styleName = n; i.familyName = FAMILY_VAR
            i.designLocation = {"Weight": d}; ds3.addInstance(i)
        inst = Instantiator.from_designspace(ds3)
        gen = {i.styleName: inst.generate_instance(i) for i in ds3.instances}
        # Features und Kerning-Klassen sind Sache des Standard-Masters: alle
        # Master tragen die des Regular (Thin und Bold weichen in der Quelle ab)
        for f in list(gen.values()) + [fonts["Thin"], fonts["Bold"]]:
            f.features.text = fonts["Regular"].features.text
            f.groups.clear(); f.groups.update(fonts["Regular"].groups)
            # Komponenten in der Reihenfolge des Regular (der Instantiator
            # ordnet sie teils um; CFF2 verlangt gleiche Reihenfolge)
            for g in f:
                if len(g.components) > 1:
                    order = [c.baseGlyph for c in fonts["Regular"][g.name].components]
                    g.components.sort(key=lambda c: order.index(c.baseGlyph))
        # --- Variable: Masters Flüstern, Regular, Klar (Standard), Bold
        master = [("Flüstern", gen["Flüstern"]), ("Regular", fonts["Regular"]),
                  ("Klar", gen["Klar"]), ("Bold", fonts["Bold"])]
        for n, f in master:
            set_info(f, FAMILY_VAR, "Klar", 440, angle, "GoetheanumKursivVariabel")
        ds = DesignSpaceDocument()
        ax = AxisDescriptor(); ax.tag, ax.name = "wght", "Weight"
        ax.minimum, ax.default, ax.maximum = 190, 440, 725
        ax.map = [(w, d) for n, w, t, d in tabelle]
        ds.addAxis(ax)
        loc = {"Flüstern": zw["Flüstern"], "Regular": stems["Regular"],
               "Klar": zw["Klar"], "Bold": stems["Bold"]}
        for n, f in master:
            s = SourceDescriptor(); s.font = f; s.name = n; s.location = {"Weight": loc[n]}
            ds.addSource(s)
        for n, w, t, d in tabelle:
            i = InstanceDescriptor(); i.familyName = FAMILY_VAR; i.styleName = n
            i.designLocation = {"Weight": d}
            i.postScriptFontName = "GoetheanumKursivVariabel-%s" % ASCII.get(n, n)
            ds.addInstance(i)
        vf = ufo2ft.compileVariableCFF2(ds, optimizeCFF=0, useProductionNames=True)
        P.stilsets_alle_sprachen(vf)
        stat_table(vf, True)
        vf["OS/2"].fsSelection = (vf["OS/2"].fsSelection & ~0x40) | 0x1  # ITALIC
        vf["head"].macStyle |= 0x2
        _fest(vf); vf.save(OUT_VAR)
        print("geschrieben:", os.path.relpath(OUT_VAR, REPO))
        # --- statisch Klar
        k = gen["Klar"]
        set_info(k, FAMILY_STAT, "Klar", 440, angle, "GoetheanumKursiv-Klar")
        otf = ufo2ft.compileOTF(k, removeOverlaps=True, optimizeCFF=0, useProductionNames=True)
        P.stilsets_alle_sprachen(otf)
        _fest(otf); otf.save(OUT_STAT)
        for flavor in ("woff2", "woff"):
            w = TTFont(OUT_STAT); w.flavor = flavor; w.recalcTimestamp = False
            w.save(OUT_WEB % (flavor, flavor))
        print("geschrieben:", os.path.relpath(OUT_STAT, REPO), "+ woff2/woff",
              "– I-Stamm %.1f (Ziel %.1f)" % (P.stem_otf(OUT_STAT), zw["Klar"]))


if __name__ == "__main__":
    main()

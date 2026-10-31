#!/usr/bin/env python3
# Probe E1 (31. 10. 2026): eine Kursive der Hausschrift aus Titillium Sans Pro
# Italic. Baut «Goetheanum Kursiv Probe Klar» – eine PROBE, nicht Teil des
# Pakets (Ablage assets/fonts/goetheanum/Probe/, von pack_release_zip.py nicht
# erfasst). Befund: docs/befunde/kursive-probe-e1-2026-10-31.md
#
# Quelle: https://github.com/chialab/titillium_pro (OFL), Branch main,
# Commit 65ca1530 (4. 2. 2026). Drei kompatible Kursiv-Master als UFO
# (Thin / Regular / Bold Italic). Der Klon ist fremder Inhalt: in einen eigenen
# Ordner legen, dieses Skript mit `python3 -I` aufrufen, Pfad als Argument:
#
#   git clone --depth 1 https://github.com/chialab/titillium_pro /tmp/tp
#   python3 -I tools/goetheanum-fontfix/build_kursiv_probe.py /tmp/tp
#
# Was das Skript tut:
#   1. Gewicht: Achse in Stammeinheiten (waagrechter Schnitt durch das I der
#      drei Master). Zielwert = senkrechte Stammdicke des Hausschnitts
#      (Klar: 82) geteilt durch cos(12°) – so ist der geneigte Stamm
#      quer zur Strichrichtung so dick wie der aufrechte.
#   2. Upright-Formen: ss01 (einstöckiges a) und ss02 (gerades l) der Pro
#      werden zur Grundform; die Text-Formen bleiben über ss01/ss02 erreichbar.
#      g, y, t der Pro-Kursiven entsprechen schon der Hausform.
#   3. Vertikalmetriken wie die Hausschnitte (typo 750/−250, lineGap 0,
#      USE_TYPO_METRICS, win/hhea gleich) – gleiche Zeilenhöhe im Satz.
#   4. Namen und Version als Probe gekennzeichnet; OTF + woff2.
# Idempotent: feste Zeitstempel, gleicher Eingang ergibt gleiche Dateien.
#
# Gewichtstabelle für alle fünf Schnitte: `--tabelle` (baut nichts).
import math, os, shutil, sys, tempfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
HOUSE = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
OUT = os.path.join(REPO, "assets/fonts/goetheanum/Probe")
COMMIT = "65ca1530fcc8ab4a864e4f3bc87672e5b8da821f"
MASTERS = [("Thin", 100), ("Regular", 400), ("Bold", 700)]
SCHNITTE = [("Leise", 265), ("Ruhig", 350), ("Klar", 440), ("Deutlich", 580), ("Laut", 680)]
BAUEN = ["Klar"]
FAMILY = "Goetheanum Kursiv Probe"
VERSION = "0.100"
EPOCH = 3_844_800_000  # 31. 10. 2025 in Mac-Epoche (Sekunden seit 1904), fest

from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen


def stem_otf(path):
    """Waagrechte Stammdicke des I (Fläche / Höhe), Hausschnitt."""
    f = TTFont(path); gs = f.getGlyphSet(); g = gs[f.getBestCmap()[ord("I")]]
    a = AreaPen(gs); g.draw(a); b = BoundsPen(gs); g.draw(b)
    return abs(a.value) / (b.bounds[3] - b.bounds[1])


def stem_ufo(font):
    g = font["I"]; a = AreaPen(font); g.draw(a); b = BoundsPen(font); g.draw(b)
    return abs(a.value) / (b.bounds[3] - b.bounds[1])


def house(name):
    return os.path.join(HOUSE, "Goetheanum-Schrift-v2.9-%s.otf" % name)


def prepare(src, tmp):
    import ufoLib2
    ufo = os.path.join(src, "Sans", "UFO")
    paths = {}
    for m, _ in MASTERS:
        s = os.path.join(ufo, "Titillium Sans Pro-%s Italic.ufo" % m)
        d = os.path.join(tmp, "%s.ufo" % m)
        shutil.copytree(s, d)
        lc = os.path.join(d, "layercontents.plist")
        if not os.path.isdir(os.path.join(d, "glyphs.public.background")):
            t = open(lc, encoding="utf-8").read()
            t = re.sub(r"\s*<array>\s*<string>public\.background</string>\s*"
                       r"<string>glyphs\.public\.background</string>\s*</array>", "", t)
            open(lc, "w", encoding="utf-8").write(t)
        paths[m] = d
    # Dem Bold-Master fehlt fontinfo.plist: vom Regular übernehmen.
    if not os.path.exists(os.path.join(paths["Bold"], "fontinfo.plist")):
        shutil.copy(os.path.join(paths["Regular"], "fontinfo.plist"), paths["Bold"])
    fill_bold(src, paths)
    fonts = {m: ufoLib2.Font.open(p) for m, p in paths.items()}
    stems = {m: stem_ufo(fonts[m]) for m in fonts}
    angle = fonts["Regular"].info.italicAngle
    return paths, fonts, stems, angle


def _sig(rec):
    out, cur = [], []
    for op, a, k in rec:
        if op == "beginPath": cur = []
        elif op == "addPoint": cur.append(a[1] or "off")
        elif op == "endPath": out.append(tuple(cur))
        elif op == "addComponent": out.append(("comp", a[0]))
    return out


def fill_bold(src, paths):
    """Im Bold-Italic-UFO (Commit 65ca1530) fehlen 152 Glyphendateien
    (Versalien A–N samt Akzenten und Listenzeichen). Auffüllen aus der
    mitgelieferten BoldItalic.woff2 – die ist punktgleich aus demselben Master
    kompiliert (geprüft an den vorhandenen Glyphen) –, wenn die Punktstruktur
    zum Regular-Master passt; reine Komponenten-Glyphen vom Regular. Wo die woff2 abweicht (Überlappungen beim
    Kompilieren entfernt: B D G und ihre Akzente u. a.), wird der Bold-Master
    aus Thin und Regular fortgeschrieben (Regular + k·(Regular − Thin), k aus
    den I-Stämmen). Für Klar ist das eine Fortschreibung um 13 % über Regular
    hinaus; für Deutlich/Laut wären die echten Master nötig."""
    import plistlib, ufoLib2
    from fontTools.pens.recordingPen import RecordingPointPen
    bold = paths["Bold"]; cp = os.path.join(bold, "glyphs", "contents.plist")
    contents = plistlib.load(open(cp, "rb"))
    missing = [g for g, f in contents.items()
               if not os.path.exists(os.path.join(bold, "glyphs", f))]
    if not missing:
        return
    for g in missing:
        del contents[g]
    plistlib.dump(contents, open(cp, "wb"))
    reg = ufoLib2.Font.open(paths["Regular"]); bf = ufoLib2.Font.open(bold)
    thin = ufoLib2.Font.open(paths["Thin"])
    woff = TTFont(os.path.join(src, "Sans", "WEB", "TitilliumSansPro-BoldItalic.woff2"))
    wgs, wcmap, worder = woff.getGlyphSet(), woff.getBestCmap(), set(woff.getGlyphOrder())
    wi = wgs[wcmap[ord("I")]]; a = AreaPen(wgs); wi.draw(a); b = BoundsPen(wgs); wi.draw(b)
    sb, sr, st = abs(a.value) / (b.bounds[3] - b.bounds[1]), stem_ufo(reg), stem_ufo(thin)
    k = (sb - sr) / (sr - st)
    filled, left = 0, []
    for g in missing:
        r = reg[g]; rr = RecordingPointPen(); r.drawPoints(rr); rsig = _sig(rr.value)
        ng = bf.newGlyph(g); ng.unicodes = list(r.unicodes)
        if r.components and not r.contours:
            for c in r.components: ng.components.append(c)
            ng.width = r.width; filled += 1; continue
        wn = g if g in worder else (wcmap.get(r.unicodes[0]) if r.unicodes else None)
        if wn:
            wr = RecordingPointPen(); wgs[wn].drawPoints(wr)
            if _sig(wr.value) == rsig:
                wr.replay(ng.getPointPen()); ng.width = woff["hmtx"][wn][0]; filled += 1
                continue
        tr = RecordingPointPen(); thin[g].drawPoints(tr)
        if _sig(tr.value) == rsig and not r.components:
            tp = [x for x in tr.value]; out = []
            for (op, a1, kw), (_, a2, _) in zip(rr.value, tp):
                if op == "addPoint":
                    (xr, yr), (xt, yt) = a1[0], a2[0]
                    a1 = ((round(xr + k * (xr - xt)), round(yr + k * (yr - yt))),) + tuple(a1[1:])
                out.append((op, a1, kw))
            pen = ng.getPointPen()
            for op, a1, kw in out: getattr(pen, op)(*a1, **kw)
            ng.width = round(r.width + k * (r.width - thin[g].width)); left.append(g)
            continue
        del bf[g]; left.append(g + "(weg)")
    bf.save(bold, overwrite=True)
    print("Bold-Master: %d fehlende Glyphen aus der woff2/Regular, %d fortgeschrieben "
          "(k = %.2f): %s" % (filled, len(left), k, " ".join(left)))


def target_stem(name, angle):
    return stem_otf(house(name)) / math.cos(math.radians(abs(angle)))


def pro_weight(stem, stems):
    seq = [(stems[m], w) for m, w in MASTERS]
    for (s0, w0), (s1, w1) in zip(seq, seq[1:]):
        if stem <= s1 or (s1, w1) == seq[-1]:
            return w0 + (stem - s0) / (s1 - s0) * (w1 - w0)


def designspace(paths, stems, instances):
    from fontTools.designspaceLib import (DesignSpaceDocument, AxisDescriptor,
                                          SourceDescriptor, InstanceDescriptor)
    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.tag = "wght"; ax.name = "Weight"
    ax.minimum, ax.default, ax.maximum = 100, 400, 700
    ax.map = [(w, stems[m]) for m, w in MASTERS]
    ds.addAxis(ax)
    for m, w in MASTERS:
        s = SourceDescriptor(); s.path = paths[m]; s.name = m
        s.location = {"Weight": stems[m]}
        if m == "Regular":
            s.copyInfo = s.copyFeatures = s.copyGroups = s.copyLib = True
        ds.addSource(s)
    for name, stem in instances:
        i = InstanceDescriptor(); i.familyName = FAMILY; i.styleName = name
        i.designLocation = {"Weight": stem}; i.name = name
        ds.addInstance(i)
    return ds


def swap_upright(font):
    """ss01/ss02-Formen (einstöckiges a, gerades l) werden Grundform."""
    pairs = []
    for tag in ("ss01", "ss02"):
        block = re.search(r"feature %s \{(.*?)\} %s;" % (tag, tag), font.features.text, re.S)
        for base, alt in re.findall(r"sub (\S+) by (\S+);", block.group(1)):
            if base in font and alt in font and (base, alt) not in pairs:
                pairs.append((base, alt))
    for base, alt in pairs:
        a, b = font[base], font[alt]
        ca, cb = list(a.contours), list(b.contours)
        coa, cob = list(a.components), list(b.components)
        wa, wb = a.width, b.width
        ana, anb = list(a.anchors), list(b.anchors)
        a.clearContours(); a.clearComponents(); b.clearContours(); b.clearComponents()
        for c in cb: a.appendContour(c)
        for c in ca: b.appendContour(c)
        for c in cob: a.components.append(c)
        for c in coa: b.components.append(c)
        a.width, b.width = wb, wa
        a.anchors, b.anchors = anb, ana
    fea = font.features.text
    fea = fea.replace('name "One story a";', 'name "Titillium-a (Text-Form)";')
    fea = fea.replace('name "Straight l";', 'name "l mit Bogen (Text-Form)";')
    font.features.text = fea
    return [p[0] for p in pairs]


def set_info(font, name, weight, angle):
    ref = TTFont(house(name))
    os2, hh = ref["OS/2"], ref["hhea"]
    i = font.info
    i.familyName = FAMILY; i.styleName = name
    i.styleMapFamilyName = "%s %s" % (FAMILY, name); i.styleMapStyleName = "italic"
    i.openTypeNamePreferredFamilyName = FAMILY
    i.openTypeNamePreferredSubfamilyName = name
    i.postscriptFontName = "GoetheanumKursivProbe-%s" % name
    i.postscriptFullName = "%s %s" % (FAMILY, name)
    i.openTypeNameUniqueID = "%s;Probe-E1;GoetheanumKursivProbe-%s" % (VERSION, name)
    i.versionMajor, i.versionMinor = 0, 100
    i.openTypeNameVersion = "Version %s; Probe E1, nicht ausliefern" % VERSION
    i.copyright = ("Copyright (c) 2024 The Titillium Pro Project Authors "
                   "(https://github.com/chialab/titillium_pro). Goetheanum-Bearbeitung 2026.")
    i.trademark = None
    i.openTypeNameManufacturer = "Goetheanum (Bearbeitung), Chialab (Titillium Pro)"
    i.openTypeNameDesigner = "Accademia di Belle Arti di Urbino; Antonio D'Elisiis (Titillium Pro)"
    i.openTypeNameDescription = ("PROBE E1: Kursive aus Titillium Sans Pro Italic, "
                                 "Upright-a und -l als Grundform. Nicht Teil des Pakets.")
    i.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, "
                             "Version 1.1.")
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
    i.openTypeOS2VendorID = ref["OS/2"].achVendID
    i.openTypeHeadCreated = "2026/10/31 00:00:00"
    i.postscriptIsFixedPitch = False
    i.openTypeOS2Type = []


def compile_font(font, name):
    import ufo2ft
    otf = ufo2ft.compileOTF(font, removeOverlaps=True, optimizeCFF=0,
                            useProductionNames=True)
    otf["head"].created = otf["head"].modified = EPOCH
    otf.recalcTimestamp = False
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, "Goetheanum-Kursiv-Probe-%s" % name)
    otf.save(base + ".otf")
    w = TTFont(base + ".otf"); w.flavor = "woff2"; w.recalcTimestamp = False
    w.save(base + ".woff2")
    return base


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("Aufruf: python3 -I build_kursiv_probe.py <Klon von chialab/titillium_pro>")
    src = os.path.abspath(args[0])
    head = os.path.join(src, ".git", "HEAD")
    if os.path.exists(head):
        try:
            import subprocess
            c = subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], capture_output=True,
                               text=True).stdout.strip()
            if c != COMMIT:
                print("Hinweis: Quelle steht auf %s, geprüft wurde %s" % (c[:8], COMMIT[:8]))
        except Exception:
            pass
    with tempfile.TemporaryDirectory() as tmp:
        paths, fonts, stems, angle = prepare(src, tmp)
        print("Neigung %.1f°, Master-Stämme (waagrecht): %s" % (
            angle, ", ".join("%s %.1f" % (m, stems[m]) for m, _ in MASTERS)))
        print("%-9s %5s %8s %10s %9s" % ("Schnitt", "Haus", "Stamm ⊥", "Ziel waagr.", "Pro-wght"))
        targets = {}
        for name, w in SCHNITTE:
            t = target_stem(name, angle); targets[name] = t
            print("%-9s %5d %8.1f %10.1f %9.0f" % (name, w, stem_otf(house(name)), t,
                                                   pro_weight(t, stems)))
        if "--tabelle" in sys.argv:
            return
        from fontmake.instantiator import Instantiator
        ds = designspace(paths, stems, [(n, targets[n]) for n in BAUEN])
        inst = Instantiator.from_designspace(ds)
        for idesc in ds.instances:
            font = inst.generate_instance(idesc)
            swapped = swap_upright(font)
            w = dict(SCHNITTE)[idesc.styleName]
            set_info(font, idesc.styleName, w, angle)
            print("%s: Grundform getauscht für %d Glyphen (%s …)" % (
                idesc.styleName, len(swapped), ", ".join(swapped[:5])))
            base = compile_font(font, idesc.styleName)
            print("geschrieben:", os.path.relpath(base, REPO) + ".otf/.woff2",
                  "– I-Stamm %.1f (Ziel %.1f)" % (stem_otf(base + ".otf"), targets[idesc.styleName]))


if __name__ == "__main__":
    main()

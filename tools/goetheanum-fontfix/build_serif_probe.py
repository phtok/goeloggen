#!/usr/bin/env python3
# PROBE, nicht Paket. Baut die «Goetheanum Serif Probe» (Etappe E4,
# docs/recherche_titillium-pro.md) aus dem Serif-Prototyp von Chialab
# (Titillium Pro Serif «version_00», Branch serif, Commit 65ca153, OFL).
#
# Was das Skript ergänzt, alles aus Teilen der Quelle oder der Hausschrift:
#   - Trema aus dem Punkt der Quelle (uni0307, der einzige gezeichnete Akzent)
#     → ä ö ü ë ï ÿ Ä Ö Ü Ë Ï als Komposition, dazu ccmp für i/j + Akzent;
#   - ß aus der Hausschrift (Klar, Stamm gleich stark: 81 zu 82 Einheiten)
#     mit dem Fuss-Serif des Serif-h; in der Kursiven geneigt (16°);
#   - einstöckiges a (ss01) nach Hausschrift-Logik: Bauch des Serif-d, oben
#     die Fahne des Serif-u (wie Klar: a = d ohne Oberlänge);
#   - leere Akzente der Quelle aus der cmap, damit é & Co. ganz in die
#     Fallback-Schrift fallen statt den Akzent zu verlieren;
#   - Leerzeichen-Formen U+00A0, U+202F, U+2009 und weiches Trennzeichen,
#     damit gesetzte Texte nicht in die Fallback-Schrift springen;
# Der Name «Titillium» ist in der Quelle als Reserved Font Name geführt
# (OFL § 3, Original Titillium); die Probe heisst darum «Goetheanum Serif Probe».
#
# Idempotent: liest nur sources/titillium-pro-serif-beta/ und die Klar-OTF,
# schreibt immer dieselben Dateien neu (fester Zeitstempel).
#   python3 tools/goetheanum-fontfix/build_serif_probe.py
import os, unicodedata
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen
import pathops

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(HERE, "sources", "titillium-pro-serif-beta")
KLAR = os.path.join(REPO, "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.8-Klar.otf")
OUT = os.path.join(REPO, "assets/fonts/proben/goetheanum-serif-probe")
VERSION = "0.1"
STAMP = 0xE0A1B000  # fester head-Zeitstempel, damit der Build bytegleich bleibt

TAN16 = 0.2867453857588079  # tan(16°), Neigung der Quell-Kursiven


def path_of(gs, name, transform=(1, 0, 0, 1, 0, 0)):
    p = pathops.Path()
    gs[name].draw(TransformPen(p.getPen(), transform))
    return p


def rect(x0, y0, x1, y1):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


def op(a, b, kind):
    return pathops.op(a, b, kind)


def rec_of_path(p):
    r = RecordingPen(); p.draw(r); return r


def rec_of(gs, name, transform=(1, 0, 0, 1, 0, 0)):
    r = RecordingPen(); gs[name].draw(TransformPen(r, transform)); return r


def bounds(rec):
    b = BoundsPen(None); rec.replay(b); return b.bounds


def merge(*recs):
    r = RecordingPen()
    for x in recs: r.value.extend(x.value)
    return r


def build(style):
    src = TTFont(os.path.join(SRC, f"TitilliumProSerif-{style}.otf"))
    klar = TTFont(KLAR)
    italic = style.endswith("Italic")
    gs = src.getGlyphSet(); cmap = dict(src.getBestCmap()); hm = src["hmtx"]
    order = list(src.getGlyphOrder())
    glyphs = {g: rec_of(gs, g) for g in order}
    adv = {g: hm[g][0] for g in order}
    skew = TAN16 if italic else 0.0

    # Ankerpunkte der Quelle (nur für den Punkt vorhanden): Mitte über x-Höhe.
    anchors = {}
    for lk in src["GPOS"].table.LookupList.Lookup:
        for st in lk.SubTable:
            if st.LookupType == 4:
                for b, r in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                    a = r.BaseAnchor[0]; anchors[b] = (a.XCoordinate, a.YCoordinate)
                for m, r in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord):
                    markanchor = (r.MarkAnchor.XCoordinate, r.MarkAnchor.YCoordinate)

    # Trema aus zwei Punkten. Abstand der Punktmitten wie in der Hausschrift
    # (Klar: 190 bei 74 breiten Punkten) auf den breiteren Serif-Punkt (94)
    # hochgerechnet: 210. Höhe: Punkt der Quelle sitzt 110 über der x-Höhe;
    # über Versalien gleicher Abstand über 700 (Klar: 120 über 691).
    dot = glyphs["uni0307"]; dx0, dy0, dx1, dy1 = bounds(dot)
    dcx = (dx0 + dx1) / 2 - skew * ((dy0 + dy1) / 2)  # Mitte auf der Grundlinie
    GAP = 210

    def dieresis_at(cx, lift):
        # cx = gewünschte Mitte (auf Höhe der x-Höhe gemessen), lift = Hub über Quelle
        out = []
        for side in (-GAP / 2, GAP / 2):
            tx = cx - (dx0 + dx1) / 2 + side + skew * lift
            out.append(rec_of(gs, "uni0307", (1, 0, 0, 1, tx, lift)))
        return merge(*out)

    def top_center(g):
        if g in anchors:
            return anchors[g][0] + skew * (500 - anchors[g][1])
        x0, y0, x1, y1 = bounds(glyphs[g])
        return (x0 + x1) / 2 + skew * (500 - (y0 + y1) / 2)

    # Kombinierendes Trema als Glyphe (für Folgen Buchstabe + U+0308).
    glyphs["uni0308"] = dieresis_at((dx0 + dx1) / 2, 0); adv["uni0308"] = 0

    new = {}
    for ch in "äöüëïÿÄÖÜËÏ":
        base_ch = unicodedata.normalize("NFD", ch)[0]
        base = cmap[ord(base_ch)]
        if base == "i": base = "dotlessi"
        lift = 180 if base_ch.isupper() else 0
        cx = top_center(base)
        gname = {"ä": "adieresis", "ö": "odieresis", "ü": "udieresis", "ë": "edieresis",
                 "ï": "idieresis", "ÿ": "ydieresis", "Ä": "Adieresis", "Ö": "Odieresis",
                 "Ü": "Udieresis", "Ë": "Edieresis", "Ï": "Idieresis"}[ch]
        glyphs[gname] = merge(glyphs[base], dieresis_at(cx, lift))
        adv[gname] = adv[base]
        new[ord(ch)] = gname

    # ß: Hausschrift-Form (Klar) + Fuss-Serif des Serif-h links unten.
    kgs = klar.getGlyphSet(); kcm = klar.getBestCmap()
    kss = kcm[0xDF]
    ess = path_of(kgs, kss)
    # Klar-Stamm 65..146 (y 250), Serif-h-Stamm 112..194: Fuss um −47 verschieben.
    # (Bei der Kursiven Fuss der Regular nehmen und alles zusammen neigen.)
    reg = src if not italic else TTFont(os.path.join(SRC, "TitilliumProSerif-Regular.otf"))
    rgs = reg.getGlyphSet()
    foot = op(path_of(rgs, "h", (1, 0, 0, 1, -47, 0)), rect(-100, -5, 240, 61), pathops.PathOp.INTERSECTION)
    ess = op(ess, foot, pathops.PathOp.UNION)
    if italic:
        ess = rec_of_path(ess); r = RecordingPen(); ess.replay(TransformPen(r, (1, 0, skew, 1, 0, 0))); ess_rec = r
    else:
        ess_rec = rec_of_path(ess)
    x0, _, x1, _ = bounds(ess_rec)
    # Seitenränder wie das Serif-h: links 37, rechts 37 (Kursive: Quelle h).
    shift = hm["h"][1] - x0
    r = RecordingPen(); ess_rec.replay(TransformPen(r, (1, 0, 0, 1, shift, 0)))
    glyphs["germandbls"] = r; adv["germandbls"] = round(x1 - x0 + 2 * hm["h"][1])
    new[0xDF] = "germandbls"

    feas = []
    # Einstöckiges a (ss01), nur aufrecht.
    if not italic:
        # Wie Klar (a = d ohne Oberlänge): Stamm des d flach auf Höhe des
        # Bauch-Scheitels (514) gekappt, keine Fahne. Die Variante mit der
        # Kopf-Fahne des u las sich im Bild als u (Befund E4).
        a1 = rec_of_path(op(path_of(gs, "d"), rect(-50, -50, 700, 514), pathops.PathOp.INTERSECTION))
        glyphs["a.ss01"] = a1; adv["a.ss01"] = adv["d"]
        ab = bounds(a1)
        glyphs["adieresis.ss01"] = merge(a1, dieresis_at((ab[0] + ab[2]) / 2 - 10, 0))
        adv["adieresis.ss01"] = adv["d"]
        feas.append("feature ss01 { sub a by a.ss01; sub adieresis by adieresis.ss01; } ss01;")

    # Leerzeichen-Formen
    glyphs["uni00A0"] = RecordingPen(); adv["uni00A0"] = adv["space"]
    glyphs["uni202F"] = RecordingPen(); adv["uni202F"] = round(adv["space"] * 0.6)
    glyphs["uni2009"] = RecordingPen(); adv["uni2009"] = round(adv["space"] * 0.6)
    new.update({0xA0: "uni00A0", 0x202F: "uni202F", 0x2009: "uni2009", 0xAD: "hyphen"})

    for k, v in new.items(): cmap[k] = v
    # Leere Akzente der Quelle (nur gezeichnet: Punkt, hier dazu Trema) aus
    # der cmap nehmen. Sonst zerlegt der Browser é in e + leeren Akzent und
    # setzt ‹Cafe› statt ‹Café›; ohne Eintrag springt die Fallback-Schrift
    # für das ganze Zeichen ein (Befund E4).
    for k in [k for k, g in cmap.items() if 0x300 <= k <= 0x36F and not bounds(glyphs[g])]:
        del cmap[k]
    neworder = order + [g for g in glyphs if g not in order]

    # ccmp der Quelle nachbauen (i/j vor Akzent oben → punktlos)
    topmarks = "[uni0307 uni0308 gravecomb acutecomb uni030B uni0302 uni030C uni0306 uni030A tildecomb uni0304 uni0312]"
    topmarks = "[" + " ".join(g for g in topmarks.strip("[]").split() if g in neworder) + "]"
    feas.insert(0, f"feature ccmp {{ sub i' {topmarks} by dotlessi; sub j' {topmarks} by uni0237; }} ccmp;")

    fam = "Goetheanum Serif Probe"
    sub = "Italic" if italic else "Regular"
    ps = f"GoetheanumSerifProbe-{sub}"
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(neworder)
    fb.setupCharacterMap(cmap)
    priv = src["CFF "].cff.topDictIndex[0].Private
    css = {}
    for g in neworder:
        pen = T2CharStringPen(adv[g], None); glyphs[g].replay(pen); css[g] = pen.getCharString()
    fb.setupCFF(ps, {"FullName": f"{fam} {sub}", "FamilyName": fam, "Weight": sub,
                     "ItalicAngle": -16 if italic else 0},
                css, {"BlueValues": list(getattr(priv, "BlueValues", [])),
                      "StdHW": getattr(priv, "StdHW", 45), "StdVW": getattr(priv, "StdVW", 82)})
    lsb = {}
    for g in neworder:
        b = bounds(glyphs[g]); lsb[g] = round(b[0]) if b else 0
    fb.setupHorizontalMetrics({g: (adv[g], lsb[g]) for g in neworder})
    fb.setupHorizontalHeader(ascent=970, descent=-230, lineGap=0)
    o = src["OS/2"]
    fb.setupOS2(version=4, sTypoAscender=o.sTypoAscender, sTypoDescender=o.sTypoDescender, sTypoLineGap=o.sTypoLineGap,
                usWinAscent=970, usWinDescent=242, sxHeight=500, sCapHeight=700,
                usWeightClass=400, fsSelection=(0x01 if italic else 0x40) | 0x80, achVendID="GOET",
                fsType=0)
    fb.setupNameTable({
        "copyright": "Copyright (c) 2024 The Titillium Pro Project Authors (https://github.com/chialab/titillium_pro). "
                     "Probe-Erweiterung 2026 Goetheanum.",
        "familyName": fam, "styleName": sub,
        "uniqueFontIdentifier": f"{VERSION};GOET;{ps}",
        "fullName": f"{fam} {sub}", "psName": ps,
        "version": f"Version {VERSION} Probe",
        "description": "PROBE, nicht für den Einsatz. Aus Titillium Pro Serif version_00 (Chialab, OFL), "
                       "ergänzt um Trema, ß, einstöckiges a (ss01). Etappe E4.",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupPost(italicAngle=-16 if italic else 0, isFixedPitch=0, underlinePosition=-100, underlineThickness=45)
    fb.font["head"].created = fb.font["head"].modified = STAMP
    fb.font["head"].macStyle = 0x02 if italic else 0
    fb.font["head"].fontRevision = float(VERSION)
    # GPOS (Punkt-Positionierung der Quelle) übernehmen, GSUB neu aus fea
    fb.font["GPOS"] = src["GPOS"]
    fb.font["GDEF"] = src["GDEF"]
    addOpenTypeFeaturesFromString(fb.font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n" + "\n".join(feas),
                                  tables=["GSUB"])
    os.makedirs(OUT, exist_ok=True)
    otf = os.path.join(OUT, f"{ps}.otf")
    fb.font.save(otf)
    f2 = TTFont(otf); f2.flavor = "woff2"; f2.save(os.path.join(OUT, f"{ps}.woff2"))
    print(otf, len(neworder), "Glyphen", len(cmap), "Zeichen")


if __name__ == "__main__":
    for s in ("Regular", "RegularItalic"):
        build(s)

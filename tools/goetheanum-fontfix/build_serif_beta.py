#!/usr/bin/env python3
# Ergänzung, nicht Paket. Baut die «Goetheanum Serif Beta» (Etappe E4,
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
# (OFL § 3, Original Titillium); die Schrift heisst darum «Goetheanum Serif Beta».
#
# Entscheid des Inhabers 25. 11. 2026: ‹Die Serif überzeugt mich im Bild gar
# nicht. Ich würde sie funktional nicht integrieren, nur als Ergänzung
# anbieten. Goetheanum Serif Beta.› Darum: neuer Name, ein ZIP zum Download
# (schriften.html § Download), keine Rolle im Regelwerk, nicht im Paket.
#
# Idempotent: liest nur sources/titillium-pro-serif-beta/, die Klar-OTF und
# (ab 0.2) den Klon der Titillium Pro, schreibt immer dieselben Dateien neu
# (fester Zeitstempel). Zwei Läufe bytegleich.
#   git clone --depth 1 https://github.com/chialab/titillium_pro /tmp/pro/tp   # Commit 65ca153
#   python3 -I tools/goetheanum-fontfix/build_serif_beta.py /tmp/pro/tp       # Fassung 0.2
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
KLAR = os.path.join(REPO, "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-Klar.otf")
OUT = os.path.join(REPO, "assets/fonts/proben/goetheanum-serif-beta")
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


# ---------------------------------------------------------------------------
# Display-Ausbau, Fassung 0.2 (Entscheid des Inhabers 26. 11. 2026: ‹als
# Möglichkeit im Display anbieten. Entsprechend optimieren.›). Was Titel und
# grosse Grade brauchen, aus Titillium Sans Pro (Chialab, OFL, Branch main,
# Commit 65ca153), gleiche Familie, gleiche Vertikalmasse 500/700:
#   - Akzente: Marken der Pro an die Serif-Buchstaben gesetzt; Lage über die
#     Anker der Pro, umgerechnet auf die Mitte (bzw. rechte Kante beim Ogonek)
#     des Serif-Buchstabens im selben Höhenband. Punkt und Trema bleiben die
#     der Serif. Kursive: Marken um 16° geneigt.
#   - Zeichen: & % € § @ + = × ° © ® $ £ … aus der Pro (Strich 78 zu 82);
#     ẞ aus der Pro mit den Fuss- und Kopf-Serifen des Serif-B.
#   - Kerning: Paare der Pro (iKern, Igino Marini), auf Glyphenpaare
#     aufgelöst. Die Breiten der Serif sind andere als in der Pro; die Werte
#     der Pro gelten als Formkorrektur (T über a, Anführung über A), nicht
#     als Abstand. Darum nur Paare, die auch hier eine Lücke schliessen
#     (negative Werte) — positive Werte der Pro antworten auf Sans-Abstände.
# Aufruf mit Pro-Klon:  python3 -I build_serif_beta.py PFAD/titillium_pro
# Ohne Pfad baut das Skript die Fassung 0.1 (nur Quelle + Hausschrift).
# ---------------------------------------------------------------------------
PRO = None
SIGNS = "&%€§@+=×°©®$£¢¥±÷·•†‡¶^~<>|¬µªº‰¦"
# Cedille, die in diesen Sprachen als Komma unten gezeichnet wird (Lettisch,
# Rumänisch-Altform); ģ (Komma oben) und ď ľ ť Ľ (Haken) fehlen bewusst.
COMMA_BELOW = set("ĢĶķĻļŅņŖŗ")
SKIP = set("ģďľťĽ")
TOPMARKS = {0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307, 0x30A, 0x30B, 0x30C}
BOTMARKS = {0x326, 0x327}
OGONEK = 0x328


def _path_from_rec(rec):
    p = pathops.Path(); rec.replay(p.getPen()); return p


def _band(path, y0, y1):
    """Tinte im Höhenband y0..y1: (xmin, xmax) oder None."""
    q = op(path, rect(-2000, y0, 4000, y1), pathops.PathOp.INTERSECTION)
    r = rec_of_path(q); b = bounds(r)
    return (b[0], b[2]) if b else None


def display_ausbau(pro, italic, skew, gs, glyphs, adv, cmap, new, markanchor):
    import sys
    sys.path.insert(0, HERE)
    from pro_quelle import Master
    m = Master(os.path.join(pro, "Sans", "UFO", "Titillium Sans Pro-Regular.ufo"))
    tilt = (1, 0, skew, 1, 0, 0)

    def pro_path(n):
        p = pathops.Path(); m.draw(n, p.getPen()); return p

    def pro_rec(n, t=tilt):
        r = RecordingPen(); m.draw(n, TransformPen(r, t)); return r

    # Zeichen (nicht Marken) um die halbe x-Höhe neigen, damit die
    # Seitenränder in der Kursiven gleich bleiben (Marken setzt der Anker).
    tilt_mid = (1, 0, skew, 1, -skew * 250, 0)

    def anchor(n, name):
        return m.anchor(n, name)

    def band_for(kind, ay):
        if kind == "top": return (ay - 140, ay + 10)
        return (-10, 120)

    def base_point(sbase, pbase, kind, ay_default):
        """Ankerpunkt (x, y) am Serif-Buchstaben."""
        aname = {"top": "top", "bottom": "bottom", "ogonek": "ogonek"}[kind]
        pa = anchor(pbase, aname) if pbase else None
        ay = pa[1] if pa else ay_default
        y0, y1 = band_for(kind, ay)
        sb = _band(_path_from_rec(glyphs[sbase]), y0, y1)
        pb = _band(pro_path(pbase), y0, y1) if pbase else None
        if kind == "ogonek":
            off = (pa[0] - pb[1]) if (pa and pb) else -40
            return sb[1] + off, 0
        off = (pa[0] - (pb[0] + pb[1]) / 2) if (pa and pb) else 0
        # Versatz der Pro (aufrecht) in der Kursiven mitneigen
        return (sb[0] + sb[1]) / 2 + off, ay

    def place(rec_mark, mpt, bpt, tilted):
        mx, my = mpt
        if tilted: mx = mx + skew * my
        r = RecordingPen()
        rec_mark.replay(TransformPen(r, (1, 0, 0, 1, bpt[0] - mx, bpt[1] - my)))
        return r

    names = {}
    made = 0
    ranges = list(range(0xC0, 0x180)) + [0x218, 0x219, 0x21A, 0x21B]
    for u in ranges:
        ch = chr(u)
        if u in cmap or u in new or ch in SKIP: continue
        d = unicodedata.normalize("NFD", ch)
        if len(d) != 2: continue
        bch, mk = d[0], ord(d[1])
        if ord(bch) not in cmap: continue
        upper = bch.isupper()
        if mk in TOPMARKS:
            kind = "top"
            sbase = {"i": "dotlessi", "j": "uni0237"}.get(bch, cmap[ord(bch)])
        elif mk in BOTMARKS:
            kind = "bottom"; sbase = cmap[ord(bch)]
            if mk == 0x327 and ch in COMMA_BELOW: mk = 0x326
        elif mk == OGONEK:
            kind = "ogonek"; sbase = cmap[ord(bch)]
        else:
            continue
        pbase = m.cmap.get(ord(bch))
        if bch == "i" and kind == "top": pbase = m.cmap.get(0x131)
        if mk == 0x307:
            # Punkt der Serif (wie i und das Trema): nicht neigen, schon kursiv.
            mrec = glyphs["uni0307"]
            bx, _ = base_point(sbase, pbase, "top", 700 if upper else 500)
            bpt = (bx + (skew * 180 if upper else 0), 680 if upper else 500)
            mpt = (markanchor[0], markanchor[1])
            mark = place(mrec, mpt, bpt, False)
        else:
            mname = m.cmap.get(mk)
            if mname is None: continue
            if upper and kind == "top" and (mname + ".case") in m.gs: mname += ".case"
            aname = "_" + kind
            ma = anchor(mname, aname)
            if ma is None: continue
            bpt = base_point(sbase, pbase, kind, 700 if upper else 500)
            mark = place(pro_rec(mname), ma, bpt, True)
        g = names.get(u) or ("uni%04X" % u)
        glyphs[g] = merge(glyphs[sbase], mark); adv[g] = adv[sbase]
        new[u] = g; made += 1

    # Zeichen aus der Pro
    for ch in SIGNS:
        u = ord(ch)
        if u in cmap or u in new or u not in m.cmap: continue
        pn = m.cmap[u]; g = "uni%04X" % u
        glyphs[g] = pro_rec(pn, tilt_mid); adv[g] = m.glyph(pn).width
        new[u] = g; made += 1

    # ẞ: Pro-Form, Kopf links und Fuss mit den Serifen des Serif-B
    if 0x1E9E in m.cmap and 0x1E9E not in cmap:
        reg = TTFont(os.path.join(SRC, "TitilliumProSerif-Regular.otf")).getGlyphSet()
        pn = m.cmap[0x1E9E]; pp = pro_path(pn)
        bp = path_of(reg, "B")
        pl = _band(pp, 250, 450); bl = _band(bp, 250, 450)
        dx = pl[0] - bl[0]
        bp = path_of(reg, "B", (1, 0, 0, 1, dx, 0))
        stemR = pl[0] + 82
        foot = op(bp, rect(-200, -5, stemR + 45, 61), pathops.PathOp.INTERSECTION)
        head = op(bp, rect(-200, 639, pl[0] + 2, 705), pathops.PathOp.INTERSECTION)
        p = op(op(pp, foot, pathops.PathOp.UNION), head, pathops.PathOp.UNION)
        r = RecordingPen(); rec_of_path(p).replay(TransformPen(r, tilt_mid))
        lsb0 = bounds(r)[0]
        shift = (30 - lsb0) if lsb0 < 30 else 0  # Serif links nicht über den Rand
        r2 = RecordingPen(); r.replay(TransformPen(r2, (1, 0, 0, 1, shift, 0)))
        glyphs["uni1E9E"] = r2; adv["uni1E9E"] = m.glyph(pn).width + round(shift)
        new[0x1E9E] = "uni1E9E"; made += 1
    print("  Display-Ausbau:", made, "Zeichen")


MIN_GAP = 40  # kleinster Tintenabstand nach dem Kerning (Serif-Platte 45)


def _profile(rec):
    """Tinte je Höhenband von 25 Einheiten: {band: (xmin, xmax)}."""
    p = _path_from_rec(rec); out = {}
    b = bounds(rec)
    if not b: return out
    for y in range(int(b[1]) // 25 * 25 - 25, int(b[3]) + 25, 25):
        r = _band(p, y, y + 25)
        if r: out[y] = r
    return out


def kern_fea(pro, italic, cmap, glyphs, adv):
    """Kerning der Pro als fea, nur schliessende Paare (siehe oben).
    Kollisionswache: die Pro kennt die Serifen nicht (L-Fuss unter T). Ein
    Wert wird so weit zurückgenommen, dass in jedem gemeinsamen Höhenband
    mindestens MIN_GAP Einheiten Luft bleiben; was dann über −10 liegt, fällt."""
    import sys
    sys.path.insert(0, HERE)
    from pro_quelle import Master
    ufo = "Titillium Sans Pro-Regular Italic.ufo" if italic else "Titillium Sans Pro-Regular.ufo"
    m = Master(os.path.join(pro, "Sans", "UFO", ufo))
    rev = {}
    for u, n in m.cmap.items():
        rev.setdefault(n, u)
    pairs = {}
    for (a, b), v in m.flat_kerning().items():
        ua, ub = rev.get(a), rev.get(b)
        if ua is None or ub is None or ua not in cmap or ub not in cmap: continue
        if v > -10: continue
        pairs[(cmap[ua], cmap[ub])] = int(round(v))
    prof = {}
    def pf(g):
        if g not in prof: prof[g] = _profile(glyphs[g])
        return prof[g]
    clamped = 0
    for (a, b), v in list(pairs.items()):
        pa, pb = pf(a), pf(b)
        gaps = [adv[a] - pa[y][1] + pb[y][0] for y in pa if y in pb]
        if not gaps: continue
        room = min(gaps) - MIN_GAP          # so viel darf zusammengerückt werden
        if -v > room:
            clamped += 1
            v = -max(0, int(room))
            if v > -10: del pairs[(a, b)]; continue
            pairs[(a, b)] = v
    print("  Kollisionswache:", clamped, "Paare zurückgenommen")
    lines = [f"  pos {a} {b} {v};" for (a, b), v in sorted(pairs.items())]
    print("  Kerning:", len(lines), "Paare")
    return "feature kern {\n" + "\n".join(lines) + "\n} kern;"


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

    # ---- Display-Ausbau (Fassung 0.2, Entscheid des Inhabers 26. 11. 2026) ----
    if PRO:
        display_ausbau(PRO, italic, skew, gs, glyphs, adv, cmap, new, markanchor)

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

    fam = "Goetheanum Serif Beta"
    sub = "Italic" if italic else "Regular"
    ps = f"GoetheanumSerifBeta-{sub}"
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
                     "Erweiterung 2026 Goetheanum.",
        "familyName": fam, "styleName": sub,
        "uniqueFontIdentifier": f"{VERSION};GOET;{ps}",
        "fullName": f"{fam} {sub}", "psName": ps,
        "version": f"Version {VERSION} Beta",
        "description": "BETA, Ergänzung zur Goetheanum Schrift für Titel und grosse Grade, nicht im Paket. "
                       "Aus Titillium Pro Serif version_00 (Chialab, OFL), ergänzt um Trema, ß, einstöckiges a (ss01)"
                       + ("; Akzente, Zeichen und Kerning aus Titillium Sans Pro (Chialab, OFL)." if PRO else "."),
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupPost(italicAngle=-16 if italic else 0, isFixedPitch=0, underlinePosition=-100, underlineThickness=45)
    fb.font["head"].created = fb.font["head"].modified = STAMP
    fb.font["head"].macStyle = 0x02 if italic else 0
    fb.font["head"].fontRevision = float(VERSION)
    if not PRO:
        # Fassung 0.1: GPOS (Punkt-Positionierung der Quelle) übernehmen, GSUB neu aus fea
        fb.font["GPOS"] = src["GPOS"]
        fb.font["GDEF"] = src["GDEF"]
        addOpenTypeFeaturesFromString(fb.font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n" + "\n".join(feas),
                                      tables=["GSUB"])
    else:
        # Fassung 0.2: Punkt-Positionierung der Quelle als fea nachgebaut, dazu Kerning.
        bases = " ".join(f"pos base {b} <anchor {round(x)} {round(y)}> mark @TOP;" for b, (x, y) in sorted(anchors.items())
                         if b in neworder)
        feas.append(f"markClass [uni0307 uni0308] <anchor {round(markanchor[0])} {round(markanchor[1])}> @TOP;\n"
                    f"feature mark {{ {bases} }} mark;")
        feas.append(kern_fea(PRO, italic, cmap, glyphs, adv))
        addOpenTypeFeaturesFromString(fb.font, "languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n" + "\n".join(feas),
                                      tables=["GSUB", "GPOS", "GDEF"])
    os.makedirs(OUT, exist_ok=True)
    otf = os.path.join(OUT, f"{ps}.otf")
    fb.font.save(otf)
    f2 = TTFont(otf); f2.flavor = "woff2"; f2.save(os.path.join(OUT, f"{ps}.woff2"))
    print(otf, len(neworder), "Glyphen", len(cmap), "Zeichen")


def pack():
    """ZIP zum Download, bytegleich (feste Zeitstempel, feste Reihenfolge)."""
    import zipfile
    zp = os.path.join(OUT, "Goetheanum-Serif-Beta.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ("GoetheanumSerifBeta-Regular.otf", "GoetheanumSerifBeta-Italic.otf", "OFL.txt", "README.md"):
            zi = zipfile.ZipInfo("Goetheanum-Serif-Beta/" + n, date_time=(2026, 11, 25, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
            z.writestr(zi, open(os.path.join(OUT, n), "rb").read())
    print(zp)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        PRO = sys.argv[1]; VERSION = "0.2"
    for s in ("Regular", "RegularItalic"):
        build(s)
    pack()

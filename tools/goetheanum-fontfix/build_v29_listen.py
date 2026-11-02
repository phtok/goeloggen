#!/usr/bin/env python3
# Hausschrift v2.9, Fassung 2.91: Listenzeichen in Kreis und Quadrat
# (Etappe E3 aus docs/recherche_titillium-pro.md). Befund und Masse:
# docs/befunde/listenziffern-e3-2026-11-02.md.
#
# Aus sauberem Stand: liest Variable und die fünf statischen Schnitte v2.9 aus
# git (SOURCE_REV), nie von der Platte; ein zweiter Lauf schreibt dieselben
# Dateien. Schreibt dieselben Dateinamen v2.9 (Fonts/, Variable/, Webfonts/),
# intern Version 2.91.
#
#  ss03 Kreis, Kontur · ss04 Kreis, gefüllt · ss05 Quadrat, Kontur ·
#  ss06 Quadrat, gefüllt – wie die Stilsets der Titillium Sans Pro.
#  Je Stilset: A–Z und 0–9 als fertige Zeichen (36), dazu 10–99 aus
#  Bausteinen: erste Ziffer mit linker Hälfte, zweite Ziffer mit rechter
#  Hälfte (je 10, zusammen 20). Ein Paar zweier Ziffern, vor und nach dem
#  keine Ziffer steht, wird in DENSELBEN Kreis bzw. dasselbe Quadrat gesetzt
#  (Entscheid des Inhabers 2. 11. 2026: «Kreis muss Kreis sein; keine
#  Ellipse»); die Ziffern dafür gleichmässig kleiner, nie gestaucht. Drei und
#  mehr Ziffern bleiben einzeln. Die Regel steht im Stilset selbst (nicht in calt), damit sie nur
#  gilt, wenn das Stilset an ist.
#
#  Form: Kreis 860 Einheiten, Quadrat 800, Mitte auf halber Versalhöhe (345);
#  innen das Hauszeichen auf 0,66 verkleinert, im gleichen Gewicht. Kontur =
#  Strich des verkleinerten Zeichens (0,66 × Stamm des I), wächst mit dem
#  Gewicht. Gefüllt = Fläche mit ausgespartem Zeichen. W und M werden schmaler
#  gesetzt, bis sie Luft zum Rand haben (Q, J ebenso, falls nötig).
#  Gebaut wird einmal an den Mastern der Variable; die statischen Schnitte
#  bekommen die Instanz der Variable an ihrem Gewicht (deckungsgleich).
#
#  Unicode: ⓪ ①–⑳ ㉑–㊿ Ⓐ–Ⓩ (Kreis, Kontur), ⓿ ❶–❿ ⓫–⓴ (Kreis, gefüllt)
#  zeigen auf dieselben Glyphen. Quadrate und gefüllte Buchstaben stehen in
#  Unicode nur ausserhalb der BMP (🄰 🅐 🅰, teils Emoji) und bleiben Stilset.
#
# Aufruf:  python3 build_v29_listen.py
import os, sys, io, copy, subprocess, tempfile, math, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
import repair_variable_v28 as R
import build_v29_pro as B

REPO = B.REPO; ROOT = B.ROOT
SOURCE_REV = "6eaeafc"                 # main mit Hausschrift v2.9 (E2, #750)
VER_OLD, VER_NEW = "2.9", "2.91"
CUTS = {"Leise": 265, "Ruhig": 350, "Klar": 440, "Deutlich": 580, "Laut": 680}

S = 0.66            # Grösse des inneren Zeichens
D = 860             # Kreisdurchmesser
Q = 800             # Quadratseite (wirkt neben dem Kreis gleich gross)
CY = 345            # Mitte: halbe Versalhöhe
SB = 60             # Rand links und rechts
LUFT = 45           # Mindestabstand Zeichen – Innenkante der Kontur
LUECKE_PAAR = 36    # Abstand der beiden Ziffern im Kreis
OV = 8              # Überlappung der Hälften an der Naht (keine Haarlinie)
KAPPA = 0.5523
SETS = (("ss03", "Kreis, Kontur", "kreis", False),
        ("ss04", "Kreis, gefüllt", "kreis", True),
        ("ss05", "Quadrat, Kontur", "quadrat", False),
        ("ss06", "Quadrat, gefüllt", "quadrat", True))
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
NAMES = dict(zip(DIGITS, ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")))


# ---------- Quellen ----------
def git_font(rel):
    blob = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (SOURCE_REV, rel)],
                          capture_output=True, check=True).stdout
    tmp = tempfile.NamedTemporaryFile(suffix=".otf", delete=False); tmp.write(blob); tmp.close()
    return TTFont(tmp.name, recalcTimestamp=False)


# ---------- Geometrie (Konturen im Format von repair_variable_v28) ----------
def closed(start, segs):
    return [start, segs + [("lineTo", [start])]]

def circle(cx, cy, r):
    """Gegen den Uhrzeigersinn (= Aussenkontur der Hausschrift)."""
    k = r * KAPPA
    return closed((cx + r, cy), [
        ("curveTo", [(cx + r, cy + k), (cx + k, cy + r), (cx, cy + r)]),
        ("curveTo", [(cx - k, cy + r), (cx - r, cy + k), (cx - r, cy)]),
        ("curveTo", [(cx - r, cy - k), (cx - k, cy - r), (cx, cy - r)]),
        ("curveTo", [(cx + k, cy - r), (cx + r, cy - k), (cx + r, cy)])])

def square(cx, cy, h):
    return closed((cx + h, cy - h), [("lineTo", [(cx + h, cy + h)]), ("lineTo", [(cx - h, cy + h)]),
                                     ("lineTo", [(cx - h, cy - h)])])

def ring(form, cx, cy, h, f):
    """Kontur: aussen gegen, innen mit dem Uhrzeigersinn."""
    if form == "kreis": return [circle(cx, cy, h), R.reverse(circle(cx, cy, h - f))]
    return [square(cx, cy, h), R.reverse(square(cx, cy, h - f))]

def disc(form, cx, cy, h):
    return [circle(cx, cy, h) if form == "kreis" else square(cx, cy, h)]

def half_left(form, xc, seam, cy, h, f, filled):
    """Linke Hälfte bis zur Naht (seam), Bogen- bzw. Eckmitte bei xc.
    Kontur: ein C (offen zur Naht), gefüllt: eine Fläche."""
    k = h * KAPPA; S_ = seam + OV
    if form == "kreis":
        outer = [("lineTo", [(xc, cy + h)]),
                 ("curveTo", [(xc - k, cy + h), (xc - h, cy + k), (xc - h, cy)]),
                 ("curveTo", [(xc - h, cy - k), (xc - k, cy - h), (xc, cy - h)]),
                 ("lineTo", [(S_, cy - h)])]
    else:
        outer = [("lineTo", [(xc - h, cy + h)]), ("lineTo", [(xc - h, cy - h)]),
                 ("lineTo", [(S_, cy - h)])]
    if filled: return [closed((S_, cy + h), outer)]
    g = h - f; kg = g * KAPPA
    if form == "kreis":
        inner = [("lineTo", [(S_, cy - g)]), ("lineTo", [(xc, cy - g)]),
                 ("curveTo", [(xc - kg, cy - g), (xc - g, cy - kg), (xc - g, cy)]),
                 ("curveTo", [(xc - g, cy + kg), (xc - kg, cy + g), (xc, cy + g)]),
                 ("lineTo", [(S_, cy + g)])]
    else:
        inner = [("lineTo", [(S_, cy - g)]), ("lineTo", [(xc - g, cy - g)]),
                 ("lineTo", [(xc - g, cy + g)]), ("lineTo", [(S_, cy + g)])]
    return [closed((S_, cy + h), outer + inner)]

def mirror(cs, axis):
    return [R.reverse(c) for c in R.mapc(cs, lambda p: (2 * axis - p[0], p[1]))]

def pts(cs):
    """Punkte auf der Kontur (Kurven abgetastet), nicht die Kontrollpunkte."""
    out = []
    for c in cs:
        cur = c[0]
        for op, ps in c[1]:
            if op == "curveTo":
                p0, (p1, p2, p3) = cur, ps
                for k in range(1, 9):
                    t = k / 8; u = 1 - t
                    out.append(tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c_ + t**3 * d
                                     for a, b, c_, d in zip(p0, p1, p2, p3)))
            else: out.append(ps[-1])
            cur = ps[-1]
    return out
def tf(cs, sx, sy, dx, dy): return R.mapc(cs, lambda p: (p[0] * sx + dx, p[1] * sy + dy))


# ---------- Bau an den Mastern der Variable ----------
class Bau:
    def __init__(s, src):
        s.src = src; n = src.n
        s.stem = [B.stem(src, i) for i in range(n)]
        s.f = [S * st for st in s.stem]                               # Strich der Kontur
        s.top_l = [B.ink(src.out(src.cmap[ord("H")])[i])[3] for i in range(n)]
        s.top_d = [B.ink(src.out(src.cmap[ord("4")])[i])[3] for i in range(n)]
        s.fits = {}

    def inner(s, ch, i, sc=S):
        """Hauszeichen verkleinert, Mitte des Versal- bzw. Ziffernbands auf CY."""
        g = s.src.cmap[ord(ch)]; cs = s.src.out(g)[i]
        if ch in "JQ":                       # Unterlänge: nach der Tinte mitteln
            _, y0, _, y1 = B.ink(cs); return tf(cs, sc, sc, 0, CY - sc * (y0 + y1) / 2)
        top = s.top_d[i] if ch in DIGITS else s.top_l[i]
        return tf(cs, sc, sc, 0, CY - sc * top / 2)

    def single(s, form, filled, ch):
        """Fertiges Zeichen. Schmaler (kx) bzw. kleiner (ku) nur, wo das Zeichen
        sonst an die Kontur stösst; ein Faktor für alle Gewichte (strengstes)."""
        h = D / 2 if form == "kreis" else Q / 2
        adv = int(2 * h + 2 * SB); cx = adv / 2
        inner = []
        for i in range(s.src.n):
            cs = s.inner(ch, i); x0, _, x1, _ = B.ink(cs)
            inner.append(R.mapc(cs, lambda p: (p[0] - (x0 + x1) / 2, p[1] - CY)))
        def ok(kx, ku, axis=None):
            for i, cs in enumerate(inner):
                lim = h - s.f[i] - LUFT; P = pts(tf(cs, kx * ku, ku, 0, 0))
                if form == "kreis":
                    if max(math.hypot(*p) for p in P) > lim: return False
                elif max(abs(p[a]) for p in P for a in ((0, 1) if axis is None else (axis,))) > lim:
                    return False
            return True
        kx = ku = 1.0
        hx = 0 if form == "quadrat" else None      # im Quadrat nur schmaler, wenn es seitlich stösst
        while not ok(kx, ku, hx) and kx > 0.80: kx = round(kx - 0.01, 2)
        while not ok(kx, ku) and ku > 0.70: ku = round(ku - 0.01, 2)
        if (kx, ku) != (1.0, 1.0): s.fits[(form, ch)] = (kx, ku)
        ms = []
        for i, cs in enumerate(inner):
            cs = tf(cs, kx * ku, ku, cx, CY)
            frame = disc(form, cx, CY, h) if filled else ring(form, cx, CY, h, s.f[i])
            ms.append(frame + ([R.reverse(c) for c in cs] if filled else cs))
        return ms, [adv] * s.src.n

    def pair_fit(s, form):
        """Grösse der Ziffern im Paar: zwei Ziffern passen in DENSELBEN Kreis
        bzw. dasselbe Quadrat wie ein Einzelzeichen (Kreis bleibt Kreis).
        Gleichmässig verkleinert, nie gestaucht; ein Wert für alle Paare."""
        h = D / 2 if form == "kreis" else Q / 2
        sc = S
        while sc > 0.3:
            ok = True
            for i in range(s.src.n):
                L = h - s.f[i] - LUFT
                for ch in DIGITS:
                    cs = s.inner(ch, i, sc); x0, _, x1, _ = B.ink(cs)
                    for first in (True, False):
                        for (x, y) in pts(cs):
                            dx = (x1 - x if first else x - x0) + LUECKE_PAAR / 2
                            dy = y - CY
                            if (math.hypot(dx, dy) if form == "kreis" else max(dx, abs(dy))) > L:
                                ok = False; break
                        if not ok: break
                    if not ok: break
                if not ok: break
            if ok: return round(sc, 3)
            sc -= 0.005
        raise SystemExit("Paar passt nicht")

    def pair_half(s, form, filled, ch, first, sc):
        """Hälfte des Kreises bzw. Quadrats mit einer Ziffer; Naht in der Mitte."""
        h = D / 2 if form == "kreis" else Q / 2
        ms = []
        for i in range(s.src.n):
            f = s.f[i]; cs = s.inner(ch, i, sc); x0, _, x1, _ = B.ink(cs)
            seam = SB + h
            if first:
                cs = R.mapc(cs, lambda p: (p[0] - x1 + seam - LUECKE_PAAR / 2, p[1]))
                frame = half_left(form, SB + h, seam, CY, h, f, filled)
            else:
                cs = R.mapc(cs, lambda p: (p[0] - x0 + LUECKE_PAAR / 2, p[1]))
                frame = mirror(half_left(form, SB + h, seam, CY, h, f, filled), seam)
                frame = R.mapc(frame, lambda p: (p[0] - seam, p[1]))
            ms.append(frame + ([R.reverse(c) for c in cs] if filled else cs))
        return ms, [SB + h] * s.src.n


def build_variable(src):
    """Neue Glyphen an den Mastern; gibt die Bauliste (Name, cp, Konturen, Vorschub) zurück."""
    bau = Bau(src); plan = []; names = {}
    def add(key, ms, advs, cp=None):
        name = src.add(cp, [B.rnd(m) for m in ms], [int(round(a)) for a in advs])
        names[key] = name; plan.append((key, name, cp, [B.rnd(m) for m in ms], advs))
        return name
    hws = {}
    for tag, _, form, filled in SETS:
        for ch in LETTERS + DIGITS:
            add((tag, ch), *bau.single(form, filled, ch))
        sc = hws.setdefault(form, bau.pair_fit(form))
        for ch in DIGITS:
            add((tag, ch, 1), *bau.pair_half(form, filled, ch, True, sc))
            add((tag, ch, 2), *bau.pair_half(form, filled, ch, False, sc))
    # Unicode: Einzelzeichen auf die Stilset-Glyphen, Paare als eigene Glyphen
    for k, cp in unicode_singles().items(): src.map(cp, names[k])
    for (tag, num), cp in unicode_pairs().items():
        a, b = "%02d" % num
        A = src.out(names[(tag, a, 1)]); Bm = src.out(names[(tag, b, 2)])
        wa = src.adv(names[(tag, a, 1)]); wb = src.adv(names[(tag, b, 2)])
        ms = [A[i] + B.move(Bm[i], wa[i], 0) for i in range(src.n)]
        add((tag, num), ms, [x + y for x, y in zip(wa, wb)], cp)
    return bau, names, plan, hws


def unicode_singles():
    m = {("ss03", "0"): 0x24EA, ("ss04", "0"): 0x24FF}
    for k in range(1, 10):
        m[("ss03", str(k))] = 0x2460 + k - 1
        m[("ss04", str(k))] = 0x2776 + k - 1
    for j, ch in enumerate(LETTERS): m[("ss03", ch)] = 0x24B6 + j
    return m

def unicode_pairs():
    m = {}
    for n in range(10, 21): m[("ss03", n)] = 0x2460 + n - 1
    for n in range(21, 36): m[("ss03", n)] = 0x3251 + n - 21
    for n in range(36, 51): m[("ss03", n)] = 0x32B1 + n - 36
    m[("ss04", 10)] = 0x277F
    for n in range(11, 21): m[("ss04", n)] = 0x24EB + n - 11
    return m


def build_static(ft, vsrc, plan, weight):
    """Instanz der Variable am Gewicht des Schnitts, Glyphe für Glyphe."""
    src = B.StatSrc(ft); v = (weight - 440) / 250 if weight < 440 else (weight - 440) / 285
    names = {}
    for key, vname, cp, ms, advs in plan:
        cs = B.rnd(vsrc.vf.outline(vname, v))
        adv = int(round(R.advances(vsrc.vf, vname)[0])) if len(set(advs)) == 1 else None
        assert adv is not None and adv == advs[0], key
        names[key] = src.add(cp, [cs], [adv])
    for k, cp in unicode_singles().items(): src.map(cp, names[k])
    return names


# ---------- GSUB ----------
def digit_alternates(ft):
    """Ziffern und ihre Formen (onum, tnum, pnum, lnum, zero …) → Ziffer."""
    cm = ft.getBestCmap(); out = {cm[ord(d)]: d for d in DIGITS}
    gsub = ft["GSUB"].table
    for _ in range(3):
        for fr in gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag not in ("onum", "tnum", "pnum", "lnum", "zero", "case"): continue
            for li in fr.Feature.LookupListIndex:
                L = gsub.LookupList.Lookup[li]
                for st in L.SubTable:
                    if L.LookupType == 7: st = st.ExtSubTable
                    for a, b_ in getattr(st, "mapping", {}).items():
                        if a in out and b_ not in out: out[b_] = out[a]
    return out


def fea_code(ft, names):
    cm = ft.getBestCmap(); alts = digit_alternates(ft)
    byd = collections.defaultdict(list)
    for g, d in alts.items(): byd[d].append(g)
    allz = " ".join(sorted(alts, key=ft.getGlyphID))
    out = ["languagesystem DFLT dflt;", "@ZIFF = [%s];" % allz]
    for tag, label, _, _ in SETS:
        for part, idx in (("erste", 1), ("zweite", 2)):
            out.append("lookup %s_%s {" % (tag, part))
            for d in DIGITS:
                out.append("  sub [%s] by %s;" % (" ".join(sorted(byd[d], key=ft.getGlyphID)), names[(tag, d, idx)]))
            out.append("} %s_%s;" % (tag, part))
        out.append("lookup %s_paar {" % tag)
        out.append("  ignore sub @ZIFF @ZIFF' @ZIFF';")
        out.append("  ignore sub @ZIFF' @ZIFF' @ZIFF;")
        out.append("  sub @ZIFF' lookup %s_erste @ZIFF' lookup %s_zweite;" % (tag, tag))
        out.append("} %s_paar;" % tag)
        out.append("lookup %s_einzeln {" % tag)
        for ch in LETTERS: out.append("  sub %s by %s;" % (cm[ord(ch)], names[(tag, ch)]))
        for d in DIGITS:
            out.append("  sub [%s] by %s;" % (" ".join(sorted(byd[d], key=ft.getGlyphID)), names[(tag, d)]))
        out.append("} %s_einzeln;" % tag)
        out.append("feature %s { featureNames { name \"%s\"; }; lookup %s_paar; lookup %s_einzeln; } %s;"
                   % (tag, label, tag, tag, tag))
    return "\n".join(out) + "\n"


def lookup_refs(L):
    """Alle SubstLookupRecord eines (Ketten-)Kontext-Lookups."""
    for st in L.SubTable:
        s = st.ExtSubTable if L.LookupType == 7 else st
        for r in getattr(s, "SubstLookupRecord", None) or []: yield r
        for rs in (getattr(s, "ChainSubRuleSet", None) or []) + (getattr(s, "ChainSubClassSet", None) or []) + \
                  (getattr(s, "SubRuleSet", None) or []) + (getattr(s, "SubClassSet", None) or []):
            if rs is None: continue
            for rule in (getattr(rs, "ChainSubRule", None) or getattr(rs, "ChainSubClassRule", None) or
                         getattr(rs, "SubRule", None) or getattr(rs, "SubClassRule", None) or []):
                for r in rule.SubstLookupRecord: yield r


def merge_features(ft, fea):
    """fea in einer Hilfsschrift übersetzen, Lookups und Features anhängen,
    in jedes LangSys eintragen; FeatureList danach nach Tag sortiert."""
    gsub = ft["GSUB"].table
    if any(fr.FeatureTag == "ss03" for fr in gsub.FeatureList.FeatureRecord): return
    tmp = TTFont(); tmp.setGlyphOrder(ft.getGlyphOrder()); tmp["name"] = copy.deepcopy(ft["name"])
    addOpenTypeFeaturesFromString(tmp, fea, tables=["GSUB"])
    t = tmp["GSUB"].table; off = len(gsub.LookupList.Lookup)
    for L in t.LookupList.Lookup:
        for r in lookup_refs(L): r.LookupListIndex += off
        gsub.LookupList.Lookup.append(L)
    gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
    have = {r.nameID for r in ft["name"].names}
    for r in tmp["name"].names:
        if r.nameID not in have: ft["name"].names.append(r)
    for fr in t.FeatureList.FeatureRecord:
        fr.Feature.LookupListIndex = [i + off for i in fr.Feature.LookupListIndex]
        gsub.FeatureList.FeatureRecord.append(fr)
        fi = len(gsub.FeatureList.FeatureRecord) - 1
        for sr in gsub.ScriptList.ScriptRecord:
            for ls in [sr.Script.DefaultLangSys] + [r.LangSys for r in sr.Script.LangSysRecord]:
                if ls is not None: ls.FeatureIndex.append(fi)
    # nach Tag sortieren (stabil), LangSys-Verweise umschreiben
    recs = gsub.FeatureList.FeatureRecord
    order = sorted(range(len(recs)), key=lambda i: recs[i].FeatureTag)
    new = {old: k for k, old in enumerate(order)}
    gsub.FeatureList.FeatureRecord = [recs[i] for i in order]
    gsub.FeatureList.FeatureCount = len(recs)
    for sr in gsub.ScriptList.ScriptRecord:
        for ls in [sr.Script.DefaultLangSys] + [r.LangSys for r in sr.Script.LangSysRecord]:
            if ls is None: continue
            ls.FeatureIndex = sorted(new[i] for i in ls.FeatureIndex); ls.FeatureCount = len(ls.FeatureIndex)


def bump(ft):
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):
            s = rec.toUnicode()
            if VER_NEW not in s: rec.string = s.replace(VER_OLD, VER_NEW, 1)
    ft["head"].fontRevision = float(VER_NEW)


def webfonts(path):
    """woff/woff2 ohne neuen Zeitstempel (sonst ist kein Lauf bitgleich)."""
    b = os.path.splitext(os.path.basename(path))[0]
    for flv in ("woff", "woff2"):
        f = TTFont(path, recalcTimestamp=False); f.flavor = flv
        f.save(os.path.join(ROOT, "Webfonts", flv, "%s.%s" % (b, flv)))


def main():
    rel = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf"
    ft = git_font(rel); vsrc = B.VarSrc(ft)
    bau, names, plan, hws = build_variable(vsrc)
    merge_features(ft, fea_code(ft, names)); bump(ft)
    out = os.path.join(REPO, rel); ft.save(out); webfonts(out)
    print("Variabel: +%d Glyphen, Ziffern im Paar %s, Strich %s" % (
        len(plan), hws, [round(x) for x in bau.f]))
    for k, v in sorted(bau.fits.items()):
        print("  schmaler/kleiner %s %s: kx %.2f, ku %.2f" % (k[0], k[1], v[0], v[1]))
    vf = TTFont(out); vsrc2 = B.VarSrc(vf)          # aus der geschriebenen Datei instanzieren
    for cut, w in CUTS.items():
        rel = "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-%s.otf" % cut
        st = git_font(rel); n = build_static(st, vsrc2, plan, w)
        merge_features(st, fea_code(st, n)); bump(st)
        out = os.path.join(REPO, rel); st.save(out); webfonts(out)
        print("  %-9s +%d Glyphen" % (cut, len(n)))
    print("v%s (intern %s) geschrieben." % (VER_OLD, VER_NEW))


if __name__ == "__main__":
    main()

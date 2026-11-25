#!/usr/bin/env python3
# Hausschrift v2.9, Fassung 2.93 (25. 11. 2026). Entscheide des Inhabers vom
# 25. 11.; Befund docs/befunde/konturrichtung-kapitaelchen-2026-11-25.md.
#
# Aus sauberem Stand: liest Variable, die fünf statischen Schnitte, Icons und
# Pfeile aus git (SOURCE_REV, Fassung 2.92), nie von der Platte; ein zweiter
# Lauf schreibt dieselben Dateien. Dateinamen bleiben v2.9, intern 2.93.
#
#  1 Konturrichtung. Jede Kontur, die eine Fläche umschliesst, läuft gegen
#    den Uhrzeigersinn, jede Punze mit ihm (konturrichtung.py entscheidet am
#    gerenderten Blatt). Falsch gedrehte Konturen werden umgekehrt – im
#    Variable Font nur, wo alle Master denselben Befund zeigen, und überall
#    nur, wo das gerenderte Blatt (Non-Zero) danach dieselbe Fläche hat.
#    Anlass: der obere Ring von ‰ (geerbt aus v1.4.43) läuft bei synthetischem
#    Fett zu.
#  2 Kapitälchen (smcp, c2sc) für die Gemeinen ohne eigene Form:
#    - Grundbuchstabe + Akzent: Kapitälchen des Grundbuchstabens; Akzente
#      oben vom Kapitälchen eines Spenders (à á â ã ā ă ż ä å ő č), gesetzt
#      wie dort zur Mitte; Akzente unten aus der Gemeinen selbst (ạ ḏ ḫ ḑ …),
#      unter die Mitte des Kapitälchens gestellt; Ogonek wie bei ą.
#    - ə ɛ ɨ ɲ ʉ und c2sc ẞ: aus der Versalie nach dem Modell der Kapitälchen
#      (build.py: Versalie bei Gewicht +110, auf 511/690 verkleinert, Laufweite
#      30); Mischfaktor je Master an den vorhandenen Paaren gemessen.
#    - π: Kapitälchen-Π aus Stamm und Balken der Kapitälchen H und T.
#    - zusammengesetzt: ĳ = i + j, ß = s + s (Duden: SS), ﬁ = f + i, ﬂ = f + l.
#    - gleiche Form: µ μ → Kapitälchen m, ȷ → j.
#    - ƒ bleibt (Währungszeichen Gulden; die Schrift hat kein Ƒ).
#    Die Versalien dazu (Ǎ … Ĳ Ə …, İ) bekommen c2sc. Kerning: das neue
#    Kapitälchen erbt die Klassen seines Grundbuchstabens.
#  3 Version 2.93 (name, head) in allen sieben Dateien.
#
# Aufruf:  python3 build_v293.py
import os, sys, unicodedata, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen
import pathops
import repair_variable_v28 as R
import sync_statics_v28 as SY
import build_v29_pro as B
import konturrichtung as K
import build_v29_listen as Lst

REPO = B.REPO; ROOT = B.ROOT
SOURCE_REV = "aa45e0a"                 # main mit Fassung 2.92 (#753 ff.)
VER_OLD, VER_NEW = ("2.92", "2.9"), "2.93"
CUTS = {"Leise": 265, "Ruhig": 350, "Klar": 440, "Deutlich": 580, "Laut": 680}
VAR = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf"
STAT = "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v2.9-%s.otf"
NEBEN = ["assets/fonts/goetheanum/Fonts/Goetheanum-Icons-v2.9.otf",
         "assets/fonts/goetheanum/Fonts/Goetheanum-Pfeile-v2.9.otf"]

# Kapitälchen-Modell (build.py, v2.4.1)
S_CAP, TRACK = 511 / 690.0, 30
# Akzent oben → (Spender, dessen Grundbuchstabe), beide als Kapitälchen
OBEN = {0x300: (0xE0, 0x61), 0x301: (0xE1, 0x61), 0x302: (0xE2, 0x61), 0x303: (0xE3, 0x61),
        0x304: (0x101, 0x61), 0x306: (0x103, 0x61), 0x307: (0x17C, 0x7A), 0x308: (0xE4, 0x61),
        0x30A: (0xE5, 0x61), 0x30B: (0x151, 0x6F), 0x30C: (0x10D, 0x63)}
UNTEN = {0x323, 0x331, 0x32E, 0x327, 0x326}
OGONEK = 0x328
NEU = "ǎǐǒǔǧǩǫǹȟȯȳḃḋḍḏḑḟḡḣḥḫḷḹḻḿṁṃṅṇṉṗṛṝṟṡṣṫṭṯṽẁẃẅẓẗạẹẽịọụỳỹ"
AUS_VERSAL = {0x0259: 0x018F, 0x025B: 0x0190, 0x0268: 0x0197, 0x0272: 0x019D, 0x0289: 0x0244}
PAARE = {0x0133: "ij", 0x00DF: "ss", 0xFB01: "fi", 0xFB02: "fl"}
GLEICH = {0x00B5: "m", 0x03BC: "m", 0x0237: "j"}
PI = 0x03C0
VERSAL_ZU = {0x0130: (0x69, 0x307)}         # İ → Kapitälchen i mit Punkt (nur c2sc)
ESZETT_VERSAL = 0x1E9E                       # c2sc ẞ → Kapitälchen-ẞ


# ---------- Quellen ----------
def git_font(rel):
    blob = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (SOURCE_REV, rel)],
                          capture_output=True, check=True).stdout
    tmp = tempfile.NamedTemporaryFile(suffix=".otf", delete=False); tmp.write(blob); tmp.close()
    return TTFont(tmp.name, recalcTimestamp=False)


def flaeche(cs):
    """Fläche des gerenderten Blatts (Non-Zero, Überlappungen aufgelöst)."""
    p = pathops.Path(fillType=pathops.FillType.WINDING); B.draw(p.getPen(), cs)
    p.simplify(); a = AreaPen(); p.draw(a); return abs(a.value)


def umgekehrt(cs, idx):
    return [R.reverse(c) if i in idx else c for i, c in enumerate(cs)]


# ---------- 1 Konturrichtung ----------
def richtung_variable(ft, cmap_name):
    vf = R.VF(ft); funde, verworfen = [], []
    for g in ft.getGlyphOrder():
        ms = vf.masters(g)
        je = [tuple(K.richtung(m)) for m in ms]
        if not any(je): continue
        neu = [umgekehrt(m, je[0]) for m in ms]
        if len(set(je)) != 1 or any(abs(flaeche(a) - flaeche(b)) > 1 for a, b in zip(ms, neu)):
            verworfen.append((g, je)); continue
        R.write_glyph(vf, g, neu); funde.append((g, je[0]))
    return funde, verworfen


def richtung_statisch(ft):
    td = ft["CFF "].cff.topDictIndex[0]
    fds = td.FDArray if hasattr(td, "FDArray") else None
    gs = ft.getGlyphSet(); funde, verworfen = [], []
    for g in ft.getGlyphOrder():
        p = RecordingPen(); gs[g].draw(p); cs = R.contours(p.value)
        bad = K.richtung(cs)
        if not bad: continue
        neu = umgekehrt(cs, bad)
        if abs(flaeche(cs) - flaeche(neu)) > 1:
            verworfen.append((g, bad)); continue
        SY.draw_into(ft, td, fds, g, lambda pen, neu=neu: B.draw(pen, neu), ft["hmtx"][g][0])
        funde.append((g, bad))
    return funde, verworfen


# ---------- 2 Kapitälchen (Variable, je Master) ----------
def gsub_map(ft, tag):
    """Die (eine) SingleSubst-Tabelle eines Features."""
    gsub = ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != tag: continue
        for li in fr.Feature.LookupListIndex:
            L = gsub.LookupList.Lookup[li]
            for st in L.SubTable:
                t = L.LookupType
                if t == 7: t = st.ExtensionLookupType; st = st.ExtSubTable
                if t == 1: return st.mapping
    raise KeyError(tag)


def cx(cs):
    b = B.ink(cs); return (b[0] + b[2]) / 2


class Kap:
    def __init__(s, vsrc):
        s.v = vsrc; s.vf = vsrc.vf; s.ft = vsrc.ft; s.cm = vsrc.cmap
        s.smcp = gsub_map(s.ft, "smcp"); s.c2sc = gsub_map(s.ft, "c2sc")
        s.t = R.measure_t(s.vf); s.tk = s.fit_t()

    def sc(s, cp): return s.smcp[s.cm[cp]]
    def M(s, g): return s.vf.masters(g)
    def A(s, g): return R.advances(s.vf, g)

    def fit_t(s):
        """Mischfaktor der Versalie je Master, aus der das Kapitälchen entsteht
        (Gewicht +110): kleinste Quadrate über H N O E S."""
        out = []
        for i in range(len(s.vf.locs)):
            num = den = 0.0
            for ch in "HNOES":
                ms = s.M(s.cm[ord(ch)]); scm = s.M(s.sc(ord(ch.lower())))
                a, b = R.flat(ms[0]), R.flat(ms[-1]); x = R.flat(scm[i])
                for k, (p, q, r) in enumerate(zip(a, b, x)):
                    sh = TRACK / 2 if k % 2 == 0 else 0
                    y = (r - sh) / S_CAP
                    num += (q - p) * (y - p); den += (q - p) ** 2
            out.append(num / den)
        return out

    def aus_versal(s, cap):
        ms = s.M(s.cm[cap]); adv = s.A(s.cm[cap])
        a0, a1 = ms[0], ms[-1]
        out, advs = [], []
        for t in s.tk:
            m = R.mix(a0, a1, t)
            out.append(R.mapc(m, lambda p: (p[0] * S_CAP + TRACK / 2, p[1] * S_CAP)))
            advs.append((adv[0] + t * (adv[-1] - adv[0])) * S_CAP + TRACK)
        return out, advs

    def fehler_modell(s):
        """Abweichung des Modells an vorhandenen Kapitälchen (Kontrolle)."""
        err = 0
        for ch in "ADKRZ":
            ms, _ = s.aus_versal(ord(ch)); ist = s.M(s.sc(ord(ch.lower())))
            for m, x in zip(ms, ist):
                err = max(err, max(abs(p - q) for p, q in zip(R.flat(m), R.flat(x))))
        return err

    def oben(s, base_ms, mark):
        """Akzent oben vom Kapitälchen-Spender, zur Mitte wie dort."""
        don, dbase = OBEN[mark]
        dm, dbm = s.M(s.sc(don)), s.M(s.sc(dbase))
        di = s.vf.locs.index(0.0)
        top = max(R.bbox(c)[3] for c in dbm[di])
        idx = [i for i, c in enumerate(dm[di]) if R.bbox(c)[1] > top - 60]
        assert idx and len(dm[di]) - len(idx) == len(dbm[di]), hex(don)
        out = []
        for Bm, D, DB in zip(base_ms, dm, dbm):
            dx = cx(Bm) - cx(DB)
            out.append(R.mapc([D[i] for i in idx], lambda p, dx=dx: (p[0] + dx, p[1])))
        return out

    def unten(s, cp, base_ms):
        """Akzent(e) unten aus der Gemeinen selbst; waagrecht so zur Mitte des
        Kapitälchens wie in der Versalie der Schrift (Ḷ: unter dem Stamm),
        auf Kapitälchengrösse verkleinert; ohne Versalie unter die Mitte."""
        low = s.M(s.cm[cp]); lb = s.M(s.cm[B.nfd(cp)[0]])
        di = s.vf.locs.index(0.0)
        def unter(g, gb):
            return [i for i, c in enumerate(g[di]) if R.bbox(c)[3] < 30
                    and not any(R.bbox(c) == R.bbox(d) for d in gb[di])]
        idx = unter(low, lb); assert idx, chr(cp)
        up = ord(chr(cp).upper()); ab = ord(chr(B.nfd(cp)[0]).upper())
        if up != cp and up in s.cm:
            cap, cb = s.M(s.cm[up]), s.M(s.cm[ab]); ci = unter(cap, cb)
            assert len(ci) == len(idx), chr(cp)
            off = [cx([C[i] for i in ci]) - cx(CB) for C, CB in zip(cap, cb)]
        else:
            off = [0] * len(low)
        out = []
        for Bm, L, o in zip(base_ms, low, off):
            mk = [L[i] for i in idx]; dx = cx(Bm) + o * S_CAP - cx(mk)
            out.append(R.mapc(mk, lambda p, dx=dx: (p[0] + dx, p[1])))
        return out

    def akzentform(s, cp):
        d = B.nfd(cp); base, marks = d[0], d[1:]
        bm = s.M(s.sc(base)); adv = s.A(s.sc(base))
        if OGONEK in marks:
            return R.repair_ogonek(s.vf, s.t, s.sc(base), s.cm[cp], s.cm[base]), adv
        teile = [list(m) for m in bm]
        if any(m in UNTEN for m in marks):
            for k, u in enumerate(s.unten(cp, bm)): teile[k] += u
        for m in marks:
            if m in UNTEN: continue
            for k, o in enumerate(s.oben(bm, m)): teile[k] += o
        return teile, adv

    def paar(s, chars):
        g1, g2 = s.sc(ord(chars[0])), s.sc(ord(chars[1]))
        m1, m2, a1, a2 = s.M(g1), s.M(g2), s.A(g1), s.A(g2)
        ms = [x + R.mapc(y, lambda p, d=d: (p[0] + d, p[1])) for x, y, d in zip(m1, m2, a1)]
        return ms, [x + y for x, y in zip(a1, a2)]

    def pi(s):
        """Kapitälchen-Π: zwei Stämme (H) und der Balken (T), eine Kontur."""
        H, T = s.M(s.sc(ord("h"))), s.M(s.sc(ord("t")))
        adv = s.A(s.sc(ord("h")))
        out = []
        for h, t in zip(H, T):
            x0, y0, x1, y1 = B.ink(h)
            ys = sorted(p[1] for c in h for p in R.points(c))
            st = s.stamm(h)
            tb = s.balken(t)
            pts = [(x0, 0), (x0 + st, 0), (x0 + st, y1 - tb), (x1 - st, y1 - tb), (x1 - st, 0),
                   (x1, 0), (x1, y1), (x0, y1)]
            out.append([[pts[0], [("lineTo", [p]) for p in pts[1:]] + [("lineTo", [pts[0]])]]])
        return out, adv

    @staticmethod
    def stamm(cs):
        """Breite des linken Stamms (an halber Höhe gemessen)."""
        x0, y0, x1, y1 = B.ink(cs); y = (y0 + y1) * 0.3
        xs = sorted(x for x in K_schnitt(cs, y))
        return xs[1] - xs[0]

    @staticmethod
    def balken(cs):
        x0, y0, x1, y1 = B.ink(cs); x = x0 + (x1 - x0) * 0.1
        ys = sorted(K_schnitt(cs, x, senkrecht=True))
        return ys[-1] - ys[-2]


def K_schnitt(cs, w, senkrecht=False):
    """Schnittpunkte der Konturen mit y = w (bzw. x = w)."""
    out = []
    for c in cs:
        P = K.polygon(c, 24)
        for (x1, y1), (x2, y2) in zip(P, P[1:] + P[:1]):
            if senkrecht: x1, y1, x2, y2 = y1, x1, y2, x2
            if (y1 - w) * (y2 - w) < 0:
                out.append(x1 + (w - y1) * (x2 - x1) / (y2 - y1))
    return out


def plan_kapitaelchen(kap):
    """Liste (Schlüssel, Master, Vorschübe, [smcp-Quellen], [c2sc-Quellen])."""
    cm = kap.cm; plan = []
    def up(cp):
        u = chr(cp).upper()
        return [ord(u)] if len(u) == 1 and ord(u) in cm and ord(u) != cp else []
    for ch in NEU:
        cp = ord(ch); ms, adv = kap.akzentform(cp)
        plan.append((ch, ms, adv, [cp], up(cp)))
    for low, cap in AUS_VERSAL.items():
        ms, adv = kap.aus_versal(cap); plan.append((chr(low), ms, adv, [low], [cap]))
    ms, adv = kap.aus_versal(ESZETT_VERSAL); plan.append(("ẞ", ms, adv, [], [ESZETT_VERSAL]))
    for cp, chars in PAARE.items():
        ms, adv = kap.paar(chars)
        plan.append((chr(cp), ms, adv, [cp], [0x0132] if cp == 0x0133 else []))
    ms, adv = kap.pi(); plan.append(("π", ms, adv, [PI], []))
    for cap, (base, mark) in VERSAL_ZU.items():
        bm = kap.M(kap.sc(base)); adv = kap.A(kap.sc(base))
        ms = [list(m) + o for m, o in zip(bm, kap.oben(bm, mark))]
        plan.append((chr(cap), ms, adv, [], [cap]))
    return plan


def kern_erben(ft, erbe):
    """Neue Glyphe in die Kerning-Klassen ihres Vorbilds (links, rechts) setzen."""
    gpos = ft["GPOS"].table
    for L in gpos.LookupList.Lookup:
        for st in L.SubTable:
            t = L.LookupType
            if t == 9: t = st.ExtensionLookupType; st = st.ExtSubTable
            if t != 2 or st.Format != 2: continue
            cov = st.Coverage.glyphs; c1 = st.ClassDef1.classDefs; c2 = st.ClassDef2.classDefs
            for neu, (links, rechts) in erbe.items():
                if links in cov and neu not in cov:
                    cov.append(neu)
                    if links in c1: c1[neu] = c1[links]
                if rechts in c2: c2[neu] = c2[rechts]
            st.Coverage.glyphs = sorted(cov, key=ft.getGlyphID)


def eintragen(ft, namen, plan, erbe_von):
    """GSUB smcp/c2sc und Kerning für die neuen Glyphen."""
    cm = ft.getBestCmap(); sm, c2 = gsub_map(ft, "smcp"), gsub_map(ft, "c2sc")
    erbe = {}
    for (key, _, _, smq, c2q), name in zip(plan, namen):
        for cp in smq:
            assert cm[cp] not in sm, key; sm[cm[cp]] = name
        for cp in c2q:
            assert cm[cp] not in c2, key; c2[cm[cp]] = name
        a, b = erbe_von(key)
        if a: erbe[name] = (sm[cm[ord(a)]], sm[cm[ord(b)]])
    for cp, ch in GLEICH.items():
        assert sm.get(cm[cp], sm[cm[ord(ch)]]) == sm[cm[ord(ch)]]   # µ und μ: eine Glyphe
        sm[cm[cp]] = sm[cm[ord(ch)]]
    kern_erben(ft, erbe)


def erbe_von(key):
    """(linker, rechter) Nachbar fürs Kerning: Grundbuchstabe bzw. Teile."""
    cp = ord(key)
    if cp in PAARE: return PAARE[cp][0], PAARE[cp][1]
    if key in NEU or cp in VERSAL_ZU:
        b = chr(VERSAL_ZU[cp][0]) if cp in VERSAL_ZU else chr(B.nfd(cp)[0])
        return b, b
    return None, None


def bump(ft):
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):
            s_ = rec.toUnicode()
            if VER_NEW in s_: continue
            for old in VER_OLD:
                if old in s_: rec.string = s_.replace(old, VER_NEW, 1); break
    ft["head"].fontRevision = float(VER_NEW)


def build_static(ft, vsrc, plan, vnamen, weight):
    src = B.StatSrc(ft); v = (weight - 440) / 250 if weight < 440 else (weight - 440) / 285
    L = vsrc.vf.locs; namen = []
    for vname in vnamen:
        cs = B.rnd(vsrc.vf.outline(vname, v))
        a = R.advances(vsrc.vf, vname)
        k = next(k for k in range(len(L) - 1) if L[k] <= v <= L[k + 1])
        adv = int(round(a[k] + (a[k + 1] - a[k]) * (v - L[k]) / (L[k + 1] - L[k])))
        namen.append(src.add(None, [cs], [adv]))
    return namen


def bericht(label, ft, funde, verworfen):
    cm = {}
    for cp, g in ft.getBestCmap().items(): cm.setdefault(g, cp)
    z = lambda g: chr(cm[g]) if g in cm else g
    print("%s: %d Glyphen gedreht: %s" % (label, len(funde), " ".join(z(g) for g, _ in funde)))
    if verworfen: print("   belassen (Blatt würde sich ändern): %s" % " ".join(z(g) for g, _ in verworfen))


def main():
    ft = git_font(VAR)
    f, v = richtung_variable(ft, None); bericht("Variabel", ft, f, v)
    vsrc = B.VarSrc(ft); kap = Kap(vsrc)
    print("Kapitälchen-Modell: Mischfaktor je Master %s, Abweichung %.1f Einheiten"
          % ([round(x, 3) for x in kap.tk], kap.fehler_modell()))
    plan = plan_kapitaelchen(kap)
    vnamen = [vsrc.add(None, [B.rnd(m) for m in ms], [int(round(a)) for a in adv])
              for _, ms, adv, _, _ in plan]
    eintragen(ft, vnamen, plan, erbe_von); bump(ft)
    out = os.path.join(REPO, VAR); ft.save(out); Lst.webfonts(out)
    print("Variabel: +%d Kapitälchen (%s), smcp gleich: %s" % (
        len(plan), "".join(k for k, *_ in plan), "".join(chr(c) for c in GLEICH)))
    vf = TTFont(out); vsrc2 = B.VarSrc(vf)
    for cut, w in CUTS.items():
        rel = STAT % cut; st = git_font(rel)
        f, v = richtung_statisch(st); bericht("  " + cut, st, f, v)
        namen = build_static(st, vsrc2, plan, vnamen, w)
        eintragen(st, namen, plan, erbe_von); bump(st)
        out = os.path.join(REPO, rel); st.save(out); Lst.webfonts(out)
    for rel in NEBEN:
        st = git_font(rel); f, v = richtung_statisch(st)
        bericht("  " + os.path.basename(rel), st, f, v); bump(st)
        out = os.path.join(REPO, rel); st.save(out); Lst.webfonts(out)
    print("v2.9 (intern %s) geschrieben." % VER_NEW)


if __name__ == "__main__":
    main()

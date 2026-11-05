#!/usr/bin/env python3
# Hausschrift v2.9 (Kandidat): Abgleich mit Titillium Sans Pro (Chialab, OFL),
# Etappe E2 aus docs/recherche_titillium-pro.md. Befund und Zahlen:
# docs/befunde/schrift-v29-titillium-pro.md.
#
# Aus sauberem Stand: liest Variable und die fünf statischen Schnitte v2.8 aus
# git (SOURCE_REV), nie von der Platte – ein zweiter Lauf schreibt dieselben
# Dateien. Schreibt die v2.9-OTF (Fonts/, Variable/) und ihre Webfonts.
#
#  1 Zeichen. Neue Buchstaben werden aus den eigenen Teilen der Hausschrift
#    gesetzt (Grundbuchstabe + Akzent eines vorhandenen Zeichens), damit die
#    Upright-Formen bleiben; die Lage folgt der Hausschrift (Akzentmitte über
#    vorhandenen Zeichen wie â, ţ), sonst den Ankern der Pro, auf die Breite
#    des Hausbuchstabens umgerechnet. Aus der Pro geborgt werden nur Formen,
#    die es im Haus nicht gibt (Ə Ɛ ɛ Ɨ ɨ Ʉ ʉ Ɲ ɲ, Währungen, ℮, Kreise),
#    nach Stammbreite zwischen Thin/Regular/Bold gemischt und auf die
#    schmalere Hausproportion gestaucht (Stamm ausgeglichen).
#  2 Kombinierende Akzente (U+0300 …) als Nullbreiten-Zeichen; ccmp setzt
#    Grundbuchstabe + Akzent zum fertigen Zeichen zusammen (NFD-Text).
#  3 Kerning. Für Paare formgleicher Zeichen (Versalien, Ziffern, Zeichen,
#    Gemeine ausser a g y t l) gilt das Kerning der Pro (iKern), je Master
#    nach Stammbreite gemischt und mit dem Breitenverhältnis Haus/Pro der
#    Buchstaben skaliert (≈ 0,92: die Pro ist breiter gezeichnet, ihre Ränder
#    sind im selben Mass weiter). Werte auf ein Raster von 4 Einheiten gerundet.
#    Die Paare der Pro-Gruppen bleiben so Klassen (Dateigrösse). Alle übrigen
#    Paare behalten den Hauswert. Variable: Kerning je Master (GDEF-VarStore).
#  4 Version 2.9 (name, head), Dateinamen v2.9.
#
# Aufruf:  python3 -I build_v29_pro.py PFAD/titillium_pro   (Branch main)
import os, sys, subprocess, tempfile, unicodedata, statistics, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.otlLib import builder as otl
from fontTools.otlLib.optimize.gpos import compact_lookup
from fontTools.varLib.varStore import OnlineVarStoreBuilder
from fontTools.varLib.builder import buildVarDevTable
import repair_variable_v28 as R
import sync_statics_v28 as SY
from pro_quelle import Pro

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
SOURCE_REV = "97b9e3c"                     # main mit Hausschrift v2.8 (31. 10. 2026)
OLD, NEW = "2.8", "2.9"
CUTS = ("Leise", "Ruhig", "Klar", "Deutlich", "Laut")

# Pro-Zeichen, die NICHT kommen (Begründung im Befund)
SKIP = set(range(0x2190, 0x219A))                       # Pfeile: Hausform ist ‹Goetheanum Pfeile›
SKIP |= set(range(0x2460, 0x246A)) | {0x24EA, 0x24FF} | set(range(0x2776, 0x277F))   # Kreisziffern: E3
SKIP |= {0x1EAA, 0x1EAB, 0x1EB0, 0x1EC4, 0x1EC5, 0x1ED6, 0x1ED7}   # Vietnamesisch gestapelt, Rest fehlt
SKIP |= {0x013F, 0x0140, 0x0149}                        # Ŀ ŀ ŉ: von Unicode abgeraten
SKIP |= {0x0312, 0x0313, 0x0335, 0x0338}                # Akzente ohne zusammengesetztes Zeichen
SKIP |= {0x20AA}                                        # ₪: in der Pro falsch geformt (chialab/titillium_pro#12)
SKIP |= {0x2116}                                        # №: bewusst weggelassen, im deutschen Satz gilt «Nr.»
BORROW_LETTER = [0x018F, 0x0190, 0x025B, 0x0197, 0x0268, 0x0244, 0x0289, 0x019D, 0x0272,
                 0x212E]                                 # Ə Ɛ ɛ Ɨ ɨ Ʉ ʉ Ɲ ɲ ℮
BORROW_FIGURE = [0x20B9, 0x20BD, 0x20B4, 0x0E3F, 0x25CB, 0x25CF, 0x25CC]   # ₹ ₽ ₴ ฿ ○ ● ◌
ALIAS = {0x03BC: 0x00B5, 0x03A9: 0x2126, 0x0394: 0x2206, 0x2000: 0x2002, 0x2001: 0x2003}
LIGA_ALIAS = {0xFB01: "fi", 0xFB02: "fl"}
SPACES = {0x205F: 222}                                   # mittleres math. Leerzeichen, 4/18 Geviert
FRACTIONS = {0x2150: ("1", "7"), 0x2151: ("1", "9"), 0x2152: ("1", "10"), 0x2153: ("1", "3"),
             0x2154: ("2", "3"), 0x2155: ("1", "5"), 0x2156: ("2", "5"), 0x2157: ("3", "5"),
             0x2158: ("4", "5"), 0x2159: ("1", "6"), 0x215A: ("5", "6"), 0x215B: ("1", "8"),
             0x215C: ("3", "8"), 0x215D: ("5", "8"), 0x215E: ("7", "8"), 0x215F: ("1", ""),
             0x2189: ("0", "3")}
# Akzent-Spender: Name → (Versal-Zeichen, Versal-Grund, Gemein-Zeichen, Gemein-Grund)
DONORS = {0x300: (0xC0, 0x41, 0xE0, 0x61), 0x301: (0xC1, 0x41, 0xE1, 0x61),
          0x302: (0xC2, 0x41, 0xE2, 0x61), 0x303: (0xC3, 0x41, 0xE3, 0x61),
          0x304: (0x100, 0x41, 0x101, 0x61), 0x306: (0x102, 0x41, 0x103, 0x61),
          0x307: (0x17B, 0x5A, 0x17C, 0x7A), 0x308: (0xC4, 0x41, 0xE4, 0x61),
          0x30A: (0xC5, 0x41, 0xE5, 0x61), 0x30B: (0x150, 0x4F, 0x151, 0x6F),
          0x30C: (0x10C, 0x43, 0x10D, 0x63)}
BELOW_FROM = {0x323: 0x307, 0x331: 0x304, 0x32E: 0x306}   # unten aus dem Akzent oben
SIDE_DONORS = {0x327: (0xC7, 0x43, 0xE7, 0x63), 0x326: (0x218, 0x53, 0x219, 0x73),
               0x328: (0x118, 0x45, 0x119, 0x65)}
TOP_REF = (0x302, 0x308, 0x304, 0x307, 0x30C, 0x306, 0x30A, 0x303)   # symmetrisch: Mitte = Anker
BOTTOM_REF = (0x327, 0x326)
COMBINING = [0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307, 0x308, 0x30A, 0x30B, 0x30C,
             0x323, 0x326, 0x327, 0x328, 0x32E, 0x331]
GUILL = {0x00AB, 0x00BB, 0x2039, 0x203A}                  # Hausform nach G16, Entscheid 30. 10.


# ---------- Quellen ----------
def git_font(rel):
    blob = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (SOURCE_REV, rel)],
                          capture_output=True, check=True).stdout
    tmp = tempfile.NamedTemporaryFile(suffix=".otf", delete=False); tmp.write(blob); tmp.close()
    return TTFont(tmp.name, recalcTimestamp=False)


def rnd(cs): return R.mapc(cs, lambda p: (round(p[0]), round(p[1])))
def move(cs, dx, dy): return R.mapc(cs, lambda p: (p[0] + dx, p[1] + dy))


def ink(cs):
    b = BoundsPen(None); draw(b, cs); return b.bounds


def draw(pen, cs):
    for c in cs:
        pen.moveTo(c[0]); segs = c[1]
        if segs and segs[-1][0] == "lineTo" and tuple(segs[-1][1][-1]) == tuple(c[0]):
            segs = segs[:-1]
        for op, ps in segs: getattr(pen, op)(*ps)
        pen.closePath()


class VarSrc:
    """Variable Font: jede Grösse als Liste je Master (vf.locs)."""
    def __init__(s, ft):
        s.ft = ft; s.vf = R.VF(ft); s.n = len(s.vf.locs); s.cmap = ft.getBestCmap()
        s.weights = [R.unnorm(v) for v in s.vf.locs]
        s.new = {}

    def out(s, g): return s.vf.masters(g)
    def adv(s, g): return [round(a) for a in R.advances(s.vf, g)]

    def add(s, cp, masters, advs):
        ft = s.ft; td = ft["CFF2"].cff.topDictIndex[0]
        src = td.CharStrings[".notdef"]; src.decompile()
        cs = type(src)(program=list(src.program), private=src.private, globalSubrs=src.globalSubrs)
        name = "cid%05d" % (max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1)
        td.CharStrings.charStringsIndex.append(cs)
        td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex) - 1
        td.charset.append(name)
        if getattr(td, "FDSelect", None) is not None: td.FDSelect.append(0)
        ft.setGlyphOrder(list(td.charset))
        di = s.vf.locs.index(0.0)
        b = ink(masters[di])
        ft["hmtx"].metrics[name] = (advs[di], int(round(b[0])) if b else 0)
        R.set_advances(s.vf, name, advs)
        if masters[0]: R.write_glyph(s.vf, name, masters)
        else:
            c = td.CharStrings[name]; c.program = []; c.bytecode = None
        s.vf.fixed[name] = masters
        s.map(cp, name)
        return name

    def map(s, cp, name):
        if cp is None: return
        for t in s.ft["cmap"].tables:
            if t.isUnicode() and (cp <= 0xFFFF or t.format == 12): t.cmap[cp] = name
        s.cmap[cp] = name; s.vf.cmap[cp] = name


class StatSrc:
    """Statischer Schnitt: dieselbe Schnittstelle mit genau einem «Master»."""
    def __init__(s, ft):
        s.ft = ft; s.n = 1; s.cmap = ft.getBestCmap(); s.gs = ft.getGlyphSet()
        s.weights = [ft["OS/2"].usWeightClass]; s.cache = {}

    def out(s, g):
        if g not in s.cache:
            p = RecordingPen(); s.gs[g].draw(p); s.cache[g] = [rnd(R.contours(p.value))]
        return s.cache[g]

    def adv(s, g): return [s.ft["hmtx"][g][0]]

    def add(s, cp, masters, advs):
        st = s.ft; td = st["CFF "].cff.topDictIndex[0]
        src = td.CharStrings[".notdef"]; src.decompile()
        cs = type(src)(program=list(src.program), private=src.private, globalSubrs=src.globalSubrs)
        name = "cid%05d" % (max(int(n[3:]) for n in td.charset if n.startswith("cid")) + 1)
        td.CharStrings.charStringsIndex.append(cs)
        td.CharStrings.charStrings[name] = len(td.CharStrings.charStringsIndex) - 1
        td.charset.append(name)
        fds = td.FDArray if hasattr(td, "FDArray") else None
        if fds is not None: td.FDSelect.append(td.FDSelect[st.getGlyphID(st.getBestCmap()[0x48])])
        st["hmtx"].metrics[name] = (advs[0], 0)
        st.setGlyphOrder(list(td.charset))
        SY.draw_into(st, td, fds, name, lambda pen: draw(pen, masters[0]), advs[0])
        s.cache[name] = [rnd(masters[0])]; s.gs = st.getGlyphSet()
        s.map(cp, name)
        return name

    def map(s, cp, name):
        if cp is None: return
        for t in s.ft["cmap"].tables:
            if t.isUnicode() and (cp <= 0xFFFF or t.format == 12): t.cmap[cp] = name
        s.cmap[cp] = name


# ---------- Hausmasse ----------
def stem(src, i):
    x0, _, x1, _ = ink(src.out(src.cmap[ord("I")])[i]); return x1 - x0

def nfd(cp): return [ord(c) for c in unicodedata.normalize("NFD", chr(cp))]

def precomposed(src, base, mark):
    c = unicodedata.normalize("NFC", chr(base) + chr(mark))
    return ord(c) if len(c) == 1 and ord(c) in src.cmap and ord(c) not in src.new_cps else None

def split_marks(src, pre_g, base_g, i):
    """Konturen des Zeichens, die nicht im Grundbuchstaben stehen (= Akzent)."""
    pre, base = src.out(pre_g)[i], src.out(base_g)[i]
    bb = [R.bbox(c) for c in base]
    out = []
    for c in pre:
        b = R.bbox(c)
        if not any(max(abs(x - y) for x, y in zip(b, q)) <= 2 for q in bb): out.append(c)
    return out

def is_upper(cp): return unicodedata.category(chr(cp)) == "Lu"


class Placer:
    """Akzentlage je Master: Anker aus der Hausschrift, sonst aus der Pro."""
    def __init__(s, src, pro):
        s.src, s.pro = src, pro
        s.pw = [pro.weights(stem(src, i)) for i in range(src.n)]

    def pro_x(s, cp, name, i):
        pn = s.pro.cmap.get(cp)
        if pn is None: return None
        a = s.pro.anchor(pn, name, s.pw[i])
        if a is None: return None
        px0, _, px1, _ = s.pro.ink(pn, s.pw[i])
        hx0, _, hx1, _ = ink(s.src.out(s.src.cmap[cp])[i])
        return hx0 + (a[0] - px0) / (px1 - px0) * (hx1 - hx0)

    def anchor(s, cp, kind, i):
        refs = TOP_REF if kind == "top" else BOTTOM_REF
        for m in refs:
            if m == 0x30C and chr(cp) in "dltL": continue        # dort ist der Haken ein Apostroph
            pc = precomposed(s.src, cp, m)
            if pc is None: continue
            mk = split_marks(s.src, s.src.cmap[pc], s.src.cmap[cp], i)
            if mk:
                x0, _, x1, _ = ink(mk); return (x0 + x1) / 2
        x = s.pro_x(cp, kind, i)
        if x is not None: return x
        x0, _, x1, _ = ink(s.src.out(s.src.cmap[cp])[i]); return (x0 + x1) / 2

    def ogonek_x(s, cp, i):
        x = s.pro_x(cp, "ogonek", i)
        if x is not None: return x
        return ink(s.src.out(s.src.cmap[cp])[i])[2]


def mark_library(src, pl):
    """Akzente je Master, relativ zu (Anker, Oberkante bzw. Grundlinie)."""
    lib = collections.defaultdict(dict)                   # (mark, 'uc'|'lc') -> [Konturen je Master]
    for m, (uc, ub, lc, lb) in DONORS.items():
        for case, pc, bc in (("uc", uc, ub), ("lc", lc, lb)):
            per = []
            for i in range(src.n):
                mk = split_marks(src, src.cmap[pc], src.cmap[bc], i)
                top = ink(src.out(src.cmap[bc])[i])[3]
                per.append(move(mk, -pl.anchor(bc, "top", i), -top))
            lib[m][case] = per
    for m, up in BELOW_FROM.items():                        # unten = oben gespiegelt um die Lücke
        for case in ("uc", "lc"):
            per = []
            for mk in lib[up][case]:
                _, y0, _, y1 = ink(mk); per.append(move(mk, 0, -2 * y0 - (y1 - y0)))
            lib[m][case] = per
    for m, (uc, ub, lc, lb) in SIDE_DONORS.items():
        for case, pc, bc in (("uc", uc, ub), ("lc", lc, lb)):
            per = []
            for i in range(src.n):
                mk = [c for c in split_marks(src, src.cmap[pc], src.cmap[bc], i) if R.bbox(c)[3] < 40]
                ax = pl.ogonek_x(bc, i) if m == 0x328 else pl.anchor(bc, "bottom", i)
                per.append(move(mk, -ax, 0))
            if all(per): lib[m][case] = per
            elif m in SPACING:                          # Akzent mit dem Buchstaben verschmolzen:
                lib[m][case] = spacing_mark(src, pl, m, pc, bc)   # Einzelakzent ¸ ˛ setzen
    return lib


SPACING = {0x327: 0x00B8, 0x328: 0x02DB}


def spacing_mark(src, pl, m, pc, bc):
    """Cedille/Ogonek aus dem Einzelzeichen ¸ ˛: Höhe wie im Vorbild (Ç ç, Ę ę),
    Cedille mittig unter dem Anker, Ogonek mit dem rechten Überstand des Vorbilds."""
    g = src.cmap[SPACING[m]]; per = []
    for i in range(src.n):
        mk = src.out(g)[i]; x0, y0, x1, y1 = ink(mk)
        P = ink(src.out(src.cmap[pc])[i])
        dy = P[1] - y0
        if m == 0x328:
            ax = pl.ogonek_x(bc, i); dx = (P[2] - ax) - x1     # rechte Kante relativ zum Anker
        else:
            dx = -(x0 + x1) / 2
        per.append(move(mk, dx, dy))
    return per


# ---------- Neue Zeichen ----------
def composites(src, pro):
    """Codepoints der Pro, die aus Hausteilen gesetzt werden: (cp, Grund, [Akzente])."""
    out = []
    for cp in sorted(set(pro.cmap) - set(src.cmap) - SKIP):
        if unicodedata.category(chr(cp)) not in ("Lu", "Ll"): continue
        d = nfd(cp)
        if len(d) < 2: continue
        base, marks = d[0], d[1:]
        above = [m for m in marks if unicodedata.combining(chr(m)) == 230]
        if len(above) > 1: continue
        out.append((cp, base, marks))
    return out


def build_glyphs(src, pro, report):
    src.new_cps = set()
    pl = Placer(src, pro); lib = mark_library(src, pl)
    added = collections.OrderedDict()
    def add(cp, masters, advs, kind):
        name = src.add(cp, [rnd(m) for m in masters], [int(round(a)) for a in advs])
        src.new_cps.add(cp); added[cp] = kind; return name
    # Aliase
    for cp, to in ALIAS.items():
        if to in src.cmap and cp not in src.cmap: src.map(cp, src.cmap[to]); added[cp] = "Alias"
    for cp, liga in LIGA_ALIAS.items():
        g = R.gsub_liga(src.ft, [src.cmap[ord(c)] for c in liga], "liga")
        src.map(cp, g); added[cp] = "Alias"
    for cp, w in SPACES.items(): add(cp, [[]] * src.n, [w] * src.n, "Leerzeichen")
    # ȷ (Grundform für ǰ-Fälle) und ə
    j = src.cmap[ord("j")]; xh = [ink(src.out(src.cmap[ord("x")])[i])[3] for i in range(src.n)]
    add(0x0237, [[c for c in src.out(j)[i] if R.bbox(c)[1] < xh[i] * 0.9] for i in range(src.n)],
        src.adv(j), "aus j")
    e = src.cmap[ord("e")]; ms = []
    for i in range(src.n):
        x0, y0, x1, y1 = ink(src.out(e)[i])
        ms.append(R.mapc(src.out(e)[i], lambda p, a=x0 + x1, b=y0 + y1: (a - p[0], b - p[1])))
    add(0x0259, ms, src.adv(e), "e gedreht")
    # Ĳ ĳ
    for cp, a, b in ((0x0132, "I", "J"), (0x0133, "i", "j")):
        ga, gb = src.cmap[ord(a)], src.cmap[ord(b)]
        add(cp, [src.out(ga)[i] + move(src.out(gb)[i], src.adv(ga)[i], 0) for i in range(src.n)],
            [x + y for x, y in zip(src.adv(ga), src.adv(gb))], "zwei Buchstaben")
    # Grundbuchstabe + Akzent
    for cp, base, marks in composites(src, pro):
        if base not in src.cmap: report["fehlt"].append(cp); continue
        b_cp = base
        if any(unicodedata.combining(chr(m)) == 230 for m in marks):
            b_cp = {ord("i"): 0x0131, ord("j"): 0x0237}.get(base, base)
        case = "uc" if is_upper(base) else "lc"
        if any(case not in lib.get(m, {}) for m in marks):
            report["fehlt"].append(cp); continue
        g = src.cmap[b_cp]; ms = []
        for i in range(src.n):
            B = src.out(g)[i]; top = ink(B)[3]; cs = list(B)
            for m in marks:
                mk = lib[m][case][i]
                if unicodedata.combining(chr(m)) == 230:
                    cs += move(mk, pl.anchor(b_cp if b_cp in src.cmap else base, "top", i), top)
                elif m == 0x328:
                    cs += move(mk, pl.ogonek_x(base, i), 0)
                else:
                    cs += move(mk, pl.anchor(base, "bottom", i), 0)
            ms.append(cs)
        add(cp, ms, src.adv(g), "gesetzt")
    # Brüche aus Zähler, Bruchstrich, Nenner (wie frac sie setzt)
    numr = {d: R.gsub_single(src.ft, src.cmap[ord(d)], "frac") for d in "0123456789"}
    dnom = {}
    gsub = src.ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag != "frac": continue
        for li in fr.Feature.LookupListIndex:
            for st in gsub.LookupList.Lookup[li].SubTable:
                for r in getattr(st, "SubstLookupRecord", []):
                    mp = gsub.LookupList.Lookup[r.LookupListIndex].SubTable[0].mapping
                    for d, n in numr.items():
                        if n in mp: dnom[d] = mp[n]
    sl = src.cmap[0x2044]
    for cp, (num, den) in FRACTIONS.items():
        parts = [numr[d] for d in num] + [sl] + [dnom[d] for d in den]
        ms, advs = [], []
        for i in range(src.n):
            x = 0; cs = []
            for p in parts: cs += move(src.out(p)[i], x, 0); x += src.adv(p)[i]
            ms.append(cs); advs.append(x)
        add(cp, ms, advs, "Bruch")
    # Aus der Pro geborgt
    s_let, s_fig = ratios(src, pro, pl)
    capH = [ink(src.out(src.cmap[ord("H")])[i])[3] for i in range(src.n)]
    proH = pro.m[1].ink(pro.cmap[ord("H")])[3]
    for cp in BORROW_LETTER + BORROW_FIGURE:
        pn = pro.cmap[cp]
        if not pro.compatible(pn): report["fehlt"].append(cp); continue
        ms, advs = [], []
        for i in range(src.n):
            sx = (s_let if cp in BORROW_LETTER else s_fig)[i]
            w = pro.weights(stem(src, i) / sx)
            sy = capH[i] / proH if unicodedata.category(chr(cp)) in ("Lu", "Sc", "So") and cp not in (0x25CB, 0x25CF, 0x25CC, 0x212E) else 1.0
            cs = R.contours(pro.outline(pn, w))
            ms.append(R.mapc(cs, lambda p, sx=sx, sy=sy: (p[0] * sx, p[1] * sy)))
            advs.append(pro.width(pn, w) * sx)
        add(cp, ms, advs, "Pro")
    # Kombinierende Akzente: Nullbreite über/unter einem mittleren Gemeinen
    n_adv = src.adv(src.cmap[ord("n")]); xh_top = [ink(src.out(src.cmap[ord("x")])[i])[3] for i in range(src.n)]
    for m in COMBINING:
        if "lc" not in lib.get(m, {}): report["fehlt"].append(m); continue
        ms = []
        for i in range(src.n):
            mk = lib[m]["lc"][i]
            dy = xh_top[i] if unicodedata.combining(chr(m)) == 230 else 0
            ms.append(move(mk, -n_adv[i] / 2, dy))
        add(m, ms, [0] * src.n, "Akzent")
    return added


def ratios(src, pro, pl):
    """Breitenverhältnis Haus/Pro je Master: Buchstaben und Ziffern getrennt."""
    let = [c for c in "BCDEFHKLMNOPRSUVWXZbcdehmnopqsuvwxz"]
    fig = [c for c in "0235689"]
    out = []
    for group in (let, fig):
        r = []
        for i in range(src.n):
            v = []
            for ch in group:
                hx0, _, hx1, _ = ink(src.out(src.cmap[ord(ch)])[i])
                px0, _, px1, _ = pro.ink(pro.cmap[ord(ch)], pl.pw[i])
                v.append((hx1 - hx0) / (px1 - px0))
            r.append(statistics.median(v))
        out.append(r)
    return out


# ---------- ccmp: Grundbuchstabe + kombinierender Akzent → fertiges Zeichen ----------
def add_ccmp(ft, cmap):
    gsub = ft["GSUB"].table
    if any(fr.FeatureTag == "ccmp" for fr in gsub.FeatureList.FeatureRecord): return 0
    ligs = {}
    marks = set(COMBINING)
    for cp, g in cmap.items():
        d = nfd(cp)
        if len(d) < 2 or not all(m in marks and m in cmap for m in d[1:]) or d[0] not in cmap: continue
        ligs[tuple(cmap[x] for x in d)] = g
    st = otl.buildLigatureSubstSubtable(ligs)
    lk = otl.buildLookup([st])
    gsub.LookupList.Lookup.insert(0, lk); gsub.LookupList.LookupCount += 1
    for fr in gsub.FeatureList.FeatureRecord:
        fr.Feature.LookupListIndex = [i + 1 for i in fr.Feature.LookupListIndex]
    for L in gsub.LookupList.Lookup[1:]:
        for st_ in L.SubTable:
            s = st_.ExtSubTable if L.LookupType == 7 else st_
            for attr in ("SubstLookupRecord",):
                for r in getattr(s, attr, []) or []: r.LookupListIndex += 1
            for rs in (getattr(s, "ChainSubRuleSet", None) or []) + (getattr(s, "ChainSubClassSet", None) or []) + \
                      (getattr(s, "SubRuleSet", None) or []) + (getattr(s, "SubClassSet", None) or []):
                if rs is None: continue
                for rule in (getattr(rs, "ChainSubRule", None) or getattr(rs, "ChainSubClassRule", None) or
                             getattr(rs, "SubRule", None) or getattr(rs, "SubClassRule", None) or []):
                    for r in rule.SubstLookupRecord: r.LookupListIndex += 1
    fr = ot.FeatureRecord(); fr.FeatureTag = "ccmp"; fr.Feature = ot.Feature()
    fr.Feature.FeatureParams = None; fr.Feature.LookupListIndex = [0]; fr.Feature.LookupCount = 1
    gsub.FeatureList.FeatureRecord.append(fr); gsub.FeatureList.FeatureCount += 1
    fi = len(gsub.FeatureList.FeatureRecord) - 1
    for sr in gsub.ScriptList.ScriptRecord:
        for ls in [sr.Script.DefaultLangSys] + [r.LangSys for r in sr.Script.LangSysRecord]:
            if ls is None: continue
            ls.FeatureIndex.insert(0, fi); ls.FeatureCount = len(ls.FeatureIndex)
    return len(ligs)


# ---------- Kerning ----------
QUANT = int(os.environ.get("KERN_RASTER", "4"))   # Raster der übertragenen Werte (Einheiten)

def quant(v):
    """Auf das Raster runden: 4 Einheiten sind bei 16 px 0,06 px – unsichtbar,
    lassen aber gleiche Zeilen zu Klassen verschmelzen (Dateigrösse)."""
    return int(QUANT * round(v / QUANT))

def house_kerning(ft):
    out = {}; g = ft["GPOS"].table
    lis = sorted({i for fr in g.FeatureList.FeatureRecord if fr.FeatureTag == "kern"
                  for i in fr.Feature.LookupListIndex})
    for li in lis:
        L = g.LookupList.Lookup[li]
        for stb in L.SubTable:
            s = stb.ExtSubTable if L.LookupType == 9 else stb
            cov = s.Coverage.glyphs
            if s.Format == 1:
                for g1, ps in zip(cov, s.PairSet):
                    for r in ps.PairValueRecord:
                        out.setdefault((g1, r.SecondGlyph), r.Value1.XAdvance if r.Value1 else 0)
            else:
                c1 = s.ClassDef1.classDefs; inv2 = collections.defaultdict(list)
                for gg, c in s.ClassDef2.classDefs.items(): inv2[c].append(gg)
                for g1 in cov:
                    for k2, rec in enumerate(s.Class1Record[c1.get(g1, 0)].Class2Record):
                        v = rec.Value1.XAdvance if rec.Value1 else 0
                        if v:
                            for g2 in inv2.get(k2, []): out.setdefault((g1, g2), v)
    return out, lis


def same_form(src, pro, pl, cp):
    """Formgleich mit der Pro: nicht aus a g y t l, keine Hausform (Guillemets),
    Breite und Höhe im Verhältnis der Familie."""
    if cp in GUILL or cp not in pro.cmap or cp not in src.cmap: return False
    base = chr(nfd(cp)[0])
    if base in "agytl": return False
    if cp in src.new_cps and cp in BORROW_LETTER + BORROW_FIGURE: return True
    cat = unicodedata.category(chr(cp))
    if cat[0] not in "LNPS": return False
    i = 0
    b = ink(src.out(src.cmap[cp])[i]); p = pro.ink(pro.cmap[cp], pl.pw[i])
    if not b or not p: return False
    rw = (b[2] - b[0]) / max(p[2] - p[0], 1); rh = (b[3] - b[1]) / max(p[3] - p[1], 1)
    return 0.84 <= rw <= 1.08 and 0.93 <= rh <= 1.07


def kerning(src, pro, report):
    ft = src.ft
    hk, lis = house_kerning(ft)
    pl = Placer(src, pro)
    F = {cp for cp in src.cmap if same_form(src, pro, pl, cp)}
    Fg = {src.cmap[cp] for cp in F}
    s_let, _ = ratios(src, pro, pl)              # Breite Haus/Pro der Buchstaben je Master
    prev = {n: cp for cp, n in pro.cmap.items()}
    hpairs = {k: v for k, v in hk.items() if not (k[0] in Fg and k[1] in Fg)}
    fpairs = {}; big = []
    for (pa, pb) in pro.kerned_pairs():
        ca, cb = prev.get(pa), prev.get(pb)
        if ca not in F or cb not in F: continue
        if pro.cmap[ca] != pa or pro.cmap[cb] != pb: continue
        vals = [quant(pro.kern(pa, pb, pl.pw[i]) * s_let[i]) for i in range(src.n)]
        if not any(vals): continue
        if any(abs(v) > 160 for v in vals): big.append((chr(ca) + chr(cb), vals))
        fpairs[(src.cmap[ca], src.cmap[cb])] = tuple(vals)
    report["kern"] = dict(haus=len(hk), haus_behalten=len(hpairs),
                          formgleich_zeichen=len(F), pro_paare=len(fpairs),
                          gesamt=len(fpairs) + len(hpairs), gross=big[:20])
    report["kern_F"] = F
    write_kerning(src, fpairs, hpairs, lis)
    return fpairs, hpairs


def class_subtable(pairs, vr, go):
    """Glyphen mit gleicher Zeile bzw. Spalte zu Klassen zusammenfassen."""
    rows = collections.defaultdict(dict); cols = collections.defaultdict(dict)
    for (a, b_), v in pairs.items(): rows[a][b_] = v; cols[b_][a] = v
    lc = collections.defaultdict(list); rc = collections.defaultdict(list)
    for a, r in rows.items(): lc[tuple(sorted(r.items()))].append(a)
    for b_, c in cols.items(): rc[tuple(sorted(c.items()))].append(b_)
    rclass = {}
    for k, gl in rc.items():
        for g in gl: rclass[g] = tuple(sorted(gl))
    cp = {}
    for k, gl in lc.items():
        left = tuple(sorted(gl))
        for b_, v in rows[gl[0]].items():
            cp[(left, rclass[b_])] = (vr(v), None)
    return otl.buildPairPosClassesSubtable(cp, go)


def write_kerning(src, fpairs, hpairs, lis):
    """Zwei Lookups mit getrennten Paarmengen (ihre Werte addieren sich darum nie):
    formgleiche Paare aus der Pro als Klassen, die übrigen Hauspaare einzeln."""
    ft = src.ft; gp = ft["GPOS"].table
    variable = src.n > 1
    if variable:
        vf = src.vf
        b = OnlineVarStoreBuilder(["wght"])
        b.setSupports([{"wght": r} for r in vf.regions])
        idx = {}
        def vr(vals):
            if len(set(vals)) == 1:
                return otl.buildValue({"XAdvance": vals[0]})
            d = R.solve(vf, list(vals))
            if vals not in idx:
                idx[vals] = b.storeDeltas([int(round(x)) for x in d[1:]])
            v = otl.buildValue({"XAdvance": int(round(d[0]))})
            v.XAdvDevice = buildVarDevTable(idx[vals])
            return v
    else:
        def vr(vals): return otl.buildValue({"XAdvance": vals[0]})
    go = ft.getReverseGlyphMap()
    st = class_subtable(fpairs, vr, go)
    lk = otl.buildLookup([st])
    if variable:
        vs = b.finish()
        mapping = vs.optimize()
        for rec1 in st.Class1Record:
            for rec2 in rec1.Class2Record:
                d = getattr(rec2.Value1, "XAdvDevice", None)
                if d is not None:
                    old = (d.StartSize << 16) | d.EndSize
                    new = mapping[old]; d.StartSize, d.EndSize = new >> 16, new & 0xFFFF
        if "GDEF" not in ft:
            from fontTools.ttLib import newTable
            ft["GDEF"] = newTable("GDEF"); ft["GDEF"].table = ot.GDEF()
            ft["GDEF"].table.GlyphClassDef = ft["GDEF"].table.AttachList = None
            ft["GDEF"].table.LigCaretList = ft["GDEF"].table.MarkAttachClassDef = None
            ft["GDEF"].table.MarkGlyphSetsDef = None
        ft["GDEF"].table.Version = 0x00010003
        ft["GDEF"].table.VarStore = vs
    hl = otl.buildLookup([class_subtable(hpairs, lambda v: otl.buildValue({"XAdvance": v}), go)])
    # alte kern-Lookups ersetzen: erster = Pro, zweiter = Haus (Indizes bleiben)
    gp.LookupList.Lookup[lis[0]] = lk
    if len(lis) > 1:
        gp.LookupList.Lookup[lis[1]] = hl
        for i in lis[2:]: gp.LookupList.Lookup[i] = otl.buildLookup([otl.buildPairPosGlyphsSubtable({}, go)])
    else:
        gp.LookupList.Lookup.append(hl); gp.LookupList.LookupCount = len(gp.LookupList.Lookup)
        for fr in gp.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                fr.Feature.LookupListIndex.append(len(gp.LookupList.Lookup) - 1)
                fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    compact_lookup(ft, 5, lk); compact_lookup(ft, 5, hl)


def cpsp_add(ft, cps):
    gp = ft["GPOS"].table; cm = ft.getBestCmap()
    for fr in gp.FeatureList.FeatureRecord:
        if fr.FeatureTag != "cpsp": continue
        for li in fr.Feature.LookupListIndex:
            for s in gp.LookupList.Lookup[li].SubTable:
                if s.Format != 1: continue
                for cp in cps:
                    g = cm.get(cp)
                    if g and unicodedata.category(chr(cp)) == "Lu" and g not in s.Coverage.glyphs:
                        s.Coverage.glyphs.append(g)
                s.Coverage.glyphs.sort(key=ft.getGlyphID)


# ---------- Version ----------
def bump(ft):
    for rec in ft["name"].names:
        if rec.nameID in (3, 5):
            s = rec.toUnicode()
            if OLD in s: rec.string = s.replace(OLD, NEW)
    ft["head"].fontRevision = float(NEW)


def webfonts(path):
    b = os.path.splitext(os.path.basename(path))[0]
    for flv in ("woff", "woff2"):
        f = TTFont(path); f.flavor = flv
        f.save(os.path.join(ROOT, "Webfonts", flv, "%s.%s" % (b, flv)))


def fix_dieresis(src):
    """¨ (U+00A8): Vorschub schrumpfte über die Achse (791 in Flüstern … 514 in
    Schreien; AUDIT 29. 10., «geringfügig»). Die Pro wächst mit dem Gewicht
    (325 · 373 · 444). Neu symmetrisch: linker Rand + Tinte + gleicher Rand."""
    g = src.cmap[0x00A8]
    advs = [int(round(ink(src.out(g)[i])[0] + ink(src.out(g)[i])[2])) for i in range(src.n)]
    if isinstance(src, VarSrc): R.set_advances(src.vf, g, advs)
    else: src.ft["hmtx"][g] = (advs[0], src.ft["hmtx"][g][1])
    return advs


def process(ft, src, pro, label):
    report = collections.defaultdict(list)
    print("  %-9s ¨ Vorschub %s" % (label, fix_dieresis(src)))
    added = build_glyphs(src, pro, report)
    n_ccmp = add_ccmp(ft, src.cmap)
    cpsp_add(ft, list(added))
    kerning(src, pro, report)
    bump(ft)
    kinds = collections.Counter(added.values())
    print("  %-9s +%d Zeichen (%s), ccmp %d, fehlt %s" % (
        label, len(added), ", ".join("%d %s" % (n, k) for k, n in kinds.items()), n_ccmp,
        " ".join("U+%04X" % c for c in report["fehlt"]) or "–"))
    k = report["kern"]
    print("            Kerning: Haus %(haus)d Paare, davon behalten %(haus_behalten)d; "
          "Pro-Paare formgleich %(pro_paare)d (%(formgleich_zeichen)d Zeichen); gesamt %(gesamt)d" % k)
    if k["gross"]: print("            gross:", k["gross"])
    return added, report


def main():
    if len(sys.argv) < 2: sys.exit(__doc__ or "Aufruf: build_v29_pro.py PFAD/titillium_pro")
    pro = Pro(sys.argv[1])
    print("Pro-Stämme Thin/Regular/Bold:", pro.stems)
    rel = "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v%s.otf" % OLD
    ft = git_font(rel); src = VarSrc(ft)
    process(ft, src, pro, "Variabel")
    out = os.path.join(REPO, rel.replace("v" + OLD, "v" + NEW)); ft.save(out); webfonts(out)
    for cut in [c for c in CUTS if c in os.environ.get("NUR", " ".join(CUTS))]:
        rel = "assets/fonts/goetheanum/Fonts/Goetheanum-Schrift-v%s-%s.otf" % (OLD, cut)
        ft = git_font(rel); src = StatSrc(ft)
        process(ft, src, pro, cut)
        out = os.path.join(REPO, rel.replace("v" + OLD, "v" + NEW)); ft.save(out); webfonts(out)
    print("v%s geschrieben (Fonts/, Variable/, Webfonts/)." % NEW)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Baut das Versaleszett ẞ (U+1E9E) in die vier statischen Schnitte
# (Leise · Klar · Deutlich · Laut). Quelle sind die zwei von Philipp
# gezeichneten, punktkompatiblen Master in eszett-masters.json (leicht =
# Flüstern, Kapitälhöhe 700; fett = Schreien, Kapitälhöhe 680). Für jeden
# Schnitt wird der Master so interpoliert, dass Stamm (= I-Stamm des Schnitts)
# und Versalhöhe (= H des Schnitts) exakt getroffen werden; die Seitenränder
# folgen dem ‹B› des jeweiligen Schnitts (linke Gerade wie B-links, rechte
# Rundung wie B-rechts). Idempotent: ersetzt ein vorhandenes U+1E9E an Ort und
# Stelle, sonst neu angelegt. Webfonts (woff/woff2) werden mitgezogen.
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_specials as BS
from fontfix import _charstring
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
MASTERS = os.path.join(HERE, "eszett-masters.json")
CUTS = ["Leise", "Klar", "Deutlich", "Laut"]

def lerp(a, b, t): return a + (b - a) * t

class Esz:
    """Interpoliert die zwei Master und setzt sie maßgerecht in einen Schnitt."""
    def __init__(self, path):
        d = json.load(open(path)); self.F = d["F"]; self.S = d["S"]
    def interp(self, t):
        return [(ta, [(lerp(xa, xb, t), lerp(ya, yb, t))
                      for (xa, ya), (xb, yb) in zip(pa, pb)])
                for (ta, pa), (tb, pb) in zip(self.F, self.S)]
    @staticmethod
    def stem_of(sg):                 # Stammbreite: Innenkante (Knoten 7) − Außenkante
        minx = min(p[0] for _, ps in sg for p in ps)
        return sg[7][1][0][0] - minx
    @staticmethod
    def cap_of(sg): return max(p[1] for _, ps in sg for p in ps)
    def solve_t(self, stem_t, cap_t):
        def sf(t):
            sg = self.interp(t); return self.stem_of(sg) * cap_t / self.cap_of(sg)
        if sf(1.0) <= stem_t: return 1.0
        if sf(0.0) >= stem_t: return 0.0
        lo, hi = 0.0, 1.0
        for _ in range(60):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if sf(m) < stem_t else (lo, m)
        return (lo + hi) / 2
    def fit(self, stem_t, cap_t, lsb_t, rsb_t):
        t = self.solve_t(stem_t, cap_t); sg = self.interp(t)
        s = cap_t / self.cap_of(sg)
        sg = [(tp, [(x * s, y * s) for x, y in ps]) for tp, ps in sg]
        minx = min(p[0] for _, ps in sg for p in ps); dx = lsb_t - minx
        sg = [(tp, [(x + dx, y) for x, y in ps]) for tp, ps in sg]
        maxx = max(p[0] for _, ps in sg for p in ps)
        adv = round(maxx + rsb_t)
        return sg, adv, round(lsb_t)
    @staticmethod
    def recording(sg):
        rec = [("moveTo", (tuple(sg[0][1][0]),))]
        for tp, ps in sg:
            rec.append(("lineTo", (tuple(ps[1]),)) if tp == "L"
                       else ("curveTo", (tuple(ps[1]), tuple(ps[2]), tuple(ps[3]))))
        rec.append(("closePath", ()))
        return rec

def cut_metrics(ft):
    gs = ft.getGlyphSet(); cmap = ft.getBestCmap()
    def bb(ch):
        p = BoundsPen(gs); gs[cmap[ord(ch)]].draw(p); return p.bounds
    I = bb("I"); H = bb("H"); B = bb("B")
    Badv = ft["hmtx"][cmap[ord("B")]][0]
    return I[2] - I[0], H[3] - H[1], B[0], Badv - B[2]    # stem, cap, B-lsb, B-rsb

def replace_or_add(ft, rec, adv, lsb, uni=0x1E9E):
    cmap = ft.getBestCmap()
    if uni in cmap:                                       # ersetzen, Glyphenname behalten
        name = cmap[uni]
        cff = ft["CFF "].cff; td = cff[cff.fontNames[0]]
        idx = td.CharStrings.charStrings[name]
        td.CharStrings.charStringsIndex[idx] = _charstring(ft, rec, adv)
        ft["hmtx"].metrics[name] = (int(round(adv)), int(round(lsb)))
        return name + " (ersetzt)"
    return BS.add_glyph(ft, rec, adv, lsb, uni)

def main():
    esz = Esz(MASTERS)
    for cut in CUTS:
        p = os.path.join(FONTS, "Goetheanum-Schrift-v2.5-%s.otf" % cut)
        ft = TTFont(p)
        stem, cap, blsb, brsb = cut_metrics(ft)
        sg, adv, lsb = esz.fit(stem, cap, blsb, brsb)
        nm = replace_or_add(ft, esz.recording(sg), adv, lsb)
        ft.save(p)
        print("%-9s ẞ %-14s stem=%.0f cap=%.0f adv=%d lsb=%d"
              % (cut, nm, esz.stem_of(sg), esz.cap_of(sg), adv, lsb))
        for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
            f = TTFont(p); f.flavor = flv
            f.save(os.path.join(WF, sub, "Goetheanum-Schrift-v2.5-%s.%s" % (cut, flv)))
    print("statische Schnitte + Webfonts neu")

if __name__ == "__main__":
    main()

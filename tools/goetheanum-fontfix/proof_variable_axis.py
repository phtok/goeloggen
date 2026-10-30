#!/usr/bin/env python3
# Prüfmass für den Variable Font (Befund 29. 10. 2026, AUDIT.md): instanziert an
# den sieben Stufen 190 · 265 · 350 · 440 · 580 · 680 · 725 und misst je Glyphe
#   - Tintenfläche: wächst mit dem Gewicht (streng, Toleranz 0,5 %),
#   - Tintenbreite: nimmt mit dem Gewicht nicht ab (Toleranz 2 Einheiten; nur
#     für die Glyphen des Befunds – æ œ ∫ ŧ werden bewusst etwas schmaler),
#   - Zuwachs oben: Fläche 580 → 725 im Verhältnis zu 440 → 580 nicht unter der
#     Hälfte des Familien-Medians (fängt die Klemme, an der Kapitälchen,
#     Kurzziffern und Ø oben stehen blieben),
#   - Konturzentren: wandern zwischen Nachbarstufen um höchstens 40 Einheiten,
#   - Vorschub ⁄ (U+2044): klein, ≥ 0 und mit dem Gewicht nicht fallend.
# Ohne Argumente: die Glyphen des Befunds. --alle: jede erreichbare Glyphe
# (über cmap oder GSUB); unerreichbare Restglyphen zählen nicht.
# Exit 1 bei einem Verstoss.
# Aufruf:  python3 proof_variable_axis.py [--alle] [Pfad-zur-Variable.otf]
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VARDIR = os.path.join(REPO, "assets/fonts/goetheanum/Variable")
STUFEN = (190, 265, 350, 440, 580, 680, 725)
BEFUND = [0x00AB, 0x00BB, 0x201E, 0x201A, 0x00F7, 0x25CA, 0x0025, 0x0170,
          0x0104, 0x012E, 0x0024, 0x2022, 0x2044, 0x0171, 0x00E5, 0x0105,
          0x012F, 0x014B, 0x01FB, 0x00BF, 0x00A1, 0x2013, 0x2014, 0x00B7,
          0x0028, 0x0029, 0x005B, 0x005D, 0x007B, 0x007D, 0x0030]
# beim Durchlauf über alle Glyphen nachgefunden (Breite hier nicht geprüft:
# T-Balken und Haken werden mit dem Gewicht bewusst etwas kürzer)
NACHTRAG = [0x20AC, 0x01FF, 0x00DB] + [ord(c) for c in "myñýÿħńňŧŷžû"]
FEATS = ("smcp", "case", "zero")
LIGEN = ()
MAXWEG = 40


def reachable(ft, cps=None):
    """Glyphen über cmap (ggf. nur cps) plus deren Einzelersetzungen in GSUB."""
    cmap = ft.getBestCmap(); names = {v: k for k, v in cmap.items()}
    seeds = {cmap[c] for c in (cps or cmap) if c in cmap}
    out = set(seeds); gsub = ft["GSUB"].table
    for fr in gsub.FeatureList.FeatureRecord:
        if cps and fr.FeatureTag not in FEATS + ("liga",): continue
        for li in fr.Feature.LookupListIndex:
            L = gsub.LookupList.Lookup[li]
            for st in L.SubTable:
                if L.LookupType == 7: st = st.ExtSubTable
                for a, b in getattr(st, "mapping", {}).items():
                    if a in seeds or not cps: out.add(b)
                for a, bs in getattr(st, "alternates", {}).items():
                    if not cps: out.update(bs)
                for a, ls in getattr(st, "ligatures", {}).items():
                    for l in ls:
                        if not cps or "".join(chr(names[x]) for x in [a] + l.Component
                                              if x in names) in LIGEN:
                            out.add(l.LigGlyph)
    return sorted(out)


def measure(ft, glyphs):
    gs = ft.getGlyphSet(); res = {}
    for g in glyphs:
        rec = DecomposingRecordingPen(gs); gs[g].draw(rec)
        ap = AreaPen(); bp = BoundsPen(gs); cen = []; cur = []
        for op, a in rec.value:
            getattr(ap, op)(*a); getattr(bp, op)(*a)
            if op == "moveTo": cur = [a[0]]
            elif op in ("closePath", "endPath"):
                cen.append((sum(p[0] for p in cur) / len(cur), sum(p[1] for p in cur) / len(cur)))
            else: cur += list(a)
        b = bp.bounds
        res[g] = dict(flaeche=abs(ap.value), breite=(b[2] - b[0]) if b else 0,
                      zentren=cen, vorschub=ft["hmtx"][g][0])
    return res


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    alle = "--alle" in sys.argv
    path = args[0] if args else sorted(glob.glob(os.path.join(VARDIR, "Goetheanum-Variabel-v*.otf")))[-1]
    base = TTFont(path)
    glyphs = reachable(base, None if alle else BEFUND + NACHTRAG)
    breite_pruefen = set() if alle else set(reachable(base, BEFUND))
    names = {v: k for k, v in base.getBestCmap().items()}
    m = {}
    for w in STUFEN:
        ft = TTFont(path); instantiateVariableFont(ft, {"wght": w}, inplace=True)
        m[w] = measure(ft, glyphs)
    frac = base.getBestCmap()[0x2044]
    def oben(g):
        f = [m[w][g]["flaeche"] for w in (440, 580, 725)]
        return (f[2] - f[1]) / (f[1] - f[0]) if f[1] - f[0] > 1 else None
    alle_g = reachable(base, None)
    for w in STUFEN:
        if any(g not in m[w] for g in alle_g):
            ft = TTFont(path); instantiateVariableFont(ft, {"wght": w}, inplace=True)
            m[w].update(measure(ft, [g for g in alle_g if g not in m[w]]))
    quoten = sorted(q for q in (oben(g) for g in alle_g if m[440][g]["zentren"]) if q is not None)
    median_oben = quoten[len(quoten) // 2]
    fehler = 0
    for g in glyphs:
        row = [m[w][g] for w in STUFEN]
        if not row[0]["zentren"]: continue
        label = "%s %s" % (g, chr(names[g]) if g in names else "")
        f = [r["flaeche"] for r in row]; b = [r["breite"] for r in row]
        probleme = []
        if any(f[i + 1] < f[i] * 1.005 for i in range(len(f) - 1)):
            probleme.append("Fläche " + " · ".join("%d" % round(x) for x in f))
        if g in breite_pruefen and any(b[i + 1] < b[i] - 2 for i in range(len(b) - 1)):
            probleme.append("Breite " + " · ".join("%d" % round(x) for x in b))
        q = oben(g)
        if q is not None and q < 0.5 * median_oben:
            probleme.append("Zuwachs oben %.2f (Median %.2f)" % (q, median_oben))
        weg = 0
        for i in range(len(row) - 1):
            za, zb = row[i]["zentren"], row[i + 1]["zentren"]
            if len(za) != len(zb): probleme.append("Konturzahl springt"); break
            weg = max([weg] + [abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(za, zb)])
        if round(weg) > MAXWEG: probleme.append("Konturzentrum wandert %d" % round(weg))
        if g == frac:
            v = [r["vorschub"] for r in row]
            if any(x < 0 or x > 100 for x in v) or any(v[i + 1] < v[i] for i in range(len(v) - 1)):
                probleme.append("Vorschub " + " · ".join(map(str, v)))
        if probleme:
            fehler += 1; print("  ✗ %-14s %s" % (label, "; ".join(probleme)))
        elif not alle:
            print("  ✓ %-14s Fläche %s" % (label, " · ".join("%d" % round(x / 100) for x in f)))
    print("%s: %d Glyphen an %s geprüft, %d mit Verstoss." %
          (os.path.basename(path), len(glyphs), "/".join(map(str, STUFEN)), fehler))
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()

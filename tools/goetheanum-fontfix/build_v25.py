#!/usr/bin/env python3
# Assemble v2.5 static cuts by patching the built v2.4.1 cuts:
#   + ligatures (liga/calt)  + specials (prime/doublePrime/figureDash/numero
#   + zero.slash with 'zero' feature)  + version bump 2.4.1 -> 2.5.
# Stages to /tmp/v25 and renders a final HarfBuzz proof.
import os, sys, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
import build_ligatures as L
import build_specials as S
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
NEWVER = "2.5"

def add_single_feature(ft, tag, mapping):
    li = L.add_single_lookup(ft, mapping); L.register_feature(ft, tag, li)

def bump_version(ft, ps):
    nm = ft["name"]
    for rec in nm.names:
        if rec.nameID == 5: rec.string = "Version %s" % NEWVER
        elif rec.nameID == 3: rec.string = "%s;GOEA;%s" % (NEWVER, ps)
    ft["head"].fontRevision = 2.5

def patch_cut(cut, src, out):
    # 1) ligatures into a temp
    tmp = "/tmp/_v25_%s.otf" % cut
    L.inject(cut, src, tmp)
    ft = TTFont(tmp); cmap = ft.getBestCmap()
    ps = ft["name"].getDebugName(6) or ("Goetheanum-Schrift-%s" % cut)
    # 2) specials
    sp = S.build_specials(ft)
    zeroname = None
    for key, (uni, recv, adv, lsb) in sp.items():
        name = S.add_glyph(ft, recv, adv, lsb, uni)
        if key == "zeroslash": zeroname = name
    # 3) zero feature: 0 -> zero.slash
    add_single_feature(ft, "zero", {cmap[0x30]: zeroname})
    # 4) version
    bump_version(ft, ps)
    ft.save(out)
    return sp

if __name__ == "__main__":
    OUT = "/tmp/v25"; os.makedirs(OUT, exist_ok=True)
    for cut in ["Leise", "Klar", "Laut"]:
        src = glob.glob(os.path.join(REPO, "assets/fonts/goetheanum/**/*v2.4.1-%s.otf" % cut), recursive=True)[0]
        out = os.path.join(OUT, "Goetheanum-Schrift-v2.5-%s.otf" % cut)
        patch_cut(cut, src, out)
        print("  built", os.path.basename(out))
    # ---- final proof (HarfBuzz) ----
    import uharfbuzz as hb
    from fontTools.pens.recordingPen import RecordingPen
    import cairosvg
    LINES = ["Auffällige, fließende Schriftzüge — der Stoff, das Schiff, schaffen, Auflage, Grafik, sanfte Kraft, oft geprüft.",
             "№ 3477 · 47° 32′ 18″ · 1914‒1918 · Telefon 0761 · die schlummernde 0 (zero)"]
    def line(path, txt, feats):
        face = hb.Face(hb.Blob.from_file_path(path)); font = hb.Font(face)
        buf = hb.Buffer(); buf.add_str(txt); buf.guess_segment_properties(); hb.shape(font, buf, feats)
        ft = TTFont(path); gs = ft.getGlyphSet(); go = ft.getGlyphOrder(); d = []; x = 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            rp = RecordingPen(); gs[go[info.codepoint]].draw(rp)
            for c, pts in rp.value:
                Q = [((x + pos.x_offset + px), py) for px, py in pts]
                if c == "moveTo": d.append("M%.1f %.1f" % Q[0])
                elif c == "lineTo": d.append("L%.1f %.1f" % Q[0])
                elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (Q[0]+Q[1]+Q[2]))
                elif c == "qCurveTo": d.append("Q" + " ".join("%.1f %.1f" % q for q in Q))
                elif c == "closePath": d.append("Z")
            x += pos.x_advance
        return "".join(d), x
    sc = 0.038; pad = 30; out_svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="%d"><rect width="100%%" height="100%%" fill="#faf8f4"/>' % 360]
    y = pad
    for cut in ["Leise", "Klar", "Laut"]:
        p = os.path.join(OUT, "Goetheanum-Schrift-v2.5-%s.otf" % cut)
        y += 22; out_svg.append('<text x="%d" y="%d" font-family="Helvetica" font-size="12" fill="#9aa0a6">%s</text>' % (pad, y-6, cut))
        d1, _ = line(p, LINES[0], {"liga": True, "calt": True})
        d2, _ = line(p, LINES[1], {"zero": True, "onum": False})
        base = y + 1000*sc
        out_svg.append('<g transform="translate(%d,%.1f) scale(%.4f,-%.4f)"><path d="%s" fill="#23272b"/></g>' % (pad, base, sc, sc, d1)); y += 1000*sc*1.05
        base = y + 1000*sc
        out_svg.append('<g transform="translate(%d,%.1f) scale(%.4f,-%.4f)"><path d="%s" fill="#23272b"/></g>' % (pad, base, sc, sc, d2)); y += 1000*sc*1.35
    out_svg.append("</svg>")
    open("/tmp/v25final.svg", "w").write("\n".join(out_svg))
    cairosvg.svg2png(url="/tmp/v25final.svg", write_to="/tmp/v25final.png", scale=2)
    print("wrote /tmp/v25final.png")

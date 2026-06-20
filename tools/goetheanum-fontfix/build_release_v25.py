#!/usr/bin/env python3
# v2.5 release assembler (patch of the v2.4.1 outputs):
#   static cuts  -> + ligatures + specials + version (build_v25)
#   variable/icons -> version bump only (ligatures in the variable follow later)
#   webfonts (woff/woff2) regenerated from the v2.5 OTFs
# Old v2.4.1 binaries/webfonts are removed so the release is clean.
import os, sys, glob, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
import build_v25 as V
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(REPO, "assets/fonts/goetheanum")
NEW = "2.5"; OLD = "2.4.1"

def bump_meta(ft):
    ps = ft["name"].getDebugName(6) or ""
    for rec in ft["name"].names:
        if rec.nameID == 5: rec.string = "Version %s" % NEW
        elif rec.nameID == 3: rec.string = "%s;GOEA;%s" % (NEW, ps)
    ft["head"].fontRevision = 2.5

def main():
    Fonts = os.path.join(FONTS, "Fonts"); Var = os.path.join(FONTS, "Variable")
    Wf2 = os.path.join(FONTS, "Webfonts/woff2"); Wf = os.path.join(FONTS, "Webfonts/woff")
    # 1) static cuts: ligatures + specials + version
    for cut in ["Leise", "Klar", "Laut"]:
        src = glob.glob(os.path.join(FONTS, "**", "*v%s-%s.otf" % (OLD, cut)), recursive=True)[0]
        out = os.path.join(Fonts, "Goetheanum-Schrift-v%s-%s.otf" % (NEW, cut))
        V.patch_cut(cut, src, out)
        print("  static", cut)
    # 2) variable + icons: version bump (copy)
    for pat, sub in [("*Variabel-v%s.otf" % OLD, Var), ("*Icons-v%s.otf" % OLD, Fonts)]:
        src = glob.glob(os.path.join(FONTS, "**", pat), recursive=True)[0]
        ft = TTFont(src); bump_meta(ft)
        out = os.path.join(sub, os.path.basename(src).replace(OLD, NEW)); ft.save(out)
        print("  bumped", os.path.basename(out))
    # 3) webfonts from all v2.5 OTFs
    for p in glob.glob(os.path.join(Fonts, "*-v%s-*.otf" % NEW)) + glob.glob(os.path.join(Fonts, "*-v%s.otf" % NEW)) + glob.glob(os.path.join(Var, "*-v%s.otf" % NEW)):
        base = os.path.splitext(os.path.basename(p))[0]
        for fl, d in (("woff", Wf), ("woff2", Wf2)):
            f = TTFont(p); f.flavor = fl; f.save(os.path.join(d, "%s.%s" % (base, fl)))
    print("  webfonts rebuilt")
    # 4) remove old v2.4.1 binaries + webfonts
    for p in (glob.glob(os.path.join(Fonts, "*v%s*" % OLD)) + glob.glob(os.path.join(Var, "*v%s*" % OLD))
              + glob.glob(os.path.join(Wf, "*v%s*" % OLD)) + glob.glob(os.path.join(Wf2, "*v%s*" % OLD))):
        os.remove(p)
    print("  removed old v%s binaries" % OLD)

if __name__ == "__main__":
    main(); print("v2.5 binaries + webfonts done")

#!/usr/bin/env python3
# Packt das Download-ZIP Goetheanum-Schriften-v2.7.zip reproduzierbar aus dem
# aktuellen Stand auf der Platte (Office-TTF, Variable, Webfonts, Icons/Pfeile,
# Fallback, Beipackzettel, Lizenzen). Deterministisch (fester Zeitstempel,
# sortiert), damit das Binär-Diff minimal bleibt. Nach Font- oder Beipack-
# zettel-Änderungen ausführen.
# Die statischen Schnitt-OTF (Fonts/Goetheanum-Schrift-*.otf) sind seit dem
# Trio-Umbau reine BUILD-QUELLEN und werden nicht mehr ausgeliefert — sonst
# kollidieren sie mit der gleichnamigen Office-Familie.
import os, glob, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.join(REPO, "assets/fonts/goetheanum")
VERSION = "2.7"
TOP = "Goetheanum-Schriften-v%s" % VERSION

def members():
    g = lambda *p: sorted(glob.glob(os.path.join(ROOT, *p)))
    out = []
    out += [os.path.join(ROOT, "Beipackzettel-Goetheanum-Schriften.pdf")]
    out += g("Fallback", "*")
    out += g("Fonts", "Goetheanum-Icons-*.otf")
    out += g("Fonts", "Goetheanum-Pfeile-*.otf")
    out += g("Office", "*.ttf")
    out += [os.path.join(ROOT, "OFL.txt"), os.path.join(ROOT, "README.md")]
    out += g("Variable", "*.otf")
    out += g("Webfonts", "woff", "*.woff")
    out += g("Webfonts", "woff2", "*.woff2")
    return [p for p in out if os.path.isfile(p)]

def main():
    out = os.path.join(ROOT, TOP + ".zip")
    mem = members()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for src in mem:
            arc = os.path.join(TOP, os.path.relpath(src, ROOT))
            zi = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))   # deterministisch
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(src, "rb") as fh:
                z.writestr(zi, fh.read())
    print("%s.zip (%d Dateien)" % (TOP, len(mem)))

if __name__ == "__main__":
    main()

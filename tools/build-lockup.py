#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum-Lockup reproduzierbar bauen (Icon + „Goetheanum" + Unterzeile).

Nutzt dieselbe Engine wie der Logo-Generator: die eingebetteten Wortmarken-
Outlines (GLYPHS), die Marke (ICON) und die textToPath-Geometrie werden direkt
aus apps/logo-generator/index.html gelesen. So entsteht ein echtes Lockup als
SVG – kein freihändig gezeichnetes Logo.

Nutzung:
  tools/build-lockup.py Werkzeuge                         -> assets/logos/goetheanum-werkzeuge.svg
  tools/build-lockup.py Schriften --slug schriften
  tools/build-lockup.py Werkzeuge --brand "#0061a9" --line1 "#575756"
"""
import sys, os, re, json, math, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "apps", "logo-generator", "index.html")

# Lockup-Geometrie wie im Generator (Layout „desktop"): fs=10.3, Text bei x=19.5,
# Zeilen-Grundlinien y=10.05 und 20.05, Höhe 22.24; Breite = max(Zeilenbreiten)+25.
FS = 10.3; FONT_UPM = 1000
X = 19.5; Y1 = 10.05; Y2 = 20.05; H = 22.24; PAD = 25


def _extract_braced(src, start):
    """Liest ein {...}-Objektliteral ab start; Klammern in Strings werden ignoriert."""
    depth = 0; k = start; instr = False; esc = False
    while k < len(src):
        c = src[k]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: return src[start:k + 1]
        k += 1
    raise ValueError("Klammern unausgeglichen – GLYPHS nicht gefunden")


def load_engine():
    t = open(SRC, encoding="utf-8").read()
    gi = t.find("var GLYPHS=")
    glyphs = json.loads(_extract_braced(t, t.find("{", gi)))
    a = t.find("var ICON=[") + len("var ICON=")
    icon = json.loads(t[a:t.find("];", a) + 1])
    return glyphs, icon


def text_to_path(glyphs, text, x, y, fs):
    scale = fs / FONT_UPM; cx = x; out = []
    for ch in text:
        g = glyphs.get(ch)
        if not g:
            cx += fs * 0.3  # unbekanntes Zeichen: schmale Lücke
            continue
        if g.get("path"):
            out.append('<path d="%s" transform="translate(%s,%s) scale(%s,%s)"/>'
                       % (g["path"], round(cx, 3), y, round(scale, 6), round(-scale, 6)))
        cx += g["width"] * scale
    return "".join(out), cx - x


def build(line2, brand, line1col):
    glyphs, icon = load_engine()
    missing = [c for c in set(line2) if c not in glyphs and not c.isspace()]
    if missing:
        sys.stderr.write("Warnung: Glyphen fehlen in der Engine: %s\n" % "".join(missing))
    t1, w1 = text_to_path(glyphs, "Goetheanum", X, Y1, FS)
    t2, w2 = text_to_path(glyphs, line2, X, Y2, FS)
    w = math.ceil(max(w1, w2) + PAD)
    ico = "".join('<path d="%s" fill="%s"/>' % (d, brand) for d in icon)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'role="img" aria-label="Goetheanum %s">%s'
            '<g fill="%s">%s</g><g fill="%s">%s</g></svg>'
            % (w, H, line2, ico, line1col, t1, brand, t2))


def main():
    ap = argparse.ArgumentParser(description="Goetheanum-Lockup als SVG bauen.")
    ap.add_argument("line2", help="Unterzeile, z. B. Werkzeuge")
    ap.add_argument("--slug", help="Dateiname-Teil (Default: aus Unterzeile)")
    ap.add_argument("--brand", default="#0061a9", help="Markenfarbe (Icon + Unterzeile)")
    ap.add_argument("--line1", default="#575756", help="Farbe der Zeile „Goetheanum")
    ap.add_argument("--out", help="Zielpfad (überschreibt --slug)")
    a = ap.parse_args()
    slug = a.slug or re.sub(r"[^a-z0-9]+", "-", a.line2.lower()).strip("-")
    out = a.out or os.path.join(ROOT, "assets", "logos", "goetheanum-%s.svg" % slug)
    svg = build(a.line2, a.brand, a.line1)
    open(out, "w", encoding="utf-8").write(svg)
    print("geschrieben:", os.path.relpath(out, ROOT), "(%d Bytes)" % len(svg))


if __name__ == "__main__":
    main()

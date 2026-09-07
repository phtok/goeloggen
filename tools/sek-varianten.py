#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sektionsfarben: helle und dunkle Variante je Sektion – gerechnet, nicht gefühlt.

Aus jeder Basis-Sektionsfarbe (--sek-<key> in design-system/tokens.css, Quelle
der Werte: assets/goe-orgs.js) entstehen in OKLCH drei abgeleitete Töne:

  (ebenso --bereich-<key>-… für Bereiche mit eigener Farbe: Bühne, Bau-Administration)
  --sek-<key>-dunkel   matte, tiefe FLÄCHE – trägt Weiss (--on-accent), ≥ 5.5:1.
                       Markenfest (kippt nicht mit Hell/Dunkel).
  --sek-<key>-hell     leise TINT-Fläche – trägt --ink oder --sek-<key>-ink.
                       Im Dunkelmodus wird sie ein tiefer, stiller Ton (Flächen
                       gehören dem Theme, B05) – der Text darauf bleibt --ink.
  --sek-<key>-ink      die Sektion als TEXT (Kicker, Link, Ton-in-Ton auf hell).
                       Hell = der dunkle Ton; Dunkel = ein heller Hauch der Sektion.
                       Muster wie --gold-ink / --ok-ink: eine Farbe braucht beide
                       Gestalten, sonst wird die Fläche als Schrift missbraucht.

Alles gleiche Helligkeit (OKLab L) und gedeckelte Buntheit (C) je Rolle, damit die
zwölf Sektionen als EINE Reihe wirken und Weiss/Ink überall gleich gut steht.
Der Farbton (H) bleibt der der Sektion.

Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/sek-varianten.py            Vorschau (Werte + Kontraste)
  python3 tools/sek-varianten.py --apply    schreibt den Block in tokens.css
                                             und tokens.json (idempotent)
  python3 tools/sek-varianten.py --json     alle Töne als JSON (für Seiten)
Die Kontraste prüft anschliessend tools/check-on-sek.py (bricht bei < 4.5:1).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_CSS = os.path.join(ROOT, "design-system", "tokens.css")
TOKENS_JSON = os.path.join(ROOT, "design-system", "tokens.json")

# --- Rezept (die Zahlen, über die entschieden wurde) ------------------------
REZEPT = {
    # Fläche dunkel: L 0.47 → Weiss ≥ 5.5:1 auf jeder Sektion; C höchstens 0.085
    # (matt: kräftige Basistöne haben 0.13–0.20). Faktor hält leise Basistöne leise.
    "dunkel":   {"L": 0.47, "C_max": 0.085, "C_faktor": 0.62},
    # Fläche hell (Hellmodus): ein Farbhauch, kaum mehr als Papier – L 0.965, Buntheit
    # sehr niedrig (Beschluss 7. 9. 2026: «zarter, weniger leuchtend»). --ink ≥ 13:1,
    # der dunkle Ton ≥ 6:1.
    "hell":     {"L": 0.965, "C_max": 0.022, "C_faktor": 0.20},
    # Fläche hell (Dunkelmodus): derselbe Hauch, gespiegelt – ein stiller Ton knapp
    # über --paper (#16191c, L ≈ 0.20) und --soft (L ≈ 0.24).
    "hell_dk":  {"L": 0.27, "C_max": 0.035, "C_faktor": 0.25},
    # Text im Dunkelmodus: heller Hauch der Sektion – ≥ 4.5:1 auf hell_dk UND --paper.
    "ink_dk":   {"L": 0.82, "C_max": 0.090, "C_faktor": 0.60},
}
# Bewusst KEIN Sonderfall je Sektion: eine Regel für alle, damit die Reihe stimmt.

# --- Farbmathematik (sRGB ⇄ OKLCH, WCAG-Kontrast) ---------------------------
def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#" + "".join("%02x" % round(max(0, min(1, c)) * 255) for c in rgb)

def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def unlin(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def rgb_to_oklab(rgb):
    r, g, b = (lin(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)

def oklab_to_rgb(lab):
    L, a, b = lab
    l = L + 0.3963377774 * a + 0.2158037573 * b
    m = L - 0.1055613458 * a - 0.0638541728 * b
    s = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l ** 3, m ** 3, s ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(unlin(c) for c in (r, g, bb))

def to_oklch(hexv):
    import math
    L, a, b = rgb_to_oklab(hex_to_rgb(hexv))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360

def from_oklch(L, C, H):
    """OKLCH → Hex; liegt der Ton ausserhalb sRGB, wird C reduziert (Farbton bleibt)."""
    import math
    for _ in range(40):
        a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
        rgb = oklab_to_rgb((L, a, b))
        if all(-0.0005 <= c <= 1.0005 for c in rgb):
            return rgb_to_hex(rgb)
        C *= 0.94
    return rgb_to_hex(oklab_to_rgb((L, 0, 0)))

def luminance(hexv):
    r, g, b = (lin(c) for c in hex_to_rgb(hexv))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def kontrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)))
    return (lb + 0.05) / (la + 0.05)

# --- Ableitung ----------------------------------------------------------------
def ableiten(hexv, rolle):
    r = REZEPT[rolle]
    L, C, H = to_oklch(hexv)
    return from_oklch(r["L"], min(C * r["C_faktor"], r["C_max"]), H)

# Zwei Familien: Sektionen (--sek-*) und Bereiche mit eigener Farbe (--bereich-<key>).
# --bereich ohne Schlüssel ist der Standard (= Markenblau) und bekommt keine Varianten.
FAMILIEN = (("sek", "sektion-varianten"), ("bereich", "bereich-varianten"))

def basis_lesen():
    css = open(TOKENS_CSS, encoding="utf-8").read()
    kopf = css.split("/* @sek-varianten", 1)[0]     # nur den Basis-Block lesen
    out = []
    for fam, _ in FAMILIEN:
        for k, v, d in re.findall(r"--%s-([\w]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;\s*(?:/\*\s*(.*?)\s*\*/)?" % fam, kopf):
            out.append((fam, k, v.lower(), d or ""))
    return out

def varianten():
    return [{"fam": f, "key": k, "basis": v, "name": d,
             "dunkel": ableiten(v, "dunkel"), "hell": ableiten(v, "hell"),
             "hell_dk": ableiten(v, "hell_dk"), "ink_dk": ableiten(v, "ink_dk")}
            for f, k, v, d in basis_lesen()]

MARK_A = "/* @sek-varianten:start – GENERIERT von tools/sek-varianten.py, nicht von Hand ändern */"
MARK_E = "/* @sek-varianten:ende */"
MARK_DK_A = "  /* @sek-varianten-dunkelmodus:start – GENERIERT von tools/sek-varianten.py */"
MARK_DK_E = "  /* @sek-varianten-dunkelmodus:ende */"

def css_block(vs):
    z = [MARK_A,
         "/* --- Sektionsfarben: helle und dunkle Variante (Beschluss 7. September 2026) ---",
         "   --sek-*-dunkel  matte, tiefe Fläche – Weiss drauf (--on-accent), ≥ 5.5:1, MARKENFEST.",
         "   --sek-*-hell    leise Tint-Fläche – --ink oder --sek-*-ink drauf; kippt im Dunkel",
         "                   zu einem stillen, tiefen Ton (Fläche = Theme, B05).",
         "   --sek-*-ink     die Sektion als TEXT (Kicker, Link) – hell: = dunkler Ton, dunkel:",
         "                   heller Hauch. Hält ≥ 4.5:1 auf --paper, --soft und --sek-*-hell.",
         "   Rezept: OKLCH, gleiche Helligkeit je Rolle (dunkel L .47 · hell L .935), Buntheit",
         "   gedeckelt (matt). Gerechnet: tools/sek-varianten.py · geprüft: tools/check-on-sek.py. */",
         ":root{"]
    for v in vs:
        p = "--%s-%s" % (v["fam"], v["key"])
        z.append("  %s-dunkel:%s; %s-hell:%s; %s-ink:%s;" % (p, v["dunkel"], p, v["hell"], p, v["dunkel"]))
    z.append("}")
    z.append(":root[data-theme=\"dark\"]{")
    for v in vs:
        p = "--%s-%s" % (v["fam"], v["key"])
        z.append("  %s-hell:%s; %s-ink:%s;" % (p, v["hell_dk"], p, v["ink_dk"]))
    z.append("}")
    z.append(MARK_E)
    return "\n".join(z)

def apply_css(vs):
    css = open(TOKENS_CSS, encoding="utf-8").read()
    block = css_block(vs)
    if MARK_A in css:
        neu = re.sub(re.escape(MARK_A) + r".*?" + re.escape(MARK_E), lambda m: block, css, flags=re.S)
    else:
        # hinter den Dunkelmodus-Block, vor die Welten
        anker = "/* --- Welten (Dialekte)"
        assert anker in css, "Anker für den Varianten-Block nicht gefunden"
        neu = css.replace(anker, block + "\n\n" + anker, 1)
    if neu != css:
        open(TOKENS_CSS, "w", encoding="utf-8").write(neu)
        return True
    return False

def apply_json(vs):
    """Schreibt den Block "sektion-varianten" im kompakten Hausformat (eine Zeile je
    Wert), damit der Rest der Datei unberührt bleibt – json.dumps würde alles umbrechen."""
    txt = open(TOKENS_JSON, encoding="utf-8").read()
    neu = txt
    for fam, gruppe in FAMILIEN:
        fv = [v for v in vs if v["fam"] == fam]
        if not fv:
            continue
        z = ['    "%s": {' % gruppe,
             '      "$description": "Abgeleitete Töne (%s) – generiert von tools/sek-varianten.py (nicht von Hand ändern). '
             'dunkel: matte Fläche, Weiss drauf, markenfest. hell: Farbhauch, --ink drauf; '
             'hell_dunkelmodus gilt im Dunkel. ink: Farbe als Text (hell = dunkel; ink_dunkelmodus im Dunkel).",' % fam]
        for i, v in enumerate(fv):
            z.append('      "%s": { "dunkel": { "$value": "%s" }, "hell": { "$value": "%s" }, '
                     '"hell_dunkelmodus": { "$value": "%s" }, "ink": { "$value": "%s" }, '
                     '"ink_dunkelmodus": { "$value": "%s" }, "$description": "%s" }%s'
                     % (v["key"], v["dunkel"], v["hell"], v["hell_dk"], v["dunkel"], v["ink_dk"],
                        v["name"].replace('"', "'"), "," if i < len(fv) - 1 else ""))
        z.append('    }')
        block = "\n".join(z)
        start = neu.find('    "%s": {' % gruppe)
        if start >= 0:
            # bis zur schliessenden Klammer auf derselben Einrücktiefe
            ende = neu.index("\n    }", start) + len("\n    }")
            neu = neu[:start] + block + neu[ende:]
        else:
            anker = neu.index('\n  },\n  "font"')      # Ende des "color"-Objekts
            neu = neu[:anker] + ",\n" + block + neu[anker:]
    if neu != txt:
        open(TOKENS_JSON, "w", encoding="utf-8").write(neu)
        return True
    return False

def vorschau(vs):
    print("%-12s %-8s %-8s W/dk  %-8s ink/h dk/h  %-8s ink/hd %-8s i/hd i/pap" %
          ("key", "basis", "dunkel", "hell", "hell_dk", "ink_dk"))
    for v in vs:
        print("%-16s %-8s %-8s %4.1f  %-8s %4.1f  %4.1f  %-8s %4.1f   %-8s %4.1f %4.1f" % (
            v["fam"] + "-" + v["key"], v["basis"], v["dunkel"], kontrast("#fff", v["dunkel"]),
            v["hell"], kontrast("#23272b", v["hell"]), kontrast(v["dunkel"], v["hell"]),
            v["hell_dk"], kontrast("#e6e8ea", v["hell_dk"]),
            v["ink_dk"], kontrast(v["ink_dk"], v["hell_dk"]), kontrast(v["ink_dk"], "#16191c")))

def main(argv):
    vs = varianten()
    if "--json" in argv:
        print(json.dumps(vs, ensure_ascii=False, indent=1)); return 0
    if "--apply" in argv:
        a = apply_css(vs); b = apply_json(vs)
        print("tokens.css %s · tokens.json %s" % ("geschrieben" if a else "unverändert",
                                                    "geschrieben" if b else "unverändert"))
        return 0
    vorschau(vs); return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

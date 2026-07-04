#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzwingt die kanonische Typo-Leiter (B6, Beier) auf design-system/base.css.

Zwei harte Regeln aus design-system/type-scale.json:
  TS1  Goetheanum-Textrolle mit font-size < 18px MUSS font-weight >= 580 (Deutlich) tragen.
  TS2  Leise (Gewicht 265 bzw. --w-leise) als Lesetext MUSS >= 22px sein.

Geprüft werden die Regel-Blöcke in base.css: Selektoren, die eine font-size in px
setzen. Die Familie wird als Goetheanum gewertet, wenn font-family fehlt (Body-Erbe
= Display) oder var(--font)/var(--font-display) ist; Source (var(--font-text) u. a.)
ist ausgenommen. Verstösse melden (Warnung); mit --strict brechen sie den Build.
Aufruf:  python3 tools/check-type-scale.py [--strict]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "design-system", "base.css")
SCALE = os.path.join(ROOT, "design-system", "type-scale.json")
WEIGHTS = {"w-leise": 265, "w-text": 440, "w-deutlich": 580, "w-strong": 680}


def load_floor():
    import json
    g = json.load(open(SCALE, encoding="utf-8"))["grenzwerte"]
    return g["klar_min_px"], g["leise_min_px"], g["min_gewicht_unter_18"]


def px(decls):
    m = re.search(r"font-size:\s*([0-9.]+)px", decls)
    return float(m.group(1)) if m else None


def weight(decls):
    m = re.search(r"font-weight:\s*var\(--(w-[\w-]+)\)", decls)
    if m:
        return WEIGHTS.get(m.group(1))
    m = re.search(r"font-weight:\s*(\d{3})", decls)
    return int(m.group(1)) if m else None


def is_source(decls):
    return "var(--font-text)" in decls or "Source Sans" in decls


def is_display(decls):
    return "var(--font-display)" in decls or 'font-family:"Goetheanum"' in decls or "var(--font)" in decls


def main():
    strict = "--strict" in sys.argv
    css = re.sub(r"/\*.*?\*/", "", open(BASE, encoding="utf-8").read(), flags=re.S)
    klar_min, leise_min, min_w = load_floor()
    warns = []
    for sel, decls in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        sel = sel.strip()
        if sel.startswith("@") or ":" in sel and "::" not in sel and "hover" in sel:
            pass
        size = px(decls)
        if size is None:
            continue
        w = weight(decls)
        # TS1: Goetheanum (nicht Source) < 18px braucht >= Deutlich
        if size < klar_min and not is_source(decls):
            # nur wenn Familie Display ist ODER unspezifiziert (erbt Display) UND ein Gewicht gesetzt ist
            fam_ok = is_display(decls) or ("font-family" not in decls)
            if fam_ok and w is not None and w < min_w:
                warns.append("TS1  %-26s  %.4gpx Goetheanum, Gewicht %d < %d" % (sel[:26], size, w, min_w))
        # TS2: Leise (265) als Lesetext braucht >= 22px
        if w == WEIGHTS["w-leise"] and size < leise_min:
            warns.append("TS2  %-26s  Leise bei %.4gpx < %dpx" % (sel[:26], size, leise_min))
    if warns:
        head = "✗ Typo-Leiter verletzt:" if strict else "⚠ Typo-Leiter – Hinweise:"
        print(head); print("\n".join("  " + w for w in warns))
        return 1 if strict else 0
    print("✓ Typo-Leiter eingehalten (TS1/TS2) in base.css.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

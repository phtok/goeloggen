#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prüft die Vordergrund-auf-Sektionsfläche-Kontraste (WCAG 1.4.3, A6).

Für jedes --sek-<key> in design-system/tokens.css muss --on-sek-<key> existieren
und auf seiner Fläche ≥ 4.5:1 erreichen. Unterschreiten (oder ein fehlendes
Gegenstück) bricht den Build. Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/check-on-sek.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(ROOT, "design-system", "tokens.css")
AA = 4.5


def _hex(v):
    v = v.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lum(rgb):
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((_lum(_hex(a)), _lum(_hex(b))))
    return (lb + 0.05) / (la + 0.05)


def main():
    css = open(TOKENS, encoding="utf-8").read()
    sek = dict(re.findall(r"--sek-([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", css))
    on = dict(re.findall(r"--on-sek-([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", css))
    fails = []
    for key, bg in sek.items():
        fg = on.get(key)
        if fg is None:
            fails.append("  --on-sek-%s fehlt (Fläche %s)" % (key, bg)); continue
        r = ratio(fg, bg)
        if r < AA:
            fails.append("  --on-sek-%s (%s) auf --sek-%s (%s): %.2f < %.1f" % (key, fg, key, bg, r, AA))
    if fails:
        print("✗ Sektions-Vordergrund unter WCAG AA:"); print("\n".join(fails)); return 1
    print("✓ Alle %d --on-sek-* halten ≥ %.1f:1 auf ihrer Fläche." % (len(sek), AA))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prüft die Vordergrund-auf-Sektionsfläche-Kontraste (WCAG 1.4.3, A6).

Für jedes --sek-<key> in design-system/tokens.css muss --on-sek-<key> existieren
und auf seiner Fläche ≥ 4.5:1 erreichen. Seit dem 7. September 2026 gilt dasselbe
für die abgeleiteten Varianten (tools/sek-varianten.py):
  Weiss (--on-accent)        auf --sek-<key>-dunkel            ≥ 4.5 (Ziel ≥ 5.5)
  --ink                      auf --sek-<key>-hell (hell/dunkel) ≥ 4.5
  --sek-<key>-ink            auf --sek-<key>-hell, --paper, --soft (je Theme) ≥ 4.5
Unterschreiten (oder ein fehlendes Gegenstück) bricht den Build. Aufruf aus dem
Repo-Wurzelverzeichnis:
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


def _tokens(css):
    """Alle --name:#hex-Paare, in Reihenfolge; spätere Definitionen überschreiben."""
    d = {}
    for name, val in re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", css):
        d[name] = val
    return d


def main():
    css = open(TOKENS, encoding="utf-8").read()
    # Hell-Theme = alles ausser den [data-theme="dark"]-Blöcken; Dunkel = Hell + Dunkel-Blöcke
    dark_blocks = re.findall(r':root\[data-theme="dark"\]\s*\{(.*?)\}', css, re.S)
    light_css = re.sub(r':root\[data-theme="dark"\]\s*\{.*?\}', "", css, flags=re.S)
    light_css = re.sub(r':root\[data-welt=[^{]*\{.*?\}', "", light_css, flags=re.S)
    light = _tokens(light_css)
    dark = dict(light); dark.update(_tokens("\n".join(dark_blocks)))

    sek = {}
    for fam in ("sek", "bereich"):
        for k, v in re.findall(r"--%s-([\w]+)\s*:\s*(#[0-9a-fA-F]{3,6})" % fam, light_css):
            if not k.endswith(("-dunkel", "-hell", "-ink")):
                sek[fam + "-" + k] = v
    fails, n = [], 0

    def check(label, fg, bg, ziel=AA):
        nonlocal n
        n += 1
        r = ratio(fg, bg)
        if r < ziel:
            fails.append("  %s: %.2f < %.1f" % (label, r, ziel))

    for key, bg in sek.items():
        fg = light.get("--on-" + key)
        if fg is None:
            fails.append("  --on-%s fehlt (Fläche %s)" % (key, bg)); continue
        check("--on-%s (%s) auf --%s (%s)" % (key, fg, key, bg), fg, bg)
        # Varianten (optional, aber wenn eine da ist, müssen alle da sein)
        dunkel = light.get("--%s-dunkel" % key)
        if dunkel is None:
            continue
        for theme, t in (("hell", light), ("dunkel", dark)):
            hell, ink = t.get("--%s-hell" % key), t.get("--%s-ink" % key)
            if hell is None or ink is None:
                fails.append("  --%s-hell/-ink fehlt (Theme %s)" % (key, theme)); continue
            check("Weiss auf --%s-dunkel (%s)" % (key, dunkel), t["--on-accent"], dunkel)
            check("--ink auf --%s-hell (%s, %s)" % (key, hell, theme), t["--ink"], hell)
            check("--%s-ink (%s) auf --%s-hell (%s, %s)" % (key, ink, key, hell, theme), ink, hell)
            check("--%s-ink (%s) auf --paper (%s)" % (key, ink, theme), ink, t["--paper"])
            check("--%s-ink (%s) auf --soft (%s)" % (key, ink, theme), ink, t["--soft"])
    if fails:
        print("✗ Sektions-Kontraste unter WCAG AA:"); print("\n".join(fails)); return 1
    print("✓ %d Sektions-Kontraste (Basis + Varianten, beide Themes) halten ≥ %.1f:1." % (n, AA))
    return 0


if __name__ == "__main__":
    sys.exit(main())

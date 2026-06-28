#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum Typo-Sync — Driftwächter zwischen Kanon und Design-System.

Eine Quelle der Wahrheit: assets/typografie/goetheanum-typo-tokens.json.
Von dort fliessen Werte und Regeln ins Design-System (tokens.css), ins Handbuch
(typografie.html) und in den ausführbaren Regel-Checker (typo-regeln.yaml). Diese
Schichten dürfen nicht stillschweigend auseinanderlaufen — genau das prüft dieses
Werkzeug, damit Typografie und Design-System *permanent synchron* bleiben.

Prüfungen:
  1. Farben  — die im Kanon definierten Farben stimmen mit tokens.css überein.
  2. Regeln  — jede in Handbuch/YAML referenzierte Regel-ID existiert im Kanon
               (keine Phantom-Regeln).
  3. Abdeckung — welche Kanon-Regeln (noch) nicht im Handbuch stehen (nur Hinweis).
  4. Mass    — die kanonische Zeilenlänge (G10) ist in base.css verankert.

Exit 0 = synchron · Exit 1 = Drift (für den Commit-Hook geeignet).
Ohne Fremdpakete (wie typo-check.py).
"""
import json
import os
import re
import sys

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON    = os.path.join(ROOT, "assets", "typografie", "goetheanum-typo-tokens.json")
TOKENS   = os.path.join(ROOT, "design-system", "tokens.css")
BASE     = os.path.join(ROOT, "design-system", "base.css")
HANDBOOK = os.path.join(ROOT, "typografie.html")
YAML     = os.path.join(ROOT, "assets", "typografie", "typo-regeln.yaml")

# Kanon-Farbname  ->  tokens.css-Variable (die Hausfarben, die beide Seiten teilen)
COLOR_MAP = {
    "tinte":      "--ink",
    "tinte-leise": "--muted",
    "gold":       "--gold",
    "gold-tief":  "--gold-deep",
    "papier":     "--paper",
    "flaeche":    "--soft",
}

RID = re.compile(r"\b[GS]\d{2}\b")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def norm_hex(value):
    """#fff -> ffffff; alpha (hex8) wird auf die Grundfarbe reduziert."""
    h = value.strip().lower().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return h[:6]


def main():
    problems, infos = [], []

    canon = json.loads(read(CANON))
    regeln = canon.get("$regeln", {})
    canon_ids = {k for k in regeln if RID.fullmatch(k)}
    farbe = canon.get("farbe", {})

    tokens = read(TOKENS)
    # Nur den hellen Basis-Block :root{…} lesen (nicht :root[data-theme="dark"]).
    mblock = re.search(r":root\s*\{(.*?)\}", tokens, re.S)
    base_block = mblock.group(1) if mblock else tokens
    tokvars = dict(re.findall(r"(--[a-z-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", base_block))

    # 1) Farben synchron
    for cname, var in COLOR_MAP.items():
        cval = (farbe.get(cname) or {}).get("$value")
        tval = tokvars.get(var)
        if not cval:
            infos.append(f"Kanon-Farbe ‹{cname}› fehlt – Abgleich übersprungen.")
        elif not tval:
            problems.append(f"tokens.css: Variable {var} (für Kanon ‹{cname}›) nicht gefunden.")
        elif norm_hex(cval) != norm_hex(tval):
            problems.append(f"Farbe driftet: Kanon {cname}={cval}  ≠  tokens.css {var}={tval}")

    # 2) Referenzierte Regeln existieren im Kanon
    for label, path in [("typografie.html", HANDBOOK), ("typo-regeln.yaml", YAML)]:
        used = set(RID.findall(read(path)))
        for rid in sorted(used - canon_ids):
            problems.append(f"Phantom-Regel {rid} in {label} – fehlt im Kanon $regeln.")

    # 3) Abdeckung des Handbuchs (nur Hinweis)
    documented = set(RID.findall(read(HANDBOOK)))
    gap = sorted(canon_ids - documented)
    if gap:
        infos.append("Im Kanon, aber (noch) nicht im Handbuch dokumentiert: " + ", ".join(gap))

    # 4) Zeilenlänge (G10) im Design-System verankert (Token oder .lese)
    zl = (canon.get("mass", {}).get("zeilenlaenge") or {}).get("$value")
    if zl and zl not in (read(TOKENS) + "\n" + read(BASE)):
        problems.append(f"Zeilenlänge {zl} (G10) nicht im Design-System gefunden (--measure / .lese).")

    # --- Bericht ---
    print("Goetheanum Typo-Sync — Kanon ↔ Design-System")
    for i in infos:
        print(f"  Hinweis  {i}")
    if problems:
        print()
        for p in problems:
            print(f"  DRIFT    {p}")
        print(f"\n✗ {len(problems)} Drift(s) — Kanon und Design-System laufen auseinander.")
        return 1
    print("✓ synchron — Kanon, Design-System, Handbuch und Checker stimmen überein.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

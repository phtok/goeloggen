#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum DS-Fix – wendet die EINDEUTIGEN Struktur-Korrekturen an (Codemod).

Selbstkorrektur-Hälfte der Engine: was tools/ds-lint.py meldet, hebt dieses
Werkzeug deterministisch auf die Token-Schicht. Idempotent (var(--…) bleibt
unangetastet). Es löst NUR die Hauspalette auf – property-bewusst (weisse
SCHRIFT → --on-accent, weisse FLÄCHE → --paper). Unbekannte Einzelfarben und
physische Artefakt-Farben (gedruckte Karte ist immer weiss) bleiben stehen;
letztere mit  # ds-ok  in der Zeile schützen.

Quelle der Wahrheit:  design-system/tokens.css  (die Tokens, auf die abgebildet wird).

Nutzung:
  tools/ds-fix.py datei …            # Vorschau (dry-run, ändert nichts)
  tools/ds-fix.py --apply datei …    # schreibt die Änderungen
  tools/ds-fix.py --apply --all      # über alle versionierten Seiten
  tools/ds-fix.py --include datei …  # fügt fehlende Pflicht-Includes ein

NICHT automatisiert (zu kontext-/layoutgebunden – bewusst Handarbeit, ds-lint
zeigt die Stellen): Schriftgrößen <13px, Entfernen lokaler Rollen-Definitionen.
"""
import sys, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

C = {"red": "\033[31m", "grn": "\033[32m", "dim": "\033[2m", "b": "\033[1m", "x": "\033[0m"}
def col(s, c): return f"{C[c]}{s}{C['x']}" if sys.stdout.isatty() else s

# --- Hauspalette: (Property-Gruppe) Literal → Token ---------------------------
TEXT = {
    "#fff": "var(--on-accent)", "#ffffff": "var(--on-accent)", "white": "var(--on-accent)",
    "#23272b": "var(--ink)", "#1f2329": "var(--ink)", "#181c20": "var(--ink)", "#23262a": "var(--ink)",
    "#737a80": "var(--muted)", "#6b7177": "var(--muted)", "#5d5d5d": "var(--muted)",
    "#565b60": "var(--muted)", "#3a3f44": "var(--muted)", "#9aa0a6": "var(--muted)",
    "#9aa1a8": "var(--muted)", "#7a8086": "var(--muted)",
    "#94702e": "var(--gold-ink)", "#a07a33": "var(--gold-ink)",
    "#d7ab68": "var(--gold)", "#0061a9": "var(--blue)",
    "#3f7d46": "var(--ok)", "#b3261e": "var(--bad)", "#b3433c": "var(--bad)",
}
BG = {
    "#fff": "var(--paper)", "#ffffff": "var(--paper)", "white": "var(--paper)",
    "#faf8f4": "var(--soft)", "#f3efe7": "var(--soft)", "#f7f5f0": "var(--soft)", "#f6f3ee": "var(--soft)",
    "#0061a9": "var(--blue-solid)", "#94702e": "var(--gold-deep)", "#3f7d46": "var(--ok)",
}
PAINT = {
    "#fff": "var(--on-accent)", "#ffffff": "var(--on-accent)",
    "#23272b": "var(--ink)", "#1f2329": "var(--ink)",
    "#94702e": "var(--gold-ink)", "#d7ab68": "var(--gold)",
}
# Sektionsfarben sind Identität: dasselbe Token, egal ob Schrift/Fläche/Rand.
SEK = {
    "#a24f8a": "var(--sek-aas)", "#3b4881": "var(--sek-ps)", "#5f5599": "var(--sek-ms)",
    "#1e7b6e": "var(--sek-nws)", "#63b145": "var(--sek-lws)", "#d072a0": "var(--sek-sbk)",
    "#5168c0": "var(--sek-ssw)", "#df4164": "var(--sek-szw)", "#ff675d": "var(--sek-js)",
    "#598ddc": "var(--sek-srmk)", "#2e54a4": "var(--sek-mas)", "#f98a3c": "var(--sek-hpise)",
    "#005eb8": "var(--bereich)",
}
ALLPROPS = ["color", "background", "background-color", "fill", "stroke",
            "border", "border-color", "border-top", "border-bottom", "outline-color"]
GROUPS = [
    (["color"], TEXT),
    (["background", "background-color"], BG),
    (["fill", "stroke"], PAINT),
    (ALLPROPS, SEK),
]
BORDER_PROPS = ["border", "border-color", "border-top", "border-right", "border-bottom",
                "border-left", "border-top-color", "border-bottom-color", "outline", "outline-color"]

RE_RGBA_LINE = re.compile(r"rgba\(\s*20\s*,\s*24\s*,\s*28\s*,\s*([0-9.]+)\s*\)")


def prop_pat(prop, literal):
    # property-verankert: nicht Teil eines --custom-props / background-color usw.
    return re.compile(r"(?<![-\w])(" + re.escape(prop) + r")(?![-\w])(\s*:\s*[^;{}]*?)" +
                      re.escape(literal) + r"\b", re.I)


def fix_line(line):
    """Eine CSS-Zeile property-bewusst auf Tokens heben. Gibt (neu, n_änderungen)."""
    n = 0
    for props, mp in GROUPS:
        for prop in props:
            for lit, tok in mp.items():
                pat = prop_pat(prop, lit)
                def repl(m, tok=tok):
                    return m.group(1) + m.group(2) + tok
                line, k = pat.subn(repl, line)
                n += k
    # rgba(20,24,28,a) NUR in Rand-/Outline-Properties → --line / --line-soft
    for prop in BORDER_PROPS:
        pat = re.compile(r"(?<![-\w])(" + re.escape(prop) + r")(?![-\w])(\s*:\s*[^;{}]*?)" +
                         r"rgba\(\s*20\s*,\s*24\s*,\s*28\s*,\s*([0-9.]+)\s*\)", re.I)
        def repl(m):
            a = float(m.group(3))
            return m.group(1) + m.group(2) + ("var(--line-soft)" if a <= 0.07 else "var(--line)")
        line, k = pat.subn(repl, line)
        n += k
    return line, n


def ensure_includes(text):
    """Fehlende Pflicht-Includes (tokens.css, base.css) vor nav.css/erstes <script> setzen."""
    changed = 0
    needs = []
    for css in ["tokens.css", "base.css"]:
        if not re.search(r'href\s*=\s*["\'][^"\']*' + re.escape(css), text):
            needs.append(css)
    if not needs:
        return text, 0
    # Pfadpräfix aus vorhandenem tokens/base/nav-Link ableiten, sonst design-system/.
    m = re.search(r'href\s*=\s*["\']([^"\']*?)(?:tokens|base|nav)\.css', text)
    prefix = m.group(1) if m else "design-system/"
    links = "".join(f'<link rel="stylesheet" href="{prefix}{c}" />\n' for c in needs)
    # vor nav.css einsetzen, sonst vor </head>.
    mnav = re.search(r'[ \t]*<link[^>]*nav\.css[^>]*>\n?', text)
    if mnav:
        text = text[:mnav.start()] + links + text[mnav.start():]
    else:
        text = re.sub(r"</head>", links + "</head>", text, count=1)
    return text, len(needs)


def process(path, apply, do_includes):
    full = open(os.path.join(ROOT, path), encoding="utf-8").read()
    out, in_script, total = [], False, 0
    for line in full.splitlines(keepends=True):
        low = line.lower()
        if "<script" in low:
            in_script = True
        if in_script:
            out.append(line)
            if "</script>" in low:
                in_script = False
            continue
        if "# ds-ok" in line or "url(" in low and "color" not in low:
            out.append(line); continue
        new, n = fix_line(line)
        total += n
        out.append(new)
    text = "".join(out)
    inc = 0
    if do_includes:
        text, inc = ensure_includes(text)
    if apply and (total or inc):
        open(os.path.join(ROOT, path), "w", encoding="utf-8").write(text)
    return total, inc, text, full


def tracked_html():
    out = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT, text=True)
    # Gleicher Geltungsbereich wie der Vertrag: Archiv/Referenz/Fremdcode in Ruhe lassen.
    skip = ("/assets/", "archive/", "reference/", "vendor/", "/tools/goetheanum-fontfix/")
    return [l for l in out.splitlines() if l.strip() and not any(s in l for s in skip)]


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    do_includes = "--include" in args or "--apply" in args
    if "--all" in args:
        files = tracked_html()
    else:
        files = [a for a in args if not a.startswith("--")]
    if not files:
        print("ds-fix: Dateien nennen oder --all. (Vorschau ohne --apply)")
        return 0
    grand = 0
    for path in sorted(set(files)):
        fp = os.path.join(ROOT, path)
        if not os.path.exists(fp):
            continue
        n, inc, newtext, old = process(path, apply, do_includes)
        if n or inc:
            grand += n + inc
            tag = col("geschrieben", "grn") if apply else col("Vorschau", "dim")
            print(f"{col(path,'b')}: {n} Farb-Swaps" + (f", {inc} Include(s)" if inc else "") + f"  [{tag}]")
            if not apply:
                # knappe Vorschau der geänderten Zeilen
                for o, nw in zip(old.splitlines(), newtext.splitlines()):
                    if o != nw:
                        print(col("   - " + o.strip()[:90], "dim"))
                        print(col("   + " + nw.strip()[:90], "grn"))
    print(col(f"\n∑ {grand} Korrekturen " + ("angewendet." if apply else "(Vorschau – mit --apply schreiben)."), "b"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

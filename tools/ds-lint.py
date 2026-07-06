#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum DS-Lint – prüft die GESTALT-Konformität jeder Seite gegen den Vertrag.

Symmetrisch zu tools/typo-check.py (Sprache): dieses Werkzeug erzwingt die
Struktur des Design-Systems, statt sie hinterher von Hand nachzukontrollieren.

Quelle der Wahrheit:  design-system/contract.json  (Regeln DS01–DS07).
Geltungsbereich:      versionierte *.html mit <body> (Werkzeug-/Schau-Seiten).
                      Reine Weiterleitungs-Stubs (meta refresh) werden übersprungen.
Geprüft wird nur CSS: <style>-Blöcke und style="…"-Attribute; <script> bleibt aussen
                      vor. Inline-SVG-Attribute (fill="…") sind Inhalt, kein Stil.

Nutzung:
  tools/ds-lint.py                 # Audit über ALLE Seiten + Score
  tools/ds-lint.py datei …         # nur genannte Seiten
  tools/ds-lint.py --staged        # nur vorgemerkte (staged) HTML (für den Hook)
  tools/ds-lint.py --score         # nur die Score-Zeile

Rückgabe: 1, sobald ein Verstoss der Schwere ‹fehler› bleibt (gate-fähig).
Hinweise (‹hinweis›) melden, blockieren aber nicht.  # ds-ok  überspringt eine Zeile.
"""
import sys, os, re, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT = os.path.join(ROOT, "design-system", "contract.json")

C = {"red": "\033[31m", "yel": "\033[33m", "grn": "\033[32m",
     "dim": "\033[2m", "b": "\033[1m", "x": "\033[0m"}
def col(s, c): return f"{C[c]}{s}{C['x']}" if sys.stdout.isatty() else s

SEV_COL = {"fehler": "red", "hinweis": "yel"}


def load_contract():
    with open(CONTRACT, encoding="utf-8") as f:
        return json.load(f)


def tracked_html():
    try:
        out = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT, text=True)
    except Exception:
        out = ""
    return [l for l in out.splitlines() if l.strip()]


def staged_html():
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], cwd=ROOT, text=True)
    except Exception:
        out = ""
    return [l for l in out.splitlines() if l.endswith(".html")]


def excluded(path, c):
    g = c["geltungsbereich"]
    if any(s in path for s in g["ausgenommen_substr"]):
        return True
    if path in g["ausgenommen_dateien"]:
        return True
    return False


def is_stub(text):
    """Reine Weiterleitung oder kein eigener Körper → nicht prüfen."""
    if "<body" not in text.lower():
        return True
    if re.search(r'http-equiv\s*=\s*["\']?refresh', text, re.I):
        return True
    return False


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


# --- CSS-Kontexte aus der Datei lösen -----------------------------------------
RE_STYLE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)
RE_SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)
RE_INLINE = re.compile(r'style\s*=\s*"([^"]*)"', re.I)
RE_ATRULE = re.compile(r"@(?:media|supports|keyframes)[^{]*\{", re.I)
RE_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)

HEXLIT = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGBLIT = re.compile(r"\brgba?\s*\(", re.I)
NAMED = re.compile(r"\b(white|black)\b", re.I)
FSPX = re.compile(r"font-size\s*:\s*([0-9.]+)px", re.I)


def css_blocks(text):
    """Liste (inhalt, abs_offset) aller <style>-Blöcke."""
    return [(m.group(1), m.start(1)) for m in RE_STYLE.finditer(text)]


def last_simple(selpart):
    """Letztes einfaches Selektor-Glied (für DS04-Schlüsselklasse)."""
    tok = selpart.strip().split()[-1] if selpart.strip().split() else ""
    return tok.split(":")[0]  # Pseudoklassen weg


def check_colors_sizes(body, base_off, full, findings, c, skip_lines):
    """DS02/DS03/DS07 auf einem Deklarations-Körper (Regel oder inline)."""
    ign = set(c["farben"]["ignorierte_properties"])
    forb = {l.lower() for l in c["theme"]["verbotene_literale"]}
    floor = c["groessen"]["untergrenze_px"]
    warnpx = c["groessen"]["warnen_unter_px"]
    # Deklarationen ~ getrennt durch ; (Körper enthält keine { } mehr)
    off = 0
    for raw in body.split(";"):
        seg_off = base_off + off
        off += len(raw) + 1
        if ":" not in raw:
            continue
        # seg_off auf den Property-Anfang rücken (führende Zeilenumbrüche/Leerraum
        # überspringen) – sonst landet die Zeile auf dem vorigen ‹;› (Mehrzeilen-CSS).
        lead = len(raw) - len(raw.lstrip("\n\r\t "))
        decl = raw.strip()
        seg_off += lead
        prop, _, val = decl.partition(":")
        p = prop.strip().lower()
        if not p or p.startswith("--"):
            continue
        ln = lineno(full, seg_off)
        if ln in skip_lines:
            continue
        # --- Größen (DS03) ---
        m = FSPX.search(decl)
        if m:
            px = float(m.group(1))
            if px < floor:
                findings.append((ln, "DS03", "fehler",
                                 f"font-size:{m.group(1)}px unter {floor}px (B03)"))
            elif px < warnpx:
                findings.append((ln, "DS03", "hinweis",
                                 f"font-size:{m.group(1)}px < {warnpx}px – besser Skala-Token (--t-small)"))
        # --- Farben (DS02/DS07): nur farbtragende Properties ---
        if p in ign or "url(" in val.lower():
            continue
        vlow = val.lower()
        hexes = HEXLIT.findall(val)
        named = NAMED.findall(val)
        has_rgb = bool(RGBLIT.search(val))
        if not (hexes or named or has_rgb):
            continue
        forb_hit = [h for h in hexes if h.lower() in forb] + \
                   [n for n in named if n.lower() in forb]
        if forb_hit:
            findings.append((ln, "DS07", "fehler",
                             f"{prop.strip()}: hartes {forb_hit[0]} statt Token (--paper/--ink/--soft)"))
        # übrige Hex/rgb-Farbwerte → DS02 (Schatten etc. sind oben ausgenommen)
        other = [h for h in hexes if h.lower() not in forb]
        if other or has_rgb:
            lit = other[0] if other else "rgb()"
            findings.append((ln, "DS02", "fehler",
                             f"{prop.strip()}: hartverdrahtete Farbe {lit} – var(--…) nutzen"))


def lint_file(path, c):
    full = open(os.path.join(ROOT, path), encoding="utf-8").read()
    if is_stub(full):
        return None  # übersprungen
    findings = []
    skip_lines = {lineno(full, m.start()) for m in re.finditer(r"#\s*ds-ok", full)}

    # DS01 – Pflicht-Includes
    for inc in c["includes"]["pflicht"]:
        base = os.path.basename(inc)
        if not re.search(r'href\s*=\s*["\'][^"\']*' + re.escape(base), full):
            findings.append((1, "DS01", "fehler", f"Pflicht-Include fehlt: {inc}"))

    # DS06 – eigene Kopfzeile / Fake-Logo (nur wenn nav.js NICHT eingebunden).
    # `# ds-ok` auf der <header>-Zeile ratifiziert die Ausnahme (z. B. der
    # Nachbau einer fremden Kopfzeile auf den Perspektiven-Seiten).
    has_nav = bool(re.search(r'nav\.js', full))
    if not has_nav and re.search(r"<header\b", full, re.I):
        header_ln = lineno(full, re.search(r"<header\b", full, re.I).start())
        if header_ln not in skip_lines:
            findings.append((header_ln,
                             "DS06", "hinweis", "eigene <header>-Kopfzeile ohne nav.js – Fundament-Leiste nutzen"))

    # CSS-Kontexte (Blöcke + inline) – ohne <script>
    scriptless = RE_SCRIPT.sub(lambda m: "\n" * m.group(0).count("\n"), full)
    canon = set(c["rollen"]["kanonische_klassen"])
    emph_sel = re.compile(r"\b(strong|b|i|em|h[1-4]|body)\b|\.(kicker|kick|lede|note|hint)")

    for content, off in css_blocks(scriptless):
        cleaned = RE_ATRULE.sub(lambda m: " " * len(m.group(0)), content)
        for rm in RE_RULE.finditer(cleaned):
            sel, body = rm.group(1), rm.group(2)
            body_off = off + rm.start(2)
            check_colors_sizes(body, body_off, scriptless, findings, c, skip_lines)
            sel_ln = lineno(scriptless, off + rm.start(1))
            if sel_ln in skip_lines:
                continue
            # DS04 – kanonische Rolle lokal redefiniert? Nur SCHLÜSSEL-Selektoren
            # (bare/compound), nicht kontextuelle Überschreibungen (`.download .btn`
            # ist legitim – das ist Verortung, keine Neudefinition der Rolle).
            if "font-size" in body or re.search(r"\bcolor\s*:", body):
                for part in sel.split(","):
                    if re.search(r"[ >+~]", part.strip()):
                        continue  # Nachfahren-Selektor = Verortung, kein Redefinieren
                    classes = set(re.findall(r"\.([A-Za-z][\w-]*)", part))
                    if classes & canon:
                        hit = sorted(classes & canon)[0]
                        findings.append((sel_ln, "DS04", "hinweis",
                                         f".{hit} lokal redefiniert – kanonische Rolle aus base.css nutzen"))
                        break
            # DS05 – verbotene Hervorhebung
            if "text-transform" in body and "uppercase" in body:
                findings.append((sel_ln, "DS05", "hinweis",
                                 f"text-transform:uppercase ({sel.strip()[:32]}) – Versal nicht als Hervorhebung (G05)"))
            if "underline" in body and emph_sel.search(sel):
                findings.append((sel_ln, "DS05", "hinweis",
                                 f"underline auf Betonung ({sel.strip()[:32]}) – Laut statt Unterstrich (G05)"))

    # Inline-styles im Markup
    for m in RE_INLINE.finditer(scriptless):
        check_colors_sizes(m.group(1), m.start(1), scriptless, findings, c, skip_lines)

    findings.sort(key=lambda f: (f[0], f[1]))
    return findings


def main():
    args = [a for a in sys.argv[1:]]
    c = load_contract()
    only_score = "--score" in args
    args = [a for a in args if a != "--score"]

    if "--staged" in args:
        files = staged_html()
    elif args:
        files = args
    else:
        files = tracked_html()
    files = [f for f in files if not excluded(f, c)]

    checked = 0
    conformant = 0
    total_err = 0
    total_warn = 0
    by_rule = {}
    report = []

    for path in sorted(set(files)):
        fp = os.path.join(ROOT, path)
        if not os.path.exists(fp):
            continue
        res = lint_file(path, c)
        if res is None:
            continue  # Stub
        checked += 1
        errs = [f for f in res if f[2] == "fehler"]
        warns = [f for f in res if f[2] == "hinweis"]
        total_err += len(errs)
        total_warn += len(warns)
        for ln, rid, sev, msg in res:
            by_rule[rid] = by_rule.get(rid, 0) + 1
        if not errs:
            conformant += 1
        if res:
            report.append((path, res))

    if not only_score:
        for path, res in report:
            print(col(path, "b"))
            for ln, rid, sev, msg in res:
                tag = col(f"{rid} {sev}", SEV_COL.get(sev, "dim"))
                print(f"  {col(str(ln).rjust(4),'dim')}  {tag}  {msg}")
            print()

    score = (conformant / checked) if checked else 1.0
    bar = "█" * round(score * 24) + "·" * (24 - round(score * 24))
    print(col("── Konformität ─────────────────────────────────────────", "dim"))
    print(f"  Seiten geprüft:   {checked}")
    print(f"  konform (0 Fehler): {conformant}")
    print(f"  Verstöße:         {col(str(total_err),'red')} Fehler · {col(str(total_warn),'yel')} Hinweise")
    if by_rule:
        order = sorted(by_rule.items(), key=lambda kv: kv[0])
        print("  je Regel:         " + " · ".join(f"{k} {v}" for k, v in order))
    pct = f"{score*100:.0f}%"
    print(f"  Score:            {col(bar,'grn' if score==1 else 'yel')} {col(pct,'b')}")
    print(col("────────────────────────────────────────────────────────", "dim"))

    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())

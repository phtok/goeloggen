#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum Typo-Check – führt die Hausregeln aus, statt sie hinterher zu prüfen.

Quelle der Wahrheit:  assets/typografie/typo-regeln.yaml  (erkennen/korrektur/schwere).
Geltungsbereich:      deutscher Lesetext (de-CH) auf der publizierten HTML-Fläche.
                      Interne Doku-Markdown nur auf ausdrückliche Nennung.
Ausgenommen:          Code, <script>/<style>/<pre>/<code>, Kommentare, URLs, E-Mails.

Nutzung:
  tools/typo-check.py                 # prüft die vorgemerkten (staged) HTML-Dateien
  tools/typo-check.py datei …         # prüft genannte Dateien (auch .md/.txt)
  tools/typo-check.py --all           # prüft alle versionierten .html (Audit)
  tools/typo-check.py --fix datei …   # wendet eindeutige Korrekturen an (nur Vorschau-Hilfe)

Rückgabe: 1, sobald ein Verstoss der Schwere ‹fehler› bleibt (blockiert den Commit).
Empfehlungen werden gemeldet, blockieren aber nicht. Mit  # typo-ok  in einer Zeile
wird diese Zeile übersprungen.
"""
import sys, os, re, html, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGELN = os.path.join(ROOT, "assets", "typografie", "typo-regeln.yaml")

# Pfade, die kein Mitarbeitenden-Lesetext sind (Werkstatt, Fremdcode, Sammlungen).
EXCLUDE_SUBSTR = ("/archive/", "/assets/vendor/", "/collections/", "/tools/goetheanum-fontfix/")
EXCLUDE_BASENAMES = {
    # Werkstatt / Font-Entwicklung – kein Mitarbeiter-Lesetext.
    "proof.html", "kerning.html", "ineinander.html", "zuordnen.html",
    "ligvorschau.html", "werkzeug.html", "tester.html",
    # Lehr-/Specimen-Seiten: zeigen absichtlich ‹so nicht›-Gegenbeispiele.
    "typografie.html", "vorschau.html", "schrift-vergleich.html",
}

C = {"red":"\033[31m","yel":"\033[33m","grn":"\033[32m","dim":"\033[2m","b":"\033[1m","x":"\033[0m"}
def col(s,c): return f"{C[c]}{s}{C['x']}" if sys.stdout.isatty() else s


def load_rules(path):
    """Mini-Parser für die flache Liste in typo-regeln.yaml – ohne PyYAML-Abhängigkeit.
    Versucht zuerst PyYAML; fällt sonst auf einen gezielten Parser zurück."""
    text = open(path, encoding="utf-8").read()
    try:
        import yaml  # optional
        items = yaml.safe_load(text)
        return [r for r in items if isinstance(r, dict)]
    except Exception:
        pass
    rules, cur = [], None
    for line in text.splitlines():
        if re.match(r"\s*#", line) or not line.strip():
            continue
        m = re.match(r"-\s+(\w+):\s*(.*)$", line)
        if m:
            if cur: rules.append(cur)
            cur = {}
            key, val = m.group(1), m.group(2)
            cur[key] = _scalar(val)
            continue
        m = re.match(r"\s+(\w+):\s*(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = _scalar(m.group(2))
    if cur: rules.append(cur)
    return rules


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        inner = v[1:-1]
        return inner.replace("''", "'") if v[0] == "'" else inner
    return v


# --- Sichtbaren Lesetext aus HTML herauslösen ---------------------------------
# Nicht-Lesetext: Skripte, Stile, Code-Beispiele und Kommentare. Wird entfernt,
# Zeilenumbrüche bleiben erhalten, damit die Zeilennummern stimmen.
STRIP_BLOCKS = re.compile(r"<(script|style|pre|code|kbd|samp)\b[^>]*>.*?</\1>", re.S | re.I)
COMMENTS     = re.compile(r"<!--.*?-->", re.S)
TAGS         = re.compile(r"<[^>]+>")
URL          = re.compile(r"https?://\S+|\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

def _keep_lines(m):
    return "\n" * m.group(0).count("\n")

def visible_text(path, raw):
    if path.endswith((".md", ".markdown", ".txt")):
        # In Markdown Code-Spannen/Blöcke ausnehmen.
        raw = re.sub(r"```.*?```", _keep_lines, raw, flags=re.S)
        raw = re.sub(r"`[^`]*`", " ", raw)
        out = []
        for i, ln in enumerate(raw.splitlines()):
            t = URL.sub(" ", ln)
            # Leerraum kollabieren – Markdown-Tabellen, Einrückung und Listen-Marker
            # erzeugen Mehrfach-Leerraum, der gerendert kollabiert (sonst T01 falsch).
            t = re.sub(r"[ \t]+", " ", t)
            out.append((i + 1, t))
        return out
    # HTML: Code-/Skript-Blöcke und Kommentare entfernen, dann Tags.
    cleaned = STRIP_BLOCKS.sub(_keep_lines, raw)
    cleaned = COMMENTS.sub(_keep_lines, cleaned)
    # Absichtliche Gegenbeispiele (data-typo-ignore, Konvention wie typo_lint.py):
    # das Element samt Inhalt ausnehmen – z. B. eine durchgestrichene
    # Falsch-Anführung in einem Empfehlungs-Piktogramm.
    cleaned = re.sub(r"<(\w+)([^>]*\bdata-typo-ignore\b[^>]*)>.*?</\1>",
                     _keep_lines, cleaned, flags=re.S)
    out = []
    for i, ln in enumerate(cleaned.splitlines()):
        t = html.unescape(TAGS.sub(" ", ln))
        t = URL.sub(" ", t)
        # Leerraum kollabieren – der Browser tut es ebenso; verhindert Phantom-
        # Doppelspatien aus dem Tag-Strippen (T01 bliebe sonst falsch positiv).
        t = re.sub(r"[ \t]+", " ", t)
        out.append((i + 1, t))
    return out


def to_py(repl):
    return re.sub(r"\$(\d+)", r"\\\1", repl)


def check_file(path, rules, fix=False):
    rel = os.path.relpath(path, ROOT)
    raw = open(path, encoding="utf-8").read()
    lines = visible_text(path, raw)
    findings = []
    for lineno, text in lines:
        if "typo-ok" in text:
            continue
        for r in rules:
            if r.get("pruefung") == "lm" or "erkennen" not in r:
                continue
            try:
                pat = re.compile(r["erkennen"])
            except re.error:
                continue
            for m in pat.finditer(text):
                snippet = m.group(0).strip()
                if not snippet:
                    continue
                fixed = pat.sub(to_py(r.get("korrektur", "")), snippet) if r.get("korrektur") else ""
                findings.append((lineno, r.get("id","?"), r.get("schwere","empfehlung"),
                                 r.get("regel",""), snippet, fixed))
    return rel, findings


def excluded(path):
    p = path.replace("\\", "/")
    if any(s in p for s in EXCLUDE_SUBSTR):
        return True
    return os.path.basename(p) in EXCLUDE_BASENAMES


def git_files(args):
    # Auto-Modus prüft nur die publizierte Lesefläche (HTML). Interne Doku-Markdown
    # (CLAUDE.md, README, Strategie) ist keine gesetzte Fläche und nutzt bewusst
    # eigene Konventionen – sie wird nur auf ausdrückliche Nennung geprüft.
    if "--all" in args:
        out = subprocess.run(["git","-C",ROOT,"ls-files","*.html"],
                             capture_output=True, text=True).stdout
    else:
        out = subprocess.run(["git","-C",ROOT,"diff","--cached","--name-only","--diff-filter=ACM"],
                             capture_output=True, text=True).stdout
    files = []
    for f in out.splitlines():
        if f.endswith(".html"):
            files.append(os.path.join(ROOT, f))
    return files


def main():
    args = sys.argv[1:]
    fix = "--fix" in args
    explicit = [a for a in args if not a.startswith("--")]
    if explicit:
        files = [os.path.abspath(f) for f in explicit]
    else:
        files = git_files(args)
    files = [f for f in files if os.path.isfile(f) and not excluded(f)]

    if not files:
        print(col("Typo-Check: keine zu prüfenden Dateien.", "dim"))
        return 0

    rules = load_rules(REGELN)
    n_fehler = n_empf = 0
    for f in files:
        rel, findings = check_file(f, rules, fix)
        if not findings:
            continue
        print(col(f"\n{rel}", "b"))
        for lineno, rid, schwere, regel, snip, fixed in findings:
            is_err = (schwere == "fehler")
            tag = col("FEHLER", "red") if is_err else col("Hinweis", "yel")
            arrow = f"  →  {col(fixed,'grn')}" if fixed and fixed != snip else ""
            print(f"  {tag}  Z{lineno}  {col(rid,'b')}  ‹{snip}›{arrow}")
            print(col(f"        {regel}", "dim"))
            if is_err: n_fehler += 1
            else:      n_empf += 1

    print()
    if n_fehler:
        print(col(f"✗ {n_fehler} Fehler", "red") + (f", {n_empf} Hinweise" if n_empf else "") +
              " – Commit blockiert. Bitte beheben (oder Zeile mit  # typo-ok  ausnehmen).")
        return 1
    if n_empf:
        print(col(f"✓ keine Fehler", "grn") + f", {n_empf} Hinweis(e) – Commit erlaubt.")
        return 0
    print(col("✓ Typografie konform.", "grn"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

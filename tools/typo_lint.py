#!/usr/bin/env python3
"""Goetheanum-Typografie-Linter.

Liest die Hausregeln aus assets/typografie/typo-regeln.yaml und prueft den
SICHTBAREN deutschen Lesetext der HTML-Seiten. Code/Style/Script/URLs/E-Mails
werden ausgenommen (so verlangt es das Regelwerk). Nur die regex-pruefbaren
Regeln (`erkennen`) laufen hier; `pruefung: lm` (Urteilsregeln) werden gelistet,
aber nicht automatisch geprueft.

Teilbaeume mit  data-typo-ignore  (z. B. absichtliche Gegenbeispiele in
Lehr-/Specimen-Seiten) werden uebersprungen.
"""
import sys, os, re, json, glob
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(ROOT, "assets/typografie/typo-regeln.yaml")

SKIP_TAGS = {"script", "style", "code", "pre", "kbd", "samp", "textarea", "svg"}
URL_RE = re.compile(r"(https?://\S+|www\.\S+|\b[\w.+-]+@[\w.-]+\.\w+)")

def load_rules(path):
    """Minimaler Parser fuer die flache YAML-Liste (kein pyyaml noetig)."""
    rules, cur = [], None
    def unquote(v):
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            inner = v[1:-1]
            if v[0] == "'":
                inner = inner.replace("''", "'")  # YAML-Single-Quote-Escape
            return inner
        return v
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- "):
            if cur:
                rules.append(cur)
            cur = {}
            line = line.lstrip()[2:]
        if ":" in line:
            k, _, v = line.lstrip().partition(":")
            cur[k.strip()] = unquote(v)
    if cur:
        rules.append(cur)
    return rules

class Extractor(HTMLParser):
    """Sammelt sichtbare Textknoten mit Zeilennummer; ueberspringt SKIP_TAGS
    und alles unter data-typo-ignore."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.ignore_depth = 0
        self.stack = []          # (tag, opened_ignore)
        self.chunks = []         # (line, text)
    def handle_starttag(self, tag, attrs):
        if tag in ("br", "img", "hr", "input", "meta", "link"):
            return
        opened_ignore = any(a[0] == "data-typo-ignore" for a in attrs)
        if opened_ignore:
            self.ignore_depth += 1
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        self.stack.append((tag, opened_ignore, tag in SKIP_TAGS))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            t, oi, sk = self.stack[i]
            if t == tag:
                if oi:
                    self.ignore_depth -= 1
                if sk:
                    self.skip_depth -= 1
                del self.stack[i]
                break
    def handle_data(self, data):
        if self.skip_depth or self.ignore_depth:
            return
        if not data.strip():
            return
        line = self.getpos()[0]
        text = re.sub(r"\s+", " ", data)   # HTML-Whitespace kollabiert
        self.chunks.append((line, text))

def lint_file(path, rules):
    html = open(path, encoding="utf-8").read()
    ex = Extractor()
    ex.feed(html)
    findings = []
    for line, text in ex.chunks:
        masked = URL_RE.sub(lambda m: " " * len(m.group(0)), text)  # URLs/Mail raus
        for r in rules:
            pat = r.get("erkennen")
            if not pat:
                continue
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            for m in rx.finditer(masked):
                snip = text[max(0, m.start() - 18): m.end() + 18].strip()
                findings.append({
                    "rule": r["id"], "schwere": r.get("schwere", "?"),
                    "line": line, "match": m.group(0), "context": snip,
                    "regel": r.get("regel", ""),
                })
    return findings

def main():
    as_json = "--json" in sys.argv
    rules = load_rules(RULES_PATH)
    regex_rules = [r for r in rules if r.get("erkennen")]
    lm_rules = [r for r in rules if r.get("pruefung") == "lm"]
    targets = sorted(glob.glob(os.path.join(ROOT, "*.html"))) + \
              sorted(glob.glob(os.path.join(ROOT, "apps/*/index.html"))) + \
              sorted(glob.glob(os.path.join(ROOT, "start/*.html")))
    report = {}
    total = n_fehler = 0
    for path in targets:
        f = lint_file(path, rules)
        if f:
            report[os.path.relpath(path, ROOT)] = f
            total += len(f)
            n_fehler += sum(1 for x in f if x["schwere"] == "fehler")
    out = {
        "regex_rules": [r["id"] for r in regex_rules],
        "lm_rules": [r["id"] for r in lm_rules],
        "files_scanned": len(targets),
        "files_with_findings": len(report),
        "total_findings": total,
        "fehler": n_fehler,
        "report": report,
    }
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"Typo-Lint: {len(targets)} Seiten · {total} Treffer "
              f"({n_fehler} Fehler, {total - n_fehler} Empfehlungen)\n")
        for f, fs in report.items():
            print(f"  {f}")
            for x in sorted(fs, key=lambda x: (x["schwere"] != "fehler", x["line"])):
                mark = "✗" if x["schwere"] == "fehler" else "·"
                print(f"    {mark} {x['rule']:18} L{x['line']:<4} «{x['match']}»  {x['regel'][:60]}")
        print(f"\n{'FEHLER gefunden — Lesetext korrigieren oder data-typo-ignore.' if n_fehler else 'Keine Fehler. (Empfehlungen sind unverbindlich.)'}")
    # CI: Exit 1 nur bei harten Fehlern; Empfehlungen blockieren nicht.
    sys.exit(1 if n_fehler else 0)

if __name__ == "__main__":
    main()

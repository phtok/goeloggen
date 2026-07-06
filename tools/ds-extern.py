#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum DS-Extern – Konformitäts-Schnellbefund für FREMDE Seiten (per URL).

Ergänzt tools/ds-lint.py (der den eigenen Vertrag DS01–DS07 an eigenen Seiten
erzwingt) um einen Aussenblick: Was davon lässt sich an einer beliebigen,
live laufenden Seite MASCHINELL belegen? Geprüft wird nur, was aus HTML+CSS
statisch ablesbar ist — gerechnet, nicht geschätzt; was ein Urteil bräuchte
(z. B. Kontrast konkreter Text/Grund-Paare im Render), bleibt draussen.

Prüfungen (je Seite, bestanden/nicht bestanden → Score):
  E01 Fundament     tokens.css/base.css von werkzeuge.goetheanum.ch eingebunden?
  E02 Tokens        Farb-Literale (hex/rgb) vs. var(--…)-Nutzung in Farb-Properties (DS02)
  E03 Grössen       font-size unter 14px (B03) — Anzahl + kleinster Wert
  E04 Zeilenhöhe    line-height an body/html/p < 1.5 (B04)
  E05 Fokus         outline:none/0 vorhanden? :focus-visible vorhanden? (WCAG 2.4.7)
  E06 Sprunglink    ‹Zum Inhalt›/Skip-Link am Seitenanfang (WCAG 2.4.1)
  E07 Sprache       lang-Attribut am <html> (WCAG 3.1.1)
  E08 Versal-UI     text-transform:uppercase im CSS (G05/G23-Indikator)
  E09 Hell/Dunkel   prefers-color-scheme im CSS (B05)
  E10 Schriften     externe Font-Hosts (Google Fonts u. a.) — Selbst-Hosting?
  E11 Alt-Kultur    <img> ohne alt bzw. mit generischem alt (Image/Bild/Foto)
  E12 Auffindbar    meta robots noindex auf der Seite?

Nutzung:
  tools/ds-extern.py URL [URL …]           # Befund + Score je Seite
  tools/ds-extern.py --md AUSGABE.md URL …  # zusätzlich Markdown-Bericht schreiben

Netz: nutzt die Umgebungs-Proxys; lädt je Seite bis zu 6 verlinkte Stylesheets.
"""
import sys, os, re, ssl, urllib.request, urllib.parse, datetime

UA = "Mozilla/5.0 (kompatibel; Goetheanum-DS-Extern/1.0; +https://werkzeuge.goetheanum.ch)"
MAXB = 1_600_000
C = {"red": "\033[31m", "yel": "\033[33m", "grn": "\033[32m", "dim": "\033[2m", "b": "\033[1m", "x": "\033[0m"}
def col(s, c): return f"{C[c]}{s}{C['x']}" if sys.stdout.isatty() else s

RE_STYLE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)
RE_LINKCSS = re.compile(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]*>', re.I)
RE_HREF = re.compile(r'href=(?:["\']([^"\']+)["\']|([^\s>"\']+))', re.I)   # auch unzitierte hrefs (minifiziertes HTML)
RE_INLINE = re.compile(r'style\s*=\s*"([^"]*)"', re.I)
RE_IMG = re.compile(r"<img\b[^>]*>", re.I)
RE_ALT = re.compile(r'alt\s*=\s*["\']([^"\']*)["\']', re.I)
RE_LANG = re.compile(r"<html\b[^>]*\blang\s*=\s*[\"']([^\"']+)[\"']", re.I)
RE_NOIDX = re.compile(r'<meta[^>]+name=["\']?robots["\']?[^>]+noindex', re.I)
FSPX = re.compile(r"font-size\s*:\s*([0-9.]+)px", re.I)
LHNUM = re.compile(r"(?:^|[,{\s])(?:html|body|p)\s*(?:,[^{]*)?\{[^}]*?line-height\s*:\s*([0-9.]+)\s*[;}]", re.I | re.S)
HEXLIT = re.compile(r"(?:color|background|background-color|border(?:-\w+)?-color|fill|stroke)\s*:[^;{}]*?(#[0-9a-fA-F]{3,8}\b|rgba?\s*\()", re.I)
VARUSE = re.compile(r"var\(--")
UPPER = re.compile(r"text-transform\s*:\s*uppercase", re.I)
OUTNONE = re.compile(r"outline\s*:\s*(?:none|0)\b", re.I)
FOCVIS = re.compile(r":focus-visible", re.I)
PCS = re.compile(r"prefers-color-scheme", re.I)
EXTFONT = re.compile(r"fonts\.googleapis|fonts\.gstatic|use\.typekit|fast\.fonts", re.I)
SKIP = re.compile(r'<a[^>]+href=["\']#[^"\']*["\'][^>]*>[^<]*(?:zum inhalt|skip|inhalt überspringen|main content)', re.I)
FUND = re.compile(r"werkzeuge\.goetheanum\.ch/design-system/(?:tokens|base)\.css")

def fetch(url, binary=False):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de,en"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        data = r.read(MAXB)
    return data if binary else data.decode("utf-8", "replace")

def collect(url):
    html = fetch(url)
    css = "\n".join(RE_STYLE.findall(html))
    css += "\n" + "\n".join(RE_INLINE.findall(html))
    geladen = []
    for tag in RE_LINKCSS.findall(html)[:6]:
        m = RE_HREF.search(tag)
        if not m: continue
        cu = urllib.parse.urljoin(url, m.group(1) or m.group(2))
        try:
            css += "\n" + fetch(cu); geladen.append(cu)
        except Exception:
            pass
    return html, css, geladen, len(RE_LINKCSS.findall(html))

def pruefe(url):
    html, css, sheets, linktags = collect(url)
    f = []  # (id, bestanden|None=nicht prüfbar, detail)
    # CSS-Urteil nur, wenn die Stylesheets überwiegend ladbar waren (sonst wäre
    # ‹0 Treffer› kein Befund, sondern Blindheit).
    css_ok = len(css.strip()) >= 1000 and (linktags == 0 or len(sheets) >= max(1, (min(linktags, 6) + 1) // 2))

    f.append(("E01 Fundament", bool(FUND.search(html)),
              "tokens/base von werkzeuge.goetheanum.ch eingebunden" if FUND.search(html)
              else "Fundament nicht eingebunden (DS01-extern: der eigentliche Auftrag)"))

    if not css_ok:
        for fid in ("E02 Tokens", "E03 Grössen", "E04 Zeilenhöhe", "E05 Fokus", "E08 Versal-UI", "E09 Hell/Dunkel"):
            f.append((fid, None, "Stylesheets nicht ladbar — nicht prüfbar"))

    lits = len(HEXLIT.findall(css)); vars_ = len(VARUSE.findall(css))
    if css_ok:
        f.append(("E02 Tokens", lits == 0 or vars_ > lits,
              f"{lits} Farb-Literale in Farb-Properties · {vars_}× var(--…) (DS02)"))

    px = sorted(float(m) for m in FSPX.findall(css))
    unter = [p for p in px if p < 14]
    if css_ok: f.append(("E03 Grössen", not unter,
              (f"{len(unter)}× font-size unter 14px, kleinste {unter[0]:g}px (B03)" if unter
               else f"kleinste font-size {px[0]:g}px (B03 eingehalten)" if px else "keine px-Grössen gefunden")))

    lhs = [float(m) for m in LHNUM.findall(css)]
    schlecht = [v for v in lhs if v < 1.5]
    if css_ok: f.append(("E04 Zeilenhöhe", not schlecht,
              (f"line-height {min(schlecht):g} an body/html/p (B04: ≥1.5)" if schlecht
               else "body/p-Zeilenhöhen ≥1.5 (B04)" if lhs else "keine numerische body/p-Zeilenhöhe gefunden")))

    on = len(OUTNONE.findall(css)); fv = bool(FOCVIS.search(css))
    if css_ok: f.append(("E05 Fokus", on == 0 and fv,
              f"{on}× outline:none/0 · :focus-visible {'vorhanden' if fv else 'fehlt'} (WCAG 2.4.7)"))

    f.append(("E06 Sprunglink", bool(SKIP.search(html[:20000])),
              "Skip-Link am Seitenanfang" if SKIP.search(html[:20000]) else "kein Sprunglink gefunden (WCAG 2.4.1)"))

    lm = RE_LANG.search(html)
    f.append(("E07 Sprache", bool(lm), f"lang=\"{lm.group(1)}\"" if lm else "kein lang-Attribut am <html> (WCAG 3.1.1)"))

    up = len(UPPER.findall(css))
    if css_ok: f.append(("E08 Versal-UI", up == 0, f"{up}× text-transform:uppercase (G05/G23-Indikator)"))

    if css_ok: f.append(("E09 Hell/Dunkel", bool(PCS.search(css)),
              "prefers-color-scheme vorhanden" if PCS.search(css) else "kein Hell/Dunkel-Mechanismus im CSS (B05)"))

    ext = bool(EXTFONT.search(html) or EXTFONT.search(css))
    f.append(("E10 Schriften", not ext,
              "externe Font-Hosts (Google Fonts u. a.) — Selbst-Hosting empfohlen" if ext else "Schriften selbst gehostet"))

    imgs = RE_IMG.findall(html); ohne = 0; generisch = 0
    for tag in imgs:
        m = RE_ALT.search(tag)
        if not m: ohne += 1
        elif m.group(1).strip().lower() in ("image", "bild", "foto", "img", "photo"): generisch += 1
    f.append(("E11 Alt-Kultur", ohne == 0 and generisch == 0,
              f"{len(imgs)} Bilder · {ohne} ohne alt · {generisch} generisch (WCAG 1.1.1)"))

    f.append(("E12 Auffindbar", not RE_NOIDX.search(html),
              "meta robots noindex — Seite schliesst sich von Suche aus" if RE_NOIDX.search(html) else "indexierbar"))

    return f, sheets

def bar(p):
    n = round(p / 100 * 24)
    return "█" * n + "·" * (24 - n)

def main():
    args = sys.argv[1:]
    md_out = None
    if args[:1] == ["--md"]:
        md_out = args[1]; args = args[2:]
    if not args:
        print(__doc__); return 0
    MONATE = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    heute = datetime.date.today()
    md = [f"# Webfamilie – maschineller Konformitäts-Schnellbefund\n",
          f"Erzeugt von `tools/ds-extern.py` am {heute.day}. {MONATE[heute.month-1]} {heute.year}. "
          "Geprüft wird nur statisch Belegbares (HTML + bis zu 6 Stylesheets je Seite); "
          "gerenderte Kontrast-Paare u. Ä. stehen im Hand-Befund `webfamilie-befund.md`.\n"]
    zeilen = []
    for url in args:
        print(col(f"\n── {url} ", "b") + col("─" * max(4, 60 - len(url)), "dim"))
        try:
            fnd, sheets = pruefe(url)
        except Exception as e:
            print(col(f"  Abruf fehlgeschlagen: {e}", "red"))
            zeilen.append((url, None)); continue
        fnd.sort(key=lambda t: t[0])
        wert = [(i, b, d) for i, b, d in fnd if b is not None]
        ok = sum(1 for _, b, _ in wert if b)
        for fid, b, detail in fnd:
            mark = col("·", "dim") if b is None else (col("✓", "grn") if b else col("✗", "red"))
            print(f"  {mark} {fid:14s} {detail}")
        p = round(100 * ok / max(1, len(wert)))
        print(col(f"  Score: {bar(p)} {p}%  ({ok}/{len(wert)} prüfbar)", "b"))
        zeilen.append((url, (ok, len(wert), p, fnd)))
    if md_out:
        md.append("| Seite | Score | bestanden |\n|---|---|---|")
        for url, r in zeilen:
            md.append(f"| {url} | {'—' if r is None else str(r[2]) + ' %'} | {'—' if r is None else f'{r[0]}/{r[1]} prüfbar'} |")
        for url, r in zeilen:
            if r is None: continue
            md.append(f"\n## {url}\n")
            for fid, b, detail in r[3]:
                md.append(f"- {'·' if b is None else ('✓' if b else '✗')} **{fid}** — {detail}")
        with open(md_out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(md) + "\n")
        print(col(f"\nBericht geschrieben: {md_out}", "dim"))
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goetheanum DS-Lint – prüft die GESTALT-Konformität jeder Seite gegen den Vertrag.

Symmetrisch zu tools/typo-check.py (Sprache): dieses Werkzeug erzwingt die
Struktur des Design-Systems, statt sie hinterher von Hand nachzukontrollieren.

Quelle der Wahrheit:  design-system/contract.json  (Regeln DS01–DS10).
Geltungsbereich:      versionierte *.html mit <body> (Werkzeug-/Schau-Seiten).
                      Reine Weiterleitungs-Stubs (meta refresh) werden übersprungen.
Geprüft wird CSS aus: <style>-Blöcke, style="…"-Attribute UND repo-eigene,
                      per <link href="…css"> eingebundene *.css-Dateien (DS02/03/
                      04/05/07 – derselbe Auflösungsweg wie DS10/check_tokens;
                      externe/absolute URLs bleiben aussen vor, das Repo kann sie
                      nicht sehen). Jede verlinkte Datei wird GENAU EINMAL geprüft,
                      unabhängig davon, wie viele Seiten sie einbinden (sonst meldet
                      base.css seinen Verstoss 60-mal) – siehe lint_css_file().
                      <script> bleibt aussen vor. Inline-SVG-Attribute (fill="…")
                      sind Inhalt, kein Stil.
Blinder Fleck (Befund Konrad, 8.9.2026): bis 1.17.0 sahen DS02–DS05/DS07 nur die
                      HTML-Datei selbst – eine Seite, deren gesamte Gestalt in
                      einer eigenen verlinkten CSS-Datei steht, meldete «0 Fehler»,
                      ohne dass dort geprüft wurde. Geschlossen in 1.18.0.

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
    # Staged/Audit-Pfade kommen relativ ("assets/…") – für die Substring-
    # Ausnahmen ("/assets/") wie absolute behandeln, sonst greifen sie nie.
    p = "/" + path.lstrip("./")
    if any(s in p for s in g["ausgenommen_substr"]):
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
RE_COMMENT = re.compile(r"/\*.*?\*/", re.S)
RE_LINK_CSS = re.compile(r'<link[^>]+href\s*=\s*["\']([^"\']+\.css)["\']', re.I)

HEXLIT = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGBLIT = re.compile(r"\brgba?\s*\(", re.I)
NAMED = re.compile(r"\b(white|black)\b", re.I)
FSPX = re.compile(r"font-size\s*:\s*([0-9.]+)px", re.I)


def css_blocks(text):
    """Liste (inhalt, abs_offset) aller <style>-Blöcke."""
    return [(m.group(1), m.start(1)) for m in RE_STYLE.finditer(text)]


def strip_comments(text):
    """CSS-Kommentare zu Leerraum – Zeilenumbrüche bleiben stehen, sonst
    verschieben sich alle Zeilennummern nach dem ersten Kommentar.

    Ohne das liest »--blue-solid:#0061a9; /* Volles Blau … */« als EINE
    Deklaration, deren nächster ';'-Abschnitt bei der Property-Erkennung mit
    dem Kommentartext verklebt (»/* Volles Blau … */\\n --gold-deep« beginnt
    nicht mit »--« und rutscht durch den Custom-Property-Filter). tokens.css
    hat genau dieses Muster durchgehend – beim ersten Mitlesen verlinkter
    Fundament-CSS wären seine Definitionen reihenweise als Verstösse
    erschienen, ohne dass irgendwo ein echter steckt."""
    def repl(m):
        s = m.group(0)
        return "".join(ch if ch == "\n" else " " for ch in s)
    return RE_COMMENT.sub(repl, text)


def linked_css(full, path):
    """Repo-eigene, per <link href="…css"> eingebundene CSS-Dateien einer Seite,
    zu repo-relativen Pfaden aufgelöst – derselbe Weg, den check_tokens/DS10
    für die Token-Auflösung schon nutzt (hier für DS02/03/04/05/07 wiederverwendet,
    kein zweiter Mechanismus). Externe/absolute/Daten-URLs bleiben aussen vor:
    was nicht im Repo liegt, kann die Maschine nicht mitlesen."""
    out = []
    for rel in RE_LINK_CSS.findall(full):
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:)?//", rel, re.I) or rel.lower().startswith("data:"):
            continue
        kandidat = os.path.normpath(os.path.join(os.path.dirname(os.path.join(ROOT, path)), rel))
        if not os.path.exists(kandidat):
            continue
        try:
            if os.path.commonpath([kandidat, ROOT]) != ROOT:
                continue  # aus dem Repo heraus verlinkt – nicht mitprüfbar
        except ValueError:
            continue  # anderes Laufwerk (Windows) – kann hier nicht vorkommen, sicherheitshalber
        out.append(os.path.relpath(kandidat, ROOT))
    return out


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


_TOKENS = None
def bekannte_tokens():
    """Alle im Fundament definierten Custom Properties.

    Grund für DS10: CSS löst ein unbekanntes Token STILL zu nichts auf. Aus
    »padding:var(--s5)« wird »padding:0«, ohne Fehler, ohne Warnung – am
    9. August 2026 klebte deshalb im Sommer-Bericht die Schrift auf der
    Kartenkante, und 13 Dateien im Repo griffen nach derselben fehlenden
    Sprosse. Ein Wert, der schweigend verschwindet, ist schlimmer als einer,
    der bricht: Niemand sucht danach."""
    global _TOKENS
    if _TOKENS is None:
        _TOKENS = set()
        for datei in ("design-system/tokens.css", "design-system/base.css",
                      "design-system/nav.css"):
            pfad = os.path.join(ROOT, datei)
            if os.path.exists(pfad):
                _TOKENS |= set(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", open(pfad, encoding="utf-8").read()))
    return _TOKENS


def check_tokens(full, findings, skip_lines, path):
    """DS10 – jedes var(--x) muss ein definiertes Token treffen."""
    # Was die Datei selbst definiert (eigener <style>, Inline-Stil, JS-gesetzt),
    # zählt als bekannt – geprüft wird die Lücke zum Fundament, nicht der
    # legitime lokale Eigenbau.
    lokal = set(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", full))
    # Begleitende CSS-Dateien der Seite mitlesen (<link href="x.css">) – via
    # linked_css(), demselben Auflösungsweg, den DS02/03/04/05/07 unten nutzen.
    for relpath in linked_css(full, path):
        lokal |= set(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:", open(os.path.join(ROOT, relpath), encoding="utf-8").read()))
    bekannt = bekannte_tokens() | lokal
    gemeldet = set()
    for m in re.finditer(r"var\(\s*(--[a-zA-Z0-9_-]+)\s*([,)])", full):
        name, weiter = m.group(1), m.group(2)
        if name in bekannt or weiter == ",":   # mit Rückfallwert ist es Absicht
            continue
        ln = lineno(full, m.start())
        if ln in skip_lines or (name, ln) in gemeldet:
            continue
        gemeldet.add((name, ln))
        findings.append((ln, "DS10", "fehler",
                         f"unbekanntes Token {name} – CSS löst es still zu nichts auf; "
                         f"Skala in tokens.css prüfen oder Rückfallwert setzen"))


_EMPH_SEL = re.compile(r"\b(strong|b|i|em|h[1-4]|body)\b|\.(kicker|kick|lede|note|hint)")


def check_rules(cleaned, ref_text, base_off, findings, c, skip_lines, check_ds04=True):
    """Läuft über alle Selektor{Körper}-Regeln eines bereits Kommentar- und
    @media/@supports/@keyframes-bereinigten CSS-Texts und prüft DS02/03 (im
    Körper, via check_colors_sizes) sowie DS04/DS05 (am Selektor). EINE Stelle
    für ‹was ist ein Verstoss›, egal ob das CSS in einem <style>-Block der
    Seite steht oder in einer verlinkten Datei – lint_file() und lint_css_file()
    rufen dieselbe Funktion.

    `check_ds04` schaltet die Rollen-Redefinitions-Prüfung ab: Fundament-CSS
    (design-system/base.css & Co.) DEFINIERT .kicker/.hint/.btn/… – das ist die
    Quelle, keine seiten-lokale Redefinition ihrer selbst. Seiten-CSS (z. B.
    apps/…/campaign.css), das dieselben Klassen mit eigener font-size/color
    erneut aufmacht, bleibt geprüft."""
    for rm in RE_RULE.finditer(cleaned):
        sel, body = rm.group(1), rm.group(2)
        body_off = base_off + rm.start(2)
        check_colors_sizes(body, body_off, ref_text, findings, c, skip_lines)
        sel_ln = lineno(ref_text, base_off + rm.start(1))
        if sel_ln in skip_lines:
            continue
        # DS04 – kanonische Rolle lokal redefiniert? Nur SCHLÜSSEL-Selektoren
        # (bare/compound), nicht kontextuelle Überschreibungen (`.download .btn`
        # ist legitim – das ist Verortung, keine Neudefinition der Rolle).
        if check_ds04 and ("font-size" in body or re.search(r"\bcolor\s*:", body)):
            canon = set(c["rollen"]["kanonische_klassen"])
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
        if "underline" in body:
            # Nur auf BARE/compound-Selektoren (direkt auf strong/em/.kicker/…) ist
            # underline eine Hervorhebung. »<container> a« (Link IM Fliesstext/in
            # .note/.hint) ist Link-Konvention, nicht Betonung – DS05 nimmt Links
            # ausdrücklich aus (contract.json, Hinweis). Ohne diese Nachfahren-
            # Ausnahme meldet base.css seine eigene, bewusste Link-Regel
            # (»p a,li a,.note a,.hint a{text-decoration:underline}«) als Verstoss
            # gegen sich selbst – Befund beim ersten Mitlesen des Fundaments.
            for part in sel.split(","):
                p = part.strip()
                if re.search(r"[ >+~]", p):
                    continue
                if _EMPH_SEL.search(p):
                    findings.append((sel_ln, "DS05", "hinweis",
                                     f"underline auf Betonung ({sel.strip()[:32]}) – Laut statt Unterstrich (G05)"))
                    break


_CSS_FILE_CACHE = {}


def lint_css_file(relpath, c):
    """Prüft eine verlinkte, repo-eigene CSS-Datei GENAU EINMAL, unabhängig
    davon, wie viele HTML-Seiten sie per <link> einbinden – base.css/nav.css
    stecken auf 60+ Seiten; ohne Cache meldete jede denselben Treffer erneut.
    Ergebnis wird pro Lauf gecacht und dem Aufrufer (main()) mit den Zeilen der
    CSS-DATEI SELBST zurückgegeben (nicht der Zeile des <link>-Tags) – main()
    hängt die Herkunft (welche Seiten sie einbinden) beim Bericht an."""
    if relpath in _CSS_FILE_CACHE:
        return _CSS_FILE_CACHE[relpath]
    fp = os.path.join(ROOT, relpath)
    raw = open(fp, encoding="utf-8").read()
    text = strip_comments(raw)  # Länge/Zeilen bleiben gleich, nur Kommentare weg
    findings = []
    skip_lines = {lineno(raw, m.start()) for m in re.finditer(r"#\s*ds-ok", raw)}
    cleaned = RE_ATRULE.sub(lambda m: " " * len(m.group(0)), text)
    # design-system/*.css DEFINIERT die kanonischen Rollen – DS04 gilt für
    # Seiten-CSS, das sie NUTZT, nicht für ihre eigene Quelle.
    check_ds04 = not relpath.startswith("design-system" + os.sep)
    check_rules(cleaned, text, 0, findings, c, skip_lines, check_ds04=check_ds04)
    findings.sort(key=lambda f: (f[0], f[1]))
    _CSS_FILE_CACHE[relpath] = findings
    return findings


def lint_file(path, c):
    full = open(os.path.join(ROOT, path), encoding="utf-8").read()
    if is_stub(full):
        return None  # übersprungen
    findings = []
    skip_lines = {lineno(full, m.start()) for m in re.finditer(r"#\s*ds-ok", full)}

    # Ratifizierungs-Marker im FALSCHEN Format melden (»/* ds-ok: … */« ohne #):
    # der Checker sieht so eine Ratifizierung nicht – Wiederholungsfehler (1.7.0).
    for m in re.finditer(r"/\*\s*ds-ok", full):
        if lineno(full, m.start()) not in skip_lines:
            findings.append((lineno(full, m.start()), "DS00", "hinweis",
                             "ds-ok-Marker im falschen Format – »# ds-ok« schreiben, sonst wirkungslos"))

    # DS10 – unbekannte Token (still verschwindende Werte)
    check_tokens(full, findings, skip_lines, path)

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

    # DS08 – Marke aus dem Generator: das Favicon (Kachel) steht nie als <img>.
    marke = c.get("marke")
    if marke:
        for pat in marke.get("verbotene_muster", []):
            for m in re.finditer(pat, full, re.I):
                m_ln = lineno(full, m.start())
                if m_ln not in skip_lines:
                    findings.append((m_ln, marke["ds_id"], marke.get("schwere", "hinweis"),
                                     "Favicon-Kachel als <img> – Marke aus dem Logo-Generator nutzen (DS08)"))

    # DS09 – Fundament/Assets nie absolut über phtok.github.io einbinden: auf der
    # Custom-Domain (Auslieferung im Root, ohne /goeloggen/-Präfix) laufen die
    # URLs ins Leere → Seite ungestylt (Vorfall Signatur-Generator, PR #291).
    einb = c.get("einbindung")
    if einb:
        for m in re.finditer(einb["verbotenes_muster"], full, re.I):
            m_ln = lineno(full, m.start())
            if m_ln not in skip_lines:
                findings.append((m_ln, einb["ds_id"], einb.get("schwere", "fehler"),
                                 "Fundament/Assets absolut (phtok.github.io/goeloggen/…) – relativ einbinden; bricht auf der Custom-Domain"))

    # CSS-Kontexte (Blöcke + inline) – ohne <script>
    scriptless = RE_SCRIPT.sub(lambda m: "\n" * m.group(0).count("\n"), full)

    for content, off in css_blocks(scriptless):
        content_nc = strip_comments(content)  # gleiche Länge/Zeilen, Kommentare weg
        cleaned = RE_ATRULE.sub(lambda m: " " * len(m.group(0)), content_nc)
        check_rules(cleaned, scriptless, off, findings, c, skip_lines, check_ds04=True)

    # Inline-styles im Markup
    for m in RE_INLINE.finditer(scriptless):
        check_colors_sizes(m.group(1), m.start(1), scriptless, findings, c, skip_lines)

    findings.sort(key=lambda f: (f[0], f[1]))
    # Repo-eigene verlinkte CSS-Dateien werden NICHT hier mitgeprüft (siehe
    # lint_css_file): dieselbe Datei steckt oft in Dutzenden Seiten, und ohne
    # eigenen, gecachten Lauf würde main() ihren Verstoss pro Seite erneut
    # melden. lint_file() liefert nur, WELCHE Dateien diese Seite einbindet;
    # main() prüft jede davon genau einmal und weist die Herkunft separat aus.
    return findings, linked_css(full, path)


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
    total_err = 0
    total_warn = 0
    by_rule = {}
    report = []
    konform_pages = set()   # Seiten ohne EIGENEN Fehler – vor Abzug der CSS-Herkunft
    css_refs = {}           # csspath -> [Seiten, die sie einbinden] (Reihenfolge egal)

    for path in sorted(set(files)):
        fp = os.path.join(ROOT, path)
        if not os.path.exists(fp):
            continue
        result = lint_file(path, c)
        if result is None:
            continue  # Stub
        res, linked = result
        checked += 1
        errs = [f for f in res if f[2] == "fehler"]
        warns = [f for f in res if f[2] == "hinweis"]
        total_err += len(errs)
        total_warn += len(warns)
        for ln, rid, sev, msg in res:
            by_rule[rid] = by_rule.get(rid, 0) + 1
        if not errs:
            konform_pages.add(path)
        if res:
            report.append((path, res))
        for csspath in linked:
            css_refs.setdefault(csspath, []).append(path)

    # Jede verlinkte, repo-eigene CSS-Datei GENAU EINMAL prüfen (nicht je Seite,
    # die sie einbindet – base.css/nav.css stecken in fast allen 63 Seiten).
    # Ihre Verstösse zählen einmal in Fehler/Hinweise/je-Regel; für den SCORE
    # gilt eine Seite trotzdem als nicht konform, wenn eine von ihr eingebundene
    # CSS-Datei einen Fehler trägt – das Blatt, das gerendert wird, hat ihn ja.
    # Erstmessung: BERICHTEND, noch kein Tor. Dieselbe Vorsicht wie bei DS08
    # (Barrierefreiheit) – base.css und nav.css stecken in 52 bis 60 der 63
    # Seiten; ihre acht Altlasten sofort blockierend zu stellen hiesse, das
    # Gate fürs ganze Haus rot zu schalten, bevor jemand entscheiden konnte.
    # Der Stand steht im Vertrag (verlinktes_css.stand) und wird dort auf
    # ‹tor› gedreht, sobald der Rückstand abgetragen ist.
    css_regel = c.get("verlinktes_css", {})
    css_ist_tor = css_regel.get("stand") == "tor"

    css_report = []
    pages_mit_css_fehler = set()
    css_err_gesamt = 0
    for csspath in sorted(css_refs):
        css_findings = lint_css_file(csspath, c)
        if not css_findings:
            continue
        css_errs = [f for f in css_findings if f[2] == "fehler"]
        css_warns = [f for f in css_findings if f[2] == "hinweis"]
        css_err_gesamt += len(css_errs)
        if css_ist_tor:
            total_err += len(css_errs)
        total_warn += len(css_warns)
        for ln, rid, sev, msg in css_findings:
            by_rule[rid] = by_rule.get(rid, 0) + 1
        css_report.append((csspath, css_findings, css_refs[csspath]))
        if css_errs and css_ist_tor:
            pages_mit_css_fehler.update(css_refs[csspath])

    conformant = len(konform_pages - pages_mit_css_fehler)

    if not only_score:
        for path, res in report:
            print(col(path, "b"))
            for ln, rid, sev, msg in res:
                tag = col(f"{rid} {sev}", SEV_COL.get(sev, "dim"))
                print(f"  {col(str(ln).rjust(4),'dim')}  {tag}  {msg}")
            print()

        if css_report:
            kopf = "── verlinkte CSS (je Datei einmal geprüft) ────────────────"
            print(col(kopf, "dim"))
            if not css_ist_tor and css_err_gesamt:
                print(col(f"   Rückstand der Erstmessung: {css_err_gesamt} Verstoss/Verstösse — "
                          "berichtend, noch kein Tor (contract.json → verlinktes_css).", "yel"))
            for csspath, css_findings, pages in css_report:
                seiten = sorted(pages)
                preview = ", ".join(seiten[:4])
                mehr = f" · +{len(seiten) - 4} weitere" if len(seiten) > 4 else ""
                print(col(csspath, "b") +
                      col(f"  (eingebunden von {len(seiten)} Seite{'n' if len(seiten) != 1 else ''}: {preview}{mehr})", "dim"))
                for ln, rid, sev, msg in css_findings:
                    tag = col(f"{rid} {sev}", SEV_COL.get(sev, "dim"))
                    print(f"  {col(str(ln).rjust(4),'dim')}  {tag}  {msg}")
                print()

    score = (conformant / checked) if checked else 1.0
    bar = "█" * round(score * 24) + "·" * (24 - round(score * 24))
    print(col("── Konformität ─────────────────────────────────────────", "dim"))
    print(f"  Seiten geprüft:   {checked}")
    print(f"  konform (0 Fehler): {conformant}")
    print(f"  Verstöße:         {col(str(total_err),'red')} Fehler · {col(str(total_warn),'yel')} Hinweise")
    if css_err_gesamt and not css_ist_tor:
        print(f"  {col('dazu berichtend:', 'yel')}  {css_err_gesamt} in verlinktem CSS (Rückstand, blockiert noch nicht)")
    if by_rule:
        order = sorted(by_rule.items(), key=lambda kv: kv[0])
        print("  je Regel:         " + " · ".join(f"{k} {v}" for k, v in order))
    pct = f"{score*100:.0f}%"
    print(f"  Score:            {col(bar,'grn' if score==1 else 'yel')} {col(pct,'b')}")
    print(col("────────────────────────────────────────────────────────", "dim"))

    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())

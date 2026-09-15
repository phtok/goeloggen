#!/usr/bin/env python3
"""Programm der Landwirtschaftlichen Tagung von der Webseite holen.

Liest https://www.agriculture-conference.org/programm (Plenum je Tag,
Arbeitsgruppen am Vormittag und Nachmittag) sowie die Startseite (Motto,
Datum) und legt alles strukturiert in apps/lt-programm/webseite.json ab.
Die Vorschauseite apps/lt-programm/index.html und der IDML-Export lesen
nur diese Datei — die Webseite ist die Quelle, das Blatt folgt ihr.

  python3 tools/lt-programm-holen.py             # holen und schreiben
  python3 tools/lt-programm-holen.py --pruefen   # holen, vergleichen; Änderung → Exit 1
  python3 tools/lt-programm-holen.py --datei programm.html [--start start.html]
                                                 # aus gespeicherten Seiten lesen (Test)

Der Wächter (.github/workflows/lt-programm-waechter.yml) ruft das Skript
regelmässig und committet die neue Datei, wenn sich etwas geändert hat.

Ohne Fremdpakete: html.parser, json, urllib.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import urllib.request
from html.parser import HTMLParser

REPO = pathlib.Path(__file__).resolve().parents[1]
ZIEL = REPO / "apps" / "lt-programm" / "webseite.json"

URL_PROGRAMM = "https://www.agriculture-conference.org/programm"
URL_START = "https://www.agriculture-conference.org/"

SPRACHCODE = re.compile(r"^(DE|EN|FR|ES|IT|NL|RU|PT|CN|ZH|TR|FI|中文)$")
# Sprachliste: erster Eintrag ein Code, die weiteren kurz (auch «Māori», «中文»).
def ist_sprachliste(teil: str) -> list[str]:
    codes = [sauber(c) for c in teil.split(",") if sauber(c)]
    if codes and SPRACHCODE.match(codes[0]) and all(len(c) <= 8 for c in codes):
        return codes
    return []
ZEIT = re.compile(r"^\d{1,2}[:.]\d{2}$")
WOCHENTAG = re.compile(r"^(Mittwoch|Donnerstag|Freitag|Samstag|Sonntag|Montag|Dienstag),\s*(\d{1,2})\.\s*(\w+)")
AG_KOPF = re.compile(r"^(\d{1,2})\s*•\s*(.+)$")
PLATZHALTER = {"titel", "title", "n.n.", "nn", "tba", "tbd"}

# Ordnungszeichen der Webseite (LRM, NBSP) und Aufzählungspunkte vereinheitlichen.
def sauber(text: str) -> str:
    text = text.replace("\u200e", "").replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class Bloecke(HTMLParser):
    """Zerlegt die Seite in eine flache Folge von Blöcken.

    Jeder Block: {"art": "h1|h2|h3|h4|p|li|/li", "text": str, "laut": [Teile in <strong>]}.
    """

    STRUKTUR = {"h1", "h2", "h3", "h4", "p"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.bloecke: list[dict] = []
        self._skip = 0
        self._offen: dict | None = None
        self._strong = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "li":
            self.bloecke.append({"art": "li", "text": "", "laut": []})
        elif tag in self.STRUKTUR:
            self._offen = {"art": tag, "text": "", "laut": []}
        elif tag == "strong" and self._offen is not None:
            self._strong += 1
            self._offen["laut"].append("")
        elif tag == "br" and self._offen is not None:
            self._offen["text"] += " "

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag == "li":
            self.bloecke.append({"art": "/li", "text": "", "laut": []})
        elif tag in self.STRUKTUR and self._offen is not None:
            b = self._offen
            b["text"] = sauber(b["text"])
            b["laut"] = [sauber(t) for t in b["laut"] if sauber(t)]
            if b["text"]:
                self.bloecke.append(b)
            self._offen = None
            self._strong = 0
        elif tag == "strong" and self._strong:
            self._strong -= 1

    def handle_data(self, data):
        if self._skip or self._offen is None:
            return
        self._offen["text"] += data
        if self._strong and self._offen["laut"]:
            self._offen["laut"][-1] += data


def bloecke(html: str) -> list[dict]:
    p = Bloecke()
    p.feed(html)
    return p.bloecke


# --------------------------------------------------------------------------- Plenum

def plenum_zeile(text: str) -> dict:
    """«15:00 • Eröffnung • DE, EN» → {zeit, titel, art, sprachen}."""
    teile = [sauber(t) for t in text.split("•")]
    teile = [t for t in teile if t]
    aus: dict = {"zeit": None, "titel": "", "art": "", "sprachen": []}
    if teile and ZEIT.match(teile[0]):
        aus["zeit"] = teile.pop(0).replace(".", ":")
    if teile and ist_sprachliste(teile[-1]):
        aus["sprachen"] = ist_sprachliste(teile.pop())
    if len(teile) >= 2:
        aus["titel"], aus["art"] = teile[0], " • ".join(teile[1:])
    elif teile:
        aus["titel"] = teile[0]
    if aus["titel"].lower().strip(" .") in PLATZHALTER:
        aus["titel_offen"] = True
    return aus


def plenum_lesen(bl: list[dict]) -> list[dict]:
    tage: list[dict] = []
    i = 0
    while i < len(bl):
        b = bl[i]
        if b["art"] == "h4" and WOCHENTAG.match(b["text"]):
            m = WOCHENTAG.match(b["text"])
            tag = {"wochentag": m.group(1), "tag": int(m.group(2)), "monat": m.group(3),
                   "kopf": b["text"], "veranstaltungen": []}
            i += 1
            letzte_zeit = None
            while i < len(bl) and bl[i]["art"] not in ("h4", "h2", "/li"):
                p = bl[i]
                if p["art"] == "p" and ("•" in p["text"] or ZEIT.match(p["text"].split(" ")[0])):
                    v = plenum_zeile(p["text"])
                    if v["zeit"] is None:
                        v["zeit"] = letzte_zeit
                        v["gleicher_block"] = True
                    letzte_zeit = v["zeit"]
                    # Folgezeile ohne «•» = Mitwirkende
                    if i + 1 < len(bl) and bl[i + 1]["art"] == "p" and "•" not in bl[i + 1]["text"]:
                        v["mitwirkende"] = [sauber(n) for n in bl[i + 1]["text"].split(",") if sauber(n)]
                        i += 1
                    else:
                        v["mitwirkende"] = []
                    tag["veranstaltungen"].append(v)
                i += 1
            if tag["veranstaltungen"]:
                tage.append(tag)
            continue
        i += 1
    return tage


# --------------------------------------------------------------------------- Arbeitsgruppen

def ag_kopfzeile(text: str) -> dict:
    """«Julia Wright, Stefan Doeblin • DE, EN • Raum» → mitwirkende, sprachen, ort."""
    teile = [sauber(t) for t in text.split("•") if sauber(t)]
    aus = {"mitwirkende": [], "sprachen": [], "ort": ""}
    if teile:
        aus["mitwirkende"] = [sauber(n) for n in teile.pop(0).split(",") if sauber(n)]
    for t in teile:
        if ist_sprachliste(t):
            aus["sprachen"] = ist_sprachliste(t)
        else:
            aus["ort"] = t
    return aus


def arbeitsgruppen_lesen(bl: list[dict]) -> dict[str, list[dict]]:
    """Gibt {"vormittag": [...], "nachmittag": [...]} samt Zeitfenster-Zeile zurück."""
    bloecke_ag: dict[str, list[dict]] = {"vormittag": [], "nachmittag": []}
    fenster: dict[str, str] = {}
    block = None
    i = 0
    while i < len(bl):
        b = bl[i]
        if b["art"] == "h2":
            t = b["text"].lower()
            if "arbeitsgruppen" in t and "vormittag" in t:
                block = "vormittag"
            elif "arbeitsgruppen" in t and "nachmittag" in t:
                block = "nachmittag"
            else:
                block = None
            # Zeitfenster-Zeile («4. bis 6. Februar • 10:45 - 12:30 • …») steht je
            # nach Seitenaufbau kurz vor oder nach der Überschrift.
            if block:
                for j in range(max(0, i - 3), min(len(bl), i + 4)):
                    if bl[j]["art"] == "p" and re.search(r"\d{1,2}[:.]\d{2}", bl[j]["text"]) and "•" in bl[j]["text"]:
                        fenster[block] = bl[j]["text"]
                        break
        elif block and b["art"] == "h4" and AG_KOPF.match(b["text"]):
            m = AG_KOPF.match(b["text"])
            ag = {"nr": int(m.group(1)), "block": block, "titel_1": sauber(m.group(2)),
                  "titel_2": "", "mitwirkende": [], "sprachen": [], "ort": "",
                  "text_1": [], "text_2": []}
            i += 1
            erste = True
            in_zweiter = False
            while i < len(bl) and bl[i]["art"] not in ("h4", "h2", "/li"):
                p = bl[i]
                if p["art"] == "p":
                    if erste:
                        ag.update(ag_kopfzeile(p["text"]))
                        erste = False
                    elif p["laut"] and sauber(" ".join(p["laut"])) == p["text"] and not in_zweiter:
                        ag["titel_2"] = p["text"]
                        in_zweiter = True
                    elif p["text"].isupper() and len(p["text"]) < 40:
                        pass  # Schaltflächen wie «PREPARE ONLINE», «BRIEF • LETTER»
                    else:
                        ag["text_2" if in_zweiter else "text_1"].append(p["text"])
                i += 1
            bloecke_ag[block].append(ag)
            continue
        i += 1
    for block, liste in bloecke_ag.items():
        for ag in liste:
            ag["fenster"] = fenster.get(block, "")
            sprachen_zuordnen(ag)
    return bloecke_ag


def sprachen_zuordnen(ag: dict) -> None:
    """Titel den Sprachen zuordnen: die deutsche Seite zeigt den Titel in der
    ersten Sprache im Kopf, die zweite Sprache als fetten Absatz im Text."""
    sp = ag["sprachen"]
    titel = {}
    if sp:
        titel[sp[0]] = ag["titel_1"]
        if ag["titel_2"] and len(sp) > 1:
            titel[sp[1]] = ag["titel_2"]
        elif ag["titel_2"]:
            titel["?"] = ag["titel_2"]
    else:
        titel["?"] = ag["titel_1"]
    ag["titel"] = titel


# --------------------------------------------------------------------------- Startseite

def start_lesen(html: str) -> dict:
    bl = bloecke(html)
    aus = {"motto": "", "datum": "", "ort": ""}
    for b in bl:
        if b["art"] == "h1" and not aus["motto"]:
            aus["motto"] = re.split(r"Landwirtschaftliche Tagung|Agriculture Conference", b["text"])[0].strip()
    m = re.search(r"(\d{1,2})\.\s*(?:bis|–|-)\s*(\d{1,2})\.\s*([A-Za-zäöü]+)\s*(\d{4})", html)
    if m:
        aus["datum"] = f"{m.group(1)}. bis {m.group(2)}. {m.group(3)} {m.group(4)}"
        aus["von"] = int(m.group(1)); aus["bis"] = int(m.group(2))
        aus["monat"] = m.group(3); aus["jahr"] = int(m.group(4))
    return aus


# --------------------------------------------------------------------------- Ablauf

def holen(url: str) -> str:
    anfrage = urllib.request.Request(url, headers={"User-Agent": "goetheanum-werkzeuge/lt-programm"})
    with urllib.request.urlopen(anfrage, timeout=40) as antwort:
        return antwort.read().decode("utf-8", errors="replace")


def lesen(programm_html: str, start_html: str | None) -> dict:
    bl = bloecke(programm_html)
    ag = arbeitsgruppen_lesen(bl)
    daten = {
        "quelle": URL_PROGRAMM,
        "tagung": start_lesen(start_html) if start_html else {},
        "plenum": plenum_lesen(bl),
        "arbeitsgruppen": ag["vormittag"] + ag["nachmittag"],
    }
    kern = json.dumps({k: v for k, v in daten.items()}, ensure_ascii=False, sort_keys=True)
    daten["pruefsumme"] = hashlib.sha256(kern.encode("utf-8")).hexdigest()[:16]
    return daten


def main() -> int:
    argv = sys.argv[1:]
    pruefen = "--pruefen" in argv
    if "--datei" in argv:
        programm_html = pathlib.Path(argv[argv.index("--datei") + 1]).read_text(encoding="utf-8")
        start_html = None
        if "--start" in argv:
            start_html = pathlib.Path(argv[argv.index("--start") + 1]).read_text(encoding="utf-8")
    else:
        programm_html = holen(URL_PROGRAMM)
        start_html = holen(URL_START)
    neu = lesen(programm_html, start_html)
    n_ag = len(neu["arbeitsgruppen"])
    n_pl = sum(len(t["veranstaltungen"]) for t in neu["plenum"])
    print(f"  Webseite: {n_pl} Plenumsveranstaltungen an {len(neu['plenum'])} Tagen, {n_ag} Arbeitsgruppen")
    if n_ag == 0 or n_pl == 0:
        print("  ! Seite nicht wie erwartet aufgebaut — nichts geschrieben")
        return 2

    alt = json.loads(ZIEL.read_text(encoding="utf-8")) if ZIEL.exists() else {}
    if alt.get("pruefsumme") == neu["pruefsumme"]:
        print("  = unverändert gegenüber dem Stand")
        return 0
    if pruefen and alt:
        print("  ≠ Webseite hat sich gegenüber dem Stand geändert")
    if "--start" in argv or "--datei" not in argv or not alt.get("tagung"):
        pass
    elif not neu["tagung"]:
        neu["tagung"] = alt["tagung"]  # Offline-Test ohne Startseite: Motto behalten
    neu["stand"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    ZIEL.write_text(json.dumps(neu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  ✓ geschrieben: {ZIEL.relative_to(REPO)}")
    return 1 if pruefen else 0


if __name__ == "__main__":
    sys.exit(main())

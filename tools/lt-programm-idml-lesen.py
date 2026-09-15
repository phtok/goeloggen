#!/usr/bin/env python3
"""Textrahmen der Tagungsprogramm-Vorlage (IDML) lesen und die Slot-Tabelle prüfen.

Die Rückseite des Faltblatts (Seite 2 in apps/lt-programm/vorlage/LT27.idml)
besteht aus vielen einzelnen Textrahmen. apps/lt-programm/vorlage/slots.json
sagt, welcher Rahmen (Story-ID) welchen Inhalt trägt; der Export
(apps/lt-programm/idml-export.js) schreibt nur in diese Rahmen.

  python3 tools/lt-programm-idml-lesen.py                 # Slots prüfen, Text je Slot zeigen
  python3 tools/lt-programm-idml-lesen.py --alle          # jeden Rahmen der Seite zeigen (auch ohne Slot)
  python3 tools/lt-programm-idml-lesen.py --datei X.idml  # eine andere Datei lesen (z. B. einen Export)
  python3 tools/lt-programm-idml-lesen.py --slot mi_1500  # nur einen Slot

Exit 1, wenn ein Slot auf eine Story zeigt, die es auf der Seite nicht gibt.
Ohne Fremdpakete: zipfile, xml.etree.
"""

from __future__ import annotations

import json
import pathlib
import sys
import xml.etree.ElementTree as ET
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
ORDNER = REPO / "apps" / "lt-programm" / "vorlage"


def story_absaetze(xml: bytes) -> list[tuple[str, list[tuple[str, str]]]]:
    """[(Absatzformat, [(Schnitt, Text), …]), …] — Text mit ¶ für Absatzende, ⏎ für Zeilenumbruch."""
    root = ET.fromstring(xml)
    aus = []
    for psr in root.iter("ParagraphStyleRange"):
        stil = psr.get("AppliedParagraphStyle", "").replace("ParagraphStyle/", "")
        runs: list[tuple[str, str]] = []
        for csr in psr.iter("CharacterStyleRange"):
            schnitt = csr.get("FontStyle", "")
            umbruch = csr.get("ParagraphBreakType", "")
            text = ""
            for kind in csr:
                if kind.tag == "Content":
                    text += (kind.text or "").replace(" ", "⏎")
                elif kind.tag == "Br":
                    text += "‖" if umbruch == "NextColumn" else "¶"
            if text:
                runs.append((schnitt, text))
        aus.append((stil, runs))
    return aus


def seite_lesen(idml: pathlib.Path, seite: str) -> dict[str, list]:
    """{story_id: Absätze} für alle Textrahmen der Seite mit dem Namen `seite`."""
    stories: dict[str, list] = {}
    with zipfile.ZipFile(idml) as z:
        spreads = [n for n in z.namelist() if n.startswith("Spreads/")]
        ids: list[str] = []
        for sp in spreads:
            root = ET.fromstring(z.read(sp))
            if any(p.get("Name") == seite for p in root.iter("Page")):
                ids = [tf.get("ParentStory") for tf in root.iter("TextFrame")]
                break
        for sid in dict.fromkeys(ids):
            name = f"Stories/Story_{sid}.xml"
            if name in z.namelist():
                stories[sid] = story_absaetze(z.read(name))
    return stories


def zeigen(sid: str, absaetze: list, breite: int = 110) -> None:
    for stil, runs in absaetze:
        text = "".join(t for _, t in runs)
        schnitte = "/".join(dict.fromkeys(s for s, _ in runs))
        print(f"    [{stil} · {schnitte}] {text[:breite]}")


def main() -> int:
    argv = sys.argv[1:]
    slots = json.loads((ORDNER / "slots.json").read_text(encoding="utf-8"))
    datei = pathlib.Path(argv[argv.index("--datei") + 1]) if "--datei" in argv else ORDNER / slots["vorlage"]
    nur = argv[argv.index("--slot") + 1] if "--slot" in argv else None
    stories = seite_lesen(datei, slots["seite"])
    print(f"{datei.name}: Seite {slots['seite']} hat {len(stories)} Textrahmen")
    fehler = 0
    belegt = set()
    for name, slot in slots["slots"].items():
        if nur and name != nur:
            continue
        sid = slot["story"]
        belegt.add(sid)
        if sid not in stories:
            print(f"  ✗ {name}: Story {sid} nicht auf der Seite")
            fehler += 1
            continue
        print(f"  ✓ {name} ({sid}, {slot['art']})")
        zeigen(sid, stories[sid])
    if "--alle" in argv:
        print("\nRahmen ohne Slot:")
        for sid, absaetze in stories.items():
            if sid not in belegt:
                print(f"  · {sid}")
                zeigen(sid, absaetze)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())

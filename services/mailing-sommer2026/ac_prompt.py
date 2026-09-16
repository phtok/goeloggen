#!/usr/bin/env python3
"""ac_prompt.py — hält den AC-Automation-Prompt (AC-AUTOMATION.md) aktuell.

Der Prompt-Fliesstext ist stabil und steht in AC-AUTOMATION.md. Volatil ist nur
die **Mail-Tabelle** (Betreff, Alt-Betreff, utm_content, HTML-URL je Mail) — die
leitet dieses Skript aus heroes.json/config.json/links.py ab, damit sie nach
einer Copy-Änderung nie veraltet.

    python3 ac_prompt.py           # Tabellen-Block auf stdout (zur Ansicht)
    python3 ac_prompt.py --write   # den Block in AC-AUTOMATION.md ersetzen
                                    # (zwischen den TABELLEN-Markern)

Ablauf bei kleinen Änderungen: heroes.json anpassen → build_editor.py --publish →
ac_prompt.py --write → AC-AUTOMATION.md ist wieder der fertige Prompt.
"""
import json, sys
from pathlib import Path
import links

ROOT = Path(__file__).parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
H = json.loads((ROOT / "heroes.json").read_text(encoding="utf-8"))
DOC = ROOT / "AC-AUTOMATION.md"
START, ENDE = "<!-- TABELLEN:START -->", "<!-- TABELLEN:END -->"

# Mail-URL-Basis aus asset_base_url ableiten (…/assets → …/mails/).
BASE = (CFG.get("asset_base_url") or "").rstrip("/")
MAILS = BASE.rsplit("/assets", 1)[0] + "/mails" if BASE else "(asset_base_url leer)"

# Anzeige je Segment (Reihenfolge + Überschrift des Angebots) — Prosa, kein Datenfeld.
SEG_ORDER = ["nurtv", "nurws", "noabo"]
SEG_KOPF = {
    "nurtv": "S26 · NurTV→WS (Angebot: Wochenschrift lesen)",
    "nurws": "S26 · NurWS→TV (Angebot: goetheanum.tv sehen)",
    "noabo": "S26 · NoAbo (beide Angebote; jede Mail führt mit einem Button zur Übersicht)",
}
MOTIV_OF = {H["motive"][m]["segment"]: m for m in H["motive"]}


def zeile(motiv, welle, lang):
    seg = H["motive"][motiv]["segment"]
    c = H["wellen"][motiv][welle][lang]
    ziele = links.ziele_for(seg, welle)
    content = links.utm_content(welle, seg, ziele[0], len(ziele) > 1)
    alt = c.get("alt", "").strip() if welle == "w3" else ""
    url = f"{MAILS}/mail_{motiv}_{welle}_{lang}.html"
    return (f"| {welle} | {lang.upper()} | {c['betreff']} | {alt or '—'} "
            f"| `{content}` | {url} |")


def tabellen():
    out = [f"*Mail-Tabelle automatisch erzeugt aus heroes.json — nicht von Hand "
           f"pflegen; neu erzeugen mit `python3 ac_prompt.py --write`.*", ""]
    n_mails = 0
    for seg in SEG_ORDER:
        motiv = MOTIV_OF[seg]
        out.append(f"### {SEG_KOPF[seg]}\n")
        out.append("| Welle | Sprache | Betreff | Alt-Betreff (nur w3-Zweig «Nicht-Öffner») | utm_content | HTML-Quelle |")
        out.append("|---|---|---|---|---|---|")
        for welle in H["wellenplan"][seg]:
            for lang in CFG["sprachen"]:
                out.append(zeile(motiv, welle, lang))
                n_mails += 1
        out.append("")
    w3 = sum(1 for seg in SEG_ORDER for w in H["wellenplan"][seg] if w == "w3") * len(CFG["sprachen"])
    out.append(f"Macht **{n_mails + w3} E-Mail-Schritte** insgesamt: {n_mails} Mails, wobei die "
               f"{w3} w3-Mails je zweimal eingehängt werden (Standard- und Alt-Betreff, gleiches HTML).")
    return "\n".join(out)


def main():
    block = tabellen()
    if "--write" not in sys.argv:
        print(block)
        return
    if not DOC.exists():
        sys.exit(f"{DOC.name} fehlt — erst den Prompt-Rahmen anlegen (mit {START}/{ENDE}-Markern).")
    txt = DOC.read_text(encoding="utf-8")
    if START not in txt or ENDE not in txt:
        sys.exit(f"Marker {START}/{ENDE} fehlen in {DOC.name}.")
    vor, _, rest = txt.partition(START)
    _, _, nach = rest.partition(ENDE)
    neu = f"{vor}{START}\n{block}\n{ENDE}{nach}"
    DOC.write_text(neu, encoding="utf-8")
    print(f"{DOC.name}: Tabellen-Block aktualisiert.")


if __name__ == "__main__":
    main()

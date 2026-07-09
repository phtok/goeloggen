"""
links.py — baut die UTM-Links aus (segment, welle, ziel, sprache).

Verifiziert gegen public.sommer2026_links_public(): das Cockpit verknuepft
Link und Anmeldung AUSSCHLIESSLICH ueber vier Felder:
    utm_campaign + utm_source + utm_medium + utm_content
landing/sprache/url sind reine Register-Etiketten und zaehlen NICHT mit.

utm_content-Regel (deckungsgleich mit den bereits eingespielten 24 Zeilen):
    "w{n}_{segment}"                      bei einem Button
    "w{n}_{segment}_{ws|tv}"              bei zwei Buttons (nur noabo w1/w3)

`python3 links.py` leitet alle Register-Zeilen aus heroes.json/config.json ab
(Wellenplan × CTA-Ziele je Welle × Sprachen) — zum Abgleich mit dem Register.
"""
import json
from pathlib import Path

CFG = json.loads((Path(__file__).parent / "config.json").read_text(encoding="utf-8"))

ZIEL_SUFFIX = {"wos": "ws", "gtv": "tv", "uebersicht": "uebersicht"}


def utm_content(welle: str, segment: str, ziel: str, mehrere_ctas: bool) -> str:
    base = f"{welle}_{segment}"
    return f"{base}_{ZIEL_SUFFIX[ziel]}" if mehrere_ctas else base


def build_url(ziel: str, sprache: str, content: str) -> str:
    base = CFG["landing"][ziel][sprache]
    fix = CFG["utm_fix"]
    q = (f"utm_source={fix['utm_source']}&utm_medium={fix['utm_medium']}"
         f"&utm_campaign={fix['utm_campaign']}&utm_content={content}")
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{q}"


def link_for(welle: str, segment: str, ziel: str, sprache: str, mehrere_ctas: bool) -> dict:
    content = utm_content(welle, segment, ziel, mehrere_ctas)
    return {
        "utm_source": CFG["utm_fix"]["utm_source"],
        "utm_medium": CFG["utm_fix"]["utm_medium"],
        "utm_campaign": CFG["utm_fix"]["utm_campaign"],
        "utm_content": content,
        "landing": ziel,
        "sprache": sprache,
        "url": build_url(ziel, sprache, content),
        "rolle": CFG["segmente"][segment]["rolle"],
        "ersteller": "ph",
    }


def ziele_for(segment: str, welle: str) -> list:
    """CTA-Ziele je Welle: wellen_ctas aus config, sonst das eine Segment-Ziel."""
    scfg = CFG["segmente"][segment]
    return (scfg.get("wellen_ctas") or {}).get(welle) or [scfg["ziele"][0]]


def all_rows():
    """Alle Register-Zeilen aus heroes.json/config.json ableiten (fuer Abgleich/Neu-Sync)."""
    H = json.loads((Path(__file__).parent / "heroes.json").read_text(encoding="utf-8"))
    rows = []
    for segment, wellen in H["wellenplan"].items():
        for welle in wellen:
            ziele = ziele_for(segment, welle)
            mehrere = len(ziele) > 1
            for sprache in CFG["sprachen"]:
                for ziel in ziele:
                    rows.append(link_for(welle, segment, ziel, sprache, mehrere))
    return rows


def to_insert_sql() -> str:
    """SQL, das den Registerstand rekonstruiert (idempotent-Guard beachten!)."""
    cols = "utm_source, utm_medium, utm_campaign, utm_content, landing, sprache, url, rolle, ersteller"
    vals = []
    for r in all_rows():
        vals.append("('{utm_source}','{utm_medium}','{utm_campaign}','{utm_content}',"
                    "'{landing}','{sprache}','{url}','{rolle}','{ersteller}')".format(**r))
    return f"insert into public.sommer2026_links ({cols})\nvalues\n  " + ",\n  ".join(vals) + ";"


if __name__ == "__main__":
    rows = all_rows()
    print(f"{len(rows)} Links abgeleitet:\n")
    for r in rows:
        print(f"  {r['sprache']}  {r['utm_content']:<16} -> {r['url']}")

#!/usr/bin/env python3
"""ruecklauf.py — das deterministische Herz des Rücklauf-Agenten.

Liest die OFFENEN Gegenlese-Kommentare aus Supabase (`sommer2026_mail_comments`)
und macht daraus eine Arbeitsliste, die auf die EXAKTE Stelle in `heroes.json`
zeigt — mit dem aktuellen Text als Kontext. Das ist der Teil, den ein Sprach-
modell nicht jedes Mal neu erraten soll: welcher Kommentar noch offen ist, wo
sein Feld in der Quelle wohnt, und wie der Text dort gerade lautet.

    python3 ruecklauf.py            # Briefing (Markdown) auf stdout
    python3 ruecklauf.py --json     # dieselbe Arbeitsliste maschinenlesbar
    python3 ruecklauf.py --alle     # auch erledigte Kommentare (Rückschau)

Nur Lesen. Korrigiert wird von Hand oder vom Agenten in heroes.json; das
Erledigt-Setzen läuft über den Editor bzw. die RPC `sommer2026_comment_erledigt`.
Der Schlüssel ist der browser-taugliche Publishable Key (RLS: anon darf nur
select+insert) — kein Secret, dieselbe Leseberechtigung wie der Editor.
"""
import json, os, ssl, sys, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
H = json.loads((ROOT / "heroes.json").read_text(encoding="utf-8"))
SB = CFG["supabase"]
KEY = os.environ.get("SUPABASE_ANON_KEY") or SB.get("publishable_key", "")
SEG_OF = {m: H["motive"][m]["segment"] for m in H["motive"]}

# Feld im Kommentar-Key -> (heroes-Pfad-Vorlage, Beschriftung). {m}/{w}/{l} werden gefüllt.
MAILFELD = {
    "betreff":   ("wellen.{m}.{w}.{l}.betreff",   "Betreff"),
    "botschaft": ("wellen.{m}.{w}.{l}.botschaft", "Botschaft (Headline)"),
    "text":      ("wellen.{m}.{w}.{l}.text",      "Fliesstext"),
    "alt":       ("wellen.{m}.{w}.{l}.alt",       "Alt-Betreff (AC-Split)"),
    "preheader": ("wellen.{m}.{w}.{l}.preheader", "Preheader"),
    "cta":       ("motive.{m}.{l}.cta_labels",    "CTA-Beschriftung"),
}
SHARED = {  # shared#<element> -> (heroes-Pfad je Sprache oder None, Beschriftung)
    "badge":      ("badge.{l}",      "Badge"),
    "beweisband": ("proof.{l}",      "Beweis-Band"),
    "proof":      ("proof.{l}",      "Beweis-Band"),
    "kleinzeile": ("kleinzeile.*.{l}", "Kleinzeile (je Motiv)"),
    "footer":     (None,             "Footer — steht in build_editor.py, nicht in heroes.json"),
    "wortmarke":  (None,             "Wortmarke — Logo-Asset, nicht in heroes.json"),
    "button":     (None,             "Button-Stil — Theme in config.json"),
}


def hole(pfad, default=None):
    """Punktpfad in heroes.json auflösen ('wellen.lesen.w1.de.betreff')."""
    cur = H
    for teil in pfad.split("."):
        if isinstance(cur, dict) and teil in cur:
            cur = cur[teil]
        else:
            return default
    return cur


def fetch(alle=False):
    q = {"select": "id,created_at,mail_key,sprache,autor,kommentar,erledigt",
         "order": "created_at.asc"}
    if not alle:
        q["erledigt"] = "not.eq.true"
    url = f"{SB['url']}/rest/v1/{SB['kommentar_tabelle']}?" + urllib.parse.urlencode(q)
    ctx = ssl.create_default_context()
    caf = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    if os.path.exists(caf):
        try: ctx.load_verify_locations(caf)
        except Exception: pass
    req = urllib.request.Request(url, headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return json.loads(r.read().decode("utf-8"))


def zerlege(mail_key):
    """mail_key -> strukturierte Verortung + heroes-Pfade + aktueller Text."""
    wo, _, feld = mail_key.partition("#")
    feld = feld or "gesamt"
    if wo == "shared":
        # feld ist entweder blank (Karten-Kommentar: shared#badge) ODER qualifiziert
        # (WYSIWYG-Overlay: shared#badge#de, shared#kleinzeile#lesen#de). Qualifiziert
        # → genau EIN Pfad, sprach-/motiv-eindeutig; blank → Übersicht wie bisher.
        teile = feld.split("#")
        element = teile[0]
        tmpl, label = SHARED.get(element, (None, element))
        if tmpl and len(teile) > 1:
            lang = teile[-1]
            if "*" in tmpl:  # kleinzeile: element#motiv#lang
                motiv = teile[1] if len(teile) > 2 else None
                pfad = tmpl.replace("*", motiv).format(l=lang) if motiv else None
            else:            # badge/proof: element#lang
                pfad = tmpl.format(l=lang)
            return {"art": "shared", "element": element, "label": label,
                    "sprache": lang, "pfad": pfad,
                    "aktuell": hole(pfad) if pfad else None}
        aktuell = {}
        if tmpl and "*" in tmpl:  # je Motiv
            for m in H["motive"]:
                aktuell[m] = {l: hole(tmpl.replace("*", m).format(l=l)) for l in ("de", "en")}
        elif tmpl:
            aktuell = {l: hole(tmpl.format(l=l)) for l in ("de", "en")}
        return {"art": "shared", "element": element, "label": label,
                "pfad": tmpl, "aktuell": aktuell}
    teile = wo.split("_")
    if len(teile) < 3:
        return {"art": "unbekannt", "roh": mail_key}
    lang, welle, motiv = teile[-1], teile[-2], "_".join(teile[:-2])
    seg = SEG_OF.get(motiv, "?")
    mail = hole(f"wellen.{motiv}.{welle}.{lang}", {}) or {}
    if feld == "gesamt":
        pfad, label = f"wellen.{motiv}.{welle}.{lang}", "ganze Mail"
        aktuell = {k: mail.get(k) for k in ("betreff", "botschaft", "text", "alt") if mail.get(k)}
    else:
        tmpl, label = MAILFELD.get(feld.lower(), (f"wellen.{motiv}.{welle}.{lang}.{feld}", feld))
        pfad = tmpl.format(m=motiv, w=welle, l=lang)
        aktuell = hole(pfad)
    return {"art": "mail", "segment": seg, "motiv": motiv, "welle": welle,
            "sprache": lang, "feld": feld, "label": label, "pfad": pfad, "aktuell": aktuell}


def zeit(iso):
    return (iso or "").replace("T", " ")[:16]


def briefing(rows):
    if not rows:
        print("Keine offenen Kommentare — nichts zu tun.")
        return
    print(f"# Rücklauf-Briefing · {len(rows)} offene Kommentar(e)\n")
    print("Korrigiert wird ausschliesslich in `heroes.json` an den genannten Pfaden. "
          "Danach: `python3 build_editor.py --publish`, PR, nach Merge `--verify`, "
          "erst dann die Kommentare erledigt setzen.\n")
    for c in rows:
        v = zerlege(c["mail_key"])
        if v["art"] == "mail":
            kopf = f"{v['segment']} · {v['motiv']} · {v['welle']} · {v['sprache'].upper()} — {v['label']}"
        elif v["art"] == "shared":
            kopf = f"Gemeinsam — {v['label']}"
        else:
            kopf = f"(unklar) {v['roh']}"
        print(f"## {kopf}")
        # ‹Fassung → …› = konkreter Editor-Vorschlag (neue Feld-Fassung), kein freier Kommentar.
        k = c["kommentar"] or ""
        if k.startswith("Fassung → ") or k.startswith("Fassung -> "):
            neu = k.split("→", 1)[-1].split("->", 1)[-1].strip()
            print(f"- **Fassungsvorschlag** ({c['autor'] or '?'}, {zeit(c['created_at'])}) — "
                  f"neuer Feldtext, direkt einsetzbar:\n```\n{neu}\n```")
        else:
            print(f"- **Kommentar** ({c['autor'] or '?'}, {zeit(c['created_at'])}): {k}")
        if v.get("pfad"):
            print(f"- **heroes.json-Pfad**: `{v['pfad']}`")
        akt = v.get("aktuell")
        if akt:
            print(f"- **Aktueller Text**:\n```\n{json.dumps(akt, ensure_ascii=False, indent=2)}\n```")
        print(f"- **Kommentar-ID** (zum Erledigen): `{c['id']}`  ·  Key: `{c['mail_key']}`\n")


def main():
    if not KEY:
        sys.exit("Kein Supabase-Key: SUPABASE_ANON_KEY setzen oder publishable_key in config.json.")
    alle = "--alle" in sys.argv
    try:
        rows = fetch(alle)
    except Exception as e:
        sys.exit(f"Kommentare nicht ladbar: {e}")
    if "--json" in sys.argv:
        out = [{"kommentar": c, "verortung": zerlege(c["mail_key"])} for c in rows]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        briefing(rows)


if __name__ == "__main__":
    main()

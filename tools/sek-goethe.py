#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sektionsfarben nach Goethes Farbenkreis – Laborpalette, gerechnet, nicht gefühlt.

Alternatives Farbkonzept (Labor, nicht ratifiziert): die zwölf Sektionen der
Hochschule liegen auf Goethes sinnlich-sittlichem Farbenkreis (Zur Farbenlehre,
1810, Didaktischer Teil, 6. Abteilung, §§ 758–829; Farbenkreis «zur
Symbolisierung des menschlichen Geistes- und Seelenlebens», 1809). Jede Sektion
hat einen ORT auf dem Kreis (Goethes Farbname), gehört zu einer GRUPPE
(Purpur · warme Seite · Grün · kühle Seite) und trägt einen Grund aus Goethes
Text, den die Sektion gern für sich lesen kann.

Drei Vorgaben des Auftraggebers (9. September 2026):
  1. Jede Basisfarbe trägt Weiss UND steht als Schrift auf Papier – beides
     ≥ 4.5:1 (Ziel 4.6:1 auf Weiss, 4.5:1 auf --soft). Das ist eine Bedingung an
     die Leuchtdichte: der Löser sucht je Farbton die hellste Stufe, die sie hält.
  2. Sprachlich beleidigt die Zuordnung niemanden und legt niemandem etwas
     bei: nur Goethes bejahende Sätze, keine Rangwörter des Blattes von 1809.
     Jede Sektion kann ihren Ort ablehnen («status»: offen · angenommen · veto).
  3. Die heutigen Farbtöne bleiben, wo es geht: nur die Pädagogik wechselt die
     Familie (Indigo → Blaugrün, weil fünf Sektionen zwischen Blau und Blaurot
     standen); Musik/Sprache rückt ins lichtere Blau, alles andere behält
     seine Farbigkeit und wird nur tiefer.
  4. Kein Gelb (Anmerkung 9. 9. 2026): Gold gehört der Bühne, und ein Gelb,
     das Weiss trägt, wirkt braun – Goethe selbst: ins Minus gezogen macht es
     ‹eine sehr unangenehme Wirkung› (§ 770). Der Kreis bleibt zwischen Rotgelb
     und Grün leer.

Die drei Gestalten entstehen mit DEMSELBEN Rezept wie die heutigen
Sektionsfarben (tools/sek-varianten.py wird importiert): dunkel (Fläche für
Weiss, tiefer als die Basis), hell (Hauch), ink (im Hellmodus = die Basis
selbst, denn sie steht ja als Schrift; im Dunkelmodus ein heller Hauch).

Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/sek-goethe.py            Vorschau (Werte, Kontraste, Kreis)
  python3 tools/sek-goethe.py --apply    schreibt assets/sek-goethe.js (idempotent)
Die Seite sektionsfarben-goethe.html liest diese Datei.
"""
import json, os, re, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_CSS = os.path.join(ROOT, "design-system", "tokens.css")
ORGS_JS = os.path.join(ROOT, "assets", "goe-orgs.js")
OUT_JS = os.path.join(ROOT, "assets", "sek-goethe.js")

_spec = importlib.util.spec_from_file_location("sekvar", os.path.join(ROOT, "tools", "sek-varianten.py"))
sv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sv)

AA, ZIEL_WEISS = 4.5, 4.6

# --- Goethes Kreis: sechs Farben, Purpur oben, warme Seite rechts ---------------
# (Name, Winkel auf dem Blatt, OKLCH-Farbton des Ankers, L und C fürs Kreisbild).
ANKER = [
    ("Purpur",  0,   350, 0.55, 0.18),
    ("Gelbrot", 60,  35,  0.62, 0.19),
    ("Gelb",    120, 96,  0.85, 0.17),
    ("Grün",    180, 140, 0.66, 0.16),
    ("Blau",    240, 250, 0.55, 0.15),
    ("Blaurot", 300, 300, 0.50, 0.16),
]
# Äusserer Ring des Blattes von 1809: vier Sphären des Seelenlebens, je anderthalb
# Farbfelder. Sie beschreiben die Wirkung der FARBEN und stehen nur im Kreisbild;
# die Sektionen werden nicht danach gruppiert.
SPHAEREN = [
    {"id": "vernunft",     "name": "Vernunft",     "von": 0,   "bis": 90},
    {"id": "verstand",     "name": "Verstand",     "von": 90,  "bis": 180},
    {"id": "sinnlichkeit", "name": "Sinnlichkeit", "von": 180, "bis": 270},
    {"id": "phantasie",    "name": "Phantasie",    "von": 270, "bis": 360},
]
# Gruppen für die Ordnung: Goethes eigene Gliederung des Kreises.
GRUPPEN = [
    {"id": "purpur", "name": "Purpur – die Steigerung",
     "desc": "Oben, wo sich beide Seiten des Kreises vereinigen. Goethe: ‹in der Vereinigung der gesteigerten Pole eine eigentliche Beruhigung› (§ 794)."},
    {"id": "warm",   "name": "Die warme Seite – Gelbrot, Rotgelb",
     "desc": "Goethes Plusseite: die Farben, die ‹regsam, lebhaft, strebend› stimmen (§ 764) – vom Purpurrot bis zum Orange. Ohne Gelb: ein Gelb, das Weiss trägt, wäre ‹ins Minus gezogen› (§ 770), und Gold gehört der Bühne."},
    {"id": "gruen",  "name": "Grün – die Vereinigung",
     "desc": "Unten, wo Gelb und Blau sich real mischen und ‹das Auge und das Gemüt› ruhen (§ 802)."},
    {"id": "kuehl",  "name": "Die kühle Seite – Blau, Rotblau",
     "desc": "Goethes Minusseite: Blau ‹als Farbe eine Energie› (§ 779), die Farbe des Himmels und der Ferne, sich sanft ins Rote steigernd."},
]

# --- Die Ordnung: Sektion → Ort auf dem Kreis (H), Buntheit, Grund ---------------
# Reihenfolge im Uhrzeigersinn ab Purpur. «L» steht nur dort, wo die Basis tiefer
# bleibt als die hellste erlaubte Stufe (heutige Tiefe bewahrt); sonst rechnet
# der Löser die hellste Stufe, die Weiss trägt. «grund» ist der Satz für die
# Seite, «para» die Belegstelle, «status» die Rückmeldung der Sektion.
ORDNUNG = [
    {"key": "aas",   "ort": "Purpur",            "gruppe": "purpur", "H": 335, "C": 0.160, "L": 0.55,
     "grund": "Purpur ist für Goethe die Farbe, die ‹teils actu, teils potentia alle andern Farben enthalte›: der Scheitel des Kreises, in dem sich die gesteigerten Pole vereinigen. Die Sektion, die das Ganze trägt, steht dort.",
     "para": "§§ 793–794", "status": "offen"},
    {"key": "sbk",   "ort": "Purpur, zur warmen Seite", "gruppe": "purpur", "H": 358, "C": 0.170,
     "grund": "Von der Wirkung des Purpurs sagt Goethe, sie sei ‹so einzig wie ihre Natur›: ‹Ernst und Würde› wie ‹Huld und Anmut›. Auf dem Blatt von 1809 steht dieses Rot für das Schöne – der Ort der bildenden Künste.",
     "para": "§ 796", "status": "offen"},
    {"key": "szw",   "ort": "Gelbrot",           "gruppe": "warm",   "H": 18,  "C": 0.190,
     "grund": "Gelbrot ist die Farbe des Tuns: ‹Die aktive Seite ist hier in ihrer höchsten Energie.› Sozialwissenschaft als Wille, im Sozialen etwas zu bewirken.",
     "para": "§ 775", "status": "offen"},
    {"key": "js",    "ort": "Rotgelb",           "gruppe": "warm",   "H": 35,  "C": 0.170,
     "grund": "Im Rotgelb ‹wächst die Farbe an Energie und erscheint mächtiger und herrlicher›; es gibt ‹das Gefühl von Wärme und Wonne› und ist ‹die Farbe der höhern Glut› – die Jugend.",
     "para": "§§ 772–773", "status": "offen"},
    {"key": "hpise", "ort": "Gelb, zum Rotgelb", "gruppe": "warm",   "H": 55,  "C": 0.140,
     "grund": "Gelb macht ‹einen durchaus warmen und behaglichen Eindruck›, und ins Rotgelb gesteigert ist es ‹bei Umgebungen angenehm›: Wärme, die aufnimmt und Raum gibt.",
     "para": "§§ 768, 773", "status": "offen"},
    {"key": "lws",   "ort": "Grün",              "gruppe": "gruen",  "H": 140, "C": 0.150,
     "grund": "In Grün findet das Auge ‹eine reale Befriedigung›; wenn die beiden Mutterfarben ‹sich in der Mischung genau das Gleichgewicht halten›, ruht ‹das Auge und das Gemüt› darauf ‹wie auf einem Einfachen›. Erde und Wachstum.",
     "para": "§ 802", "status": "offen"},
    {"key": "nws",   "ort": "Meergrün",          "gruppe": "gruen",  "H": 181, "C": 0.100, "L": 0.53,
     "grund": "Grün entsteht, wenn Gelb und Blau ‹gleich bei ihrem ersten Erscheinen› zusammenkommen – die beiden Urfarben, die Goethe aus Licht und Finsternis ableitet. Wo Grün ins Blau übergeht, nennt er das Meergrün ‹eine liebliche Farbe›. Die Sektion, die seine Naturforschung weiterführt.",
     "para": "§§ 785, 801", "status": "offen"},
    {"key": "ps",    "ort": "Blau, zum Grün",    "gruppe": "kuehl",  "H": 205, "C": 0.110,
     "grund": "Wo Grün ins Blau übergeht: die ‹reale Befriedigung› des Grün (§ 802) wird zur ‹Energie› des Blau (§ 779) – Ruhe, aus der Kraft wird. Das Kind, das wächst; die Pädagogik.",
     "para": "§§ 779, 802", "status": "offen"},
    {"key": "srmk",  "ort": "Blau, licht",       "gruppe": "kuehl",  "H": 232, "C": 0.115,
     "grund": "Blau ‹ist als Farbe eine Energie›; es hat ‹etwas Widersprechendes von Reiz und Ruhe im Anblick›, und wir sehen es gern an, ‹weil es uns nach sich zieht›. Bewegung in der Ruhe: Sprache, Musik, Eurythmie.",
     "para": "§§ 779, 781", "status": "offen"},
    {"key": "mas",   "ort": "Blau",              "gruppe": "kuehl",  "H": 258, "C": 0.150, "L": 0.47,
     "grund": "‹Wie wir den hohen Himmel, die fernen Berge blau sehen›: Blau ist die Farbe des Himmels und der Ferne – Mathematik und Astronomie.",
     "para": "§ 780", "status": "offen"},
    {"key": "ssw",   "ort": "Blau, zum Rotblau", "gruppe": "kuehl",  "H": 282, "C": 0.150, "L": 0.54,
     "grund": "Blau ‹steigert sich sehr sanft ins Rote›; mit dieser Farbe wünscht man ‹immer fortzugehen› und dabei ‹einen Punkt zu finden, wo man ausruhen könnte› – die Bewegung des Lesens. Sprache, Dichtung, Geistesgeschichte.",
     "para": "§§ 787–788", "status": "offen"},
    {"key": "ms",    "ort": "Rotblau",           "gruppe": "kuehl",  "H": 300, "C": 0.135, "L": 0.50,
     "grund": "Ins Rote gesteigert ‹erhält› das Blau ‹etwas Wirksames›, sagt Goethe – Wirksamkeit ist das Wort der Heilkunst. Die Medizin behält ihr Violett und steht auf dem Kreis zwischen Blau und Purpur.",
     "para": "§ 787", "status": "offen"},
]
STATUS = ("offen", "angenommen", "veto")

def theme_tokens():
    """--paper/--soft/--ink je Theme aus tokens.css (erste Definition = hell, zweite = dunkel)."""
    css = open(TOKENS_CSS, encoding="utf-8").read()
    out = {}
    for name in ("paper", "soft", "ink"):
        vals = re.findall(r"--%s\s*:\s*(#[0-9a-fA-F]{3,6})" % name, css)
        out[name] = (vals[0].lower(), vals[1].lower())
    return out

def orgs():
    js = open(ORGS_JS, encoding="utf-8").read()
    m = re.search(r"const GCI_ORGS = (\{.*?\});", js, re.S)
    return json.loads(m.group(1))

def winkel(H):
    """OKLCH-Farbton → Platz auf Goethes Kreis (Grad, Purpur = 0, im Uhrzeigersinn)."""
    h = (H - 350) % 360
    pts = [((a[2] - 350) % 360, a[1]) for a in ANKER] + [(360, 360)]
    for (h0, w0), (h1, w1) in zip(pts, pts[1:]):
        if h0 <= h <= h1:
            return round(w0 + (w1 - w0) * (h - h0) / (h1 - h0), 1)
    return 0.0

def hellste_stufe(H, C, soft):
    """Die hellste OKLCH-Helligkeit, bei der die Farbe Weiss ≥ ZIEL_WEISS hält und
    als Schrift auf --soft und auf ihrem eigenen Hauch ≥ AA steht. Bisektion;
    Buntheit bleibt (am Gamut-Rand gesenkt)."""
    lo, hi = 0.2, 0.9
    for _ in range(40):
        mid = (lo + hi) / 2
        hx = sv.from_oklch(mid, C, H)
        hauch = ableiten(H, mid, C, "hell", 0)
        if sv.kontrast(hx, "#ffffff") >= ZIEL_WEISS and sv.kontrast(hx, soft) >= AA and sv.kontrast(hx, hauch) >= AA:
            lo = mid
        else:
            hi = mid
    return lo

def ableiten(H, L, C, rolle, pos):
    r = sv.REZEPT[rolle]
    return sv.from_oklch(r["L"] + r.get("spanne", 0) * pos, min(C * r["C_faktor"], r["C_max"]), H)

def sichern(hexv, H, pruef, schritt=-0.01):
    """Helligkeit in Hundertstel-Schritten verschieben, bis pruef(hex) wahr ist."""
    L, C, _ = sv.to_oklch(hexv)
    for _ in range(40):
        if pruef(hexv):
            return hexv
        L += schritt
        hexv = sv.from_oklch(L, C, H)
    raise SystemExit("keine Helligkeit gefunden für H %s" % H)

def palette():
    T = theme_tokens(); O = orgs(); soft = T["soft"][0]
    # Basis: hellste Stufe, die Weiss trägt – oder tiefer, wo die Sektion heute tiefer ist.
    basen = []
    for s in ORDNUNG:
        Lmax = hellste_stufe(s["H"], s["C"], soft)
        L = min(Lmax, s.get("L", Lmax))
        basen.append(sv.from_oklch(L, s["C"], s["H"]))
    Ls = [sv.to_oklch(b)[0] for b in basen]; lo, hi = min(Ls), max(Ls)
    out = []
    for s, basis in zip(ORDNUNG, basen):
        H, C = s["H"], s["C"]
        Lb = sv.to_oklch(basis)[0]
        pos = (Lb - lo) / (hi - lo) - 0.5
        assert sv.kontrast(basis, "#ffffff") >= AA and sv.kontrast(basis, soft) >= AA, s["key"]
        # Dunkel: Rezept, aber mindestens sechs Hundertstel tiefer als die Basis.
        dunkel = ableiten(H, Lb, C, "dunkel", pos)
        if sv.to_oklch(dunkel)[0] > Lb - 0.06:
            dunkel = sv.from_oklch(Lb - 0.06, min(C * sv.REZEPT["dunkel"]["C_faktor"], sv.REZEPT["dunkel"]["C_max"]), H)
        dunkel = sichern(dunkel, H, lambda x: sv.kontrast(x, "#ffffff") >= 5.0)
        hell = ableiten(H, Lb, C, "hell", pos)
        hell_dk = ableiten(H, Lb, C, "hell_dk", pos)
        ink = basis  # Vorgabe 1: die Basis selbst ist die Schrift.
        assert sv.kontrast(ink, hell) >= AA, s["key"]
        ink_dk = sichern(ableiten(H, Lb, C, "ink_dk", pos), H,
                         lambda x: min(sv.kontrast(x, T["paper"][1]), sv.kontrast(x, T["soft"][1]), sv.kontrast(x, hell_dk)) >= AA, +0.01)
        o = O.get(s["key"], {})
        heute = (o.get("color") or "").lower()
        out.append({
            "key": s["key"], "name": o.get("name_de", s["key"]), "kurz": o.get("short_de", s["key"]),
            "ort": s["ort"], "gruppe": s["gruppe"], "status": s.get("status", "offen"),
            "winkel": winkel(H), "H": H, "L": round(Lb, 3), "C": C,
            "basis": basis, "on": "#fff", "dunkel": dunkel, "hell": hell, "hell_dk": hell_dk,
            "ink": ink, "ink_dk": ink_dk, "heute": heute,
            "heute_winkel": winkel(sv.to_oklch(heute)[2]) if heute else None,
            "heute_weiss": round(sv.kontrast(heute, "#ffffff"), 2) if heute else None,
            "grund": s["grund"], "para": s["para"],
            "kontrast": {
                "weiss_auf_basis": round(sv.kontrast(basis, "#ffffff"), 2),
                "basis_auf_soft": round(sv.kontrast(basis, soft), 2),
                "weiss_auf_dunkel": round(sv.kontrast(dunkel, "#ffffff"), 2),
                "ink_auf_hell": round(sv.kontrast(T["ink"][0], hell), 2),
                "basis_auf_hell": round(sv.kontrast(basis, hell), 2),
                "tinte_dk_auf_papier": round(sv.kontrast(ink_dk, T["paper"][1]), 2),
                "tinte_dk_auf_hell": round(sv.kontrast(ink_dk, hell_dk), 2),
                "ink_dk_auf_hell_dk": round(sv.kontrast(T["ink"][1], hell_dk), 2),
            }})
    return out

def harmonien(pal):
    """Goethe § 809–810: der bewegliche Durchmesser – jede Farbe fordert ihre
    Gegenfarbe. Paare, in denen beide Sektionen einander gegenüberliegen."""
    def gegen(a):
        ziel = (a["winkel"] + 180) % 360
        return min((p for p in pal if p is not a), key=lambda p: min(abs(p["winkel"] - ziel), 360 - abs(p["winkel"] - ziel)))
    paare, seen = [], set()
    for a in pal:
        b = gegen(a)
        if gegen(b) is not a:
            continue
        k = tuple(sorted((a["key"], b["key"])))
        if k in seen:
            continue
        seen.add(k); paare.append({"a": a["key"], "b": b["key"]})
    return paare

def schreiben(pal):
    daten = {"$quelle": "GENERIERT von tools/sek-goethe.py – nicht von Hand ändern. Goethe, Zur Farbenlehre (1810), Didaktischer Teil, 6. Abteilung, §§ 758–829; Farbenkreis 1809 (Freies Deutsches Hochstift).",
             "anker": [{"name": a[0], "winkel": a[1], "H": a[2], "hex": sv.from_oklch(a[3], a[4], a[2])} for a in ANKER],
             "sphaeren": SPHAEREN, "gruppen": GRUPPEN, "sektionen": pal, "harmonien": harmonien(pal)}
    js = "/* GENERIERT von tools/sek-goethe.py – nicht von Hand ändern. */\nwindow.GOE_SEK_GOETHE = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n"
    alt = open(OUT_JS, encoding="utf-8").read() if os.path.exists(OUT_JS) else ""
    if alt != js:
        open(OUT_JS, "w", encoding="utf-8").write(js); print("geschrieben:", os.path.relpath(OUT_JS, ROOT))
    else:
        print("unverändert:", os.path.relpath(OUT_JS, ROOT))

def main():
    for s in ORDNUNG:
        assert s.get("status", "offen") in STATUS, s["key"]
    pal = palette()
    print("%-6s %-22s %6s  %-8s %-8s %-8s %-8s  Weiss/Basis Basis/soft Weiss/dunkel Basis/hell dk:Tinte/Papier  heute Weiss" %
          ("Key", "Ort", "Winkel", "Basis", "dunkel", "hell", "ink_dk"))
    for p in pal:
        k = p["kontrast"]
        print("%-6s %-22s %6.1f  %-8s %-8s %-8s %-8s  %5.2f %5.2f %5.2f %5.2f %5.2f   %s %.2f" %
              (p["key"], p["ort"], p["winkel"], p["basis"], p["dunkel"], p["hell"], p["ink_dk"],
               k["weiss_auf_basis"], k["basis_auf_soft"], k["weiss_auf_dunkel"], k["basis_auf_hell"], k["tinte_dk_auf_papier"], p["heute"], p["heute_weiss"]))
    print("\nHarmonien (§ 810, Gegenüber auf dem Kreis):")
    for h in harmonien(pal):
        print("  %s ↔ %s" % (h["a"], h["b"]))
    if "--apply" in sys.argv:
        schreiben(pal)

if __name__ == "__main__":
    main()

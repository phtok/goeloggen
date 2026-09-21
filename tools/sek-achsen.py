#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Doppelfarben: die Sektionen auf den Achsen von Goethes Farbenkreis (Labor).

Vierte Fassung des Farbkonzepts (Auftrag 21. September 2026). Der Anlass war das
Gelb: es kann leuchten oder tragen, nie beides. PostFinance löst dasselbe Problem
mit zwei Farben (gemessen an der Quelle: --postfinancegelb #FFCC00 als Fläche,
--petrol #004B5A als Schrift und als weisstragende Fläche). Dieses Werkzeug
begründet dieselbe Bauart aus Goethe – und macht sie zum System für alle zwölf
Sektionen:

  DER GEDANKE. Goethes Kreis ist eine Polarität, kein Musterbuch: Plusseite und
  Minusseite, Licht und Finsternis. Keine Farbe ist für sich ganz; das Auge
  fordert die entgegengesetzte und stellt die Totalität her («Gelb fordert
  Rot-Blau, Blau fordert Rot-Gelb, Purpur fordert Grün», §§ 805–812). Darum steht
  keine Sektion auf einem PUNKT des Kreises, sondern auf einer ACHSE: einem
  Leuchten und einem Grund, die einander fordern.

  DIE PHYSIK. Dass es zwei sein müssen, ist keine Setzung: eine Farbe der
  Lichtseite verliert ihre Farbigkeit, sobald sie tief genug für Weiss wird
  (Gelb bei 4.5:1 ist Oliv), eine Farbe der Minusseite verliert sie, sobald sie
  hell genug zum Leuchten wird. Die Achse gibt jeder Sektion beides: die
  Lichtseite leuchtet, die Minusseite trägt.

  DIE ORDNUNG. Zwölf Plätze à 30°, sechs Achsen, je zwei Sektionen. Wessen
  eigener Platz auf der Lichtseite liegt, führt mit dem Leuchten (Fläche hell,
  Schrift im Grund der Achse). Wessen Platz auf der Minusseite liegt, führt mit
  dem Grund (Fläche tief, Weiss darauf, das Leuchten als Zeichen). Alle zwölf
  schreiben damit in der Hälfte des Kreises, die im Purpur der Allgemeinen
  Anthroposophischen Sektion gipfelt.

  DIE MONOFARBEN. Goetheanum-Blau (#0061a9) und Bühnengold (#968250) stehen auf
  keiner Achse und darum auch nicht im Ring. Sie bleiben einfarbig und tragen
  Weiss – daran sind sie im Hausbild sofort zu erkennen: die Sektionen sprechen
  im Paar, das Haus und die Bühne sprechen allein. Beide liegen im Farbton nahe
  bei einem Sektionston; wie weit sie davon abstehen, rechnet «naehe» aus (der
  Abstand entsteht über Helligkeit und Buntheit, nicht über den Farbton).

Gerechnet wird in OKLCH mit den Hausmitteln (tools/sek-varianten.py). Jeder Wert
ist geprüft, nicht gefühlt: das Skript bricht ab, wenn eine Bedingung reisst.

Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/sek-achsen.py            Vorschau (Werte + Kontraste)
  python3 tools/sek-achsen.py --apply    schreibt assets/sek-achsen.js (idempotent)
Die Seite sektionsfarben-achsen.html liest diese Datei.
"""
import json, os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JS = os.path.join(ROOT, "assets", "sek-achsen.js")

def _lade(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "tools", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

sv = _lade("sek-varianten")
sg = _lade("sek-goethe")

T = sg.theme_tokens()
WEISS, SOFT, INK = "#ffffff", T["soft"][0], T["ink"][0]
PAPER_DK, SOFT_DK, INK_DK = T["paper"][1], T["soft"][1], T["ink"][1]
AA = 4.5

# --- Die zwölf Plätze auf Goethes Blatt (30°, Purpur oben, warm rechts) ------------
# Farbton in OKLCH je Platz – dieselbe Zuordnung wie tools/sek-goethe-varianten.py.
def winkel_zu_H(w):
    pts = [((a[2] - 350) % 360, a[1]) for a in sg.ANKER] + [(360, 360)]
    w %= 360
    for (h0, w0), (h1, w1) in zip(pts, pts[1:]):
        if w0 <= w <= w1:
            return (350 + h0 + (h1 - h0) * (w - w0) / (w1 - w0)) % 360
    return 350.0

# --- Die sechs Achsen ---------------------------------------------------------------
# «licht» = der Platz auf der Lichtseite (Fläche, die leuchtet),
# «grund» = der geforderte Gegenplatz (Fläche, die Weiss trägt und als Schrift steht).
# «C» ist die angestrebte Buntheit; am Gamut-Rand senkt from_oklch sie selbst.
ACHSEN = [
    {"id": "ganzes", "name": "Das Ganze und die Erde",
     "a": {"platz": 180, "ort": "Grün",       "natur": "licht", "C": 0.165, "fest": "#63b145"},
     "b": {"platz": 0,   "ort": "Purpur",     "natur": "grund", "C": 0.140, "L_hell": 0.72},
     "satz": "Purpur fordert Grün – Goethes eigenes Beispiel für die Totalität (§ 810).",
     "sektionen": {"a": "lws", "b": "aas"}},
    {"id": "anschauung", "name": "Die Kunst und die Anschauung",
     "a": {"platz": 30,  "ort": "Purpurrot",  "natur": "licht", "C": 0.170, "L_hell": 0.755},
     "b": {"platz": 210, "ort": "Meergrün",   "natur": "grund", "C": 0.105, "L_hell": 0.80},
     "satz": "Die Farbe der ‹Huld und Anmut› (§ 796) fordert das Meergrün, ‹eine liebliche Farbe› (§ 801).",
     "sektionen": {"a": "sbk", "b": "nws"}},
    {"id": "buehne", "name": "Die Bühne und die Ferne",
     "a": {"platz": 50,  "ort": "Gelbrot",    "natur": "grund", "C": 0.190, "L_hell": 0.74},
     "b": {"platz": 230, "ort": "Blau",       "natur": "grund", "C": 0.130, "L_hell": 0.80},
     "satz": "Goethe: ‹Blau fordert Rot-Gelb› (§ 810). Gelbrot ist die einzige Farbe der Lichtseite, die tief werden kann, ohne schmutzig zu werden – darum führt die Bühne ein echtes Rot. Die Achse steht zehn Grad gedreht, damit das Markenblau des Hauses frei bleibt.",
     "sektionen": {"a": "srmk", "b": "mas"}},
    {"id": "glut", "name": "Die Glut und das Wort",
     "a": {"platz": 90,  "ort": "Rotgelb",    "natur": "licht", "C": 0.175, "L_hell": 0.78},
     "b": {"platz": 270, "ort": "Blau, tief", "natur": "grund", "C": 0.135, "L_hell": 0.80},
     "satz": "‹Wärme und Wonne› (§ 773) gegenüber dem Blau, mit dem man ‹immer fortzugehen› wünscht (§ 788).",
     "sektionen": {"a": "js", "b": "ssw"}},
    {"id": "licht", "name": "Das Licht und das Soziale",
     "a": {"platz": 120, "ort": "Gelb",       "natur": "licht", "C": 0.180, "L_hell": 0.88},
     "b": {"platz": 300, "ort": "Blaurot",    "natur": "grund", "C": 0.135, "L_hell": 0.80},
     "satz": "‹Gelb fordert Rot-Blau› (§ 810) – dieselbe Bauart, die PostFinance mit Gelb und Petrol fährt, hier aus dem Kreis gewonnen.",
     "sektionen": {"a": "ps", "b": "szw"}},
    {"id": "heilen", "name": "Das Wachsen und das Heilen",
     "a": {"platz": 150, "ort": "Gelbgrün",   "natur": "licht", "C": 0.165, "L_hell": 0.84},
     "b": {"platz": 330, "ort": "Rotblau",    "natur": "grund", "C": 0.120, "L_hell": 0.80},
     "satz": "Wo Gelb sich ins Grüne senkt, beginnt die Vereinigung der Urfarben (§ 785); ihr gegenüber das Rotblau, das ‹etwas Wirksames› erhält (§ 787).",
     "sektionen": {"a": "hpise", "b": "ms"}},
]

# --- Was jede Sektion an ihrem Platz liest ------------------------------------------
# «satz» ist die Kurzform für die Karte, «grund_text» der Grund zum Nachlesen,
# «para» die Belegstelle, «wandert» sagt, was sich gegenüber der Fassung 3 ändert.
SEKTIONEN = {
    "aas":  {"satz": "Das Ganze: Purpur ‹enthält alle andern Farben›.",
             "grund_text": "Purpur ist für Goethe die Farbe, die ‹teils actu, teils potentia alle andern Farben enthalte› – der Scheitel, in dem sich die gesteigerten Pole vereinigen. Sie trägt den tiefen Grund; ihr Leuchten ist das Grün der Erde, das sie fordert.",
             "para": "§§ 793–794", "wandert": "bleibt im Purpur"},
    "lws":  {"satz": "Die Erde: ‹reale Befriedigung›.",
             "grund_text": "In Grün findet das Auge ‹eine reale Befriedigung›; ruhen Gelb und Blau im Gleichgewicht, ruht ‹das Auge und das Gemüt› darauf ‹wie auf einem Einfachen›. Das etablierte Grün #63b145 bleibt als Leuchten exakt erhalten.",
             "para": "§ 802", "wandert": "Grün bleibt exakt"},
    "sbk":  {"satz": "Das Schöne: ‹Huld und Anmut›.",
             "grund_text": "Vom Purpur sagt Goethe, seine Wirkung sei ‹so einzig wie seine Natur›: ‹Ernst und Würde› ebenso wie ‹Huld und Anmut›. Das Purpurrot ist das Leuchten der bildenden Künste; ihr Grund ist das Meergrün der Naturanschauung.",
             "para": "§ 796", "wandert": "bleibt im Purpurrot"},
    "nws":  {"satz": "Die Anschauung: Gelb und Blau bei ihrem ersten Erscheinen.",
             "grund_text": "Grün entsteht, wenn Gelb und Blau ‹gleich bei ihrem ersten Erscheinen› zusammenkommen; wo es ins Blaue übergeht, nennt Goethe das Meergrün ‹eine liebliche Farbe›. Als Grund trägt es Weiss und steht als Schrift.",
             "para": "§§ 785, 801", "wandert": "bleibt im Meergrün"},
    "srmk": {"satz": "Die Bühne: ‹die aktive Seite in ihrer höchsten Energie›.",
             "grund_text": "Vom Gelbrot sagt Goethe: ‹Die aktive Seite ist hier in ihrer höchsten Energie.› Das ist das Rot, das die Sektion für ihren Bühnencharakter gewünscht hat – und zugleich der Platz, den Goethes Kreis für das Tätige vorsieht. Ihr Grund ist das Blau der Ferne, das dieses Rot fordert.",
             "para": "§ 775", "wandert": "vom Blau ins Gelbrot – auf eigenen Wunsch"},
    "mas":  {"satz": "Die Ferne: ‹die fernen Berge blau›.",
             "grund_text": "‹Wie wir den hohen Himmel, die fernen Berge blau sehen›: Blau ist die Farbe des Himmels und der Ferne. Als Grund trägt es Weiss; sein Leuchten ist das Gelbrot, das Goethe dem Blau als geforderte Farbe zuordnet.",
             "para": "§§ 780, 810", "wandert": "bleibt im Blau"},
    "js":   {"satz": "Die Glut: ‹Wärme und Wonne›.",
             "grund_text": "Im Rotgelb ‹wächst die Farbe an Energie und erscheint mächtiger und herrlicher›; es gibt ‹das Gefühl von Wärme und Wonne› und ist ‹die Farbe der höhern Glut›.",
             "para": "§§ 772–773", "wandert": "bleibt im Rotgelb"},
    "ssw":  {"satz": "Das Lesen: ‹fortgehen› und ‹ausruhen›.",
             "grund_text": "Mit dem tiefen Blau wünscht man ‹immer fortzugehen› und dabei ‹einen Punkt zu finden, wo man ausruhen könnte› – die Bewegung des Lesens. Als Grund trägt es den Satz, sein Leuchten ist die Glut des Rotgelb.",
             "para": "§§ 781, 788", "wandert": "ein Feld tiefer ins Blau"},
    "ps":   {"satz": "Das Licht: ‹die nächste Farbe am Licht›.",
             "grund_text": "Gelb ist ‹die nächste Farbe am Licht›, ‹heiter, munter, sanft reizend›. Es bleibt, was es ist – ein leuchtendes Gelb, das nie tief gezogen wird (§ 770) –, und schreibt im Rot-Blau, das Goethes Auge dazu fordert.",
             "para": "§§ 765–766, 810", "wandert": "bleibt im Gelb – jetzt ungebremst"},
    "szw":  {"satz": "Der Weg: ‹fortgehen› und ein Punkt zum Ausruhen.",
             "grund_text": "Das Blaurot ist die Farbe, in der sich das Blau ‹sehr sanft ins Rote› steigert: Bewegung, die einen Ruhepunkt sucht. Für eine Sektion, die sich neu aufstellt, ist das der Platz – und ihr Leuchten ist das Gelb der Pädagogik, mit der sie die Achse teilt.",
             "para": "§§ 787–788", "wandert": "vom Gelbrot ins Blaurot"},
    "hpise":{"satz": "Das Wachsen: wo Gelb sich ins Grüne senkt.",
             "grund_text": "Gelb und Blau vereinigen sich ‹gleich bei ihrem ersten Erscheinen› zum Grün; das Gelbgrün ist der Anfang dieser Vereinigung – das Werdende. Ihr Grund ist das Rotblau, das sie mit der Medizinischen Sektion teilt.",
             "para": "§ 785", "wandert": "vom Rotgelb ins Gelbgrün"},
    "ms":   {"satz": "Das Wirksame: ‹erhält dadurch etwas Wirksames›.",
             "grund_text": "Ins Rote gesteigert ‹erhält› das Blau ‹etwas Wirksames›, sagt Goethe – Wirksamkeit ist das Wort der Heilkunst. Der Platz liegt unmittelbar neben dem Purpur des Ganzen, wie es die Geschichte der Sektion sagt.",
             "para": "§ 787", "wandert": "bleibt im Rotblau"},
}

MONO = [
    {"key": "goetheanum", "name": "Goetheanum", "hex": "#0061a9",
     "grund_text": "Das Markenblau des Ganzen. Es steht auf keiner Achse, braucht keine zweite Farbe und trägt Weiss – daran ist das Haus zu erkennen."},
    {"key": "buehne", "name": "Bühne", "hex": "#968250",
     "grund_text": "Das Gold der Bühne liegt mit Farbton 88 im Gelbfeld des Kreises. Es bleibt einfarbig und besetzt damit den Platz, den keine Sektion als Fläche halten kann."},
]

# --- Farbmathematik -----------------------------------------------------------------
# Der Grund ist nie heller als GRUND_MIN – sonst fiele die tragende Reihe
# auseinander (ein Feld beinahe schwarz, das nächste ein mittleres Violett).
GRUND_MIN = 6.0

def tiefste_stufe(H, C, leuchten, hauch):
    """Die HELLSTE Stufe des Grundtons, die alle Pflichten hält: Weiss darauf
    ≥ GRUND_MIN (und damit er selbst als Schrift auf Papier ebenso), auf der
    Karte ≥ 4.5, auf dem Leuchten der Achse ≥ 4.5, auf dem Hauch ≥ 4.5.
    Je heller das Leuchten, desto freier darf der Grund stehen – das ist die
    Physik der Achse, nicht eine Setzung."""
    L = 0.75
    while L > 0.15:
        hx = sv.from_oklch(L, C, H)
        if (sv.kontrast(hx, WEISS) >= GRUND_MIN and sv.kontrast(hx, SOFT) >= AA
                and sv.kontrast(hx, leuchten) >= AA and sv.kontrast(hx, hauch) >= AA):
            return hx
        L -= 0.0025
    raise SystemExit("kein Grund gefunden für H %s" % H)

def hauch(H, C, dunkel=False):
    r = sv.REZEPT["hell_dk" if dunkel else "hell"]
    return sv.from_oklch(r["L"], min(C * r["C_faktor"], r["C_max"]), H)

def tinte_dk(H, C):
    """Die Sektion als Schrift im Dunkelmodus – heller Hauch ihrer eigenen Farbe."""
    r = sv.REZEPT["ink_dk"]
    hx = sv.from_oklch(r["L"], min(C * r["C_faktor"], r["C_max"]), H)
    while min(sv.kontrast(hx, PAPER_DK), sv.kontrast(hx, SOFT_DK)) < AA:
        L, C2, _ = sv.to_oklch(hx)
        hx = sv.from_oklch(L + 0.01, C2, H)
    return hx

def k(a, b):
    return round(sv.kontrast(a, b), 2)

def hell_ton(pol):
    """Die leuchtende Gestalt eines Platzes: gesetzte Helligkeit, volle Buntheit.
    Das etablierte Grün der Landwirtschaft steht fest."""
    if pol.get("fest"):
        return pol["fest"]
    H = winkel_zu_H(pol["platz"])
    return sv.from_oklch(pol["L_hell"], pol["C"], H)

def tief_ton(pol, gegen_hell):
    """Die tragende Gestalt eines Platzes: die hellste Stufe, die Weiss trägt
    (≥ GRUND_MIN, damit die Reihe zusammenhält), auf der Karte und auf ihrem
    eigenen Hauch ≥ 4.5 steht – und auf der leuchtenden Gestalt der Gegenseite,
    denn dort schreibt sie."""
    H = winkel_zu_H(pol["platz"]); C = pol["C"]
    hch = hauch(H, C)
    L = 0.75
    while L > 0.15:
        hx = sv.from_oklch(L, C, H)
        if (sv.kontrast(hx, WEISS) >= GRUND_MIN and sv.kontrast(hx, SOFT) >= AA
                and sv.kontrast(hx, hch) >= AA and sv.kontrast(hx, gegen_hell) >= AA):
            return hx
        L -= 0.0025
    raise SystemExit("kein Grund gefunden für Platz %s" % pol["platz"])

def bauen():
    orgs = sg.orgs()
    achsen, sektionen = [], []
    for a in ACHSEN:
        A, B = a["a"], a["b"]
        hell = {"a": hell_ton(A), "b": hell_ton(B)}
        tief = {"a": tief_ton(A, hell["b"]), "b": tief_ton(B, hell["a"])}
        pole = {}
        for seite in ("a", "b"):
            P = a[seite]
            H = sv.to_oklch(hell[seite])[2] if P.get("fest") else winkel_zu_H(P["platz"])
            C = sv.to_oklch(hell[seite])[1] if P.get("fest") else P["C"]
            eigen = hell[seite] if P["natur"] == "licht" else tief[seite]
            gegen = tief["b" if seite == "a" else "a"] if P["natur"] == "licht" else hell["b" if seite == "a" else "a"]
            pole[seite] = {"ort": P["ort"], "platz": P["platz"], "natur": P["natur"],
                           "H": round(H, 1), "C": round(C, 3), "key": a["sektionen"][seite],
                           "hell": hell[seite], "tief": tief[seite],
                           "eigen": eigen, "gegen": gegen,
                           "hauch": hauch(H, C), "hauch_dk": hauch(H, C, True),
                           "tinte_dk": tinte_dk(H, C)}
            # Die eine Regel, gemessen: auf jeder Fläche steht, was sie trägt.
            traeger = WEISS if P["natur"] == "grund" else gegen
            assert sv.kontrast(eigen, traeger) >= AA, (a["id"], seite, "Fläche trägt ihre Schrift nicht")
            assert sv.kontrast(gegen, eigen) >= AA, (a["id"], seite, "Zeichen steht nicht auf der Fläche")
            if P["natur"] == "grund":
                assert sv.kontrast(eigen, SOFT) >= AA, (a["id"], seite, "Grund steht nicht als Schrift auf der Karte")
        paar = {"id": a["id"], "name": a["name"], "satz": a["satz"], "a": pole["a"], "b": pole["b"],
                "kontrast": {
                    "a_flaeche_schrift": k(pole["a"]["eigen"], WEISS if A["natur"] == "grund" else pole["a"]["gegen"]),
                    "b_flaeche_schrift": k(pole["b"]["eigen"], WEISS if B["natur"] == "grund" else pole["b"]["gegen"]),
                    "a_zeichen": k(pole["a"]["gegen"], pole["a"]["eigen"]),
                    "b_zeichen": k(pole["b"]["gegen"], pole["b"]["eigen"]),
                    "a_auf_papier": k(pole["a"]["eigen"] if A["natur"] == "grund" else pole["a"]["gegen"], WEISS),
                    "b_auf_papier": k(pole["b"]["eigen"] if B["natur"] == "grund" else pole["b"]["gegen"], WEISS)}}
        achsen.append(paar)
        for seite in ("a", "b"):
            P = pole[seite]; key = P["key"]
            o = orgs.get(key, {}); t = SEKTIONEN[key]
            gegen_pol = pole["b" if seite == "a" else "a"]
            heute = (o.get("color") or "").lower()
            # Schrift auf Papier: die tragende Gestalt der Sektion – die eigene,
            # wenn sie tief ist, sonst die geforderte Farbe der Achse.
            schrift = P["eigen"] if P["natur"] == "grund" else P["gegen"]
            sektionen.append({
                "key": key, "name": o.get("name_de", key), "kurz": o.get("short_de", key),
                "achse": a["id"], "achse_name": a["name"], "natur": P["natur"],
                "ort": P["ort"], "platz": P["platz"], "partner_key": gegen_pol["key"],
                "flaeche": P["eigen"], "zeichen": P["gegen"], "schrift": schrift,
                "hauch": P["hauch"], "hauch_dk": P["hauch_dk"], "tinte_dk": P["tinte_dk"],
                "heute": heute, "heute_weiss": k(heute, WEISS) if heute else None,
                "satz": t["satz"], "grund_text": t["grund_text"], "para": t["para"],
                "wandert": t["wandert"], "status": "offen",
                "kontrast": {"schrift_auf_flaeche": k(P["eigen"], WEISS if P["natur"] == "grund" else P["gegen"]),
                             "zeichen_auf_flaeche": k(P["gegen"], P["eigen"]),
                             "schrift_auf_papier": k(schrift, WEISS),
                             "schrift_auf_karte": k(schrift, SOFT),
                             "schrift_auf_hauch": k(schrift, P["hauch"])}})
    mono = []
    for m in MONO:
        L, C, H = sv.to_oklch(m["hex"])
        platz = sg.winkel(H)
        def abstand(s):
            d = abs(s["platz"] - platz) % 360
            return min(d, 360 - d)
        nah = min(sektionen, key=abstand)
        Ln, Cn, _ = sv.to_oklch(nah["flaeche"])
        mono.append(dict(m, H=round(H, 1), platz=round(platz, 1), L=round(L, 2), C=round(C, 3),
                         hauch=hauch(H, C), weiss=k(m["hex"], WEISS),
                         naehe={"key": nah["key"], "name": nah["name"], "kurz": nah["kurz"],
                                "hex": nah["flaeche"], "platz_abstand": round(abstand(nah), 1),
                                "kontrast": k(m["hex"], nah["flaeche"]),
                                "d_L": round(abs(L - Ln), 2), "d_C": round(abs(C - Cn), 3)}))
    return achsen, sektionen, mono

def schreiben(achsen, sektionen, mono):
    daten = {"$quelle": "GENERIERT von tools/sek-achsen.py – nicht von Hand ändern. Goethe, Zur Farbenlehre (1810), §§ 758–829; Farbenkreis 1809.",
             "anker": [{"name": a[0], "winkel": a[1], "H": a[2], "hex": sv.from_oklch(a[3], a[4], a[2])} for a in sg.ANKER],
             "achsen": achsen, "sektionen": sektionen, "mono": mono,
             "vorbild": {"name": "PostFinance", "gelb": "#FFCC00", "petrol": "#004B5A",
                         "abstand": 108, "kontrast": k("#004b5a", "#ffcc00"),
                         "quelle": "gemessen an den CSS-Variablen --postfinancegelb und --petrol"}}
    js = ("/* GENERIERT von tools/sek-achsen.py – nicht von Hand ändern. */\n"
          "window.GOE_SEK_ACHSEN = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n")
    alt = open(OUT_JS, encoding="utf-8").read() if os.path.exists(OUT_JS) else ""
    if alt != js:
        open(OUT_JS, "w", encoding="utf-8").write(js); print("geschrieben:", os.path.relpath(OUT_JS, ROOT))
    else:
        print("unverändert:", os.path.relpath(OUT_JS, ROOT))

def main():
    achsen, sektionen, mono = bauen()
    print("%-11s %-24s %-9s %-9s   %s" % ("Achse", "Pol", "Fläche", "Zeichen", "Fläche/Schrift  Zeichen  Schrift/Papier"))
    for a in achsen:
        c = a["kontrast"]
        for seite in ("a", "b"):
            P = a[seite]
            print("%-11s %-24s %-9s %-9s   %5.2f %5.2f %5.2f" % (
                a["id"] if seite == "a" else "", P["ort"] + " (" + P["natur"] + ")",
                P["eigen"], P["gegen"], c[seite + "_flaeche_schrift"], c[seite + "_zeichen"], c[seite + "_auf_papier"]))
    print()
    print("%-6s %-6s %-12s %-9s %-9s %-9s  %s" % ("Key", "Natur", "Ort", "Fläche", "Zeichen", "Schrift", "wandert"))
    for s_ in sektionen:
        print("%-6s %-6s %-12s %-9s %-9s %-9s  %s" % (
            s_["key"], s_["natur"], s_["ort"], s_["flaeche"], s_["zeichen"], s_["schrift"], s_["wandert"]))
    for m in mono:
        n = m["naehe"]
        print("Mono %-11s %s  nächster Sektionston: %s %s (%.1f° entfernt, Kontrast %.2f)" % (
            m["name"], m["hex"], n["kurz"], n["hex"], n["platz_abstand"], n["kontrast"]))
    if "--apply" in sys.argv:
        schreiben(achsen, sektionen, mono)

if __name__ == "__main__":
    main()

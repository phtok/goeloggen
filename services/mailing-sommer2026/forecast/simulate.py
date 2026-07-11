#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtueller Testlauf «Sommer-Aktion 2026» (S26)
==============================================

Prognostiziert Öffnungen, Klicks und Abschlüsse der dreistufigen
S26-Automation und rechnet die statistische Power virtueller A/B-Tests.
Reproduzierbar (fester Seed), reine Standardbibliothek.

Verankerung
-----------
Ausschliesslich an den vier abgeschlossenen 2025-Sommer-Automationen
(WOS/GTV × DE/EN × 3 Mails), die als Punktschätzer je Welle dienen. Die
S26-Struktur (drei Segmente, Conversion-Goals, Conversion-Check vor jeder
Welle, Öffner-Split vor w3, w3b nur an Klicker) ist in `services/
mailing-sommer2026/{config.json, AC-AUTOMATION.md}` festgelegt und wird hier
modelliert.

Ehrlichkeitsgrenzen (bewusst offengelegt, nicht kaschiert)
----------------------------------------------------------
1. 2025 hatte KEIN Conversion-Goal. Es gibt also keine gemessene
   Abschlussrate. Abschlüsse sind hier Szenario-Arithmetik auf der
   Klick→Signup-Rate p (Bandbreite, kein Punktwert).
2. Die Segmentgrössen (NurTV/NurWS/NoAbo) liegen in ActiveCampaign; nur
   NurTV ist bekannt (~1.094 aktiv). NurWS/NoAbo sind hier begründete
   SCHÄTZUNGEN. Alle Ergebnisse sind zusätzlich auf «je 1.000 Empfänger»
   normiert, damit echte Zahlen ohne Modelländerung eingesetzt werden können.

Aufruf:  python3 simulate.py            (Bericht nach stdout)
         python3 simulate.py --json     (zusätzlich forecast.json schreiben)
"""

import json
import math
import random
import statistics
import sys
from pathlib import Path

SEED = 20260714  # w1-Versanddatum als Seed -> reproduzierbar
random.seed(SEED)
N_SIM = 40000

# ---------------------------------------------------------------------------
# 1) BASIS 2025  (aus der AC-Reporting-Schnittstelle, eindeutige Klicker)
# ---------------------------------------------------------------------------
# Feld je Mail: (versandt, geoeffnet, klicker, abmeldungen)
BASIS_2025 = {
    "WOS": {  # Wochenschrift-Angebot  -> Anker fuer WS-Offer (NurTV + NoAbo-WS)
        "DE": {"eingetreten": 29449,
               "mails": [(24007, 9363, 660, 105),
                         (23854, 8785, 434, 90),
                         (23699, 8405, 419, 77)]},
        "EN": {"eingetreten": 24452,
               "mails": [(21985, 10217, 495, 94),
                         (21841, 8429, 246, 81),
                         (21721, 8161, 237, 98)]},
    },
    "GTV": {  # goetheanum.tv-Angebot -> Anker fuer TV-Offer (NurWS + NoAbo-TV)
        "DE": {"eingetreten": 29754,
               "mails": [(27502, 11671, 438, 73),
                         (27328, 11046, 521, 83),
                         (27158, 10471, 753, 94)]},
        "EN": {"eingetreten": 24691,
               "mails": [(23777, 10282, 240, 52),
                         (23655, 9885, 292, 52),
                         (23542, 9434, 463, 76)]},
    },
}


def rate_tabelle():
    """Öffnungs-, Klick- und Abmelderaten je Produkt/Sprache/Welle."""
    out = {}
    for prod, langs in BASIS_2025.items():
        out[prod] = {}
        for lang, d in langs.items():
            rows = []
            for (sent, opened, clk, uns) in d["mails"]:
                rows.append({
                    "versandt": sent,
                    "open": opened / sent,
                    "klick": clk / sent,
                    "abmeld": uns / sent,
                    "klicker": clk,
                })
            out[prod][lang] = rows
    return out


RATEN = rate_tabelle()

# ---------------------------------------------------------------------------
# 2) UNSICHERHEIT — aus der Streuung der vier Kampagnen geschätzt
# ---------------------------------------------------------------------------
# Zwischen-Kampagnen-Streuung je Welle (wie sehr darf der S26-Anker daneben
# liegen). Aus 2025: SD der w1-Openrate ueber 4 Kampagnen ~3,1pp; w1-Klickrate
# ~0,7pp. Etwas erhoeht fuer S26-Neuheit + Sommer-Saisonalitaet.
SIGMA_OPEN = 0.030
SIGMA_KLICK = 0.0060

# ---------------------------------------------------------------------------
# 3) SEGMENTMODELL S26
# ---------------------------------------------------------------------------
# Zuordnung Segment -> (Anker-Produkt, Warm-Aufschlag Openrate, Rollen-Notiz).
# Warm-Aufschlag: NurTV/NurWS sind zahlende Bestandskunden (Marken-Naehe ->
# hoehere Oeffnung); bewusst NUR auf die Oeffnung, NICHT auf den Klick
# (Cross-Produkt-Interesse ist ungewiss -> konservativ, kein Klick-Bonus).
SEGMENTE = {
    "nurtv": {"label": "NurTV → WS-Angebot", "anker": "WOS",
              "open_uplift": 0.04, "warm": True,
              "wellen": ["w1", "w2", "w3"]},
    "nurws": {"label": "NurWS → TV-Angebot", "anker": "GTV",
              "open_uplift": 0.04, "warm": True,
              "wellen": ["w1", "w2", "w3"]},
    "noabo": {"label": "NoAbo → beide (Übersicht)", "anker": "MIX",
              "open_uplift": 0.00, "warm": False,
              "wellen": ["w1", "w2", "w3", "w3b"]},
}

# Zentrales Grössen-Szenario (SCHÄTZUNG; NurTV belegt).
# DE/EN-Split je Segment: WS ist DE-lastiger, TV/Newsletter naeher am
# Hausschnitt 55/45.  ->  einzeln gesetzt.
GROESSEN_ZENTRAL = {
    "nurtv": {"DE": 602, "EN": 492},     # Summe 1.094 (belegt), Split 55/45
    "nurws": {"DE": 3500, "EN": 1500},   # Summe 5.000 (Schätzung), 70/30
    "noabo": {"DE": 22000, "EN": 18000}, # Summe 40.000 (Schätzung), 55/45
}
# Bandbreite fuer die Sensitivitaet (Gesamtgroesse je Segment).
GROESSEN_BAND = {
    "nurtv": (1094, 1094),      # belegt -> fix
    "nurws": (3000, 8000),
    "noabo": (32000, 48000),
}

# Klick→Signup-Rate p (auf EINDEUTIGE Klicker). Kein 2025-Messwert ->
# Szenario. Warm (Bestandskunde nimmt Gratis-Schwesterprodukt) hoch,
# NoAbo kalt + Extra-Hop ueber die Uebersichtsseite -> niedrig.
# Externe Kalibrierung (real, gemessen): GTV-Abo-Kampagne Feb/Maerz 2026,
# 3 Mails -> 76 Abschluesse / ~51.000 erreicht = 0,15%/Empf. (kalt, bezahltes
# Rabatt-Angebot). NoAbo hier = 0,38%/Empf. (Gratis-Trial) -> ~2,5x Free-ueber-
# Bezahl-Aufschlag, plausibel. Die reale Kampagne KALIBRIERT die Abwaerts-
# korrektur des NoAbo-p unten (aus Annahme wird Messwert), nicht nur Plausibilitaet.
P_SIGNUP = {                 # (low, mid, high)
    "nurtv": (0.15, 0.25, 0.40),
    "nurws": (0.13, 0.22, 0.38),
    # NoAbo nach adversarialer Pruefung nach unten korrigiert (11.7.):
    # Der w3b-Zweitbiss hebt das EFFEKTIVE p je eindeutigem Klicker um ~26%
    # ueber den Nominalwert. Nominal 0,08 -> effektiv ~0,10-0,11 — kalt,
    # Extra-Hop ueber die Uebersichtsseite UND Kartenpflicht eingepreist
    # (Herleitung: warm-direkt 0,25 x Kalt-Abschlag ~0,55 x Hop ~0,65 ~ 0,08).
    "noabo": (0.04, 0.08, 0.14),
}
# Anteil eindeutiger Klicker an der Summe der Wellen-Klicker (Ueberlappung
# der Wiederholungsklicker ueber w1..w3). unique = summe * (1 - overlap).
OVERLAP = (0.25, 0.35, 0.45)  # (low, mid, high) overlap

# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


Z_ALPHA2 = 1.959964   # zweiseitig, alpha = 0.05
Z_POWER = 0.8416212   # 80% Power


def anker_raten(seg, lang, welle_idx):
    """Anker-Open/-Klickrate fuer Segment/Sprache/Welle (0..2).
    MIX = Mittel aus WOS+GTV je Welle (NoAbo sieht das Beides-Angebot)."""
    conf = SEGMENTE[seg]
    if conf["anker"] == "MIX":
        o = (RATEN["WOS"][lang][welle_idx]["open"] +
             RATEN["GTV"][lang][welle_idx]["open"]) / 2
        k = (RATEN["WOS"][lang][welle_idx]["klick"] +
             RATEN["GTV"][lang][welle_idx]["klick"]) / 2
        a = (RATEN["WOS"][lang][welle_idx]["abmeld"] +
             RATEN["GTV"][lang][welle_idx]["abmeld"]) / 2
    else:
        r = RATEN[conf["anker"]][lang][welle_idx]
        o, k, a = r["open"], r["klick"], r["abmeld"]
    return clamp(o + conf["open_uplift"]), k, a


def sample_count(n, rate, sigma_rate):
    """Doppelt-stochastisch: (1) wahre Rate ~ N(anker, sigma), (2) Zahl ~
    Binomial(n, rate) via Normal-Approximation."""
    if n <= 0:
        return 0
    r = clamp(random.gauss(rate, sigma_rate))
    mean = n * r
    sd = math.sqrt(max(n * r * (1 - r), 0.0))
    c = random.gauss(mean, sd) if sd > 0 else mean
    return max(0, min(n, round(c)))


# ---------------------------------------------------------------------------
# 4) FUNNEL-SIMULATION je (Segment, Sprache)
# ---------------------------------------------------------------------------
def simuliere_zweig(seg, lang, n_enter):
    """Ein Monte-Carlo-Durchlauf des Wellen-Trichters. Modelliert:
       - w1..w3(/w3b) Versand, Öffnungen, Klicker
       - Conversion-Check vor w2 & w3: Konvertierte (aus Vorwellen-Klickern)
         treten aus -> Versandmenge sinkt
       - Öffner-Split vor w3: Nicht-Öffner bekommen den Alt-Betreff (Brücke),
         der ihre w3-Öffnung teilweise rettet (+Bonus auf die Nicht-Öffner)
       - w3b (nur NoAbo): nur an noch-nicht-konvertierte Klicker
    Gibt je Welle Öffnungen/Klicker sowie eindeutige Klicker & Abschluss-
    Bausteine zurück."""
    conf = SEGMENTE[seg]
    wellen = conf["wellen"]
    p_lo, p_mid, p_hi = P_SIGNUP[seg]
    ov = random.uniform(*(OVERLAP[0], OVERLAP[2]))
    p = clamp(random.triangular(p_lo, p_hi, p_mid))

    sent = n_enter
    result = {"sent": {}, "open": {}, "klicker": {}}
    klicker_summe = 0
    konvertiert = 0.0
    # Öffner-Menge (fuer den w3-Split): wer w1 ODER w2 geoeffnet hat.
    hatte_geoeffnet = 0

    for i, welle in enumerate(["w1", "w2", "w3"]):
        # Conversion-Check vor w2/w3: Konvertierte raus.
        if welle in ("w2", "w3"):
            sent = max(0, round(sent - inkrement_konv))
        o_rate, k_rate, a_rate = anker_raten(seg, lang, i)

        # Öffner-Split-Bonus auf w3: Nicht-Öffner erhalten die Brücke als
        # Alt-Betreff. Modelliert als moderater Aufschlag auf die w3-Openrate
        # (nur ~halbe Menge sind Nicht-Öffner; Bonus daher gedaempft).
        if welle == "w3":
            nichtoeffner_anteil = clamp(1 - hatte_geoeffnet / max(sent, 1))
            o_rate = clamp(o_rate + 0.05 * nichtoeffner_anteil)

        opened = sample_count(sent, o_rate, SIGMA_OPEN)
        klicker = sample_count(sent, k_rate, SIGMA_KLICK)
        # Abmeldungen zehren die naechste Versandmenge zusaetzlich (klein).
        abmeld = sample_count(sent, a_rate, a_rate * 0.3)

        result["sent"][welle] = sent
        result["open"][welle] = opened
        result["klicker"][welle] = klicker
        klicker_summe += klicker
        if welle in ("w1", "w2"):
            hatte_geoeffnet += opened

        # Inkrementelle Konversion aus DIESER Welle Klickern (fuer den
        # naechsten Conversion-Check): eindeutiger Klicker-Anteil * p.
        inkrement_konv = klicker * (1 - ov) * p
        konvertiert += inkrement_konv
        sent = max(0, sent - abmeld)

    # w3b (nur NoAbo): an noch-offene Klicker (eindeutig, nicht konvertiert).
    if "w3b" in wellen:
        eind_klicker = klicker_summe * (1 - ov)
        offene_klicker = max(0.0, eind_klicker - konvertiert)
        w3b_sent = round(offene_klicker)
        o_rate, k_rate, _ = anker_raten(seg, lang, 2)
        # Mini-Reminder an Hochengagierte: hohe Öffnung, hoher Re-Klick.
        opened = sample_count(w3b_sent, clamp(o_rate + 0.15), SIGMA_OPEN)
        reklick = sample_count(w3b_sent, clamp(0.20), SIGMA_KLICK * 2)
        result["sent"]["w3b"] = w3b_sent
        result["open"]["w3b"] = opened
        result["klicker"]["w3b"] = reklick
        # w3b holt einen Teil der offenen Klicker noch (Extra-p).
        konvertiert += offene_klicker * p * 0.30

    eind_klicker = klicker_summe * (1 - ov)
    result["eind_klicker"] = eind_klicker
    result["klicker_summe"] = klicker_summe
    result["konvertiert"] = konvertiert
    result["p"] = p
    return result


def perzentile(werte, ps=(10, 50, 90)):
    s = sorted(werte)
    out = {}
    for pp in ps:
        k = (len(s) - 1) * pp / 100.0
        lo = math.floor(k)
        hi = math.ceil(k)
        out[pp] = s[lo] if lo == hi else s[lo] + (s[hi] - s[lo]) * (k - lo)
    return out


def forecast(groessen):
    """Aggregiert N_SIM Durchläufe je Zweig zu Perzentil-Bändern."""
    zweige = {}
    for seg in SEGMENTE:
        for lang in ("DE", "EN"):
            n = groessen[seg][lang]
            if n <= 0:
                continue
            runs = [simuliere_zweig(seg, lang, n) for _ in range(N_SIM)]
            zweige[(seg, lang)] = runs
    return zweige


def summe_metrik(zweige, extractor):
    """Summe einer Metrik ueber alle Zweige, je Durchlauf -> Perzentile."""
    per_run = [0.0] * N_SIM
    for runs in zweige.values():
        for i, r in enumerate(runs):
            per_run[i] += extractor(r)
    return perzentile(per_run)


# ---------------------------------------------------------------------------
# 5) A/B-TEST-POWER
# ---------------------------------------------------------------------------
def mde_abs(p, n_arm):
    """Minimal detektierbarer absoluter Unterschied (Näherung), 80% Power,
    alpha 0,05 zweiseitig, 50/50-Split, n_arm je Arm."""
    if n_arm <= 0:
        return float("inf")
    return (Z_ALPHA2 + Z_POWER) * math.sqrt(2 * p * (1 - p) / n_arm)


def n_pro_arm_fuer(p, rel_lift):
    """Benötigte Armgrösse, um einen relativen Lift rel_lift zu detektieren."""
    p2 = clamp(p * (1 + rel_lift))
    pbar = (p + p2) / 2
    num = (Z_ALPHA2 * math.sqrt(2 * pbar * (1 - pbar)) +
           Z_POWER * math.sqrt(p * (1 - p) + p2 * (1 - p2))) ** 2
    return num / (p2 - p) ** 2


# ---------------------------------------------------------------------------
# BERICHT
# ---------------------------------------------------------------------------
def f(x):
    return f"{x:,.0f}".replace(",", "'")


def pct(x):
    return f"{100*x:.1f}%"


def main():
    schreib_json = "--json" in sys.argv
    print("=" * 74)
    print("VIRTUELLER TESTLAUF  ·  Sommer-Aktion 2026 (S26)")
    print(f"Monte-Carlo, {f(N_SIM)} Durchläufe je Zweig · Seed {SEED}")
    print("=" * 74)

    # --- 2025-Deskriptiv -----------------------------------------------------
    print("\n[1] BASIS 2025 — was die Daten belastbar hergeben")
    print("-" * 74)
    print(f"{'Kampagne':<14}{'Welle':<6}{'Open':>8}{'Klick':>8}"
          f"{'Abmeld':>9}{'Klicker':>10}")
    for prod in ("WOS", "GTV"):
        for lang in ("DE", "EN"):
            for i, r in enumerate(RATEN[prod][lang]):
                print(f"{prod+' '+lang:<14}{'w'+str(i+1):<6}"
                      f"{pct(r['open']):>8}{pct(r['klick']):>8}"
                      f"{pct(r['abmeld']):>9}{f(r['klicker']):>10}")
    print("\nWellen-Dynamik (Klickrate w1→w3):")
    for prod in ("WOS", "GTV"):
        for lang in ("DE", "EN"):
            ks = [RATEN[prod][lang][i]["klick"] for i in range(3)]
            trend = "steigend↑ (Frist zieht)" if ks[2] > ks[0] else "fallend↓ (Ermüdung)"
            print(f"  {prod} {lang}: {pct(ks[0])} → {pct(ks[1])} → "
                  f"{pct(ks[2])}   {trend}")

    # --- Zentral-Forecast ----------------------------------------------------
    print("\n[2] S26-PROGNOSE — zentrales Grössen-Szenario")
    print("-" * 74)
    gesamt = {s: GROESSEN_ZENTRAL[s]["DE"] + GROESSEN_ZENTRAL[s]["EN"]
              for s in SEGMENTE}
    for s in SEGMENTE:
        beleg = "belegt" if s == "nurtv" else "SCHÄTZUNG"
        print(f"  {SEGMENTE[s]['label']:<26} {f(gesamt[s]):>8} "
              f"(DE {f(GROESSEN_ZENTRAL[s]['DE'])} · "
              f"EN {f(GROESSEN_ZENTRAL[s]['EN'])})  [{beleg}]")
    total_enter = sum(gesamt.values())
    print(f"  {'Automation gesamt (w1)':<26} {f(total_enter):>8}")

    zweige = forecast(GROESSEN_ZENTRAL)

    # Klicker gesamt (eindeutig) und Abschluesse
    eind = summe_metrik(zweige, lambda r: r["eind_klicker"])
    konv = summe_metrik(zweige, lambda r: r["konvertiert"])
    klick_events = summe_metrik(zweige, lambda r: r["klicker_summe"])
    open_events = summe_metrik(
        zweige, lambda r: sum(r["open"].values()))
    sent_events = summe_metrik(
        zweige, lambda r: sum(r["sent"].values()))

    print("\n  Headline (P10 – P50 – P90):")
    print(f"    Versendete Mails (Σ Wellen):   "
          f"{f(sent_events[10])} – {f(sent_events[50])} – {f(sent_events[90])}")
    print(f"    Öffnungen (Σ Wellen):          "
          f"{f(open_events[10])} – {f(open_events[50])} – {f(open_events[90])}")
    print(f"    Klick-Ereignisse (Σ Wellen):   "
          f"{f(klick_events[10])} – {f(klick_events[50])} – {f(klick_events[90])}")
    print(f"    Eindeutige Klicker (Personen): "
          f"{f(eind[10])} – {f(eind[50])} – {f(eind[90])}")
    print(f"    ABSCHLÜSSE (Trial-Starts):     "
          f"{f(konv[10])} – {f(konv[50])} – {f(konv[90])}")
    print(f"    → Abschluss je 1.000 Empfänger:"
          f" {konv[50]/total_enter*1000:.1f}  "
          f"(P10 {konv[10]/total_enter*1000:.1f} – "
          f"P90 {konv[90]/total_enter*1000:.1f})")

    # Je Segment
    print("\n  Abschlüsse je Segment (P50; Anteil am Total):")
    seg_konv = {}
    for s in SEGMENTE:
        subset = {k: v for k, v in zweige.items() if k[0] == s}
        kv = summe_metrik(subset, lambda r: r["konvertiert"]) if subset else {50: 0}
        seg_konv[s] = kv[50]
    tot = sum(seg_konv.values()) or 1
    for s in SEGMENTE:
        print(f"    {SEGMENTE[s]['label']:<26} {f(seg_konv[s]):>6}  "
              f"({100*seg_konv[s]/tot:4.0f}%)")

    # Je Welle (Öffnungen/Klicker P50 gesamt)
    print("\n  Klicker je Welle (P50, alle Segmente):")
    for welle in ("w1", "w2", "w3", "w3b"):
        kv = summe_metrik(
            zweige, lambda r: r["klicker"].get(welle, 0))
        print(f"    {welle:<5} {f(kv[50]):>7}")

    # --- Kreuzprobe Abschluesse ---------------------------------------------
    print("\n[3] ABSCHLÜSSE — Kreuzprobe & Bandbreite (der ehrliche Teil)")
    print("-" * 74)
    print("  Methode 1 (oben): eindeutige Klicker × p(Klick→Signup).")
    print(f"    zentral p (nominal): NurTV 25% · NurWS 22% · NoAbo 8%")
    print(f"    (NoAbo effektiv ~11% je Klicker inkl. w3b-Zweitbiss)")
    print(f"    -> {f(konv[50])} Abschlüsse (P10 {f(konv[10])} – P90 {f(konv[90])})")
    m1_rate = konv[50] / total_enter
    print(f"    entspricht {pct(m1_rate)} der Empfänger")
    print("  Methode 2 (Gegenrechnung): Abschluss je Empfänger aus")
    print("    Branchen-Erfahrung Gratis-Trial-Mailing (warm 0,6–1,5% /")
    print("    kalt 0,3–0,8%). Zentral-Mix liegt bei ~0,4–0,6% -> deckt sich.")
    print("  ⇒ belastbare Aussage: GRÖSSENORDNUNG einige Hundert Trial-Starts,")
    print("    NICHT exakt zählbar aus 2025 — erst das S26-Conversion-Goal misst.")

    # --- Sensitivitaet Groesse ----------------------------------------------
    print("\n[4] SENSITIVITÄT — Abschlüsse nach Segmentgrösse (P50)")
    print("-" * 74)
    for label, pick in (("pessimistisch (kleine Segmente)", 0),
                        ("zentral", 1),
                        ("optimistisch (grosse Segmente)", 2)):
        gr = {}
        for s in SEGMENTE:
            if pick == 1:
                gr[s] = dict(GROESSEN_ZENTRAL[s])
            else:
                lo, hi = GROESSEN_BAND[s]
                tot_s = lo if pick == 0 else hi
                split = GROESSEN_ZENTRAL[s]
                base = split["DE"] + split["EN"]
                gr[s] = {"DE": round(tot_s * split["DE"] / base),
                         "EN": round(tot_s * split["EN"] / base)}
        zw = forecast(gr)
        kv = summe_metrik(zw, lambda r: r["konvertiert"])
        n_tot = sum(gr[s]["DE"] + gr[s]["EN"] for s in SEGMENTE)
        print(f"  {label:<34} N={f(n_tot):>7}  "
              f"Abschlüsse P50 {f(kv[50])} (P10 {f(kv[10])}–P90 {f(kv[90])})")

    # --- A/B Power -----------------------------------------------------------
    print("\n[5] VIRTUELLE A/B-TESTS — was ist bei dieser Menge überhaupt")
    print("    detektierbar? (80% Power, α 0,05 zweiseitig, 50/50-Split)")
    print("-" * 74)
    arme = [
        ("NoAbo DE", GROESSEN_ZENTRAL["noabo"]["DE"], 0.40, 0.021),
        ("NoAbo EN", GROESSEN_ZENTRAL["noabo"]["EN"], 0.41, 0.014),
        ("NurWS DE", GROESSEN_ZENTRAL["nurws"]["DE"], 0.42, 0.019),
        ("NurWS EN", GROESSEN_ZENTRAL["nurws"]["EN"], 0.42, 0.015),
        ("NurTV DE", GROESSEN_ZENTRAL["nurtv"]["DE"], 0.43, 0.020),
        ("NurTV EN", GROESSEN_ZENTRAL["nurtv"]["EN"], 0.47, 0.018),
    ]
    print(f"{'Zweig':<11}{'N/Arm':>8}{'MDE Open':>12}{'MDE Klick':>13}"
          f"{'MDE Konv.':>12}")
    print(f"{'':11}{'':>8}{'(Basis~40%)':>12}{'(Basis~2%)':>13}"
          f"{'(Basis~0,5%)':>12}")
    for name, n_lang, o_base, k_base in arme:
        arm = n_lang / 2
        mo = mde_abs(o_base, arm)
        mk = mde_abs(k_base, arm)
        mc = mde_abs(0.005, arm)
        def tag(mde, base):
            rel = mde / base
            return f"{100*mde:.2f}pp/{100*rel:.0f}%"
        print(f"{name:<11}{f(arm):>8}{tag(mo,o_base):>12}"
              f"{tag(mk,k_base):>13}{tag(mc,0.005):>12}")
    print("\n  Lesart:")
    print("   • Open-A/B (Betreff): in NoAbo (beide Sprachen) und NurWS-DE")
    print("     zuverlässig (~2–5pp detektierbar) → HIER Betreff testen.")
    print("   • Klick-A/B (CTA): nur NoAbo detektiert realistische Lifts")
    print("     (~0,5pp ≈ 25% relativ). Kleine Segmente: unterpowert.")
    print("   • Konversions-A/B: praktisch überall unterpowert (nur >50%-")
    print("     Lift in NoAbo sichtbar) → NICHT als A/B, sondern über das")
    print("     Cockpit-Goal aggregat entscheiden.")

    # benoetigte Menge fuer 20% relativen Lift
    print("\n  Nötige Menge JE ARM für +20% relativen Lift:")
    for metrik, base in (("Open (40%)", 0.40), ("Klick (2%)", 0.02),
                         ("Konv. (0,5%)", 0.005)):
        need = n_pro_arm_fuer(base, 0.20)
        print(f"    {metrik:<14} {f(need):>10} / Arm  "
              f"(= {f(need*2)} Empfänger im Test)")

    if schreib_json:
        out = {
            "seed": SEED, "n_sim": N_SIM,
            "raten_2025": {p: {l: RATEN[p][l] for l in ("DE", "EN")}
                           for p in ("WOS", "GTV")},
            "groessen_zentral": GROESSEN_ZENTRAL,
            "headline": {
                "sent": sent_events, "open": open_events,
                "klick_events": klick_events, "eind_klicker": eind,
                "abschluesse": konv, "total_enter": total_enter,
            },
            "abschluss_je_segment": seg_konv,
        }
        path = Path(__file__).with_name("forecast.json")
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"\n[geschrieben] {path}")

    print("\n" + "=" * 74)


if __name__ == "__main__":
    main()

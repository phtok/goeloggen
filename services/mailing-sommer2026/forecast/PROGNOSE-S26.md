# Virtueller Testlauf — Sommer-Aktion 2026 (S26)

*Prognose der Klick- und Abschlusszahlen, verankert an den vier abgeschlossenen
Sommer-2025-Automationen. Reproduzierbar über `simulate.py` (Seed 20260714).
Die Abschluss-Schätzung wurde in einer adversarialen Agenten-Runde geprüft und
nach unten korrigiert — siehe Abschnitt 3.*

---

## Kurzfassung — die zwei Zahlen, nach denen gefragt wurde

Im zentralen Grössen-Szenario (**~46.100 Empfänger**: NurTV 1.094 · NurWS ~5.000 ·
NoAbo ~40.000):

| Grösse | P10 | **Erwartung (P50)** | P90 |
|---|---:|---:|---:|
| Öffnungen (Σ aller Wellen) | 55.000 | **56.800** | 58.700 |
| Klick-Ereignisse (Σ Wellen) | 2.120 | **2.500** | 2.890 |
| **Eindeutige Klicker (Personen)** | 1.350 | **1.620** | 1.910 |
| **Abschlüsse (Trial-Starts)** | 164 | **~208** | 260 |

**Klicks:** rund **1.620 eindeutige Klicker** (≈ 2.500 Klick-Ereignisse über die
Wellen). **Abschlüsse:** Grössenordnung **rund zweihundert Trial-Starts**, zentral
**~208** — mit der Einschränkung unten. **74 % der Abschlüsse kommen aus NoAbo**
(Masse), obwohl dessen Rate am niedrigsten ist.

---

## Die wichtige Vorbemerkung (bevor jemand die 208 für bare Münze nimmt)

Zwei Dinge begrenzen jede Punktzahl ehrlich — beide hast Du selbst schon benannt:

1. **2025 gab es kein Conversion-Goal.** Es existiert keine gemessene
   Abschlussrate. Die Abschlusszahl ist **Szenario-Arithmetik** auf einer
   angenommenen Klick→Signup-Rate, kein aus Daten gemessener Wert.
2. **Die Segmentgrössen liegen in ActiveCampaign, nicht im Repo.** Nur NurTV
   (~1.094) ist belegt; NurWS und NoAbo sind **begründete Schätzungen**. Der
   ActiveCampaign-Connector war in dieser Session **nicht authentifiziert** — ich
   konnte die echten Zahlen nicht ziehen. Darum ist alles zusätzlich auf
   ‹je 1.000 Empfänger› normiert.

> **Abschluss je 1.000 Empfänger: ~4,5** (P10 3,5 – P90 5,6).
> Das ist die übertragbare Kennzahl. Multipliziere sie mit Deiner echten
> Automationsgrösse — der Rest sind meine Grössen-Annahmen.

---

## 1 · Was die 2025-Daten belastbar hergeben

Zwei Muster tragen die ganze Prognose:

**Muster A — EN öffnet stärker als DE, besonders beim WS-Angebot.**
WOS EN w1 46,5 % gegen WOS DE 39,0 %. Beim TV-Angebot ist die Lücke klein
(GTV DE 42,4 % ≈ GTV EN 43,2 %). → Der DE-Betreff des **WS-Angebots** ist der
erste Optimierungsverdacht.

**Muster B — die Klick-Dynamik läuft je Angebot gegenläufig:**

| Angebot | Sprache | Klick w1 → w2 → w3 | Richtung |
|---|---|---|---|
| WS (Wochenschrift) | DE | 2,7 % → 1,8 % → 1,8 % | **fällt** (Ermüdung) |
| WS | EN | 2,3 % → 1,1 % → 1,1 % | **fällt** |
| TV (goetheanum.tv) | DE | 1,6 % → 1,9 % → **2,8 %** | **steigt** (Frist zieht) |
| TV | EN | 1,0 % → 1,2 % → **2,0 %** | **steigt** |

Die **Frist-Mail zieht beim TV-Angebot**, beim WS-Angebot verpufft sie. Das ist
das stärkste Einzelsignal der 2025-Daten und der Kern des A/B-Teils weiter unten.

**Abmeldungen:** je Mail **< 0,5 %** der Versandmenge (52–105 absolut). Der oft
zitierte 12,5-%-Wert stammt aus der winzigen Neujahr-Kampagne (8 Sendungen) und
ist statistisch nicht übertragbar.

---

## 2 · Die Prognose im Detail

Der Trichter je Segment × Sprache × Welle, mit den S26-Besonderheiten (die es
2025 nicht gab): **Conversion-Check vor w2/w3**, **Öffner-Split vor w3**,
**w3b nur an noch-offene Klicker** (nur NoAbo).

**Klicker je Welle (P50, alle Segmente):**

| Welle | Klicker | Bemerkung |
|---|---:|---|
| w1 | ~870 | Ankündigung/Brücke |
| w2 | ~720 | Erinnerung + Datum |
| w3 | ~910 | Frist — **klickstärkste Welle** |
| w3b | ~255 | Mini-Reminder, nur NoAbo-Klicker |

**Abschlüsse je Segment (P50):**

| Segment | Abschlüsse | Anteil | Rate /1.000 | warum |
|---|---:|---:|---:|---|
| NoAbo → beide | ~152 | 74 % | ~3,8 | **Masse schlägt Rate** — der Löwenanteil |
| NurWS → TV | ~44 | 21 % | ~8,8 | mittleres Segment, TV-Frist-Effekt hilft |
| NurTV → WS | ~10 | 5 % | ~9,1 | winziges Segment (1.094), trotz warmer Rate |

Lehre: **NoAbo entscheidet das Ergebnis.** Jede Optimierung, die dort auch nur
einen halben Prozentpunkt Klick bewegt, ist mehr wert als jede Perfektion an den
kleinen warmen Segmenten. Zugleich: die **warmen Segmente haben die höhere Rate
je 1.000** — sie sind effizienter, nur klein.

---

## 3 · Abschlüsse — der ehrliche Teil (adversarial geprüft)

Ich habe die Abschluss-Schätzung von mehreren Agenten parallel angreifen lassen.
Zwei Befunde haben die Zahl bewegt:

**Belegte Benchmarks (Web-Recherche).** Klicker→Trial-Start liegt bei Abo-/Medien-
Produkten im Band **10–25 %** (E-Mail-Traffic-Median auf fokussierte Landingpages
~19 %; kalte Trial-Signups nur 2–5 %, best-in-class >11 %). Die **Sommer-Schwäche**
(Juli/August, schwächste Öffnungsmonate) steckt bereits in meinen 2025-Sommer-
Ankern — kein zusätzlicher Abschlag nötig.

**Die Korrektur, die zählt (NoAbo).** Mein ursprüngliches nominales p = 12 % für
NoAbo war **effektiv ~16 %** — der w3b-Zweitbiss (Mini-Reminder an offene Klicker)
hebt die tatsächliche Konversion je eindeutigem Klicker um ~26 % über den
Nominalwert. Effektiv 16 % ist für ein **kaltes** Publikum mit **Extra-Hop über die
Übersichtsseite** und **Kartenpflicht** (Uscreen-Trial) zu optimistisch. Deshalb
korrigiert auf **nominal 8 %** (effektiv ~11 %) — hergeleitet als warm-direkt 25 %
× Kalt-Abschlag ~0,55 × Hop-Abschlag ~0,65. **Das senkt die Headline von ~276 auf
~208.** Die warmen Segmente (NurTV 25 %, NurWS 22 %) blieben unverändert — die
Prüfung bestätigte sie als haltbar.

**Kreuzprobe.** Der Zentral-Mix ergibt ~0,45 % Abschluss je Empfänger — deckt sich
mit Erfahrungswerten (warm 0,6–1,5 %, kalt 0,3–0,8 %).

**Konsistenz mit Deiner Beobachtung.** Du hast angemerkt, der Wellen-Schwund 2025
sei mit ~300–400 Kontakten winzig gewesen. Genau das passt: **rund zweihundert
Abschlüsse über eine 46.000er-Automation verschwinden im ±300er-Rauschen der
Versandmengen.** Die Abwesenheit eines sichtbaren Schwunds *widerlegt* die 208
nicht — sie ist mit ihr vereinbar.

**Testbare Vorhersage für S26.** Weil diesmal der Conversion-Check Konvertierte
*aktiv austreten lässt*, sollte der Wellen-Schwund **sichtbar höher** liegen als
2025 (grob von ~150/Welle auf ~230–280/Welle in NoAbo). **Dieser Zuwachs IST das
Konversionssignal** — schon bevor das Goal zählt. Bleibt er aus, konvertiert das
Angebot schlechter als angenommen (dann ist die Übersichtsseite der Verdächtige).

> **Belastbare Aussage:** Grössenordnung **rund zweihundert Trial-Starts**, zentral
> ~208 (164–260). Exakt zählbar wird das erst durch das S26-Conversion-Goal —
> weshalb dessen sauberes Setzen je Automation der wichtigste Messhebel ist.

---

## 4 · Wo performt ihr noch nicht optimal — die virtuellen A/B-Tests

Zuerst die nüchterne Frage: **Was lässt sich bei dieser Menge überhaupt messen?**
(80 % Power, α 0,05 zweiseitig, 50/50-Split — minimal detektierbarer Effekt MDE):

| Zweig | N/Arm | MDE Öffnung | MDE Klick | MDE Konversion |
|---|---:|---|---|---|
| NoAbo DE | 11.000 | 1,85 pp / 5 % | 0,54 pp / 26 % | 0,27 pp / 53 % |
| NoAbo EN | 9.000 | 2,05 pp / 5 % | 0,49 pp / 35 % | 0,29 pp / 59 % |
| NurWS DE | 1.750 | 4,67 pp / 11 % | 1,29 pp / 68 % | — |
| NurWS EN | 750 | 7,14 pp / 17 % | — | — |
| NurTV DE/EN | ~300 | ~11–13 pp / 26 % | — | — |

**Die drei Leitplanken:**

- **Betreff-/Öffnungs-Tests** sind in **NoAbo (beide Sprachen)** und **NurWS-DE**
  zuverlässig (2–5 pp detektierbar). → Hier gehört der A/B-Aufwand hin.
- **Klick-/CTA-Tests** sind **nur in NoAbo** sinnvoll und erkennen dort nur
  **grosse** Lifts (~0,5 pp ≈ 26 % relativ). Für einen 20-%-Lift bräuchtest Du
  DE+EN gepoolt (~42.000 Empfänger im Test). Kleine Segmente: **unterpowert — nicht
  testen, sondern die 2025-Erkenntnis übertragen.**
- **Konversions-A/B ist praktisch unmöglich** (selbst NoAbo erkennt nur > 50-%-
  Lifts). → Konversion **nicht** per A/B entscheiden, sondern **aggregat über das
  Cockpit-Goal** messen.

### Der Plan, nach Erwartungswert × Power gereiht

**1 · DE-Betreff des WS-Angebots (NoAbo DE · Öffnung · gut gepowert).**
Grösste sichtbare Lücke 2025: WOS DE öffnete 39,0 % gegen WOS EN 46,5 %.
A = Standard-Ankündigung · B = Brücken-Betreff «Was Sie sehen, jetzt auch lesen».
Ziel +3–5 pp Öffnung. Bestens detektierbar (MDE 1,85 pp). *Hausregel: Betreff
normal, keine Versalien/Verknappung (G05).*

**2 · Frist-Dramaturgie auf das WS-Angebot übertragen (NoAbo/NurTV, w3 · Klick).**
Das stärkste 2025-Signal: TV-Klick steigt zur Frist (2,8 / 2,0 %), WS-Klick fällt
(1,8 / 1,1 %). Die Frist-Rahmung, die beim TV-Angebot zieht, auf die WS-Wellen
übertragen. A = WS-w3 wie bisher · B = echte Frist-Rahmung wie GTV. Grösster
**Klick**-Hebel — aber nur in NoAbo überhaupt messbar (grenzwertig); in den kleinen
Segmenten als Erkenntnis direkt übernehmen, nicht testen.

**3 · w3-Alt-Betreff für Nicht-Öffner (NoAbo · Öffnung · gut gepowert).**
w3 ist die klickstärkste Welle; Nicht-Öffner dort zu öffnen ist hochwertig. Der
Öffner-Split existiert bereits — teste die **Formulierung** des Alt-Betreffs.
A = Brücke-Rahmung · B = Szene/Inventar («800 Videos warten»). Ziel +2–4 pp.

**Was NICHT getestet wird — und warum das auch eine Antwort ist:**
Die letzte Welle ist **abmelde-unkritisch**. Benchmark: gesunde Abmelderate
0,1–0,5 %/Versand, Spike erst > 1 %. NoAbo (kalt, 40k) landet am oberen Ende der
gesunden Spanne, aber die **eingebaute Entschärfung ist lehrbuchmässig**: der
w3-Öffner-Split gibt Nicht-Öffnern einen frischen Betreff (Frequenz-Überdruss =
40–50 % aller Abmeldegründe), und w3b trifft die kalte Masse **nicht** ein viertes
Mal. Da 2025 schon **ohne** diese Schutzmechanismen < 0,5 % blieb, ist ein Spike
unwahrscheinlich. → **Keine zusätzliche Dringlichkeit hineintexten** (deckt sich
mit der Würde-Verbotsliste und Deiner Vorgabe, w3 nicht zu verschärfen).

---

## 5 · Sensitivität — es hängt an den Segmentgrössen

| Szenario | N gesamt | Abschlüsse (P50) | Band |
|---|---:|---:|---|
| pessimistisch (kleine Segmente) | 36.100 | 159 | 125–200 |
| **zentral** | 46.100 | **207** | 164–259 |
| optimistisch (grosse Segmente) | 57.100 | 264 | 210–328 |

Die Spannweite kommt fast ganz aus **NurWS** und **NoAbo** (NurTV ist belegt und
klein). **Nenne mir die drei echten Grössen, und das Band kollabiert.**

---

## 6 · Methodik & Reproduzierbarkeit

- **`simulate.py`** — Monte-Carlo, 40.000 Durchläufe je Zweig, fester Seed.
  Doppelt-stochastisch: (1) wahre S26-Rate ~ N(2025-Anker, Streuung aus der
  Kampagnen-Spanne), (2) Zahl ~ Binomial. Bänder = Perzentile P10/P50/P90.
- **`basis-2025.json`** — die vier Kampagnen als Eingabe (Deine AC-Zahlen).
- **`forecast.json`** — maschinenlesbarer Ergebnis-Dump (fürs Cockpit/Dashboard).
- Aufruf: `python3 simulate.py` (Bericht) · `--json` (Ergebnis-Datei).

**Bewusste Konservativität:** warme Segmente bekommen +4 pp Öffnung, aber **keinen**
Klick-Bonus. NoAbo-p nach adversarialer Prüfung auf nominal 8 % gesenkt. Da NoAbo
74 % der Abschlüsse trägt, ist diese eine Zahl der grösste Hebel der ganzen
Prognose — deshalb bewusst am unteren, verteidigbaren Rand angesetzt.

---

## 7 · Was ich als Nächstes schärfen kann

1. **Die drei echten Segmentgrössen einsetzen** (aus AC) → Band kollabiert.
2. **Eindeutige Klick→Abo-Konversion je 2025-Kampagne** über die Kontaktlisten
   annähern (wie von Dir angeboten) — der ehrlichste Abschluss-Ersatz und die
   direkte Kalibrierung von p. Braucht AC-Zugriff (Connector autorisieren).
3. Nach w1-Versand: **Ist-Öffnung/-Klick gegen die Prognose** halten und das
   Modell nachziehen — die Bänder verengen sich mit jeder gelaufenen Welle.

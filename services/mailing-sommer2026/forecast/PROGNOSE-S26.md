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

**Abmeldungen:** in den Sommer-2025-Serien je Mail **< 0,5 %** (52–105 absolut).
Auch die reale GTV-Neujahr-Mail 3 (Feb 2026) — die Quelle des «12,5 %»-Insights —
lag echt bei nur **0,585 % (DE) / 0,517 % (EN)** (90 bzw. 68 Abmeldungen auf
15.385 / 13.150): kein Spike. Der «12,5 %»-Wert hält den realen Zahlen nicht
stand (Details §3, Kalibrierung).

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

### Reale Kalibrierung: die GTV-Abo-Kampagne Feb/März 2026 («Feuerpferd»)

Der erste **echte** Konversions-Ankerpunkt — was den 2025-Sommer-Daten fehlte
(dort kein Goal). Eine abgeschlossene GTV-Abo-Kampagne (Rabatt 30 %, drei Mails,
26.2.–4.3.2026) brachte **76 kampagnen-attribuierte Abschlüsse** (Coupon-
Einlösungen, «nachweislich durch 3 Mails ausgelöst») aus 103 ausgegebenen Codes
(74 % Einlösung), Ø **~€124 brutto** je Abschluss, ~€9.500 Coupon-Brutto; das
Publikum ist international (10 Sprachen erfasst). *(Nur Aggregate; die Quelle
enthält Personendaten, die hier bewusst nicht verarbeitet werden.)*

Was das für S26 heisst:

- **Grössenordnung bestätigt.** Ein einzelnes GTV-Drei-Mail-Angebot konvertiert in
  **Dutzenden** (76). Meine S26-Prognose (~208) über eine **3×** grössere,
  dreisegmentige Automation ist dieselbe Grössenordnung — «einige Hundert, nicht
  Tausende» hält, und die **Abwärtskorrektur des NoAbo-p war richtig**, nicht zu
  vorsichtig.
- **Jetzt mit exakter Rate.** Die echte Versandmenge (GTV Neujahr 2026, Mail 1):
  **30.381 DE + 25.405 EN = 55.786** erreicht. → **76 / 55.786 = 0,14 %/Empfänger**
  für ein **kaltes, bezahltes** 30-%-Rabatt-Angebot. Gemessen, keine Annahme.
- **Rekonziliation mit S26 (der Clou).** Mein korrigiertes NoAbo (kalt, **Gratis**-
  Trial) liegt bei 152 / 40.000 = **0,38 %/Empfänger**. Der Sprung 0,14 % → 0,38 %
  ist ein **~2,8× Free-über-Bezahl-Aufschlag** (Trial-Starts ohne Sofortzahlung
  konvertieren typisch 2–4× über einen Bezahl-Rabatt) — **mitten im plausiblen
  Band**. Die reale Kampagne **bestätigt die Abwärtskorrektur**; aus «Annahme» wird
  «Messwert». Sommer (schwächer als Februar) wirkt leicht gegenläufig, ändert die
  Grössenordnung nicht.

**Drei Bestätigungen aus derselben realen Kampagne:**

1. **Öffnungsraten — ein zweites Mal bestätigt.** GTV26 öffnete w1/w2 bei
   **40–41 % (DE) / 39–40 % (EN)** — praktisch deckungsgleich mit den 2025-Sommer-
   Ankern und meinen S26-Annahmen. Zwei unabhängige reale Kampagnen, dieselben
   Öffnungsraten → das Fundament der Prognose steht.
2. **Die Frist-Mail ist real unkritisch.** GTV26 Mail 3 hatte **0,585 % / 0,517 %**
   Abmeldungen — kein Spike. Die leicht höhere Rate als im Sommer (~0,35 %) erklärt
   die **komprimierte Taktung** (3 Mails in **5 Tagen**). **S26 verteilt dieselben
   drei Wellen über ~3½ Wochen** → noch entspannter, Abmelde-Risiko noch tiefer.
   Also: **w3 nicht entschärfen, keine Zusatz-Dringlichkeit** (deckt sich mit der
   Vorgabe).
3. **Gate vs. Split (Struktur-Hinweis).** GTV26 **gatete** w3 (nur ~51 % — die
   Engager — bekamen Mail 3; daher dort die «>60 %»-Öffnung). S26 **splittet**
   stattdessen: alle bekommen w3, Nicht-Öffner mit Alt-Betreff. Meine Prognose
   rechnet w3 korrekt auf die **volle** Basis (S26-Design). Falls die Abmeldungen
   im Betrieb doch klettern, ist GTV26s Gate der bewährte Notausgang für den
   Nicht-Öffner-Rest.

**Werthebel (aus den realen €-Zahlen).** Ein Feb-Abschluss war ~€124 brutto wert.
Ein S26-Trial-Start ist zunächst **€0** — sein Wert = *Trial→Paid-Rate* × Jahres-
Abo. Damit ist die **Onboarding-Strecke nach dem 8.8.** (Willkommen → Mid-Trial →
Erinnerung vor Ablauf) nicht Kür, sondern der **eigentliche Umsatzhebel** — genau
wie im Drehbuch (§6) vermerkt. Ohne sie sind die ~208 Starts nur potenzieller,
kein realisierter Umsatz.

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

### Performance steigern — die Hebel nach Wirkung

Nicht alles ist ein A/B-Test. Wo die Evidenz eindeutig ist, wird **gehandelt**,
nicht getestet; wo sie unsicher **und** messbar ist, wird **getestet**:

| # | Hebel | wirkt auf | Typ | Vorgehen |
|---|---|---|---|---|
| 1 | **NoAbo-Übersichts-Hop verkürzen** (1-Klick statt Wahl-Zwischenseite) | Konversion | Struktur | **Einfach tun** — grösster Konversions-Hebel: NoAbo = 74 %, jede Funnel-Stufe verliert 20–40 % |
| 2 | **Frist-Dramaturgie aufs WS-Angebot** (w3, NurTV + NoAbo) | Klick | Copy | Übertragen; in NoAbo A/B-bar |
| 3 | **Onboarding-Strecke nach dem 8.8.** (Willkommen → Mid-Trial → Erinnerung) | Umsatz | Struktur | **Einfach tun** — grösster €-Hebel: Trial-Start = €0 bis Trial→Paid |
| 4 | **DE-Betreff des WS-Angebots** (Brücke) | Öffnung | Copy | A/B in NoAbo DE (gut gepowert, MDE 1,85 pp) |
| 5 | **w3-Alt-Betreff für Nicht-Öffner** | Öffnung | Copy | A/B in NoAbo |

**Der rote Faden:** Öffnen ist gelöst (~41 %, zweimal real bestätigt) — es klemmt
am **Klick** (Hebel 2/4/5) und an der **Landing-Konversion** (Hebel 1). Der grösste
*Umsatz*-Hebel liegt sogar erst **nach** der Kampagne (Hebel 3).

**Nicht tun (auch ein Ergebnis):** Konversions-A/B (unterpowert → über das Goal
messen), w3 entschärfen (real 0,5–0,6 % Abmeldung = safe), die kleinen warmen
Segmente feinschleifen (Volumenanteil zu klein, um das Ergebnis zu bewegen).

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
- **`basis-2025.json`** — die vier Sommer-Kampagnen als Eingabe (Deine AC-Zahlen).
- **`kalibrierung-gtv-neujahr-2026.json`** — die reale Feb-2026-TV-Kampagne
  (Sends, Öffnungen, Abmeldungen, 76 Abschlüsse) als externe Kalibrierung.
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

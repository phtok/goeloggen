# Lead-Maschine — Pflichtenheft der fünf Schleifen

*Arbeitsstand. Ausführungs-Spezifikation zu `docs/marketing-maschine.md` §6.
Eine Schleife gilt als «gebaut», wenn sie ohne wöchentliches Zutun läuft und
ihre Messpunkte im Cockpit erscheinen. Stack-Voraussetzungen (Uscreen-Coupons
und Abandoned-Cart, Zoho Double-Opt-in, Supabase Edge Functions + `pg_cron`)
sind belegt — Quellen im Konzept §15.*

---

## Schleife 1 — Seelenkalender-Keil

**Zweck:** freier Wochenspruch als Eintrittstür; wöchentlicher Takt = Takt der
Wochenschrift; Leads aus Ring 2 (anthroposophisch Berührte).

**Baustufe A — Web (gebaut):** `apps/seelenkalender/` zeigt den Spruch der
laufenden Woche (Oster-Anker, Gauss-Osterformel, Woche 1 = Osterwoche), blättern,
kopieren/teilen, Vertiefungs-Verweise mit UTM (`utm_campaign=evergreen`,
`utm_content=seelenkalender`). Verstexte gemeinfrei (Steiner 1912/13), Quelle
anthro.world, alle 52 eindeutig extrahiert; Stichproben (1, 12, 26, 40, 52)
verifiziert.

**Baustufe B — Versand-Strecke:**
1. Anmeldung: Formular (Paperform-Muster wie Sommer-Aktion) → Webhook →
   `marketing_leads` (gehashte E-Mail, Einwilligung Double-Opt-in, Herkunfts-Motiv).
2. Versand: wöchentlich (So/Mo früh) per Edge Function + `pg_cron`; Inhalt =
   Spruch der Woche + **ein** Vertiefungs-Verweis (WoS oder GTV, alternierend,
   Frequenz-Deckel beachten). ESP-Entscheid (Zoho Campaigns vs. schlanker
   SMTP-Dienst) = offene Entscheidung im Konzept §14.
3. Jede Ausgabe trägt UTM je Motiv (`vers_NN`), Attribution besteht.

**Baustufe C — Verbreitung:** einbettbares Widget (ein `<script>`-Einzeiler für
Partnerseiten, Schleife 3) + Spruch-Kachel als Bild (Schleife 4, Cover-Generator-
Muster).

**Messpunkte:** Netto-Listenwachstum/Woche · Öffnungs-/Klickrate ·
Klicks zur Vertiefung je `vers_NN` · Trials mit Herkunft `seelenkalender`.
**Aufwand:** einmalig 2–4 Tage (B), laufend ≈ 0 (Inhalt ist fix, 52 Wochen).

---

## Schleife 2 — Archiv als Sog

**Zweck:** 100 Jahrgänge + ~500 Aufnahmen von totem Bestand zu kumulativ
wachsender Eintrittsfläche machen.

**Baustufen:**
1. **«Vor 100 Jahren»** — tagesgenau ein Archivstück (Titel, Auszug, Scan) als
   Auto-Post (Web-Seite + Newsletter-Baustein + Kachel). Voraussetzung: Zugriff
   auf digitalisierte Jahrgänge (Bestand `collections/jahrgaenge` — Umfang und
   Rechte **zu klären**, offene Entscheidung).
2. **Offene Volltextsuche** — Index öffentlich (jeder Treffer = Sucheintrag),
   Volltext hinter E-Mail-Freischaltung (Lead) bzw. Abo (Konversion).
3. **«Frag das Archiv»** — semantische Suche (Supabase `pgvector`, Embeddings je
   Absatz; Antwort mit Fundstellen-Zitaten, **keine** freie Generierung ohne
   Quelle — Würde-Regel). Jede Anfrage ohne Abo endet in einer
   Freischaltungs-Einladung.

**Messpunkte:** organische Einstiege/Monat (kumulativ) · Freischaltungen ·
Suche→Trial-Konversion. **Aufwand:** der grösste der fünf — je Baustufe einzeln
schätzen; 1 ist klein, 2–3 hängen an der Digitalisierungs-Frage.

---

## Schleife 3 — Netzwerk als Kanal (Partner-Kit)

**Zweck:** die über 1200 Waldorfschulen, Weleda/Demeter-Kreise, Kliniken, Zweige
und die Christengemeinschaft als vertrauenswürdige Verteilknoten gewinnen —
Reichweite mit Vertrauen statt Geld.

**Bausteine:**
1. **Partner-Register** (`marketing_partner`): Institution, Sprache, Kanal
   (Eltern-Newsletter, Aushang, Website), Ansprechperson (gehasht/extern gepflegt).
2. **Monats-Kit**, automatisch aus Schleife 4 gespeist: eine Spruch-Kachel, eine
   Archiv-Perle, ein Clip-Verweis — je Partner mit **eigenem UTM-Rücklink**
   (UTM-Generator besteht) und einbettbarem Widget (Schleife 1C).
3. **Gegenwert statt Bitte:** das Kit ist für den Partner selbst brauchbar
   (fertiger Inhalt für dessen Newsletter) — deshalb wird es genommen.
4. Quartalsweise: Partner-Rangliste im Cockpit (Konversionen je Rücklink),
   stille Partner erhalten ein anderes Kit, nicht mehr Druck (Würde-Regel).

**Messpunkte:** aktive Partner · Konversionen je Partner-Motiv · CPA = 0.
**Aufwand:** einmalig Kit-Vorlage + Register; laufend ≈ 1 h/Monat Kuratierung.

---

## Schleife 4 — Atomisierungs-Pipeline

**Zweck:** aus jeder Redaktions-Einheit (Artikel/Aufnahme) automatisch fünf
Lead-Flächen — Kosten je Kontakt gegen null.

**Pipeline je Einheit:**
| Fläche | Werkzeug | Automatisierungsgrad |
|---|---|---|
| Zitat-Kachel (Hausschrift) | bestehender Cover-/Kachel-Generator | Vorlage + Text einsetzen |
| 60-Sekunden-Clip | Schnitt aus GTV-Aufnahme | halbautomatisch (Markierung) |
| Newsletter-Anriss | Redaktionstext, gekürzt | Vorlage |
| Archiv-/SEO-Seite | statische Seite je Beitrag | automatisch |
| Seelenkalender-Bezug | Verweis Spruch ↔ Thema | redaktionell, 1 Zeile |

Jede Fläche trägt ihr UTM-Motiv; die Attribution je Motiv besteht im Cockpit.
**Messpunkte:** Flächen je Einheit · Konversion je Fläche · beste Motive je
Quartal (Entscheid: mehr davon). **Aufwand:** Vorlagen einmalig; laufend Minuten
je Einheit statt Stunden.

---

## Schleife 5 — Würdevolles Schenken

**Zweck:** aus Bindung Akquise machen — ohne Rabatt-Rhetorik.

**Mechanik:** «Schenke einen Monat»: Abonnent löst Geschenk aus → Empfänger
erhält persönliche Übergabe (Karte/Mail mit Absender-Name, hausgesetzt) + Code.
Technisch: Uscreen-Coupon (100 %, Dauer `Once` bzw. `Repeating` für
Mehrmonats-Geschenke) — **belegt vorhanden, keine Zusatzkosten**. Für die
Wochenschrift analog über Zoho-Gutschein (zu verifizieren) oder manuelle Liste
in Stufe 1.

**Regeln (Würde):** kein Countdown, kein Kettenzwang, Empfänger kann still
ablehnen; ein Geschenk je Empfänger je Jahr (Frequenz-Deckel).

**Messpunkte:** Geschenke je 100 Abonnenten · Einlösequote · Bleibe-Quote der
Beschenkten nach 3 Monaten (Kohorten-Muster des Sommer-Zählers). **Aufwand:**
Coupon-Vorlage + Übergabe-Vorlage einmalig; laufend ≈ 0.

---

## Reihenfolge & Abhängigkeiten

1. **Jetzt:** Schleife 1B (Versand) — kleinster Bau, grösster Taktgewinn;
   braucht nur ESP-Entscheid (§14 im Konzept).
2. **Dann:** Schleife 4 (Vorlagen) — speist 3 und verbilligt alles Weitere.
3. **Dann:** Schleife 3 (Partner-Kit) — braucht 4 als Zulieferer.
4. **Parallel klein:** Schleife 5 (Coupon + Vorlage, Weihnachtsfenster als
   erster Test — Massnahme im Protokoll).
5. **Gross, eigenes Vorhaben:** Schleife 2 (Digitalisierungs-/Rechtsfrage
   zuerst klären).

Jede Schleife wird als **Massnahme im Protokoll** geführt (Hypothese → Ist →
Entscheid), Zeitaufwand wie Geld bilanziert (Konzept §12d).

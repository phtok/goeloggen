# Die Marketing-Maschine — Wochenschrift & goetheanum.tv

*Arbeitsstand. Grundlage: die vorhandene Kampagnen-Infrastruktur (Sommer-Zähler
2026), das Strategieblatt (`docs/strategie.md`), sowie eine mehrsträngige,
quellengeprüfte Recherche zu Vergleichsprodukten, Abo-Ökonomie, dem empirischen
Marketing-Kanon (Sharp/Ehrenberg-Bass, Binet & Field), Marty Neumeier und
Null-Budget-Wachstum. Belegte Zahlen sind mit Quelle und Abrufdatum in §14
geführt; jede Aussage trägt einen Evidenzgrad: **[belegt]** (Primärquelle,
adversarisch geprüft), **[plausibel]** (Quelle vorhanden, nicht gegengeprüft),
**[anekdotisch]** (Einzelfall, illustrativ).*

> **Kernsatz vorweg.** Es gibt keine Marketing-Maschine zu bauen — es gibt eine
> zu **verstetigen**. Die Sommer-Aktion 2026 ist bereits die erste Umdrehung:
> Lead-Erfassung, UTM-Attribution je Motiv, Wirkungskette Sichtbarkeit →
> Aktivierung → Wirkung → Bindung, CPA je Massnahme, Uscreen- und
> Paperform-Webhooks live. Dieses Dokument macht aus der einmaligen Aktion ein
> **Jahresrad** und aus dem Cockpit einen **Regelkreis**.

---

## 1. Ausgangslage & Zahlenbasis

Zwei Produkte, ein Haus, ein Publikum mit grosser Überschneidung.

| | Wochenschrift «Das Goetheanum» | goetheanum.tv |
|---|---|---|
| seit | 1921 | jung, Uscreen-gehostet |
| Umfang | wöchentlich, DE/EN | ~500 Aufnahmen, wöchentlich neu |
| Bestand | Druckauflage ~4650, ~15 000 Leser | Abo mit 7-Tage-Trial |
| Formate | Papier · Digital | Stream (Monats-/Jahresabo) |
| Abrechnung | Zoho | Uscreen |
| Wahrheitsstand | Zoho Subscriptions | Uscreen |

*(Interne Zahlen — 4650 / 15 000 / ~500 — sind aus den Mediadaten bzw. der
Aufgabenstellung übernommen und vor der Fortschreibung **zu bestätigen**.)*

**Was heute schon gemessen wird.** Der Sommer-Zähler liest die Aktion als
**Kette**, nicht als Einzelzahl: sechs Ströme (WoS DE/EN × Papier/Digital, GTV
DE/EN), Attribution bis auf das **Motiv** (`reel_ernst_zuercher` vs.
`footer_link`), CPA je **Massnahme** aus dem Massnahmen-Protokoll, der
Drei-Monats-Moment als Kohorten-Entscheid (`bleibt` / `gekuendigt` /
`laeuft-aus`). Das Konzept beginnt also nicht bei null, sondern bei einer
laufenden, datensparsamen Messmaschine (nur Summen verlassen die Datenbank,
E-Mails nur gehasht). Details: `services/sommer-zaehler/README.md`.

**Die heutigen Kanäle** (in §Recherche R1 zu vervollständigen): Websites
`dasgoetheanum.com` und `goetheanum.tv`, die Portal-Seite `goetheanum.ch`,
Redaktions-Newsletter, YouTube (Live-Streams), Instagram/Facebook/LinkedIn,
Print als eigenes Reichweitenmedium. Die Sommer-Aktion 2026 fährt sechs
Landingpages auf eigenen Subdomains (`tv-sommer2026.goetheanum.tv`,
`ws-sommer2026.dasgoetheanum.com`, je DE/EN).

---

## 2. Die Zielmarke ehrlich gelesen

«Obere fünfstellige Abozahl» heisst 10–20× des heutigen Bestands. Diese Zahl
gehört an den Anfang, nicht ans Ende — weil sie die ganze Strategie bestimmt.

**Die Fermi-Rechnung, nüchtern.** Drei Ringe:

1. **Kernmilieu** (anthroposophisch gebunden): Mitglieder der Allgemeinen
   Anthroposophischen Gesellschaft, aktive Zweige, Wochenschrift-Stammleser.
   Grössenordnung Zehntausende weltweit — aber grösstenteils bereits erreicht
   oder bewusst nicht abonnierend. Hier liegt **Bindung und Rückgewinnung**,
   kaum noch Neuwachstum.
2. **Angrenzende Milieus** (anthroposophisch berührt): Waldorf-Elternschaft
   weltweit, Demeter-Kundschaft, Weleda-Verwenderinnen, anthroposophische
   Medizin, Christengemeinschaft. Hunderttausende bis Millionen Menschen mit
   **latentem** Interesse, die WoS/GTV nicht kennen oder nie einen Anlass zum
   Probieren hatten. **Hier liegt das realistische Neuwachstum.**
3. **Weiter Markt** («spiritually curious», kontemplativ Interessierte,
   englischsprachig): der grösste, aber unschärfste Ring. Nur über die
   **englische Schiene** und über Plattform-Sichtbarkeit (YouTube, SEO)
   erreichbar.

**Der empirische Deckel.** Zahlungsbereitschaft für Online-Journalismus liegt
selbst in reichen Ländern im Schnitt bei **18 %**, im deutschen Kernmarkt bei
**13 %**, in der Schweiz 2025 bei **22 %** (Norwegen als Spitze: 42 %)
**[belegt]**. Von den Nicht-Zahlern sind **64 %** durch **kein** Angebot zum
Zahlen zu bewegen **[belegt]**. Das ist die harte Wand: Reichweite lässt sich
vergrössern, aber die Konversion zu bezahltem Nischeninhalt ist gedeckelt.

**Die ehrliche Folgerung.** 10–20× ohne Produktänderung ist **nur** erreichbar,
wenn der zweite und dritte Ring erschlossen werden — also durch
**Publikums-Erweiterung**, nicht durch mehr Loyalität im Kern. Das deckt sich
mit dem Sharp/Ehrenberg-Bass-Befund: Penetrationswachstum kommt aus der
**Neukundengewinnung über die Stammkundschaft hinaus**, nicht aus gesteigerter
Kaufrate der Bestehenden **[plausibel]**. Marketing allein bringt uns die ersten
Vervielfachungen (bis in den mittleren fünfstelligen Bereich — vgl. Republik mit
~36 000 Abos, werbefrei, deutschsprachig, aus dem Stand in wenigen Jahren
**[belegt]**). Der Sprung in den **oberen** fünfstelligen Bereich ist ein
Mehrjahres-Zinseszins und hängt an der englischen Schiene (§10).

---

## 3. Markenfundament nach Neumeier — zwei Stimmen, ein Haus

Aufgebaut wie das Strategieblatt: **Onliness** (das ZAG), **Zag** (die radikale
Abweichung), **Tribe** (Brand Flip: Menschen schliessen sich Stämmen an, nicht
Produkten). Getrennt je Produkt, weil die «Jobs» verschieden sind — verbunden im
Dach, weil das Publikum eines ist.

### goetheanum.tv — Onliness

> goetheanum.tv ist der **EINZIGE** Bewegtbild-Ort, an dem hundert Jahre
> lebendige Geisteswissenschaft **aus der Quelle** sprechen — geführt von denen,
> die sie heute forschen und üben — für Menschen, die nicht **über**
> Anthroposophie lesen, sondern ihr **begegnen** wollen, in einer Zeit, in der
> Spiritualität sonst als App-Häppchen verkauft wird.

*(WAS = kuratierter Streaming-Ort · WIE = aus der Quelle, nicht über sie · WER =
Begegnungs- statt Konsum-Suchende · WO = Goetheanum/weltweit · WARUM = Begegnung
statt Information · WANN = Zeitalter der spirituellen Häppchen.)*

**Zag:** Wo alle Achtsamkeits-Apps auf **Reduktion** setzen (10 Minuten, ein
Timer, eine Stimme), setzt goetheanum.tv auf **Fülle und Herkunft** — die
unverkürzte, verortete geisteswissenschaftliche Arbeit. Das ist kein Nachteil
gegen Calm/Headspace, es ist die Abweichung.

**Tribe:** Nicht «Abonnenten einer Plattform», sondern **Mitübende einer
weltweiten Schule**. Der Brand Flip: nicht «Was verkaufen wir ihnen?», sondern
«Wer werden sie, wenn sie dabei sind?»

### Wochenschrift «Das Goetheanum» — Onliness

> Die Wochenschrift ist die **EINZIGE** Stimme, die das anthroposophische
> Weltgeschehen **wöchentlich und aus dem Zentrum** verdichtet — kein Archiv,
> kein Blog, sondern der **verlässliche Takt** einer hundertjährigen
> Gedankenbewegung — für Menschen, die Zugehörigkeit **in Ruhe** suchen, in
> einer Zeit permanenter Feed-Erregung.

*(WAS = wöchentliche Verdichtung · WIE = aus dem Zentrum, im Takt · WER =
Zugehörigkeit-in-Ruhe-Suchende · WO = weltweite Leserschaft · WARUM =
Verlässlichkeit statt Erregung · WANN = Zeitalter des Feeds.)*

**Zag:** Gegen die Beschleunigung setzt die WoS **Wöchentlichkeit als
Wert** — der Takt selbst ist das Produkt, nicht die einzelne Meldung.

**Tribe:** Leser sind **Zeitgenossen einer Bewegung**, nicht Konsumenten von
Artikeln.

### Das Dach — Brand-Commitment-Matrix (verkürzt)

| Ebene | Mensch (Publikum) | Haus (wir) |
|---|---|---|
| Identität ↔ Purpose | «Ich gehöre zu dieser Bewegung / will ihr begegnen.» | Ein würdiger, verlässlicher Ort dafür |
| Bedürfnis ↔ Onliness | «Ich will Quelle, nicht Häppchen; Takt, nicht Erregung.» | Die einzigen zwei Kanäle, die das aus dem Zentrum geben |
| Haltung ↔ Werte | Ruhe, Ernst, Zugehörigkeit | Klarheit, Würde, Datensparsamkeit |

**Cross-Selling-Grundlage:** WoS-Leser und GTV-Zuschauer sind weitgehend
**dasselbe Publikum in zwei Zuständen** — lesend und schauend. Wer den einen Job
mietet, hat oft auch den anderen. Das begründet die Bündel-Kommunikation (§7, §12),
verlangt aber Frequenz-Disziplin (§11), damit dasselbe Publikum nicht doppelt
bespielt und müde wird.

---

## 4. Empirische Grundlagen — das Marketing-Wissen, geprüft

Nicht Meinung, sondern Befundlage — jede These mit Evidenzgrad.

**Sharp / Ehrenberg-Bass — mentale & physische Verfügbarkeit.** Marken wachsen
durch **Reichweite** (viele leichte Käufer erreichen), nicht durch Loyalität
weniger. Wachstum in Abo-/Subskriptionsmärkten kommt fast vollständig aus
**Neukundengewinnung**, kaum aus Kaufraten-Steigerung **[plausibel]**.
*Übertragung mit Vorsicht:* Sharps Gesetze sind an grossen FMCG-Marken belegt;
für ein weltanschauliches Nischenprodukt gilt der Reichweiten-Vorrang
qualitativ, aber die «Light Buyer»-Basis ist kleiner und selektiver.
Konsequenz für uns: **breite, konstante mentale Verfügbarkeit** (immer auffindbar,
immer präsent) schlägt kurzfristige Konversionskampagnen — deckt sich mit
Binet & Field.

**Binet & Field — 60/40.** Langfristiger Markenaufbau (~60 % des Aufwands) und
kurzfristige Aktivierung (~40 %) müssen im Gleichgewicht stehen; reine
Aktivierung (Rabatte, Countdown) verpufft langfristig. *Für uns:* die
Kampagnenfenster (§6) sind die 40 %; der Evergreen-Sockel aus Archiv-SEO,
YouTube-Präsenz und Newsletter ist die 60 %. **[plausibel]**

**Abo-Ökonomie — Churn, LTV, Payback.** Plattformweiter Benchmark:
Gesamt-Churn **3,27 %/Monat**, davon **2,41 %** freiwillig und **0,86 %**
unfreiwillig (Zahlungsausfälle) **[belegt]**. Rund ein Viertel der Abwanderung
ist also **technisch** (Karte abgelaufen, Zahlung fehlgeschlagen) und ohne jede
Inhaltsarbeit durch **Dunning/Zahlungs-Retry** rückholbar. Jahresabos bringen
deutlich mehr Umsatz je Nutzer als Monatsabos **[plausibel]** — die Verschiebung
zur Jahreszahlweise ist eine **Rahmung**, keine Produktänderung (§12).

**Newsletter-first & Konversion.** Realistische Free→Paid-Konversion liegt
niedriger als erhofft: Platformer erreichte **~5 %** statt der angenommenen
10 % — bei 24 000 warmen Gratislesern **[anekdotisch, aber lehrreich]**. Der
Newsletter ist damit **die** zentrale Wachstumsmetrik: er ist gleichzeitig
Reichweite (mentale Verfügbarkeit) **und** der wärmste Konversionsboden.

**Empfehlungsschleifen.** Morning Brew führte über **30 %** seines Wachstums (0
→ 1,5 Mio. Abonnenten) auf ein **doppelseitiges Empfehlungsprogramm** zurück
**[plausibel]**. Ein K-Faktor knapp unter 1 verlängert jede andere Massnahme;
über 1 wächst die Liste von selbst.

**Jobs-to-be-Done.** Wer WoS abonniert, «mietet» Zugehörigkeit und Orientierung;
wer GTV abonniert, «mietet» Begegnung und Vertiefung. Kampagnen sprechen den
**Job** an, nicht das Produktmerkmal.

---

## 5. Vergleichsprodukte & Vorbilder

Drei Ringe. Je Zeile: Modell → übertragbare Lehre → was wir **nicht** übernehmen.

### Ring 1 — direkt (Spiritualität/Kontemplation im Streaming)

| Vorbild | Belegte Grössenordnung | Übertragbare Lehre | Nicht übernehmen |
|---|---|---|---|
| **Gaia Inc.** | 903 000 Mitglieder, 99 Mio. USD Umsatz, ARPU ~9–10 USD/Mt, Bruttomarge 87 %, aber Nettoverlust −4,5 Mio. **[belegt]** | Der einzige börsennotierte Nischen-SVOD zeigt die **Grössenordnung** (fast 1 Mio. zahlend) und dass **Win-back per E-Mail** ein Hauptkanal ist | Das defizitäre, akquise-getriebene Wachstum «um jeden Preis» — wir haben kein Investorengeld zu verbrennen |
| **Waking Up** | Stipendienmodell: kostenlos für alle, die nach eigener Angabe nicht zahlen können **[belegt]** | **Solidar-/Stipendienrahmung** als Würde-Signal: «Zugang unabhängig von der finanziellen Lage» | Die Guru-Zentrierung auf eine Einzelstimme |
| **Nebula** | Creator-eigenes Streaming, YouTube→Abo-Trichter **[plausibel]** | Kostenloser Kanal (YouTube) als **Trichter-Mund**, Tiefe hinter dem Abo | — |
| Tricycle, Formed, Hallow | konfessionelle Nischen-Abos | Fest-/Jahreslauf als Kampagnentakt | aggressive App-Store-Mechanik |

### Ring 2 — nah (werbefreier Nischen-Journalismus, DACH)

| Vorbild | Belegte Grössenordnung | Übertragbare Lehre |
|---|---|---|
| **Republik.ch** | ~35 959 Abos (6.7.2026); aus Crowdfunding 2017 mit 13 845 gestartet **[belegt]** | **Der** Beleg, dass ein werbefreies deutschsprachiges Nischenprodukt den mittleren fünfstelligen Bereich erreicht — und **radikale Transparenz** (öffentliches Cockpit) selbst Bindung stiftet |
| Krautreporter, De Correspondent | Mitglieder-Journalismus | Mitgliedschaft > Abo (Zugehörigkeit) |
| Reuters Digital News Report | Zahlungsbereitschaft 13–22 % **[belegt]** | Der realistische Konversionsdeckel |

### Ring 3 — fern (Wachstumsmechanik)

| Vorbild | Lehre |
|---|---|
| **Morning Brew** | Doppelseitiges Empfehlungsprogramm als Wachstumsmotor **[plausibel]** |
| MasterClass | Geschenk-Abo als Saison-Hebel |
| Museums-/Ensemble-Memberships | Stufen-Mitgliedschaft (Förder-/Solidar-Ebene) als Würde-Angebot |

**Die Republik ist unser wichtigstes Vorbild:** dieselbe Sprache, dieselbe
Region, dasselbe «werbefrei, wertegetragen», und ein **öffentliches
Transparenz-Cockpit** — genau das, was der Sommer-Zähler im Ansatz schon ist.

---

## 6. Der Jahreszyklus — das Jahresrad

Kern-Artefakt. Das Jahr hat einen **Evergreen-Sockel** (läuft immer: Archiv-SEO,
YouTube, Newsletter, Empfehlung) und **drei bis vier Kampagnenfenster**, die auf
den anthroposophischen Jahreslauf und die Abo-Saisonalität gelegt sind.

| Monat | Anlass / Jahreslauf | WoS-Themenanlass | Kampagnenfenster | Kanal-Schwerpunkt |
|---:|---|---|---|---|
| Jan | Jahresbeginn, Dreikönig | Jahresausblick | **Neujahrs-Vorsatz** (stärkstes Abo-Fenster) | Newsletter, Win-back |
| Feb | — | — | Evergreen | SEO, YouTube |
| Mär | Frühlings-Tagung | Tagungsheft | leicht | Live-Event → Trial |
| Apr | **Ostern** | Osterheft | **Oster-Impuls** | Social, Newsletter |
| Mai | — | — | Evergreen | Empfehlungsprogramm |
| Jun | **Johanni** | Sommerheft | leicht | YouTube |
| Jul | Sommer | — | **Sommer-Aktion** (bestehend: 3 Mt. gratis) | alle, Landingpages |
| Aug | Sommer | — | Sommer-Aktion (Bindung Tag-90) | E-Mail-Strecke |
| Sep | **Michaeli** (Kernfest) | Michaeli-Heft, Jahresthema | **Michaeli-Kampagne** (Haupt) | alle, Live-Event |
| Okt | Herbst-Tagungen | — | Michaeli-Nachlauf | Newsletter |
| Nov | — | — | Evergreen | SEO |
| Dez | **Weihnacht / Heilige Nächte** | Weihnachtsheft | **Geschenk-Abo** (2. starkes Fenster) | Social, Print-QR |

**Zwei empirische Anker:** Der **Januar** (Neujahrsvorsatz) und das
**Geschenkquartal** (Nov/Dez) sind marktweit die stärksten Abo-Fenster
**[plausibel]** — sie fallen glücklich mit Weihnacht und Jahresbeginn zusammen.
Die **Sommer-Aktion** ist die bereits gebaute Speiche; **Michaeli** als das
zentrale anthroposophische Fest ist der natürliche Ort der Hauptkampagne.

Jedes Fenster ist eine **Massnahme** im Protokoll (Hypothese, Kosten, erwartete
Wirkung → Ist, Entscheid). Das Rad dreht sich, das Cockpit misst jede Umdrehung.

---

## 7. Die Maschine — Automatisierungs-Architektur

Auf dem bestehenden Fundament (`services/sommer-zaehler/`, `apps/utm-generator/`).
Fünf Bauteile.

**(a) Das Lead-Objekt.** Eine Person, die Interesse zeigt (Newsletter-Anmeldung,
Trial-Start, QR-Scan, Formular), wird als Lead erfasst: **gehashte** E-Mail (Salt
in der Config, nie Klartext — wie im Sommer-Zähler), Einwilligung (Double-Opt-in),
Herkunfts-**Motiv** (volles UTM-Tupel), Interessens-Signal (WoS/GTV, DE/EN).
Capture-Punkte: Newsletter-Formular, Trial-Checkout, Landingpages, Print-QR,
Live-Event-Anmeldung.

**(b) Nurture-Strecken** (getaktete E-Mail-Folgen, im vorhandenen Stack, §10):
- **Willkommen** (neuer Newsletter-Leser): Bestes aus dem Archiv, sanfte
  Hinführung zum ersten Trial.
- **Trial-Begleitung Tag 1–7** (GTV): drei Impulse, die zum Schauen führen —
  denn wer im Trial nichts schaut, verlängert nicht.
- **Vor-Ablauf-Impuls** (Tag 5–6 des Trials, bzw. vor dem Drei-Monats-Moment der
  Sommer-Aktion): ehrliche Erinnerung + der stärkste noch nicht gesehene Inhalt.
- **Win-back** (abgelaufener Trial, ehemaliger WoS-Abonnent): Gaia belegt, dass
  **E-Mail-Win-back einer der Hauptkanäle** ist **[belegt]** — kostet nichts als
  eine gute Strecke.

**(c) Trigger** (Ereignis → Automation): Trial gestartet, Trial läuft ab,
Kündigung, Zahlungsausfall (→ Dunning, holt bis zu ~0,86 %-Punkte Churn zurück
**[belegt]**), Jahrestag, neues Themenheft/neue Live-Aufnahme.

**(d) Cross-Selling TV↔Wochenschrift & Content-Recycling.** Ein Vorgang, vier
Erscheinungsformen: **Artikel (WoS) → Clip/Aufnahme (GTV) → Newsletter-Anriss →
Landingpage.** Jeder Kanal trägt jeden. Ein WoS-Leser bekommt gelegentlich den
passenden GTV-Beitrag, ein GTV-Zuschauer den vertiefenden WoS-Artikel — **mit
Frequenz-Deckel** (§11).

**(e) Verstetigung `sommer2026_*` → `marketing_*`** *(Folge-Bauvorhaben, hier nur
als Prinzip).* Das Aktions-Schema (signups, Massnahmen-Protokoll, Trichter-RPCs)
wird vom einmaligen `sommer2026_*` zu einem dauerhaften `marketing_*`-Muster
verallgemeinert, das **jedes** Kampagnenfenster des Jahresrads aufnimmt. Kein
Code in diesem Wurf — aber die Datenmodell-Kontinuität ist der Grund, warum die
Maschine nicht neu gebaut, sondern nur geöffnet werden muss.

---

## 8. Die Null-Budget-Phase — Organik zuerst

Alles hier kostet **Zeit, kein Geld**. Reihenfolge nach Hebel.

1. **Archiv-SEO.** 500 Aufnahmen + 100 Jahrgänge Wochenschrift sind der grösste
   ungehobene Schatz — Rohstoff für **mentale Verfügbarkeit**: jeder gut
   aufbereitete Beitrag (Titel, Beschreibung, Transkript-Auszug) ist eine
   dauerhafte Eintrittstür aus der Suche. Kostenlos, kumulativ, im Sinne der
   60 % (§4).
2. **Newsletter als Leitmetrik.** Der Newsletter ist Reichweite **und** wärmster
   Konversionsboden. Netto-Wachstum der Liste ist die **North-Star-Hilfsgrösse**.
3. **YouTube-Trichter** (Nebula-Muster **[plausibel]**): freie Beiträge/Live als
   Trichter-Mund, Tiefe hinter dem Abo. Live-Streams am Goetheanum sind
   kostenloser, wiederkehrender Anlass.
4. **Doppelseitiges Empfehlungsprogramm** (Morning-Brew-Muster **[plausibel]**):
   würdig formuliert — «teilen, weil es trägt», keine Gamification-Hektik. Der
   billigste Wachstumskanal, den es gibt.
5. **Partnernetzwerk.** Waldorfschulen (Elternschaft weltweit), Demeter, Weleda,
   anthroposophische Ärzte, Christengemeinschaft, Zweige — als
   **Verteil-Multiplikatoren** (Empfehlung an ihre Kreise), nicht als Werbekauf.
6. **Angebots-Rahmungen ohne Produktänderung:** Geschenk-, Gemeinschafts- und
   Klassensatz-Abos sind **Kommunikation und Bündelung** bestehender Tarife
   (§12), kein neues Produkt.

---

## 9. Die 10-Prozent-Regel — Experiment-Governance

Ab dem ersten Gewinn dürfen 10 % in Services/Ads/Werkzeuge fliessen — **aber nur
belegt auf Wirkung, nichts läuft unbeaufsichtigt.** Der Mechanismus existiert
bereits: das **Massnahmen-Protokoll** (`sommer2026_massnahmen`). Die Regel macht
es zur Pflicht.

**Jede Ausgabe ist eine Massnahme mit zwei Zeitpunkten:**
- **Vor Freigabe:** Hypothese, geplante Kosten, erwartete Wirkung (Reichweite →
  Klicks → Trials → Abos).
- **Nach Ablauf:** Ist-Reichweite, Ist-Klicks, Ist-Abos, **CPA je Massnahme**,
  Entscheid: **skalieren · anpassen · beenden**.

**Kill-Kriterien:** CPA über dem Deckungsbeitrag des gewonnenen Abos (Payback >
12 Monate) → beenden. Keine messbare Wirkung nach definiertem Fenster → beenden.
**Review-Rhythmus:** je Kampagnenfenster ein Rückblick; kein Dauerläufer ohne
Quartals-Prüfung. So bleibt das Reinvest ein Regelkreis, kein Fass ohne Boden.

---

## 10. KPI-System & Wachstumsmodell

**North-Star je Produkt:** zahlende Abos (WoS / GTV, netto nach Churn).
**Hilfsgrössen:** Newsletter-Netto-Wachstum · Trial-Starts · Trial→Paid ·
Churn (freiwillig/unfreiwillig getrennt) · CPA je Massnahme · LTV.

**Realistische Anker aus der Empirie:** Churn ~3,3 %/Monat als Ausgangserwartung
(davon ~¼ technisch rückholbar) **[belegt]**; Free→Paid **~5 %** als nüchterne
Annahme **[anekdotisch]**; Zahlungsbereitschafts-Deckel 13–22 % **[belegt]**;
Republik ~36 000 als Beleg des Erreichbaren im DACH-Raum **[belegt]**.

**Drei Szenarien** (nachrechenbar; Formel: Bestand × (1 − Churn) + Zugänge, Monat
für Monat; alle Annahmen offengelegt und **zu kalibrieren**, sobald echte
Zahlen aus dem Cockpit vorliegen):

| Szenario | Treiber | Grössenordnung (mehrjährig) | Bricht, wenn … |
|---|---|---|---|
| **Konservativ** | nur Kern + DACH, organisch | mittlerer vierstelliger Zuwachs/Jahr | Newsletter stagniert |
| **Plan** | + Partnernetz + Geschenk/Win-back + Reinvest | mittlerer fünfstelliger Bereich (Republik-Analogie) | Partner tragen nicht |
| **Kühn** | + englische Schiene + YouTube/SEO-Skalierung | oberer fünfstelliger Bereich | EN-Markt bleibt aus |

**Die tragende Annahme jedes Szenarios ist explizit** (letzte Spalte). Der obere
fünfstellige Bereich hängt an der **englischen Schiene** und an
**Plattform-Sichtbarkeit** — das ist die eine Wette, die das Zielbild trägt oder
kippt. Ehrlich benannt, nicht versteckt.

---

## 11. Spannungen & Grundsätze

Kein Anhang — ein eigenes Kapitel, weil hier die Haltung des Hauses auf die
Marktlogik trifft.

**(a) Wachstum ohne Produktänderung.** 10–20× kommt aus **Publikums-Erweiterung**
(Positionierung für Ring 2/3), nicht aus Produktumbau. Grenze der Aussage: ohne
englische Schiene ist der obere fünfstellige Bereich nicht erreichbar (§10) —
das ist Reichweitenarbeit, keine Produktarbeit, aber sie braucht Jahre.

**(b) Datensparsamkeit vs. Automation.** Das Haus führt Datensparsamkeit als
Wert (`docs/strategie.md`). Die Maschine folgt dem Sommer-Zähler-Muster:
**gehashte E-Mails, nur Summen verlassen die DB, Einwilligung per Double-Opt-in.**
Das ist kein Hindernis, sondern **Differenzierungsmerkmal** — «würdige Werbung»
als Teil der Marke, gegen die Überwachungs-Werbung des Marktes.

**(c) Würde vs. Growth-Hacking.** Ausdrückliche **Verbotsliste**: keine falsche
Verknappung («nur noch 2 Plätze»), keine Schuld-/Angst-Rhetorik, keine
Kündigungs-Labyrinthe, keine Dark Patterns. **Erlaubt:** echte Fristen (die
Sommer-Aktion *ist* befristet), ehrliche Empfehlung, transparente Zahlen
(Republik-Cockpit als Vorbild). Die Frist ist wahr — deshalb tragbar.

**(d) Null-Budget = Zeit-Budget.** «Kostenlos» heisst nicht «umsonst». Jede
organische Massnahme braucht Pflege-Stunden; ohne bezifferten Betriebsaufwand
kollabiert «nichts läuft unbeaufsichtigt». Der Aufwand gehört ins
Massnahmen-Protokoll wie das Geld.

**(e) Listen-Ermüdung.** Zwei Produkte auf **ein** Publikum ⇒ **Frequenz-Deckel**
als Regel (max. Kontakte je Person je Woche über alle Strecken), sonst frisst
Cross-Selling die Bindung.

---

## 12. Fahrplan in Phasen

Jede Phase mit Eintritts-/Austrittskriterium in Zahlen.

**Phase 0 — Messfundament (läuft).** Sommer-Aktion 2026 als erste Speiche;
Cockpit misst Kette + Attribution + CPA. *Austritt:* echte Zahlen aus mindestens
einem vollen Kampagnenfenster im Cockpit.

**Phase 1 — Maschine verstetigen (organisch, Null-Budget).**
`sommer2026_*` → `marketing_*` verallgemeinern; Nurture-Strecken (Willkommen,
Trial, Win-back) im vorhandenen Stack aufsetzen; Jahresrad in Betrieb; Archiv-SEO
und Empfehlungsprogramm starten. *Austritt:* Newsletter wächst netto; erste
Massnahmen mit positivem CPA belegt.

**Phase 2 — 10 %-Reinvest mit Governance.** Erst wenn Massnahmen belegt tragen:
gezielt 10 % des Gewinns in die wirksamsten Kanäle, jede Ausgabe im Protokoll.
*Austritt:* wiederholt positiver Payback < 12 Monate.

**Phase 3 — Skalierung EN/Partner.** Englische Schiene und Partnernetz
hochfahren — der Weg in den oberen fünfstelligen Bereich. *Austritt:* Zielmarke.

**Umsetzungs-Backlog (priorisiert, als Folgearbeit):**
1. `marketing_*`-Schema aus `sommer2026_*` ableiten (Datenkontinuität).
2. Nurture-Strecken in Uscreen/Zoho konfigurieren (§10-Machbarkeit zuerst klären).
3. Jahresrad als HTML-Werkzeug aus `design-system/starter.html` (heute nur als
   Tabelle in diesem Dokument und im Einseiter `marketing-maschine.html`).
4. Empfehlungsprogramm-Mechanik (doppelseitig, würdig).
5. Cockpit um Jahres-Ansicht erweitern (mehrere Fenster nebeneinander).

---

## 13. Offene Entscheidungen

- **E-Mail-Werkzeug (ESP):** Welche Automation trägt die Strecken — Zoho
  Campaigns (GDPR/Double-Opt-in vorhanden **[plausibel]**), Uscreens eingebaute
  Automationen, oder ein separater ESP? **Vor Phase 1 zu klären** (§10-Recherche).
- **Uscreen/Zoho-Machbarkeit:** Welche Trigger/Coupons/Pausen-Angebote der
  vorhandene Stack **ohne** Zusatzkosten hergibt — das Konzept darf keine
  Strecke versprechen, die der Stack nicht kann.
- **Englische Priorität:** Wie früh und wie stark die EN-Schiene? (Trägt das kühne
  Szenario.)
- **Verhältnis zu bestehenden Redaktions-Newslettern:** ein Absender-Haus oder
  getrennte Stimmen?
- **Zuständigkeit & Betriebsstunden:** wer pflegt die Maschine (Zeit-Budget, §11d)?
- **Zahlweise-Verschiebung:** Umstellung auf Jahreszahlweise aktiv bewerben
  (Rahmung, §4/§12) — ab wann?

---

## 14. Quellen

Belegte externe Zahlen mit Abrufdatum **6. Juli 2026**. Interne Zahlen (4650 /
15 000 / ~500) sind aus Mediadaten/Aufgabenstellung übernommen und **zu
bestätigen**.

- Gaia Inc., Q4/FY-2025-Ergebnis (903 000 Mitglieder, 99 Mio. USD, ARPU, Win-back):
  ir.gaia.com/…/gaia-reports-fourth-quarter-and-full-year-2025-results; SEC 10-K
  gaia-20251231 (sec.gov). **[belegt]**
- Waking Up, Stipendienprogramm: wakingup.com/scholarship. **[belegt]**
- Republik, Live-Cockpit (35 959 Abos, 6.7.2026): republik.ch/cockpit;
  Crowdfunding-Historie: de.wikipedia.org/wiki/Republik_(Magazin). **[belegt]**
- Reuters Institute Digital News Report 2025 (Zahlungsbereitschaft 18 %/13 %/22 %/
  42 %): reutersinstitute.politics.ox.ac.uk/digital-news-report/2025;
  fög/UZH Länderbericht Schweiz (foeg.uzh.ch). **[belegt]**
- Recurly, Churn-Benchmarks (3,27 % gesamt; 2,41 %/0,86 %):
  recurly.com/research/churn-rate-benchmarks/. **[belegt]**
- Recurly, Subscriber-Acquisition (Jahresabo-Umsatz, Win-back-Anteil,
  Pausen-Angebot): recurly.com/research/subscriber-acquisition-benchmarks/. **[plausibel, nicht gegengeprüft]**
- Uscreen-Hilfe (Abandoned-Cart-Automation, Coupon-Typen/-Dauern):
  help.uscreen.tv/…/4316101, /…/4316098. **[plausibel, nicht gegengeprüft]**
- Zoho Campaigns (GDPR/Double-Opt-in): zoho.com/campaigns/gdpr/features.html;
  help.zoho.com/…/manage-double-opt-in. **[plausibel]**
- Platformer/Casey Newton (Free→Paid ~5 %): simonowens.substack.com/…. **[anekdotisch]**
- Morning Brew (Empfehlungsprogramm >30 %): referralcandy.com/blog/morning-brew-referral-program;
  medium.com/the-mission/…. **[plausibel]**
- Byron Sharp / Ehrenberg-Bass (Penetration vor Loyalität):
  marketingscience.info/answering-critics/. **[plausibel]**
- Neumeier — *Zag*, *The Brand Gap*, *The Brand Flip* (Onliness/Zag/Tribes):
  Sekundäranwendung wie in `docs/strategie.md`. **[etabliert]**

*Hinweis: Die als **[plausibel]** / **[anekdotisch]** markierten Aussagen wurden
recherchiert, aber wegen eines abgebrochenen Prüflaufs nicht adversarisch
gegengeprüft. Vor operativem Einsatz (v. a. Stack-Machbarkeit §10/§13) direkt an
der Primärquelle verifizieren.*

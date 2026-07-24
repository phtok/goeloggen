# Wirkungs-Lesart der Sommer-Aktion — Stand 24. Juli 2026

Dieses Dokument ordnet die Anmeldungen **ohne UTM-Spur** («ohne UTM» im
Cockpit) den Aktivitäten der Kampagne zu. Es ist eine **Lesart, keine
Messung**: Alle mit ≈ markierten Zahlen sind Schätzungen. Die Datenbank
bleibt unangetastet — dort stehen nur harte Zuordnungen. Die Anteile daraus
stehen im Cockpit (`CONFIG.dunkel.anteile`) und werden dort auf den jeweils
aktuellen Stand angewandt.

Diese Fassung löst `wirkungs-lesart-22-07.md` ab (die bleibt als Historie
liegen). Sie korrigiert deren Hauptaussage.

Grundlage am Stichtag: **242 Anmeldungen**, davon **112 mit UTM** und
**130 ohne**.

## Was sich gegenüber dem 22. Juli ändert

Die Lesart vom 22. Juli schrieb der bezahlten Meta-Anzeige **≈44
Anmeldungen** zu und nannte als Ursache, der Uscreen-Checkout trage die
UTM-Spur nicht bis zur Anmeldung. Beides hält der Prüfung nicht stand.

**Die Kette ist intakt.** Nachgemessen am 24. Juli, an den ausgelieferten
Landing-Bundles und am Roh-Log:

- Die Übersichts-Landing hängt die eingehenden `utm_*` beim Klick an die
  Ziel-URL (delegierter Handler auf `pointerdown`/`click`/`keydown`).
- Die TV-Landing sichert sie in `sessionStorage` (`lovable_utm:`) und hängt
  sie an die Checkout-URL `goetheanum.tv/checkout/new?o=84317`.
- Uscreen liefert sie im `user_created`-Event: **144 von 144** dieser Events
  tragen den `utm_params`-Block, 117 davon mit gefülltem `utm_source`.
- Auf unserer Seite ist nichts liegengeblieben: **kein einziger** dunkler
  goetheanum.tv-Abschluss hat ein `user_created` mit Spur, das die Ingestion
  nicht verheftet hätte.

**Die Anzeige konvertiert kaum.** Gegenprobe an den organischen Wegen, die
denselben Weg nehmen — Kurzlink → Übersichts-Landing → TV-Landing → Uscreen,
dieselben In-App-Browser aus Instagram und Facebook:

| Quelle | Kurzlink-Klicks | goetheanum.tv-Konten mit Spur | Quote |
|---|---:|---:|---:|
| meta-anzeige (bezahlt) | 714 | 3 | 0,4 % |
| instagram organisch | 131 | 7 | 5,3 % |
| facebook organisch | 64 | 2 | 3,1 % |
| nl-tv | 52 | 4 | 7,7 % |

Wäre die Spur technisch gebrochen, müsste sie bei den organischen Stories
genauso brechen: dieselbe Landing (`spinne`, `kroete` führen auf dieselbe
Übersichts-Seite wie `dachs-4`/`elster-2`), dieselben In-App-Browser. Sie
bricht dort nicht.

## Die Placebo-Probe — warum ≈44 ein Artefakt war

Der stärkste Anker der alten Lesart war die **vermutete Herkunft**: je
dunkler Anmeldung der zeitlich nächste Kurzlink-Klick (bis 90 Min. davor).
Dieser Anker taugt nur, solange die Klicks **spärlich** sind. Die Anzeige
stellt mit 714 Klicks fast das gesamte Klick-Log — sie gewinnt damit fast
jede Nähe-Lotterie.

Prüfbar gemacht: dieselbe Zuordnung, aber die Anmeldezeiten künstlich um
±24/48 Stunden verschoben. Eine Anmeldung, die zu diesem Zeitpunkt gar nicht
stattfand, dürfte keinen Treffer bekommen.

| Quelle (9-Tage-Fenster, 81 dunkle) | echt | Placebo (Mittel) | Überschuss |
|---|---:|---:|---:|
| goetheanum.tv-Newsletter (nl-tv, tv-weekly*) | 47 | 22 | **≈25** |
| Meta-Anzeige | 72 | 57 | ≈15 |
| Social organisch | 26 | 31 | keiner |

Im sauberen Fenster 19.–23. Juli, in dem die Anzeige durchgehend lief und
die Mailing-Welle abgeklungen war, bleibt vom Anzeigen-Überschuss fast
nichts: 32 dunkle Anmeldungen, **32** mit Anzeigen-Klick in den 90 Minuten
davor — und **28** auch dann, wenn man die Anmeldung um einen Tag
verschiebt. Überschuss ≈4 auf 325 Klicks.

Bei den Newslettern trägt derselbe Anker echte Information (Überschuss das
Zwei- bis Dreifache des Placebos). Er bleibt dort gültig — nur für die
Anzeige nicht.

## Zwei weitere Anker, unabhängig davon

**Tageskurve.** Seit die Mailing-Welle abgeklungen ist (20.–23. Juli):
269 Anzeigen-Klicks, und **insgesamt** 26 goetheanum.tv-Anmeldungen, davon
14 dunkel — die sich alle Kanäle teilen. Die Grundlinie ohne Anzeige und
ohne Mailing (10.–14. Juli) lag bei rund zwei goetheanum.tv-Anmeldungen pro
Tag.

**Selbstauskunft.** «Wie sind Sie auf uns aufmerksam geworden?» ist bei
goetheanum.tv 37-mal beantwortet. Darin einmal «Instagram», einmal
«Werbung», einmal «jetzt durch Ihre Anzeige» — der Rest Mail, Newsletter,
Bestand, Empfehlung.

Alle drei Anker zeigen in dieselbe Richtung: die Anzeige trägt **einstellig
bis niedrig zweistellig**, nicht ≈44. Angesetzt wird **≈9** für die ganze
Laufzeit (Band ≈4–18).

## Kampagnenweite Rangfolge (gemessen + geschätzt)

| Rang | Aktivität | gemessen | ≈ dazu (dunkel) | ≈ gesamt |
|---|---|---:|---:|---:|
| 1 | Mailing (Welle 1) | 87 | ≈27 | **≈114** |
| 2 | Direkt · Organik · Bestand | 5 | ≈39 | **≈44** |
| 3 | goetheanum.tv-Newsletter (TV-Weekly) | 6 | ≈33 | **≈39** |
| 4 | Social organisch (Reels · Stories · Karussell) | 9 | ≈9 | **≈18** |
| 5 | Haus- und AC-Newsletter (Frühphase) | 4 | ≈12 | **≈16** |
| 6 | Meta-Anzeige (bezahlt) | 1 | ≈9 | **≈10** |
| 7 | Inserat · Print | 0 | ≈1 | **≈1** |
| | **Summe** | **112** | **130** | **242** |

Die Spalte «gemessen» sind harte UTM-Zuordnungen. «≈ dazu» verteilt das
Dunkelfeld nach den Ankern oben: Newsletter und Mailing nach dem
Placebo-Überschuss, die Anzeige nach der Obergrenze aus dem sauberen
Fenster, der Rest — die Frühphase 3.–16. Juli mit 52 dunklen ohne Anzeige
und ohne Mailing — nach Direkt, Bestand und Organik.

Drei Sätze dazu: **Das Mailing trägt die Aktion** — eine Welle, knapp die
Hälfte aller Abos. **Der grösste stille Posten ist Direkt/Bestand**, nicht
die Anzeige: Menschen, die ohnehin kommen. **Die bezahlte Anzeige ist der
teuerste Posten mit dem kleinsten Ertrag** — das ist der Befund, den die
alte Lesart hinter einem Attributions-Problem verborgen hat.

## Was daraus folgt

1. **Abschalt-Probe statt Attributions-Umbau (sofort, kostenlos).** Die
   Anzeige 3–4 Tage aussetzen und die goetheanum.tv-Anmeldungen vergleichen.
   Die Grundlinie ist gerade sauber wie nie: das Mailing ist abgeklungen,
   die nächste Welle steht erst am 30. Juli. Das beantwortet «5 oder 60»
   endgültig — und zwar in Abos, nicht in Zuordnungswahrscheinlichkeiten.
2. **Hart messbar machen, falls die Anzeige weiterläuft:** ein **eigenes
   Uscreen-Angebot** je bezahltem Weg. Der Checkout läuft über
   `?o=<offer_id>`, und `offer_id` wie `coupon` kommen im `order_paid`-Webhook
   **serverseitig** an — an Cookies, In-App-Browsern und Weiterleitungen
   vorbei. Auftrag: `services/sommer-zaehler/uscreen-angebot-attribution-auftrag.md`.
3. **Die vermutete Herkunft im Cockpit bleibt** — sie ist für die spärlichen
   Kanäle belegt. Sie darf nur nicht mehr als Hauptanker für einen Kanal
   gelesen werden, der das Klick-Log dominiert. Faustregel: wo ein Kanal mehr
   als die Hälfte aller Klicks stellt, ist seine Nähe-Zuordnung wertlos.

## Prüfwege (wiederholbar)

Alle Zahlen dieser Fassung stammen aus dem Live-Bestand. Die Placebo-Probe
ist eine Abfrage: dunkle Anmeldungen des Fensters, je Quelle die Zahl mit
Klick in den 90 Minuten davor — einmal echt, einmal mit um ±24/48 Stunden
verschobenen Anmeldezeiten. Übersteigt «echt» das Placebo nicht deutlich,
trägt der Anker für diese Quelle keine Information.

## Pflege

Die Lesart ist datiert und wird **nicht** automatisch nachgeführt. Bei einer
neuen Auswertung: Kopie mit neuem Datum anlegen, `CONFIG.dunkel` in
`apps/sommer-zaehler/campaign.js` nachziehen (Stand-Datum, Doc-Pfad,
Anteile), Cockpit zeigt sie dann automatisch auf dem jeweils aktuellen
Stand.

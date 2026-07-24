# UTM-Ablauf · Sommer-Aktion 2026 (`summer26_trial`)

Damit das Cockpit sagen kann **welche Massnahme welche nächste Handlung
wahrscheinlicher gemacht hat**, braucht jeder Link nach draussen eine eindeutige
Spur. Diese Datei ist die verbindliche Namenskonvention – wer setzt wo welchen
Link. Ohne sie entsteht ein Datenhaufen statt einer lesbaren Geschichte.

> **Am einfachsten mit dem Generator:** `apps/utm-generator/` baut die Links nach
> genau dieser Konvention (klein, ohne Umlaute/Leerzeichen), inkl. QR-Code, und
> legt sie ins Register `sommer2026_links` – so zeigt das Cockpit auch Links mit
> **null Abschlüssen** (Soll/Ist). Das Register speist die Attribution nicht
> direkt: eine Spur wird erst gelesen, wenn sie bei einer echten Anmeldung im
> Webhook mitreist (Landingpage → Formular). Dafür braucht Paperform je Formular
> versteckte Felder `utm_source/medium/campaign/content`, die sich aus der URL
> vorbefüllen – sonst kommen die UTMs nicht im Webhook an.

## Die vier Parameter (immer klein, ohne Leer-/Sonderzeichen, `_` als Trenner)

| Parameter | Frage | Werte (Beispiele) |
|---|---|---|
| `utm_campaign` | Welche Aktion? | **immer `summer26_trial`** |
| `utm_source` | Welche Plattform / Liste? | `instagram` · `facebook` · `linkedin` · `youtube` · `nl-ws` · `nl-tv` · `mailing` · `inserat` · `google` · `partner-<name>` |
| `utm_medium` | Welche Art Kontakt? | `social` · `email` · `print` · `cpc` · `popup` · `organic` · `referral` |
| `utm_content` | Welches konkrete Motiv / welche Platzierung? | `reel_ernst_zuercher` · `story_probeabo` · `teaser_kopf` · `footer_link` · `qr_inserat` · `popup_exit` · `vorab_nl1` |

**Englische Links bekommen ein eigenes `utm_content`** (Suffix `-en`, wie
`karussell-en`). Grund: Sprache ist keine eigene UTM-Dimension. Trägt die
englische Variante dasselbe Tupel wie die deutsche und unterscheidet sich nur
in der Landingpage, ist die Sprache im Register mehrdeutig — und bei
goetheanum.tv, wo sie sonst nirgends herkommt, dann gar nicht mehr feststellbar
(Befund 24.7.: 47 der 64 Tupel mehrdeutig, darum nur 2 als englisch verbuchte
TV-Abos bei 61 Anmeldungen aus dem übrigen Ausland).

Regeln: nur Kleinbuchstaben, keine Umlaute (`ue/oe/ae`), keine Leerzeichen. Der
`kanal`-Bucket im Cockpit wird aus `utm_source`/`utm_medium` abgeleitet – die
Rohwerte bleiben erhalten, damit «Nach Motiv» das einzelne Reel vom Footer-Link
unterscheidet.

## Die sechs Landingpages (Angebot × Sprache)

Drei Angebote, je Deutsch und English (EN = eigene Subdomain `…-en-…`, bei der
Übersicht der Pfad `/en`):

| Angebot | Deutsch | English |
|---|---|---|
| Übersicht · 3 Monate gratis | `https://global-sommer2026.goetheanum.online` | `https://global-sommer2026.goetheanum.online/en` |
| Wochenschrift | `https://ws-sommer2026.dasgoetheanum.com` | `https://ws-en-sommer2026.dasgoetheanum.com` |
| goetheanum.tv | `https://tv-sommer2026.goetheanum.tv` | `https://tv-en-sommer2026.goetheanum.tv` |

Ein Link führt **nie** auf die nackte Startseite, sondern immer auf eine dieser
sechs Seiten – mit angehängtem UTM-Block. Der Generator wählt sie über
Angebot + Sprache und führt die Sprache als Dimension ins Register.

## Wer erhält wo wie welchen Link

| Wer / wo | Landingpage | `utm_source` | `utm_medium` | `utm_content` (je Motiv variieren) |
|---|---|---|---|---|
| Newsletter Wochenschrift, Haupt-Teaser | ws-sommer2026 | `nl-ws` | `email` | `teaser_kopf` |
| Newsletter Wochenschrift, Footer | ws-sommer2026 | `nl-ws` | `email` | `footer_link` |
| Newsletter goetheanum.tv | tv-sommer2026 | `nl-tv` | `email` | `teaser_kopf` |
| Mailing (Entscheidungs-Mail) | ws- oder tv- | `mailing` | `email` | `<welle>_<segment>` |
| Instagram Reel | global- oder produktnah | `instagram` | `social` | `reel_<thema>` |
| Instagram Story | global- | `instagram` | `social` | `story_probeabo` |
| LinkedIn organisch | global- | `linkedin` | `social` | `post_<thema>` |
| Google Ads | produktnah | `google` | `cpc` | `<anzeigengruppe>` |
| Print-Inserat (QR-Code) | produktnah | `inserat` | `print` | `qr_<titel>_<region>` |
| Popup / Overlay auf der Website | produktnah | `popup` | `popup` | `popup_<ort>` |
| Partner-Newsletter | global- | `partner-<name>` | `referral` | `teaser` |

Beispiel-Link (Instagram Reel → Übersicht):

```
https://global-sommer2026.goetheanum.online?utm_source=instagram&utm_medium=social&utm_campaign=summer26_trial&utm_content=reel_ernst_zuercher
```

Für Print gilt: QR-Code auf **genau diesen** Link, plus optional ein kurzer
Merk-Pfad (`goetheanum.ch/sommer`) für alle, die nicht scannen. Ein eigener
Vorteilscode je Inserat macht auch die Nicht-Scanner sichtbar.

## Sonderfall: die zwei Vorab-Newsletter (zeitlich abgrenzen)

Vor dem Aktionsstart (3. Juli, 15 Uhr) gab es in **zwei Newslettern** eine
Vorveröffentlichung der Landingpages. Ihr Effekt wird zweifach isoliert:

1. **Direkt-Effekt** ist automatisch abgegrenzt: Anmeldungen **vor**
   `aktion_start` zählen nicht (die Ingestion überspringt sie). Was vor dem 3.7.
   15 Uhr kam, ist Vor-Aktion und bleibt draussen.
2. **Nachlauf-Effekt** (wer den Vorab-Link sah und **nach** Start abschloss) wird
   über `utm_content=vorab_nl1` bzw. `vorab_nl2` sichtbar – diese beiden Werte im
   Cockpit unter «Nach Motiv» getrennt lesbar. Zusätzlich beide Aussendungen als
   Zeile im **Massnahmen-Protokoll** (`rolle=sichtbarkeit`, mit Sende-Datum und
   Reichweite), damit die Vorab-Reichweite dokumentiert und datiert ist.

So lässt sich sagen: «Die Vorab-Teaser haben X Anmeldungen im Aktionszeitraum
nachgezogen», ohne sie mit dem eigentlichen Aktions-Newsletter zu vermischen.

## So liest das Cockpit die Spur (Ordnung seit dem 24. Juli)

Alles läuft in der **Gebiete-Liste** zusammen: je Gebiet (Mailing, bezahlte
Anzeige, Newsletter, Social …) eine Zeile mit der ganzen Kette.

- **Abschlüsse je Gebiet** aus `sommer2026_attribution`; die Zuordnung
  `utm_source`/`utm_medium` → Gebiet steht als Liste `GEBIETE` in
  `apps/sommer-zaehler/campaign.js` (erster Treffer gewinnt, Reihenfolge ist
  dort begründet).
- **Klicks** aus dem Link-Register (`sommer2026_links_public`, je Kurzcode
  gezählt) plus die von Hand erfassten Aktivitäts-Klicks.
- **Reichweite** aus dem Aktivitäten-Protokoll (`sommer2026_massnahmen_public`).
- **Einzelne Motive** (`utm_content`) erscheinen beim Aufklappen der Zeile und
  vollständig unter Belege → «Alle Motive einzeln».
- **Nächste Züge** liest die Lücke: jeder registrierte Link ist eine Absicht –
  Motive ohne einen einzigen Klick gelten als vorbereitet, aber nicht gezündet.

Darum lohnt sich die saubere Konvention doppelt: sie bestimmt, in welcher
Zeile eine Massnahme erscheint, und ob das Cockpit sie als offenen Zug erkennt.

## Paperform: damit die UTMs im Webhook ankommen

Die Kette ist **UTM-Link → Landingpage → Paperform-Formular → Webhook**; die UTMs
müssen sie ganz überleben. Zwei Stellen:

**1. Landingpage → Formular (Web-Seite):** Die Landingpage (`*-sommer2026…`) muss
die eingehenden `?utm_*` an das Formular weiterreichen – am «3 Monate gratis»-
Button (UTMs an die Formular-URL hängen) oder, bei eingebettetem Formular, die
Query-Parameter an den Embed durchreichen. Ohne diesen Schritt sieht Paperform
keine UTMs, egal wie sauber der Link war.

**2. In Paperform, je Formular (der eigentliche To-do):** vier **versteckte
Prefill-Felder** anlegen, deren **Key** exakt so heisst:

| Feld-Key | füllt |
|---|---|
| `utm_source` | Quelle (instagram, nl-ws …) |
| `utm_medium` | Art (social, email, print …) |
| `utm_campaign` | `summer26_trial` |
| `utm_content` | Motiv (reel_…, qr_inserat …) |

Feld hinzufügen → als *Hidden* setzen → unter *Advanced/Prefilling* den **Key** auf
`utm_source` usw. Paperform befüllt sie aus der Formular-URL. Die Function liest
diese Felder direkt (`data[]`) **und** zusätzlich Paperforms eigenes
`device.utm_*` – kommt die Spur über einen der Wege an, greift die Attribution.

Test: einen generierten Link mit `utm_*` öffnen, Formular abschicken → in
`sommer2026_signups` steht die Zeile mit gefüllten `utm_*`, im Cockpit unter
«Nach Motiv».

## Sonderfall goetheanum.tv / Uscreen: wie weit die Spur trägt

> **Stand 24. Juli 2026 — die Kette ist geprüft und intakt.** Der frühere
> Befund («der Uscreen-Checkout trägt die UTM nicht bis zur Anmeldung») ist
> widerlegt. Herleitung: `docs/wirkungs-lesart-24-07.md`.

Nachgemessen an den ausgelieferten Landing-Bundles und am Roh-Log:

- Die Übersichts-Landing hängt die eingehenden `utm_*` beim Klick an die
  Ziel-URL (delegierter Handler auf `pointerdown`/`click`/`keydown`).
- Die TV-Landing sichert sie in `sessionStorage` (`lovable_utm:`) und hängt
  sie an die Checkout-URL `goetheanum.tv/checkout/new?o=<offer_id>`.
- Uscreen liefert sie im `user_created`-Event (`utm_params`), die Ingestion
  heftet sie an die Anmeldung derselben Person.

Anders als bei Paperform gibt es weiterhin **kein** verstecktes UTM-Feld: die
Spur überlebt so weit, wie Uscreen sie in seiner eigenen Session mitführt.
Das bleibt eine echte Grenze — sie fällt nur weniger ins Gewicht als gedacht.
Belegt an den Klick-Quoten: organische Social-Wege über **dieselbe** Landing
und in denselben In-App-Browsern werden mit 3–5 % ihrer Klicks als Konto mit
Spur sichtbar, die bezahlte Meta-Anzeige mit 0,4 % (714 Klicks, 3 Konten).
Die Spur bricht dort also nicht — die Klicks werden kaum zu Anmeldungen.

**Wenn ein Weg trotzdem hart messbar sein muss** (bezahlte Anzeige, Partner,
Inserat), führt er nicht über den Browser, sondern über das Produkt: ein
**eigenes Uscreen-Angebot** je Weg. `offer_id` und `coupon` stehen im
`order_paid`-Webhook und kommen serverseitig an — an Cookies, In-App-Browsern
und Weiterleitungen vorbei. Auftrag und Mapping:
`services/sommer-zaehler/uscreen-angebot-attribution-auftrag.md`.

**Kurzlinks bleiben Pflicht** für alle geteilten Wege (`/s/<code>`, Function
`go`, 302 auf die volle UTM-URL): sie zählen den Klick in `link_hits` — die
einzige Reichweiten-Grundlage, die wir selbst besitzen. Ihre Grenze steht
ebenfalls im Lesart-Dokument: als Herkunfts-Indiz taugen sie nur, solange ein
Weg nicht fast alle Klicks stellt.

Test: einen TV-Kurzlink mit `utm_*` öffnen, Trial über den Uscreen-Checkout
starten → in `sommer2026_signups` trägt die Zeile die `utm_*`.

## Pflege

Neue Massnahme → Zeile im Massnahmen-Protokoll (`sommer2026_massnahmen`, Service-
Role) mit Datum, `rolle`, Kosten, Reichweite, Klicks und den internen Notizen.
Neue Links immer nach obiger Konvention bauen – dann erscheinen sie ohne weiteres
Zutun im Cockpit.

**Newsletter-Aussendungen (Beschluss 18.7.2026):** ab sofort werden in den
Newslettern **Generator-Links** eingesetzt (nach dieser Konvention, aus
`apps/utm-generator/`), nicht die Auto-UTMs des Newsletter-Tools. Die
Auto-Beschriftungen («Newsletter / Goetheanum Newsletter … (Copy)») bucketen
zwar grob richtig, tauchen aber im Register-Soll/Ist nie auf und tragen kein
Motiv. Bereits versendete Alt-Links bleiben, wie sie sind.

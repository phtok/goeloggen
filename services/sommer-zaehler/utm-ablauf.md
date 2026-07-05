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

Regeln: nur Kleinbuchstaben, keine Umlaute (`ue/oe/ae`), keine Leerzeichen. Der
`kanal`-Bucket im Cockpit wird aus `utm_source`/`utm_medium` abgeleitet – die
Rohwerte bleiben erhalten, damit «Nach Motiv» das einzelne Reel vom Footer-Link
unterscheidet.

## Die drei Landingpages (Ziel des Links)

- Übersicht · 3 Monate gratis → `https://global-sommer2026.goetheanum.online`
- Wochenschrift → `https://ws-sommer2026.dasgoetheanum.com`
- goetheanum.tv → `https://tv-sommer2026.goetheanum.tv`

Ein Link führt **nie** auf die nackte Startseite, sondern immer auf eine dieser
drei Seiten – mit angehängtem UTM-Block.

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

## So liest das Cockpit die Spur

- **Nach Motiv** (`sommer2026_attribution`): welches `utm_content` trug – Reel vs.
  Footer vs. Vorab-Teaser.
- **Wirkungskette** (`sommer2026_trichter`): Reichweite/Klicks aus dem
  Massnahmen-Protokoll, Abschlüsse aus den Anmeldungen.
- **Woher** (`sommer2026_kanaele`): der grobe Bucket mit Hauptaufgabe je Kanal.

## Pflege

Neue Massnahme → Zeile im Massnahmen-Protokoll (`sommer2026_massnahmen`, Service-
Role) mit Datum, `rolle`, Kosten, Reichweite, Klicks und den internen Notizen.
Neue Links immer nach obiger Konvention bauen – dann erscheinen sie ohne weiteres
Zutun im Cockpit.

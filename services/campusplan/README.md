# Campusplan · Backend

Backend der Laborseite `apps/campusplan/` (Konzept:
`docs/specs/campusplan-besucher-konzept.md`). Läuft im bestehenden
Werkzeug-Backend (Supabase `dagcsnfrlbpxcmdimnrw`), deployt am
14. September 2026 – dieser Ordner ist die **Referenzkopie**, nicht das
Deployment.

## Edge Function `campusplan-ausnahmen`

Deploy: automatisch beim Merge nach `main`
(`.github/workflows/deploy-campusplan-ausnahmen.yml`), von Hand über
«Run workflow». Seit 18. Oktober 2026 liefert sie auch die **Öffnungszeiten**
(siehe unten).

Grosser Saal und Glashaus-Ausstellung haben tagesaktuelle Einschränkungen
(Veranstaltungen, Proben, Schliesstage), die das Haus auf zwei Seiten von
goetheanum.ch als Textlisten pflegt:

- https://goetheanum.ch/de/campus/sonder-oeffnungszeiten-grossen-saal
  («Do. 17.9. 14.00-14.20 Uhr», «Sa. 26.12. geschlossen»)
- https://goetheanum.ch/de/campus/oeffnungszeiten-ausstellung-goethe
  («Geschlossen am: So. 13.9. …»)

Die Function liest beide Seiten, parst die Zeilen und liefert JSON:

```
GET https://dagcsnfrlbpxcmdimnrw.supabase.co/functions/v1/campusplan-ausnahmen
{ "stand": "2026-09-14T10:00:00Z",
  "saal":     [{ "datum": "2026-09-17", "zu": false, "zeit": "14.00–14.20", "text": "14.00–14.20 Uhr" }, …],
  "glashaus": [{ "datum": "2026-09-13", "zu": true, "text": "geschlossen" }, …],
  "fehler": [] }
```

Öffentlich, ohne Schlüssel (`verify_jwt: false`, wie `go`), ohne
Personendaten: es wird nichts gespeichert, nur goetheanum.ch gelesen.
Antwort eine Stunde cachebar; `?frisch` erzwingt das Neulesen. Fällt eine
Quelle aus, bleibt ihr Teil leer und `fehler` nennt sie — der Plan zeigt
dann den Link auf die Seite statt der Tageszeile.

Der Plan (`apps/campusplan/app.js`) fragt die Function beim Start und
zeigt zum Besuchstag «an diesem Tag 14.00–14.20 Uhr» oder «an diesem Tag
geschlossen»; ein geschlossener Ort fällt aus der Vorauswahl.

## Öffnungszeiten live (seit 18. Oktober 2026)

Auftrag: «Die Öffnungszeiten müssen immer aktuell mit der Goetheanum-Webseite
abgeglichen werden.» Die Function liest darum zusätzlich
https://goetheanum.ch/de/campus/oeffnungszeiten und gibt jeden Ort als
Zeitfenster zurück:

```
"zeiten": [
  { "titel": "Grosser Saal", "kontext": [".", "Besichtigungen"],
    "fenster": [{ "tage": [0,1,2,3,4,5,6], "von": "13:30", "bis": "14:30" }] },
  { "titel": "Haus de Jaager", …, "fenster": [{ "tage": [5], "von": "15:00", "bis": "16:00" }],
    "ersterImMonat": true, "zuMonate": [7, 8] }, …
]
```

Gelesen werden Zeilen wie «Mo. bis Do.: 14.30 - 15.30 Uhr», «Täglich: …»,
«Sa. und So.: …», «Jeden ersten Freitag im Monat: …», Folgezeilen
«und 14.00 - 16.00 Uhr» und «Juli und August 2026 geschlossen». Der Ort ist
die Zeile davor. In `apps/campusplan/gaeste.js` trägt jeder Ort dieser Seite
`quelle` (Titel oder Teil davon); der Plan nimmt die Live-Fenster und fällt
nur auf die eigenen Werte zurück, wenn die Seite nicht erreichbar ist oder
der Ort dort fehlt. Aus den Fenstern rechnet der Plan Text, «geschlossen» und
den Zeitplan; eine Tagesausnahme des Grossen Saals ersetzt das Fenster des Tags.

## Alle Quellen live (seit 18. Oktober 2026, zweite Runde)

Auftrag: «Alle Öffnungszeiten aktuell abgleichen!» Die Function liest jetzt
jede Website, auf der ein Ort des Plans seine Zeiten pflegt, mit einem
gemeinsamen Parser (Ort / Tage / Zeit, in einer oder zwei Zeilen):

| `seite` | Website | erkannt |
|---|---|---|
| `zeiten` | https://goetheanum.ch/de/campus/oeffnungszeiten | alle Orte der Seite |
| `buchhandlung` | https://www.goetheanum-buchhandlung.ch/pages/oeffnungszeiten | «Allgemeine Öffnungszeiten» |
| `bibliothek` | https://goetheanum.ch/de/dokumentation/bibliothek | «Öffnungszeiten» samt Ferien (`zuZeitraeume`) |
| `archiv` | https://www.rudolf-steiner.com/ | «Lesesaal & Shop» |
| `speisehaus` | https://www.speisehaus.ch/ | «Laden», «Wandelhalle» |

Dazu `ausstellungen`: die laufenden Ausstellungen der Sektion für Bildende
Künste (https://sbk.goetheanum.org/veranstaltungen/ausstellungen) mit ihren
Teilen und Daten aus der Einzelseite; der Plan zeigt sie bei der Galerie.

Jeder Zeitenblock trägt `seite`; `gaeste.js` nennt je Ort `seite` und
`quelle`. Erkennt die Function auf einer erreichbaren Seite nichts, steht das
in `fehler`. Der Plan zeigt jeden Ort, dessen Zeiten nicht live gefunden
wurden, als «Zeiten heute nicht bestätigt, vor dem Besuch prüfen» mit Link,
und oben einen Satz zum Stand aller Orte.

## Wächter

**Täglich** prüft `python3 tools/oeffnungszeiten-pruefen.py --live`, dass die
Function fehlerfrei lief und jede `quelle` aus `gaeste.js` live gefunden wird;
eine Lücke eröffnet ein Issue (Label campusplan). **Monatlich** zusätzlich der
Textvergleich der festen Zeiten:

Die festen Öffnungszeiten in `apps/campusplan/gaeste.js` stammen von sechs
Seiten (goetheanum.ch, Buchhandlung, Bibliothek, rudolf-steiner.com,
speisehaus.ch). `tools/oeffnungszeiten-pruefen.py` legt ihren Zeiten-Text
unter `docs/oeffnungszeiten-stand/` ab; der Workflow
`.github/workflows/oeffnungszeiten-waechter.yml` vergleicht am 1. jedes
Monats und eröffnet bei Abweichung ein Issue mit dem Unterschied. Der
Mensch prüft `gaeste.js` und schreibt den Stand neu.

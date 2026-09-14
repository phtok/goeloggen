# Campusplan · Backend

Backend der Laborseite `apps/campusplan/` (Konzept:
`docs/specs/campusplan-besucher-konzept.md`). Läuft im bestehenden
Werkzeug-Backend (Supabase `dagcsnfrlbpxcmdimnrw`), deployt am
14. September 2026 – dieser Ordner ist die **Referenzkopie**, nicht das
Deployment.

## Edge Function `campusplan-ausnahmen`

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

## Monatlicher Wächter über die festen Zeiten

Die festen Öffnungszeiten in `apps/campusplan/gaeste.js` stammen von sechs
Seiten (goetheanum.ch, Buchhandlung, Bibliothek, rudolf-steiner.com,
speisehaus.ch). `tools/oeffnungszeiten-pruefen.py` legt ihren Zeiten-Text
unter `docs/oeffnungszeiten-stand/` ab; der Workflow
`.github/workflows/oeffnungszeiten-waechter.yml` vergleicht am 1. jedes
Monats und eröffnet bei Abweichung ein Issue mit dem Unterschied. Der
Mensch prüft `gaeste.js` und schreibt den Stand neu.

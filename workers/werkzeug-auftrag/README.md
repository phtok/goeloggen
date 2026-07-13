# Werkzeug-Auftrag-Worker

Der Absende-Weg **(a)** der [Werkzeug-Schmiede](../../apps/schmiede/): nimmt einen
Auftrag der Schmiede entgegen und legt daraus ein GitHub-Issue in `phtok/goeloggen`
an (Label `werkzeug-wunsch`). So landet ein Wunsch direkt in der bestehenden
Bau-Schleife – **ohne dass die absendende Person ein GitHub-Konto braucht**. Das
Token wohnt als Secret im Worker, nie im Repo und nie im Browser.

Ohne diesen Worker ist die Schmiede trotzdem nutzbar: „Absenden" kopiert dann den
Auftrag und bittet, ihn an die Person weiterzugeben, die den Link geteilt hat.

## Was gebraucht wird

- Ein Cloudflare-Konto (wie beim Visitenkarten- und Logo-Usage-Worker).
- Ein **fein granulierter GitHub-Token** mit Recht `Issues: read and write` auf
  `phtok/goeloggen` – mehr nicht.

## Aufsetzen

```sh
cd workers/werkzeug-auftrag
cp wrangler.toml.example wrangler.toml      # wrangler.toml ist git-ignoriert

npx --yes wrangler@4 secret put GITHUB_TOKEN   # Token einmalig setzen (Secret)
npx --yes wrangler@4 deploy
```

`wrangler deploy` nennt die Worker-URL (etwa
`https://goetheanum-werkzeug-auftrag.<konto>.workers.dev`).

## Anschliessen

In `apps/schmiede/index.html` die Konstante setzen:

```js
var AUFTRAG_ENDPOINT = 'https://goetheanum-werkzeug-auftrag.<konto>.workers.dev/auftrag';
```

Danach schickt „Absenden" den Auftrag direkt in die Werkstatt und zeigt den Link
zum angelegten Issue. Solange die Konstante leer ist, bleibt es beim Kopieren.

## Wie sich die Schleife schliesst

1. Person füllt die Schmiede aus → **Absenden**.
2. Worker legt ein Issue `Werkzeug-Wunsch: …` mit Label `werkzeug-wunsch` an.
3. Die bestehende Bau-Schleife (Claude) nimmt den Wunsch auf, baut vom Starter
   aus, die Prüfmaschinen sichern das Hausbild, der PR wird gemergt.
4. Das neue Werkzeug erscheint über seinen `tools.json`-Eintrag im Hub.

## Endpunkte

| Pfad | Methode | Zweck |
|---|---|---|
| `/auftrag` (oder `/`) | POST | Auftrag annehmen → Issue anlegen. Body: `{ "titel": "…", "auftrag": "…" }` |
| `/health` | GET | Lebenszeichen |

## Missbrauch

Ein offener Endpunkt, der Issues anlegt, kann beschossen werden. Eingebaut sind
Längengrenzen und CORS. Wird es breiter geteilt, davor ein Cloudflare-Turnstile
oder eine Rate-Limit-Regel setzen – dann erst die URL streuen.

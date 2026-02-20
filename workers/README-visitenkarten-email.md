# Visitenkarten Email Export Worker

Dieser Worker nimmt Export-Requests aus `visitenkarten.html` entgegen und versendet die angeforderte Datei per E-Mail.

## Verhalten

- akzeptiert nur `POST`
- erlaubt nur Empfänger `@goetheanum.ch`
- akzeptiert nur Attachments in den Formaten:
  - `application/pdf`
  - `image/svg+xml`
  - `image/png`
- Rate-Limit pro IP (in-memory)
- BCC-Kopie an `ALERT_EMAIL`
- enthält in der Mail einen Warn-Link an `philipp.tok@goetheanum.ch`

## Setup

1. Cloudflare Worker-Dateien liegen in:
   - `/Users/philipptok/goeloggen/workers/visitenkarten-email-worker.js`
   - `/Users/philipptok/goeloggen/workers/wrangler.visitenkarten-email.toml.example`

2. Beispielkonfiguration kopieren:

```bash
cd /Users/philipptok/goeloggen/workers
cp wrangler.visitenkarten-email.toml.example wrangler.toml
```

3. Resend-API-Key setzen:

```bash
cd /Users/philipptok/goeloggen/workers
wrangler secret put RESEND_API_KEY
```

4. Deploy:

```bash
cd /Users/philipptok/goeloggen/workers
wrangler deploy
```

5. Endpoint in Frontend eintragen:

Datei `/Users/philipptok/goeloggen/assets/vk-email-config.js`:

```js
window.VK_EMAIL_EXPORT_ENDPOINT = "https://<dein-worker>.workers.dev";
```

Hinweis: Falls du im Worker einen Pfad wie `/export` verwenden willst, trage diesen komplett ein.

## Testmodus

Für einen sicheren Probelauf ohne Versand:

- in `wrangler.toml`: `DRY_RUN = "1"`

Dann gibt der Worker `ok: true` zurück, ohne eine Mail zu senden.

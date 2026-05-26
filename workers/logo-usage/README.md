# Logo Generator Usage Worker

Privacy-friendly usage statistics for the static Goetheanum Logo Generator.

## What Is Collected

- pageviews and export events
- export format: `svg`, `svg48`, `png`, `webp`, `jpg`, `pdf`
- selected logo options: org, category, layout, language, color mode, scale
- UI language, viewport size bucket, device class, country, referrer host
- hashed daily visitor key and hashed browser-session key

No raw IP address, user agent, email address, generated logo text, or custom text is stored.

## Setup

```bash
cd /Users/philipptok/goeloggen/workers/logo-usage
cp wrangler.toml.example wrangler.toml
npx --yes wrangler@4 login
npx --yes wrangler@4 d1 create goetheanum-logo-usage
```

Put the returned D1 `database_id` into `wrangler.toml`, then run:

```bash
npx --yes wrangler@4 d1 migrations apply goetheanum-logo-usage --remote
npx --yes wrangler@4 secret put USAGE_HASH_SALT
npx --yes wrangler@4 secret put REPORT_TOKEN
npx --yes wrangler@4 deploy
```

Then set the deployed URL in:

```js
// /Users/philipptok/goeloggen/assets/logo-usage-config.js
window.GOE_LOGO_USAGE_ENDPOINT = "https://<worker-name>.<account>.workers.dev";
```

## Endpoints

- `POST /collect` stores one event.
- `GET /summary?from=YYYY-MM-DD&to=YYYY-MM-DD` returns aggregated statistics.
- `GET /health` checks the Worker.

Reports require `REPORT_TOKEN`. Call them with:

```bash
curl -H "Authorization: Bearer <token>" \
  "https://<worker>/summary?from=2026-01-01&to=2026-05-31"
```

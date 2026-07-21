# Secrets & Zugänge — wie Tokens hier bereitliegen

Ziel: Zugänge (Vercel, Supabase, Resend, …) liegen **bereit** und werden **bei
Bedarf freigegeben** — ohne pro Nutzung einen Token neu zu erzeugen und wieder
zu widerrufen. Es gibt zwei Mechanismen; nimm für jeden Dienst den oberen, wenn
möglich.

## 1. MCP-Connector (OAuth) — bevorzugt, «nie einsehbar»
Einmal auf Org-Ebene in den **claude.ai-Connector-Einstellungen** autorisieren.
Danach liegt der Token in Anthropics verwaltetem Speicher, **kommt nie in den
Container** (weder Session noch Assistent sehen ihn), und wird server-seitig
eingespeist. «Freigeben bei Bedarf» = der **Pro-Chat-Schalter** je Connector.
Kein Neu-Erzeugen, kein Widerrufen pro Nutzung.

## 2. Environment-Variable — nur wo es keinen Connector gibt
Ein **langlebiger, eng gescopter** Key als Umgebungs-Variable in der
Environment-Konfiguration (`.env`-Format, `KEY=value`, ohne Anführungszeichen).
Einmal setzen, dauerhaft wiederverwenden.

> **Vorbehalt (Doku):** Ein dediziertes, verschlüsseltes Secrets-Lager gibt es
> bei Claude Code on the web noch nicht. Environment-Variablen sind für **jeden
> sichtbar, der die Umgebung bearbeiten darf**, und jeder Prozess der Session
> kann sie lesen. Darum: minimale Scopes, Ablaufdatum, und — wenn Trennung
> wichtig ist — sensible Keys in eine **eigene Umgebung**, die nur bei Bedarf
> aktiviert wird.

**Nie** Tokens in Chat, Commits oder ins Repo schreiben.

## Dienste-Register

| Dienst | Mechanismus | Secret-Name (Env) | Minimal-Scope | Stand |
|---|---|---|---|---|
| **Vercel** | Connector | — | — | verbunden |
| **Supabase** | Connector | — | — | verbunden |
| **Canva** | Connector | — | — | verbunden |
| **Google Drive** | Connector | — | — | verbunden |
| **ActiveCampaign** | Connector | — | — | installiert, **Auth erneuern** |
| **GitHub** | Connector/Proxy | (`GH_TOKEN` nur für `gh`-CLI) | `repo`, `read:org` | über Proxy |
| **Resend** | Supabase-Config-Tabelle (`seelenkalender_config`, nur Service-Role) | `resend_api_key` | nur Senden (`sending`) | per SQL-Editor setzen (`services/seelenkalender/README.md`) — **nicht** als Claude-Env nötig |
| **Sortierer-Commit** | Supabase Edge Function | `GITHUB_TOKEN`, `SORTIERER_SECRET` | Token: **nur dieses Repo**, Contents R+W | Function-Secrets im Supabase-Projekt setzen (s. u.) |
| *(Alternative: Brevo)* | Connector | — | — | im Verzeichnis, nicht installiert |

## Env-Variablen setzen (Web-UI)
Umgebung wählen → bearbeiten → **Environment variables** → `.env`-Zeilen, z. B.:

```text
RESEND_API_KEY=<eintragen, nicht hier>
```

`gh`-CLI (falls je nötig) liest automatisch `GH_TOKEN`.

## `.mcp.json` (Projekt-Scope, für key-basierte MCP-Server)
Die verwalteten Connector (Vercel/Supabase/…) werden **im claude.ai-UI**
gepflegt, **nicht** hier — deshalb ist `mcpServers` leer. Für einen
**key-basierten** Server (der einen Env-Token liest) eine Zeile ergänzen, z. B.:

```jsonc
{
  "mcpServers": {
    // Beispiel — nur eintragen, wenn ein solcher Server wirklich genutzt wird:
    // "resend": {
    //   "command": "npx",
    //   "args": ["-y", "@some/resend-mcp-server"],
    //   "env": { "RESEND_API_KEY": "${RESEND_API_KEY}" }
    // }
  }
}
```

## Sortierer «Direkt speichern» (Edge Function)

Der Sortierer (`sortierer.html`) kann die Menü-Reihenfolge direkt committen,
statt sie zu exportieren. Dahinter steht die Edge Function
`services/kistenpflege/sortierer-commit/index.ts` (Projekt
`dagcsnfrlbpxcmdimnrw`). Sie schreibt **ausschliesslich** das Feld
`reihenfolge` in die `tools.json` — winzige Wirkfläche, per Git rückholbar.

Zum Scharfschalten zweierlei, **im Supabase-Projekt** (nie hier eintragen):

1. **Deploy:** Function `sortierer-commit` aus obiger Quelle deployen (Connector
   oder `supabase functions deploy sortierer-commit`).
2. **Function-Secrets** (Dashboard → Edge Functions → Secrets, oder
   `supabase secrets set`):
   - `GITHUB_TOKEN` — fine-grained PAT, **nur `phtok/goeloggen`**, Contents:
     Read+Write. (Optional `GITHUB_REPO`/`GITHUB_BRANCH`; Vorgabe
     `phtok/goeloggen` / `main`.)
   - `SORTIERER_SECRET` — frei gewähltes langes Passwort; dasselbe gibt die
     Person beim ersten «Direkt speichern» im Browser ein (bleibt lokal).

Bis beide Secrets gesetzt sind, antwortet die Funktion bewusst mit 500
«nicht konfiguriert»; solange bleibt **«Exportieren»** der Weg (Datei
herunterladen und committen).

## Merksatz
Connector, wo es einen gibt (parat + nie einsehbar + kein Recycling); Env-Key
mit Minimal-Scope nur für den Rest; niemals im Chat oder Repo.

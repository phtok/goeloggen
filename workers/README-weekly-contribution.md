# Wöchentlicher Beitrags-Agent

Ein Cloudflare Worker, der automatisch Einladungs-E-Mails für wöchentliche Beiträge vorbereitet und versendet.

## Ablauf

| Tag | Zeit (UTC) | Aktion |
|-----|-----------|--------|
| **Donnerstag** | 09:00 | Beitragende für nächste Woche aus KV lesen, Einladungstext formulieren und zwischenspeichern |
| **Montag** | 07:00 | Vorbereitete Einladung per E-Mail an alle Empfänger senden |

Falls am Donnerstag noch kein Eintrag für die nächste Woche hinterlegt ist, geht eine Erinnerungsmail an `ADMIN_EMAIL`.

---

## Setup

### 1. KV-Namespace anlegen

```bash
wrangler kv namespace create SCHEDULE_KV
# → gibt eine ID aus, die in wrangler.toml eingetragen wird
```

### 2. Config-Datei anlegen

```bash
cp wrangler.weekly-contribution.toml.example wrangler.weekly-contribution.toml
# KV-ID und RECIPIENTS anpassen
```

### 3. Secrets setzen

```bash
wrangler secret put RESEND_API_KEY --config wrangler.weekly-contribution.toml
wrangler secret put ADMIN_TOKEN    --config wrangler.weekly-contribution.toml
```

### 4. Deployen

```bash
wrangler deploy --config wrangler.weekly-contribution.toml
```

---

## Zeitplan pflegen

Alle Admin-Anfragen benötigen den HTTP-Header:
```
Authorization: Bearer <ADMIN_TOKEN>
```

### Eintrag anlegen / aktualisieren

```bash
curl -X POST https://<worker-url>/schedule \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "week": "2026-13",
    "contributors": ["Anna Beispiel", "Max Mustermann"],
    "topic": "Meditation und Biographie",
    "note": "Beginn 08:00 Uhr im Glashaus"
  }'
```

**Felder:**
| Feld | Pflicht | Beschreibung |
|------|---------|--------------|
| `week` | ✓ | ISO-Woche im Format `YYYY-WW` |
| `contributors` | ✓ | Array von Namen |
| `topic` | – | Thema des Beitrags |
| `note` | – | Zusätzlicher Hinweis |

### Zeitplan anzeigen (nächste 8 Wochen)

```bash
curl https://<worker-url>/schedule \
  -H "Authorization: Bearer <token>"
```

### Eintrag löschen

```bash
curl -X DELETE "https://<worker-url>/schedule?week=2026-13" \
  -H "Authorization: Bearer <token>"
```

### Vorbereitete Einladung anzeigen

```bash
curl https://<worker-url>/pending \
  -H "Authorization: Bearer <token>"
```

### Einladung sofort versenden (Test)

```bash
curl -X POST https://<worker-url>/send-now \
  -H "Authorization: Bearer <token>"
```

### Vorbereitung manuell auslösen

```bash
curl -X POST https://<worker-url>/prepare-now \
  -H "Authorization: Bearer <token>"
```

---

## Beispiel-Einladungsmail

**Betreff:** Einladung Montagmorgen Montag, 30. März 2026

> Liebe Gemeinschaft,
>
> am kommenden **Montag, 30. März 2026**, wird **Anna Beispiel und Max Mustermann** einen Beitrag gestalten.
>
> **Thema:** Meditation und Biographie
>
> Beginn 08:00 Uhr im Glashaus
>
> Herzliche Einladung!
>
> *Goetheanum*

---

## Lokaler Test mit Wrangler

```bash
# Cron-Event simulieren (Donnerstag)
wrangler dev --config wrangler.weekly-contribution.toml
# → in neuem Terminal:
curl -X POST "http://localhost:8787/__scheduled?cron=0+9+*+*+4"
```

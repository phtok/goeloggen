# QR-Generator · Backend

Backend des Werkzeugs `apps/qr-generator/`: Kurzlinks mit anonymer
Scan-Zählung. Läuft im bestehenden Werkzeug-Backend (Supabase
`dagcsnfrlbpxcmdimnrw`), deployt am 10. Juli 2026 – dieser Ordner ist die
**Referenzkopie**, nicht das Deployment.

## Wie es zusammenhängt

1. Das Werkzeug legt per RPC `qr_link_anlegen` einen Code an
   (Tabelle `qr_links`: Code → Ziel-URL).
2. Der QR-Code zeigt auf `https://tools.goetheanum.ch/s/<code>` – dieselbe
   Kurzlink-Brücke wie die Sommer-Kampagne (separates Repo `phtok/goelinks`,
   Referenz in `../sommer-zaehler/kurzlink-site/`; dort ist **nichts** zu
   ändern, die 404-Brücke leitet jeden Code blind weiter).
3. Die Edge Function `go` (`../sommer-zaehler/go/index.ts`) löst den Code über
   die RPC `kurzlink_aufloesen` auf: sie liest **beide** Register –
   `sommer2026_links` (Kampagne) und `qr_links` (QR-Generator) – und zählt den
   Aufruf in `link_hits`. Ein Rundgang, der Redirect bleibt gleich schnell.
4. Das Werkzeug liest die Zahlen über die Aggregat-RPCs `qr_stats_public`
   (Summe, letzter Scan, Ziel) und `qr_stats_tage` (Scans je Tag, 30 Tage).

Weil beide Register denselben Namensraum `/s/` teilen, prüft
`qr_link_anlegen` die Eindeutigkeit über **beide** Tabellen.

## Datenschutz

Wie überall im Werkzeug-Backend (Muster `statistik.html`): Rohtabellen sind
versiegelt (RLS an, keine anon-Policy, Rechte entzogen), nur die RPCs sind
offen. Je Scan werden **nur Zeitpunkt und Code** gespeichert – keine IP, kein
User-Agent, keine Cookies, keine Personendaten. `qr_stats_public` liefert nur,
was zum Code gehört; wer den Code nicht kennt, sieht nichts.

## RPCs

| RPC | Wer | Zweck |
| --- | --- | --- |
| `qr_link_anlegen(p_code, p_url, p_ersteller)` | anon | Code anlegen: `ok` · `vergeben` · `ungueltig` · `unvollstaendig` |
| `qr_stats_public(p_code)` | anon | Summe, letzter Scan, Ziel-URL (beide Register) |
| `qr_stats_tage(p_code)` | anon | Scans je Tag, letzte 30 Tage |
| `kurzlink_aufloesen(p_code)` | nur service_role | Auflösen + Zählen für die Function `go` |

## Bewusste Entscheide (v1)

- **Keine Lösch-RPC:** ein offener Löschweg würde gedruckte Codes gefährden.
  Falls nötig, später als geschützter Weg (Muster Passwort-Hash wie bei den
  Multiplikatoren).
- **Fallback unbekannter Codes:** bleibt vorerst die Sommer-Landingpage (in
  `go/index.ts`); nach der Kampagne auf eine neutrale Seite stellen.
- **Geparkt für v2:** Logo in der QR-Mitte (erzwingt Fehlerkorrektur H und
  echte Gerätetests) sowie der Umzug des generalisierten QR-Renderers nach
  `design-system/qr.js`, sobald er sich bewährt.

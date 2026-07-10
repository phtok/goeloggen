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
User-Agent, keine Cookies, keine Personendaten.

Das Register selbst ist **offen** (Beschluss 10.7.2026, wie UTM-Generator und
Cockpit): `qr_links_public()` zeigt alle angelegten Kurzlinks mit Ziel und
Zählung. Wer hier einen Kurzlink anlegt, veröffentlicht ihn – für nicht
öffentliche Ziele ist das Werkzeug nicht gedacht.

## RPCs

| RPC | Wer | Zweck |
| --- | --- | --- |
| `qr_link_anlegen(p_code, p_url, p_ersteller)` | anon | Code anlegen: `ok` · `vergeben` · `ungueltig` · `unvollstaendig` |
| `qr_links_public()` | anon | Offenes Register: alle QR-Kurzlinks mit Ziel und Zählung |
| `qr_stats_public(p_code)` | anon | Summe, letzter Scan, Ziel-URL (beide Register) |
| `qr_stats_tage(p_code)` | anon | Scans je Tag, letzte 30 Tage |
| `qr_link_loeschen(p_code, p_passwort)` | anon, Team-Passwort | Löschen: `ok` · `passwort` · `unbekannt` (Zählung geht mit) |
| `kurzlink_aufloesen(p_code)` | nur service_role | Auflösen + Zählen für die Function `go` |

## Bewusste Entscheide (v1)

- **Löschen nur mit Team-Passwort** (Beschluss 10.7.2026, revidiert vom
  Auftraggeber): der Lösch-Knopf im Register erscheint nur im Backstage-Modus,
  der echte Riegel ist das Passwort in `qr_link_loeschen` (Hash in `qr_config`,
  Muster Multiplikatoren, Präfix `goe-qr:`). Ein offener Löschweg würde
  gedruckte Codes gefährden. Passwort ändern: neuen Hash in `qr_config`
  setzen (`update qr_config set value = encode(extensions.digest('goe-qr:' ||
  lower(trim('NEU')), 'sha256'), 'hex') where key = 'loeschen_pw_hash'`).
- **Fallback unbekannter Codes:** bleibt vorerst die Sommer-Landingpage (in
  `go/index.ts`); nach der Kampagne auf eine neutrale Seite stellen.
- **Geparkt für v2:** Logo in der QR-Mitte (erzwingt Fehlerkorrektur H und
  echte Gerätetests) sowie der Umzug des generalisierten QR-Renderers nach
  `design-system/qr.js`, sobald er sich bewährt.

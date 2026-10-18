# Mailing · Grenzgänger — Drei-Wellen-Copy je Zielkreis

Instanz der Mail-Fabrik für die Grenzgänger-Wellen
(`docs/grenzgaenger/charta.md`). Ein **Segment = ein Griff** (g0NN aus
`docs/grenzgaenger/griffe.json`); je Griff drei Wellen × zwei Sprachen.

```
heroes.json ─┐
config.json ─┼─► ../mailing-sommer2026/build_editor.py --quelle . --publish
links.py    ─┘     ─► dist/mail_{motiv}_{welle}_{sprache}.html (versandfähig)
                   ─► apps/grenzgaenger-mails/ (Editor + Assets + mails/; GitHub Pages)
                   --verify (nach dem Merge): Editor, Assets und Mail-URLs live?
```

Bauen: `pip install -r ../mailing-sommer2026/requirements.txt` ·
`npm i -g mjml` · `python3 ../mailing-sommer2026/build_editor.py --quelle . --publish`

**Die Fabrik bleibt eine:** `build_editor.py` wohnt beim Sommer 2026 und kennt
seit der `--quelle`-Parameterisierung mehrere Instanzen (`editor_app`,
`editor_kicker`, `editor_onpage` in `config.json`). Änderungen an der Fabrik
dort machen, nicht hier kopieren.

## Versandweg (anders als Sommer 2026)

Die Wellen gehen **nicht über ActiveCampaign**, sondern über die
Grenzgänger-Fang-Strecke (`services/lead-agent/`): pg_cron ruft täglich
`lead-fang?aktion=wellen`, die Function holt das gebaute Mail-HTML von
GitHub Pages (`apps/grenzgaenger-mails/mails/…`), ersetzt
`%UNSUBSCRIBELINK%` je Lead durch den Abmelde-Link und sendet per Resend.
Darum gilt wie beim Sommer: **erst mergen/deployen, dann aktivieren** —
vorher sind Mail- und Bild-URLs tot.

Die **Betreffzeilen** liest die Function aus `marketing_griffe.wellen_betreff`;
beim Aktivieren eines Griffs (`bereit → live`) aus `heroes.json` übernehmen
(`services/lead-agent/README.md`).

## Attribution

`links.py` dieser Instanz setzt `utm_content = {griff}_{welle}` (z. B.
`g001_w1`), fix dazu `utm_source=mailing`, `utm_medium=email`,
`utm_campaign=grenzgaenger` — deckungsgleich mit den Messpunkten im
Griffe-Register und ablesbar im Sommer-Zähler-Cockpit.
`python3 links.py` listet die Registerzeilen für den UTM-Generator.

## Würde-Regeln (Charta §2.2, hier verbindlich)

Keine falsche Verknappung, keine Dark Patterns; w3 nennt die Konditionen im
Klartext («das Abo endet, wann Sie es beenden»); höchstens drei Wellen je
Lead; Abmeldelink in jeder Mail.

## Motive

Die Hero-Bilder referenzieren die Sommer-JPGs
(`../mailing-sommer2026/assets/motive/`) — keine Binär-Doppel im Repo.
Eigene Motive je Zielkreis kommen dazu, sobald ein Griff sie braucht
(dann in `assets/motive/` dieser Instanz).

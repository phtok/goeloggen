# Services

Nicht-statische Unterprojekte mit eigenem Runtime- oder Worker-Kontext.

- `sommer-zaehler/` – Backend des Aktions-Cockpits (`apps/sommer-zaehler/`); zieht Aggregat-Summen aus dem Werkzeug-Supabase.
- `mailing-sommer2026/` – Mail-Fabrik der Sommer-Aktion 2026 (Quelle, Build, Gegenlese-Editor).
- `mailing-grenzgaenger/` – Mail-Fabrik der Grenzgaenger-Wellen, ein Segment je Griff.
- `lead-agent/` – Fang-Strecke des Grenzgaenger-Agenten (Edge Function `lead-fang`).
- `seelenkalender/` – Versand-Strecke des Wochenspruch-Abos (`apps/seelenkalender/`).
- `werkzeug-abo/` – Update-Abo der Werkzeuge mit Double-Opt-in (`abo.html`).
- `schmiede/` – Eingang der Wuensche aus der Werkzeug-Schmiede (`apps/schmiede/`).
- `qr-generator/` – Backend von `apps/qr-generator/`: Kurzlinks mit anonymer Scan-Zaehlung.
- `kistenpflege/` – Sortierer der Werkzeugkiste (Edge Function `sortierer-commit`).
- `werkzeugpost/` – Textbestand der Werkzeugpost (Mails, Personas).

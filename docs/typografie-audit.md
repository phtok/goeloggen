# Typografie-Audit – Hausregeln auf allen Seiten

Stand: 2026-06-24. Geprüft gegen `assets/typografie/typo-regeln.yaml`
(Quelle: `goetheanum-typo-tokens.json` → `$regeln`, Referenzdokument
`typografie.html`).

## Methode

1. **Deterministischer Linter** (`tools/typo_lint.py`): liest die
   regex-prüfbaren Regeln (G16–G22, T01) und prüft den **sichtbaren deutschen
   Lesetext** aller HTML-Seiten (Root, `apps/*/`, `start/`). Code, `<style>`,
   `<script>`, URLs und E-Mails werden ausgenommen; Teilbäume mit
   `data-typo-ignore` (absichtliche Gegenbeispiele) übersprungen.
2. **CSS-Mustersuche** für die Urteils-Regeln (G04 Gewicht, G05 Versalien/
   Sperrung/Unterstreichung).
3. **Manuelle Sichtung** jedes Treffers (echter Bruch vs. Lehrbeispiel vs.
   Fehlalarm).

33 Seiten geprüft. Ausgangslage: 65 Treffer. Nach Triage: **5 echte Brüche**,
der Rest Lehrbeispiele oder Regex-Fehlalarme.

## Behobene Brüche

| Seite | Regel | vorher | nachher |
|---|---|---|---|
| `schriften.html` | G16 Anführung (Fehler) | `→ „Installieren".` | `→ ‹Installieren›.` |
| `werkzeug.html` | G16 Anführung (Fehler) | `→ „Ziel speichern unter"` | `→ ‹Ziel speichern unter›` |
| `zuordnen.html` | G16 Anführung (Fehler) | `(z. B. „ff (Wortende)")` | `(z. B. ‹ff (Wortende)›)` |
| `schriften.html` | G21 Viersteller | `1.000 Plätze` | `1000 Plätze` |
| `schriften.html` | G22 führende Null | `09.30 Uhr` | `14.30 Uhr` (tnum-Demo bleibt bündig, ohne führende Null) |

`zuordnen.html` wird aus `tools/goetheanum-fontfix/make_mapping_tool.py`
generiert – der Generator wurde mitkorrigiert, damit der Bruch beim nächsten
Build nicht zurückkehrt.

## Urteils-Regeln (G01/G04/G05)

- **Versalien-Labels** (`.kick`/`.tag`/`.badge` mit `letter-spacing`,
  z. B. in `start/`, `schrift-vergleich.html`): **kein Bruch.** Sie sind
  Strukturebene (G01-Ausnahme: Titel/Lede/Legende/Tabellenkopf) und gesperrt
  **per Laufweite**, nicht per Leertaste (G23). G05 verbietet Versalien nur als
  **Betonung im Fließtext** – das ist hier nicht der Fall.
- **Unterstreichung** (`schriften.html`, `werkzeug.html`,
  `apps/signatur-generator`): nur `a:hover` und Link-artige Buttons – Link-
  Affordanz, **kein** Auszeichnungsmittel. Kein Bruch.
- **G04 Gewicht > Laut (680):** `font-weight:700` in `portal.html` und
  `start/index.html` (von mir eingeführt) **behoben**. Zugleich Lücke im
  Design-System geschlossen: Es gab **kein Titel-Token**. Neu in
  `design-system/tokens.css`:
  - `--w-title:580` (Deutlich – Hausschnitt für **Titel**, vgl. CLAUDE.md)
  - `--w-strong:680` jetzt klar als Hervorhebung/Inline-Fettung (Laut)
  Die Hero-Titel von `portal.html`/`start/` nutzen jetzt `var(--w-title)`.

## Offene Punkte (brauchen deine Entscheidung)

### 1. Regex-Defekte im Regelwerk – Vorschlag, nicht eigenmächtig geändert
CLAUDE.md sagt: Regelwerk nicht eigenmächtig umschreiben. Daher hier nur der
Befund. Drei `erkennen`-Muster melden **bereits korrekten** Text als Treffer
(daher 29 Empfehlungs-Fehlalarme wie „9 mm", „z. B.", „9.30 Uhr"):

| Regel | Problem | Vorschlag |
|---|---|---|
| `G20-prozent` | `(\d) ?(…)` – das optionale Leerzeichen matcht auch „9 mm" (korrekt) | Leerzeichen verbieten: `(\d)(%\|CHF\|EUR\|kg\|km\|mm\|cm\|m2\|Uhr)\b` |
| `G20-abkuerzung` | `\.\s?` matcht auch „z. B." (korrekt) | kein Spatium: `\b(z\|d\|u)\.(B\|h\|a)\.` |
| `G22-uhrzeit` | greift nur die Doppelpunkt-Form, verfehlt „09.30 Uhr" | Variante ergänzen: `\b0(\d)\.(\d{2})\s?(Uhr\|h)\b` → `$1.$2 $3` |

Außerdem fehlen zwei im Spickzettel gezeigte Fälle in der YAML: **mal** (`4x5` →
`4 × 5`) und **Datum** (`11.06.2026` → `11. Juni 2026`).

→ Wenn du zustimmst, ziehe ich diese Korrekturen in `typo-regeln.yaml` nach;
dann verschwinden die Fehlalarme und die zwei zusätzlichen Fälle werden geprüft.

### 2. Alt-Werkzeuge mit `font-weight:700` (G04)
`apps/gtv-naming`, `apps/logo-generator`, `apps/visitenkarten-generator` setzen
noch `700`. Sauber wäre `var(--w-title)` (Titel) bzw. `var(--w-strong)`
(Fettung). Kein akuter Lesetext-Bruch, aber Hausmaximum überschritten. Auf Wunsch
als eigener Aufräum-PR.

## Garantie ab jetzt

1. **Linter** `tools/typo_lint.py` – führt die Regeln aus, Exit 1 nur bei harten
   Fehlern. Lokal: `python3 tools/typo_lint.py`.
2. **CI** `.github/workflows/typo-lint.yml` – läuft bei jedem PR, der HTML/Regeln
   berührt, und blockiert den Merge bei `fehler`-Verstößen. Empfehlungen
   erscheinen im Log.
3. **`data-typo-ignore`** – Konvention für absichtliche Gegenbeispiele auf Lehr-
   und Specimen-Seiten; der Linter überspringt solche Teilbäume.
4. **CLAUDE.md** – verweist Autoren (Mensch wie KI) auf Regeln + Linter, bevor
   gesetzt wird.

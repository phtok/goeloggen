# Design-System — Beschluss-Ledger (das Gedächtnis)

Hier atmet das System: jede Verbesserung, die aus einer Seite ins **Fundament**
aufgenommen wird, steht hier mit Datum, Grund und Wirkung. Der Ledger ist die
Erinnerung des Systems an sein eigenes Wachstum — und die Quelle der
Versionsnummer (`design-system/contract.json` → `version`, SemVer).

**Der Atem (Aufnahme-Schleife).** Eine neue Lösung taucht auf einer Seite auf →
`tools/ds-lint.py` erkennt die Abweichung (DS04) → Entscheid: **aufnehmen**
(in `tokens.css`/`base.css` + `contract.json`, Eintrag hier) oder **auflösen**
(`tools/ds-fix.py` hebt sie auf die Token-Schicht zurück). Aufgenommenes gilt ab
dann überall und wird vom Checker erwartet. So wird aus einer Rand-Verbesserung
Fundament — nie lokal belassen.

Schema je Eintrag: *was · warum · Wirkung (welche Regel/Token/Komponente)*.

---

## [Unveröffentlicht]

### Aufgenommen
- **Textrollen als gemessene Grundlage** (`base.css`) — Kicker · Lede · Hinweis
  (`.note`/`.hint`/`.help`/`.desc`) · Meta (`.cap`/`.caption`/`.legend`/`.byline`) ·
  Label (`.lab`/`.role`) · Wert (`.readout`) · Code (`.code`/`.mono`).
  *Warum:* jede Seite erfand eigene Grade (11–15px) und Farben für denselben
  Zweck — uneinheitlich und teils unter der Leseschwelle. *Wirkung:* eine Quelle,
  B03-sicher, löst die Eigenlösungen ab (DS04).
- **Mobil-Baseline** (`base.css`) — Fingerziele ≥44px, Felder ≥16px, kein
  Überlauf, umbrechende Köpfe. *Wirkung:* B03/B04 als Konstruktion, nicht als
  Nachkontrolle.
- **Sektionsfarben als Tokens** (`tokens.css`/`tokens.json`) — `--sek-*` aus
  `assets/goe-orgs.js`. *Warum:* die Sektions-Identitätsfarben lebten nur in der
  Logo-Engine. *Wirkung:* überall gleich benannt, markenfest (kippen nicht mit
  Hell/Dunkel).
- **`--ok` (Erfolgsgrün)** (`tokens.css`/`tokens.json`). *Warum:* die Engine fand
  das Grün `#3f7d46` hartverdrahtet in `base.css .btn.ok` und im Schaufenster –
  ein fehlendes Token. *Wirkung:* erste echte Atem-Aufnahme: aus einer entdeckten
  Abweichung wurde Fundament; `.btn.ok` und die Status-Punkte ziehen jetzt `--ok`.

### Engine (neu)
- **`design-system/contract.json`** — maschinenlesbarer Struktur-Vertrag (DS01–DS07).
- **`tools/ds-lint.py`** — prüft Gestalt-Konformität, meldet je Regel + Score.
- **`tools/ds-fix.py`** — hebt die Hauspalette deterministisch auf Tokens (Codemod).
- **Hook** — `ds-lint --staged` läuft mit (vorerst berichtend, nicht blockierend).

> Score-Verlauf (die Messlatte): **9 %** (Engine-Einführung) → **17 %** (Fundament
> + Schaufenster) → **35 %** (öffentliche Live-Seiten) → **46 %** (Generatoren +
> Icons). 11/24 Seiten konform. Jeder Schritt bewegt diese Zahl.

### Schaufenster bildet ab, was bereitliegt (Doku + Präsentation in einem)
- Neue Abschnitte, live aus der Quelle gerendert: **Textrollen** (Kicker/Lede/
  Hinweis/Meta/Label/Wert/Code/Badge), **Sektionen & Bereiche** (volle Tabelle
  aus `goe-orgs.js` + `--sek-*`-Swatches), **Konformitäts-Engine** (Vertrag
  DS01–07 aus `contract.json`, die Schleife, der Score).
- `goe-orgs.js` ist damit im Design-System **sichtbar** und über die Quelle
  korrigierbar. Befund dabei: die Visitenkarten-App trägt eine **abgewichene
  Kopie** der Tabelle – Konsolidierung (einbinden statt kopieren) steht an.

### Lesbarkeit & Inklusivität fest verankert (recherchiert, Stand 2026)
- **Typo-Skala einen Schritt grösser**: Floor 13→**14px**, Meta/Label 14→**15–16**
  (`--t-small`), Fliesstext 17→**18–20** (`--t-body`), Lede 19→**20–23**. Grund:
  16px ist die Norm-Untergrenze, Best Practice ‹bei 16 beginnen, hochskalieren›
  (WCAG resize 1.4.4; rem-basiert). Contract-Floor (DS03) 13→14 nachgezogen; die
  literalen 13px der öffentlichen Seiten auf `--t-small` gehoben.
- **B04**: Bezug auf WCAG 2.2 SC 2.5.8 (Ziel ≥24px, wir geben 44) und 1.4.12
  (Layout übersteht erhöhte Laufweiten) in den Hausregeln verankert.
- **Icons im Dunkelmodus**: schwarze Strich-Icons als `<img>` wurden verschluckt.
  Utility `.ico-invert` (Filter im Dunkelmodus) ins Fundament; auf die Schriften-
  Icons angewandt. Besser noch: Icons als Webfont/Inline-SVG mit currentColor.

### Neue Quelle & Werkzeug
- **`assets/goe-terms.js`** (Begriffe & Übersetzungen) – auf goetheanum.ch
  geprüft: fr/es korrigiert (Hochschule = ‹Université libre de science de
  l’esprit›, Gesellschaft = ‹Société anthroposophique générale›), verifizierte
  Zeilen auf `fest`. Neue Seite **uebersetzungen.html** (durchsuchbar, klick-
  kopierbar, für die Sekretariate) + Eintrag in `tools.json` (Startkarte).

### Behoben (Mobil & Lesbarkeit – aus echtem Geräte-Befund)
- **Seitenrand am Handy** war weg: `.hero{padding:X 0 Y}` setzte den seitlichen
  Rand auf 0 und überschrieb `.wrap` – Text klebte am Glas. Fundament-Fix:
  `.hero` nutzt nur noch `padding-block` (Seitenrand kommt aus `.wrap`); die 9
  Seiten mit lokalem `.hero`-Override nachgezogen. Mobiler `.wrap`-Rand bleibt
  grosszügig (`max(22px, safe-area)`), nicht verkleinert.
- **Lede unlesbar** (in „G Leise" 265 + muted gesetzt) → auf den Lese-Schnitt
  Klar gehoben (schriften, icons, statistik). Regelbezug: Leise verschwimmt klein,
  Minimum ist Klar.

### Engine geschärft (Lernen am Bestand)
- **DS04** meldet nur noch Schlüssel-Selektoren, nicht kontextuelle Überschreibungen
  (`.download .btn` ist Verortung). **Zeilen-Treffer** liegen jetzt korrekt auf der
  Property-Zeile (Mehrzeilen-CSS) – damit greift `# ds-ok` auch in den Generatoren.
- **Artefakt-Kategorien** ratifiziert (`# ds-ok`): gedrucktes Blatt/Karte, Schnitt-
  marken, E-Mail-Leinwand, „Logo auf Dunkel"-Vorschau, Owner-Mode-Signal, Modal-Scrim.
  Die Maschine schlägt vor, der Mensch ratifiziert – die Ausnahme wird Teil des Codes.

---

## Wie eine Verbesserung aufgenommen wird (Kurz-Rezept)
1. Lösung an *einer* Seite bewährt? `ds-lint` zeigt sie als DS04-Abweichung.
2. In `tokens.css`/`base.css` heben (Token oder Rolle/Komponente). Bei neuer
   Pflicht: `contract.json` ergänzen (Regel/Klasse) **und** `version` erhöhen.
3. Eintrag hier (was · warum · Wirkung).
4. `ds-fix` über die Seiten laufen lassen, `ds-lint --score` prüfen, shippen.

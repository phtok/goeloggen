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

> Ausgangs-Score bei Einführung der Engine: **9 % konform** (343 Fehler, 23 Seiten).
> Nach Fundament + erster sicherer Anwendung (Schaufenster 100 %, Starter, Logos,
> Karten): **17 %** (328 Fehler). Das ist die Messlatte, an der das Nachziehen
> sichtbar wird – jeder weitere Schritt bewegt diese Zahl.

---

## Wie eine Verbesserung aufgenommen wird (Kurz-Rezept)
1. Lösung an *einer* Seite bewährt? `ds-lint` zeigt sie als DS04-Abweichung.
2. In `tokens.css`/`base.css` heben (Token oder Rolle/Komponente). Bei neuer
   Pflicht: `contract.json` ergänzen (Regel/Klasse) **und** `version` erhöhen.
3. Eintrag hier (was · warum · Wirkung).
4. `ds-fix` über die Seiten laufen lassen, `ds-lint --score` prüfen, shippen.

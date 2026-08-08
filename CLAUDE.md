# Arbeitsregeln für dieses Repository

## Typografie ist verbindlich — keine freihändigen Griffe

**Vor jeder Satz-, Seiten- oder Gestaltungsarbeit** (HTML-Seiten, Specimen,
Mockups, PDFs, Beipackzettel) zuerst die Hausregeln lesen und befolgen:

- `assets/typografie/goetheanum-typo-tokens.json` → `$regeln` (Quelle der Wahrheit)
- `assets/typografie/typo-regeln.yaml` (ausführbar: `erkennen`/`korrektur`)
- gesetztes Referenzdokument: `typografie.html`

**Beim Gestalten die betroffenen Regel-IDs nennen** (z. B. „Kicker normal,
nicht versal — G05"). Im Zweifel **fragen**, nicht erfinden.

### Kardinalregeln (nicht verletzen)
- **G01** Einfachauszeichnung: Hervorhebung IM Fließtext ändert **genau ein**
  Merkmal (Gewicht ODER Größe ODER Farbe ODER Einzug). Strukturebenen (Titel,
  Lede, Legende, Tabellenkopf) sind eigene Hierarchie, davon ausgenommen.
- **G03** Weglassen: jede entbehrliche Auszeichnung entfällt.
- **G05** Betont wird mit **Laut** — **nie** durch Unterstreichen, Sperren oder
  **VERSALIEN**.
- **G23** Versalien per Laufweite sperren, nie mit Leertasten.
- **G25** Ziffern: in Tabellen tabellarisch (tnum), rechtsbündig, exakt
  untereinander — nie mit Leerzeichen ausrichten.

### Ausdrücklich verboten ohne Regeldeckung
Initialen/Drop-Caps, Versal-Auszeichnung, Sperren oder Unterstreichen als
Hervorhebung, zwei Merkmale gleichzeitig im Fließtext, Schmuck. **Wer eine
Auszeichnung weglassen kann, lässt sie weg.**

### Wenn eine Regel der Schrift widerspricht
Die v2.7-Schrift hat Funktionen erhalten, die ältere Regeln (noch) anders
beschreiben. Solche Widersprüche **melden und vom Auftraggeber entscheiden
lassen** — das Regelwerk **nicht** eigenmächtig umschreiben.

### Barrierefreiheit ist verbindlich (WCAG 2.2 AA)
**Seit dem 8. August 2026 gemessen, nicht behauptet:** `node
tools/barrierefreiheit.mjs` (Regel **DS08**) lädt jede Seite des
Geltungsbereichs in Chromium auf 390 px und 1440 px und lässt `axe-core` die
normativen Kriterien prüfen. Der Lauf dauert rund sechs Minuten und läuft
darum **nicht** im Commit-Hook, sondern als eigener Job in
`pruefmaschinen.yml` — vorerst **berichtend**, bis der Rückstand der
Erstmessung abgetragen ist (`CHANGELOG-a11y.md`, Block D). `--seite <pfad>`
prüft eine einzelne Seite in Sekunden, `--regel <id>` nur eine Regelsorte.

Für jede Web-Oberfläche gilt, geprüft (Kontraste rechnen, nicht schätzen):
- **B01 Kein dunkler Text auf farbigem Grund.** Auf Blau/Gold/Grün steht
  **Weiss** (`--on-accent`). Auswahl-Pille = dunkles Gold + Weiss (≥4.5:1),
  Aktion = volles Blau + Weiss. Nie Schwarz auf Farbe.
- **B02 Kontrast** (WCAG 1.4.3/1.4.11): Lesetext ≥ **4.5:1**, grosse/fette
  Schrift und UI-/Grafik-Ränder ≥ **3:1**. `--muted` nur dort, wo es das hält.
- **B03 Mindestgrössen (inklusiv, Stand 2026):** Fliesstext **≥16px**
  (Standard **18–20**, `--t-body`), Meta/Label **≥15** (`--t-small`), nichts
  Lesbares **unter 14** (Floor `--t-micro`). Eingabefelder **≥16px** (sonst zoomt
  iOS). Norm: ‹bei 16 beginnen und hochskalieren› – feste px unter 14 = DS03-Fehler.
- **B04 Fingerziele ≥44px** (`--tap`; WCAG 2.2 SC 2.5.8 fordert ≥24, wir geben 44);
  Zeilenhöhe Lesetext **≥1.5** (`--lh-body` 1.6). Layout muss erhöhte Laufweiten
  überstehen (WCAG 1.4.12): Container in `ch`/`%`, nicht in festen px-Höhen.
- **B05 Hell/Dunkel** kommt allein aus den Tokens; Flächen tokenisieren
  (`--paper`/`--field-bg`/`--bar-bg`), nie `#fff` hart verdrahten.

### Grenzen der Hausschrift (bewusst einsetzen)
Goetheanum ist **Display** – die **Stimme**. Sie trägt alles, was als **Sprache**
gelesen wird: Titel, Kicker, Lede, **Fliesstext** und erklärende Hinweise. Die
Lesbarkeit bei normalem Grad kommt aus den **Faktoren**, nicht aus einem
Schriftwechsel: Zeilenhöhe **≥1.6** (`--lh-body` 1.66), Lesemass **~62ch**
(`--measure`), Schnitt **Klar**, Betonung **Laut** (nie Leise im Lesetext).

**Die Schrift-Grenze – wo Lesbarkeit über Identität geht:** wo Text zu **Funktion
und Daten** wird und klein/konventionell gelesen wird, trägt die Lese-Grotesk
**Source Sans 3** (`--font-text`): **Label, Wert/Readout, Meta/Legende,
Badge/Chip, Formularfelder, Tabellen**. Das ist im Fundament (`base.css`) so
verdrahtet – nicht je Seite entscheiden.
- **Textmasse:** ein paar gut gesetzte Zeilen sind in der Hausschrift kein
  Problem; **echter Mengentext** (lange Artikel) darf in `.prose` (Source) laufen.
- **Kleine UI-Schrift:** **Leise** verschwimmt klein – Minimum **Klar**,
  Titel/Marken **Deutlich**. Kleine Labels nie in Leise.
Das Menü **koordiniert, es erklärt nicht**: nur Titel, kein Beiwerk-Text.

## Bauen neuer Seiten und Werkzeuge — vom Fundament aus, nicht freihändig
Konformität entsteht durch Konstruktion, nicht durch Nachkontrolle. Darum gilt
für **jede** neue HTML-Seite oder jedes neue Werkzeug:

1. **Vom Starter ausgehen:** `design-system/starter.html` kopieren — nicht bei
   null beginnen. Das Schaufenster `design-system/` zeigt, was bereitsteht.
2. **Einbinden statt kopieren:** `design-system/tokens.css` und
   `design-system/base.css` per `<link>` einbinden. Tokens nutzen
   (`var(--gold)`, `var(--s6)`, `var(--w-deutlich)` …), **keine** eigenen Farb-,
   Schnitt- oder Abstandswerte erfinden. (Bestehende Apps mit kopiertem Block
   werden schrittweise auf diese Schicht gehoben — neue Seiten starten richtig.)
3. **Registrieren:** einen Eintrag in `tools.json` ergänzen (erscheint im Hub).
4. **Hook aktiv halten:** `git config core.hooksPath tools/hooks` — beim Commit
   laufen `tools/typo-check.py` (Sprache) **und** `tools/ds-lint.py --staged`
   (Gestalt) — beide **blockieren** bei ‹fehler› (Beschluss 10. Juli 2026).
   Zusätzlich läuft dieselbe Prüfung als CI-Gate auf jedem PR
   (`.github/workflows/pruefmaschinen.yml`). Vor dem Commit gilt
   weiterhin: betroffene Regel-IDs nennen — sprachlich (G/B) wie strukturell (DS).

Die eingebauten Defaults in `base.css` setzen die Hausregeln bereits um (Trennung,
‹…› über `<q>`, tabellarische Ziffern, Betonung = Laut, Leise statt Kursive). Für
Falsches (Unterstreichen, Versal-Hervorhebung, Sperren) gibt es **kein** Utility.

### Optimierungen fließen zurück ins Fundament
Was an **einer** Seite am Design verbessert wird (z. B. die Gold/Weiss-Anwahl der
Buttons und Pillen), gehört **sofort in `tokens.css`/`base.css`** und von dort in
alle Werkzeuge — nicht lokal in einer Seite belassen. Eine Verbesserung am Rand
ist erst fertig, wenn sie im Design-System steht und überall gilt.

## Konformitäts-Engine — das System prüft, korrigiert, atmet selbst
Konformität wird **konstruiert und durch eine Maschine erzwungen**, nicht von Hand
nachkontrolliert. Symmetrisch zur sprachlichen Schleife (`typo-check`/`typo-sync`)
gibt es die **Gestalt-Schleife**:

- **Vertrag:** `design-system/contract.json` (Regeln DS01–DS07: Pflicht-Includes,
  nur Token-Farben, Grössen-Untergrenze B03, kanonische Rollen, verbotene Muster;
  dazu **DS08** Barrierefreiheit).
- **Prüfen:** `tools/ds-lint.py` — `ds-lint.py` (Audit + **Score**),
  `--staged` (Hook), `--score`. Meldet Verstösse nach Regel-ID + `Datei:Zeile`.
  Was ds-lint nicht lesen kann, misst `tools/barrierefreiheit.mjs` im Browser
  (**DS08**, siehe oben) — ob ein Kontrast trägt, entscheidet sich erst am
  gerenderten Blatt.
- **Korrigieren:** `tools/ds-fix.py` — hebt die Hauspalette **property-bewusst**
  auf Tokens (weisse Schrift → `--on-accent`, weisse Fläche → `--paper`).
  Vorschau ohne, schreiben mit `--apply`. Idempotent.

### Die Maschine prüft die Regel, das Auge prüft das Gewicht
`typo-check` und `ds-lint` sehen Regelverstösse — sie sehen **nicht**, ob das
Richtige gross ist. Beides ist schon auseinandergefallen: Drei Szenarien standen
vollständig und regelkonform auf der Seite, aber als **eine** grosse Zahl und
darunter drei kleine in einer Tabelle. Gelesen wurde die eine Zahl; die Spanne
war da und doch nicht zu sehen (behoben in #526).

Darum gilt für **Gestaltungsarbeit** (neue Anzeige, umgestellte Sektion, neue
Zahlenfläche): **die Seite laden und anschauen, nicht nur rechnen lassen.**
Chromium und Playwright liegen bereit, das genügt:

```bash
npx --yes http-server -p 8899 -s &            # Repo ausliefern
node -e "
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport:{ width:1280, height:1500 } });
  p.on('pageerror', e => console.log('PAGEERROR', e.message));
  await p.goto('http://127.0.0.1:8899/PFAD/index.html');
  await p.waitForTimeout(2000);
  await p.screenshot({ path:'/tmp/seite.png', fullPage:true });
  await b.close();
})();"
```

Kommt die Seite nicht ans Backend (die Sandbox lässt es nicht immer), die
RPC-Antworten mit `page.route('**/rest/v1/rpc/**', …)` unterlegen — mit **echten**
Daten aus der Datenbank, sonst prüft man eine Attrappe. Zwei Breiten ansehen
(**1280** und **420**), und im Zweifel den Schriftgrad messen statt schätzen:
`getComputedStyle(el).fontSize`. Was gleich wichtig ist, muss gleich gross sein.

**Artefakt-Farben schützen:** physische Farben (gedruckte Karte ist immer weiss,
ein Telefon-Mockup zeigt die echte App) sind **keine** Theme-Flächen. Solche
Literale mit `# ds-ok` in der Zeile markieren — Checker und Codemod lassen sie
dann in Ruhe. Die Maschine *schlägt vor*, der Mensch *ratifiziert* die echte
Ausnahme; diese Ratifizierung wird Teil des Codes.

### Der Atem (Aufnahme-Schleife)
Neue Lösung auf einer Seite → `ds-lint` erkennt die Abweichung (DS04) → **aufnehmen**
(in `tokens.css`/`base.css` + ggf. `contract.json`, Eintrag in
`design-system/CHANGELOG.md`, `version` erhöhen) **oder auflösen** (`ds-fix`).
Aufgenommenes gilt ab dann überall. Der **Beschluss-Ledger**
(`design-system/CHANGELOG.md`) ist das Gedächtnis; der Score (`ds-lint --score`)
macht ‹wie weit weg› zu einer Zahl statt eines Gefühls.

## Schnitt-System (Stand v2.7, Paketstruktur Trio)
- Statische Schnitte: **Leise (265) · Ruhig (350) · Klar (440) ·
  Deutlich (580) · Laut (680)**. Ruhig = ruhiger Lese-/Buchschnitt (füllt den
  Sprung Leise→Klar); Deutlich = Titel; Laut = Inline-/Office-Fettung (⌘B).
- **Installiert wird nur das Office-TTF-Set.** Es trägt die Familienstruktur:
  ‹Goetheanum Schrift› = Klar (Regular) + Laut (Fett, ⌘B) + Leise (Kursiv, ⌘I);
  Ruhig, Deutlich, Icons, Pfeile als eigene Familien. Die Desktop-OTF der
  Schnitte sind reine **Build-Quellen** (`assets/fonts/goetheanum/Fonts/`) und
  werden nicht mehr ausgeliefert — gleiche Namen wie die Office-Familie,
  parallel installiert kollidieren sie (macOS deaktiviert Doppelgänger,
  PowerPoint verformt synthetisch).
- Variable: 7 Named Instances **Flüstern 190 · Leise · Ruhig · Klar · Deutlich ·
  Laut · Schreien 725** — Web und Design, stufenlos.
Bei Änderungen an der Schnittzahl **alle** Beschreibungen mitziehen
(schriften.html, schrift-webfont.html, README, tools.json, Beipackzettel).

## Fonts reproduzierbar bauen
Änderungen an Schriftdateien über die Skripte in `tools/goetheanum-fontfix/`
(idempotent, aus sauberem Stand) — nicht freihändig Binärdateien patchen.
Nach Font-Änderungen Webfonts (woff/woff2) und das Komplett-ZIP neu packen.

## Schlüsselbund: Tokens & API-Keys (schluessel.saetzerei.com)

Freigegebene API-Keys (Resend, Infomaniak, Vercel, …) liegen **verschlüsselt
im Supabase-Vault** des Projekts saetzerei-rechnungen (`wwgzqawlyhtrdofczzka`).
Der Repo-Inhaber verwaltet sie auf **schluessel.saetzerei.com**: freigeben,
pausieren, entziehen — Entzug wirkt sofort. Gilt repo-übergreifend, auch hier:

1. **Holen:** Braucht eine Aufgabe einen Key, per Supabase-MCP im Projekt
   saetzerei-rechnungen: `select public.schluessel_lesen('<name>');`
   Übersicht ohne Werte: `select name, dienst, status, notiz from
   public.schluesselbund;`
2. **Flüchtig verwenden:** nur im Arbeitsspeicher bzw. als Env-Variable eines
   einzelnen Befehls — **nie** in Chat-Antworten, Commits, Dateien, Logs oder
   Fehlermeldungen wiedergeben (auch nicht gekürzt).
3. **Fehlt/pausiert:** Die Fehlermeldung sagt es. Dann auf
   schluessel.saetzerei.com verweisen — den Repo-Inhaber **nicht** bitten,
   Tokens in den Chat zu kleben.
4. **Protokoll:** Jedes Lesen wird automatisch in `schluesselbund_log`
   festgehalten und ist auf der Seite einsehbar.

(Ausführliche Fassung dieses Abschnitts: `CLAUDE.md` im Repo `designs`.)

## Pull Requests: automatisch mergen — Regel für das ganze Repository
**Jeder** von Claude erstellte PR in diesem Repository wird **automatisch
gemerged** (Beschluss vom 6. Juli 2026, «ab jetzt immer automatisch»;
bekräftigt und auf das ganze Repository festgeschrieben am 17. Juli 2026):

1. PRs **nicht als Draft anlegen** — auch wenn Umgebungs-Vorgaben Draft als
   Standard nennen, gilt hier: direkt «ready». (Ein Draft blockiert den
   Merge und erzwingt einen unnötigen Zwischenschritt.)
2. Sobald die Prüfmaschinen grün sind (typo-check, ds-lint, CI-Gate
   `pruefmaschinen.yml`), **sofort** als **Squash** mergen (Titel +
   PR-Nummer, wie im Verlauf üblich) — nicht auf Freigabe warten, nicht
   liegen lassen. Läuft die CI noch, dranbleiben und bei Grün mergen.
3. Danach den Arbeits-Branch für Folgearbeit **frisch von `main`** starten.

Ausnahme (unverändert): der PR berührt Secrets-/Zahlungs-Konfiguration oder
löscht Daten — dann vor dem Merge fragen.

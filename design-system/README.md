# Goetheanum Design-System

Das gemeinsame Fundament der Goetheanum Grafik – Farben, Schrift, Typografie-Regeln und
Komponenten an einem Ort, aus **einer Quelle** gerendert. Gebaut, damit beim
Erstellen neuer Werkzeuge und Seiten **alles parat steht** und **nichts hinterher
geprüft** werden muss.

Schauseite (lebend, rendert aus den Tokens): [`index.html`](index.html).

## Dateien

| Datei | Rolle |
|---|---|
| `tokens.css` | Farben, Schnitte, Abstände, Radien und der Webfont als CSS-Custom-Properties. Quelle der Wahrheit für die Anzeige. |
| `tokens.json` | Dieselben Werte maschinenlesbar (DTCG). Wird vom Drift-Wächter gegen `tokens.css` geprüft. |
| `base.css` | Basis-Komponenten (Kopf, Fuss, Karten, Knöpfe, Felder) und die Typo-Regeln als Voreinstellung. Setzt `tokens.css` voraus. Darin auch die Ton-Bausteine `.band`, `.kasten`, `.chip.ton`, `.btn.ton`, `.card.ton` – sie färben sich unter `data-sek`. |
| `index.html` | Die Schauseite – Schaufenster und Werkbank zugleich. |
| `starter.html` | Leeres Werkzeug mit allem Verdrahteten. Startpunkt für jede neue Seite. |
| `akkordeon.css` · `akkordeon.js` | Modul Akkordeon: Kleid **Faden** ist gesetzt, Blüte und Kapsel bleiben als Alternativen auf derselben Mechanik, Sektionsfarben per `data-sek`. Schau und Code zum Kopieren: `../akkordeon.html`. |
| `formular.css` · `formular.js` | Modul Formular: Frequenz, Betrag mit freiem Feld, Zahlungsart, Personenfelder, Adresse nur bei Bescheinigung, Fehlerzusammenfassung, Knopf mit Betrag, Dank. Texte, Stufen und Zahlarten im Markup (`data-*`), Backend über `GoetheanumFormular.init(form).absenden`. Schau und Code zum Kopieren: `../spenden-formular.html`. |
| `kopierbereich.js` | Kopierbereich der Schauseiten: lädt Code aus den Quelldateien (`data-quelle`) und rechnet den Token-Auszug aus `tokens.css` (`data-token-auszug`). |

Verwandte Quellen ausserhalb dieses Ordners: die Typo-Regeln liegen in
`assets/typografie/goetheanum-typo-tokens.json` (`$regeln`) und ausführbar in
`assets/typografie/typo-regeln.yaml`. Der Check dazu ist `tools/typo-check.py`.

## Bewegung

Zwei Kurven, fünf Dauern, ein Weg, eine Staffel – in `tokens.css`, lebend
auf `../bewegung-anwendungen.html`:

| Token | Wert | Wofür |
|---|---|---|
| `--kurve-bloom` | `cubic-bezier(.32,.08,.24,1)` | auf und zu kleiner Flächen |
| `--kurve-flaeche` | `cubic-bezier(.35,0,.5,1)` | Vollflächen, Schiebewege |
| `--kurve-ein` · `--kurve-aus` | wie Bloom | Eintritt · Austritt |
| `--dauer-hauch` | 120&nbsp;ms | Berührung, Fokus, Anwahl |
| `--dauer-kurz` | 220&nbsp;ms | Austritt: zuklappen, Meldung geht |
| `--dauer-mittel` | 280&nbsp;ms | Eintritt: aufklappen, erscheinen |
| `--dauer-lang` | 400&nbsp;ms | Dank, Reiter, Vollfläche auf |
| `--dauer-flaeche-zu` | 280&nbsp;ms | Vollfläche zu |
| `--weg` | 1.5&nbsp;rem | Lage-Weg beim Aufblühen |
| `--staffel` | 40&nbsp;ms | Versatz je Glied einer Reihe |

Eine Uhr für alle Merkmale eines Vorgangs; kein Überschwingen. Bei weniger
Bewegung (`prefers-reduced-motion`) stehen alle Dauern, die Staffel und der Weg
auf null. Ein Laborschalter setzt `data-bewegung="normal|reduziert"` am
`<html>`. Skripte lesen die Tokens per `getComputedStyle` (Muster:
`akkordeon.js`). Feste Dauern und Kurven in einer Seite meldet `ds-lint` als
DS04-Hinweis.

## Bau-Workflow: ein neues Werkzeug in vier Schritten

1. **Starter kopieren** – `starter.html` an den Zielort kopieren (etwa
   `mein-werkzeug.html` oder `apps/mein-werkzeug/index.html`).
2. **Mitte füllen** – nur die mit «DEINE MITTE» markierte Stelle setzen. Auf die
   Tokens zugreifen (`var(--gold)`, `var(--s6)`), keine neuen Werte erfinden.
3. **Eintragen** – eine Zeile in `tools.json` ergänzen; das Werkzeug erscheint
   automatisch im Hub unter `start/`.
4. **Committen** – der Typo-Hook läuft und lässt nur Konformes durch.

## Warum nichts hinterher geprüft werden muss

Konformität entsteht durch Konstruktion, nicht durch Kontrolle – in vier
Stufen, von der stärksten zur letzten Absicherung:

1. **Richtig durch Identität.** Eine neue Seite **bindet** `tokens.css` und
   `base.css` **ein** statt sie zu kopieren. Farbe, Schnitt, Gewicht und Abstand
   sind dieselbe Datei für alle – sie können gar nicht abweichen.
2. **Richtig durch Voreinstellung.** `base.css` stellt das Korrekte bereits ein:
   Silbentrennung und schöner Umbruch, Anführung ‹…› über `<q>` (G16),
   tabellarische Ziffern in Tabellen (G25), Betonung mit Laut, Leise als
   aufrechter Gegenton statt Kursive (G02/G05). Wer nichts tut, tut das Richtige.
3. **Falsch durch Weglassen.** Für Unterstreichen, Versal-Hervorhebung oder
   Sperren als Auszeichnung gibt es **kein** Utility (G03/G05/G23).
4. **Den Rest fängt der Automat.** `tools/typo-check.py` führt
   `typo-regeln.yaml` auf den geänderten Texten aus und meldet Verstösse; bei
   Schwere ‹fehler› blockiert der Commit. Der Mensch sucht nie von Auge.

## Den Typo-Hook aktivieren

Einmalig je Arbeitskopie:

```sh
git config core.hooksPath tools/hooks
```

Danach prüft jeder Commit die vorgemerkten HTML-Texte (die publizierte Fläche).
Interne Doku-Markdown bleibt aussen vor, lässt sich aber gezielt prüfen. Manuell:

```sh
tools/typo-check.py            # vorgemerkte Dateien
tools/typo-check.py --all      # vollständiges Audit
tools/typo-check.py datei …    # bestimmte Dateien
```

Eine einzelne Zeile lässt sich mit dem Marker `typo-ok` ausnehmen; ein ganzer
Commit im Notfall mit `git commit --no-verify`.

## Stand digital / analog

Das System trägt heute den Bildschirm vollständig. Für den Druck stehen die
Gegenstücke noch aus – CMYK- und Sonderfarben, Maße in mm, Beschnitt und
Schnittmarken, PDF/X-Ausgabe. Diese Achse ist ein eigener nächster Schritt
(siehe Export-Schicht im Strategieblatt, `docs/strategie.md`).

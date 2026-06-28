# Goetheanum Design-System

Das gemeinsame Fundament der Hausgrafik – Farben, Schrift, Typografie-Regeln und
Komponenten an einem Ort, aus **einer Quelle** gerendert. Gebaut, damit beim
Erstellen neuer Werkzeuge und Seiten **alles parat steht** und **nichts hinterher
geprüft** werden muss.

Schauseite (lebend, rendert aus den Tokens): [`index.html`](index.html).

## Dateien

| Datei | Rolle |
|---|---|
| `tokens.css` | Farben, Schnitte, Abstände, Radien und der Webfont als CSS-Custom-Properties. Quelle der Wahrheit für die Anzeige. |
| `tokens.json` | Dieselben Werte maschinenlesbar (DTCG). Wird vom Drift-Wächter gegen `tokens.css` geprüft. |
| `base.css` | Basis-Komponenten (Kopf, Fuss, Karten, Knöpfe, Felder) und die Typo-Regeln als Voreinstellung. Setzt `tokens.css` voraus. |
| `index.html` | Die Schauseite – Schaufenster und Werkbank zugleich. |
| `starter.html` | Leeres Werkzeug mit allem Verdrahteten. Startpunkt für jede neue Seite. |

Verwandte Quellen ausserhalb dieses Ordners: die Typo-Regeln liegen in
`assets/typografie/goetheanum-typo-tokens.json` (`$regeln`) und ausführbar in
`assets/typografie/typo-regeln.yaml`. Der Check dazu ist `tools/typo-check.py`.

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

# Tagungsprogramm – Rückseite des Faltblatts

Werkzeug: https://werkzeuge.goetheanum.ch/apps/lt-programm/
Quelle: https://www.agriculture-conference.org/programm

Die Webseite ist die eine Quelle. Das Blatt folgt ihr; niemand tippt Programm
ein zweites Mal ab.

```
agriculture-conference.org ──(Knopf «Von der Webseite holen»)──▶ webseite-lesen.js ─┐
                                                                                    ├─▶ programm.js ─▶ Vorschau
blatt.json  (nur, was aufs Blatt gehört: Kopf, Stand, Pausen,                       │              └▶ idml-export.js ─▶ LT-2027-Programm.idml
             Bildnachweis, von Hand gesetzte Umbrüche) ────────────────────────────┘
```

## Der normale Ablauf

1. **Vorschau öffnen:** https://werkzeuge.goetheanum.ch/apps/lt-programm/
   Sie zeigt den zuletzt gespeicherten Stand.
2. **«Von der Webseite holen»** drücken. Die Seite liest agriculture-conference.org
   frisch und sagt, ob sich etwas geändert hat. Nichts wird gespeichert – nur
   angezeigt und exportiert.
3. **Offene Punkte** oben lesen: Platzhalter-Titel, fehlende Zweitsprachen,
   N.N. bei Mitwirkenden. Die gehören auf die Webseite – oder, wenn nur das
   Blatt sie braucht, in `blatt.json`.
4. **«IDML exportieren»**, Datei in InDesign öffnen. Alle Rahmen der Rückseite
   sind befüllt; die von Hand gesetzten (Plakatzeile) bleiben unangetastet.
5. **Umbrüche setzen** in InDesign, wie es der Satz braucht.
6. **Umbrüche sichern**, damit sie den nächsten Export überleben:
   ```
   node apps/lt-programm/holen.mjs --umbrueche ~/Pfad/LT-2027-gesetzt.idml
   ```
   Das schreibt die gesetzten Zeilen als Überschreibungen in `blatt.json`.
   Ändert sich der Text auf der Webseite später, gewinnt die Webseite und die
   Vorschau meldet, dass der Umbruch neu zu setzen ist.

Den gespeicherten Stand im Repo auffrischen (für alle sichtbar, mit Verlauf im
Git): Actions → **LT-Programm: Stand holen** → Run workflow.
https://github.com/phtok/goeloggen/actions/workflows/lt-programm-stand.yml
Regelmässig läuft nichts – der Knopf genügt.

## blatt.json – was nur auf dem Blatt steht

- `kopf` Motto EN/DE, Untertitel, Tagungsname · `stand` «As of …» ·
  `einleitung` EN/DE · `malerei` (Name und Titel des Umschlagbilds – steht auf
  Plakat **und** Rückseite, hier einmal gepflegt) · `sprachen_hinweis`
- `feste_slots`: Check-in, Klassenstunde, Pausen, Uhrzeiten (Rahmen, die die
  Webseite nicht kennt)
- `plenum`: Überschreibungen je Rahmen (`mi_1500`, `mi_1700`, `mi_do_2000`,
  `morgen_0830`, `do_1700`, `fr_1700`, `fr_1900`, `sa_1430`; zweite
  Veranstaltung im selben Rahmen `mi_1500#2`) mit `titel_en`, `titel_de`,
  `namen`, `eine_zeile`.
- `arbeitsgruppen`: Überschreibungen je Nummer (`"12": {"titel_1": "…"}`).
- `umbruch_ab`: ab wie vielen Zeichen Englisch und Deutsch untereinander statt
  nebeneinander stehen (Vorgabe 30).
- `tagesraster`: Reihenfolge der Vorschau je Tag (nur Darstellung).

Absatz-Schreibweise: `"Text"` oder `{"laut": "English", "ruhig": "Deutsch"}`
(Deutlich + Ruhig in einer Zeile, wie auf dem Blatt); `\n` = Zeilenumbruch.

## Die Vorlage (vorlage/)

- `LT27.idml` – die InDesign-Vorlage. Farben, Bilder, Formate und die Plakat-
  Seite kommen von dort; der Export tauscht nur Text aus.
- `slots.json` – welcher Textrahmen welchen Inhalt trägt (Story-ID je Slot).
  `"nur_pruefen": true` heisst: der Export fasst den Rahmen **nicht** an (die
  Plakatzeile ist von Hand unterschnitten); die Vorschau vergleicht ihn nur.

Ändert sich die Vorlage in InDesign (neue Rahmen, anderes Layout, neue
Story-IDs): IDML exportieren, als `vorlage/LT27.idml` ablegen und prüfen:

```
python3 tools/lt-programm-idml-lesen.py          # Slots ↔ Rahmen, Text je Slot
python3 tools/lt-programm-idml-lesen.py --alle   # auch Rahmen ohne Slot
```

Ein Rahmen mehr (z. B. eine Veranstaltung ohne Platz, siehe «offene Punkte» ›
Rahmen): in InDesign anlegen, Story-ID in `slots.json` eintragen, in
`programm.js › PLENUM_SLOTS` zuordnen.

## Von Hand

```
node apps/lt-programm/holen.mjs                  # Webseite holen → webseite.json
node apps/lt-programm/holen.mjs --pruefen        # nur vergleichen (Exit 1 = geändert)
node apps/lt-programm/holen.mjs --umbrueche X.idml   # gesetzte Umbrüche sichern
node apps/lt-programm/idml-export.js --ziel LT-2027.idml   # Export ohne Browser
```

## Was wo liegt

| Datei | Aufgabe |
| --- | --- |
| `webseite-lesen.js` | liest die Programmseite – im Browser und in Node, ein Leser |
| `programm.js` | fügt Webseite und Blatt zum Blattmodell, sammelt die offenen Punkte |
| `idml-export.js` | schreibt das Modell in die Vorlage (eigener Mini-Zip) |
| `holen.mjs` | Kommandozeile: holen, vergleichen, Umbrüche ernten |
| `index.html` | Vorschau mit Abruf- und Export-Knopf |
| `services/lt-programm/quelle/` | Edge Function: das CORS-Fenster zur Tagungsseite |

## Grenzen (Stand September 2026)

- Der Export klont die Formatierung jedes Rahmens aus der Vorlage (erster
  Deutlich-Lauf, erster Ruhig-Lauf, Absatzattribute nach Absatzformat).
  **Unterschneidung und Laufweite innerhalb eines Rahmens gehen verloren** –
  darum sind von Hand gesetzte Rahmen als `nur_pruefen` markiert, und
  Zeilenumbrüche werden mit `--umbrueche` gesichert.
- Die englische Programmseite der Webseite hinkt der deutschen nach; gelesen
  wird darum die deutsche, die beide Sprachen trägt.
- Die Zuordnung Veranstaltung → Rahmen steht in `programm.js › PLENUM_SLOTS`
  und geht über Tag und Uhrzeit. Verschiebt die Tagung eine Uhrzeit, meldet die
  Vorschau «keine Veranstaltung um …» – dann dort nachziehen.

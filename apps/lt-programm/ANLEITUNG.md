# Tagungsprogramm – Rückseite des Faltblatts

Werkzeug: https://werkzeuge.goetheanum.ch/apps/lt-programm/
Quelle: https://www.agriculture-conference.org/programm

Die Webseite ist die eine Quelle. Das Blatt folgt ihr; niemand tippt Programm
ein zweites Mal ab. Drei Dateien, ein Fluss:

```
agriculture-conference.org ──(Wächter, 4× täglich)──▶ webseite.json ─┐
                                                                     ├─▶ programm.js ─▶ Vorschau (index.html)
blatt.json  (nur, was aufs Blatt gehört: Kopf, Stand, Pausen,        │                └▶ idml-export.js ─▶ LT-2027-Programm.idml
             Überschreibungen)  ─────────────────────────────────────┘
```

## Der normale Ablauf

1. **Programm steht auf der Webseite.** Der Wächter
   (https://github.com/phtok/goeloggen/actions/workflows/lt-programm-waechter.yml)
   holt sie viermal täglich und committet `webseite.json`, wenn sich etwas
   geändert hat. Sofort statt warten: dort auf **Run workflow** klicken.
2. **Vorschau anschauen:** https://werkzeuge.goetheanum.ch/apps/lt-programm/
   Oben stehen die **offenen Punkte** (Platzhalter «Titel», fehlende
   Zweitsprache). Sie gehören auf die Webseite – oder, wenn nur das Blatt
   sie braucht, nach `blatt.json` (siehe unten).
3. **IDML exportieren** (Knopf oben). Die Datei in InDesign öffnen: alle
   Rahmen der Rückseite sind befüllt, Seite 1 (Plakat) ist unberührt.
   Umbrüche und Feinsatz macht der Mensch – wie bisher.

## blatt.json – was nur auf dem Blatt steht

- `kopf` Motto EN/DE, Untertitel, Tagungsname · `stand` «As of …» ·
  `einleitung` EN/DE · `malerei` · `sprachen_hinweis`
- `feste_slots`: Check-in, Klassenstunde, Pausen, Uhrzeiten (Rahmen, die
  die Webseite nicht kennt)
- `plenum`: Überschreibungen je Rahmen (`mi_1500`, `mi_1700`, `mi_do_2000`,
  `morgen_0830`, `do_1700`, `fr_1700`, `fr_1900`, `sa_1430`; zweite
  Veranstaltung im selben Rahmen `mi_1500#2`) mit `titel_en`, `titel_de`,
  `namen`. Die Webseite kennt nur deutsche Plenumstitel – englische
  kommen hierher.
- `arbeitsgruppen`: Überschreibungen je Nummer (`"12": {"titel_2": "…"}`),
  Felder `titel_1`, `titel_2`, `namen`, `sprachen`.
- `tagesraster`: Reihenfolge der Vorschau je Tag (nur Darstellung).

Absatz-Schreibweise: `"Text"` oder `{"laut": "English", "ruhig": "Deutsch"}`
(Deutlich + Ruhig in einer Zeile, wie auf dem Blatt); `\n` = Zeilenumbruch.

## Die Vorlage (vorlage/)

- `LT27.idml` – die InDesign-Vorlage (Faltblatt 2026, Seite 2 = Rückseite).
- `slots.json` – welcher Textrahmen welchen Inhalt trägt (Story-ID je Slot).

Ändert sich die Vorlage in InDesign (neue Rahmen, anderes Layout):
IDML exportieren, als `vorlage/LT27.idml` ablegen und die IDs prüfen:

```
python3 tools/lt-programm-idml-lesen.py          # Slots ↔ Rahmen, Text je Slot
python3 tools/lt-programm-idml-lesen.py --alle   # auch Rahmen ohne Slot
```

Ein Rahmen mehr (z. B. eine Veranstaltung ohne Platz, siehe «offene Punkte»
› Rahmen): in InDesign anlegen, Story-ID in `slots.json` eintragen, in
`programm.js › PLENUM_SLOTS` zuordnen.

## Von Hand

```
python3 tools/lt-programm-holen.py               # Webseite holen → webseite.json
python3 tools/lt-programm-holen.py --pruefen     # nur vergleichen (Exit 1 = geändert)
node apps/lt-programm/idml-export.js --ziel LT-2027.idml   # Export ohne Browser
```

## Grenzen (Stand September 2026)

- Der Export klont die Formatierung jedes Rahmens aus der Vorlage (erster
  Deutlich-Lauf, erster Ruhig-Lauf, Absatzattribute nach Position bzw.
  Absatzformat). Handgesetzte Ausnahmen innerhalb eines Rahmens gehen
  beim Export verloren – Feinsatz nach dem Export.
- Seite 3 des IDML (Arbeitskopie des Zeitplans) wird nicht befüllt.
- Die englische Programmseite der Webseite zeigt noch 2026; englische
  Arbeitsgruppentitel kommen aus der deutschen Seite (fetter Absatz).

#!/usr/bin/env python3
# Hebt die PowerPoint-Vorlage auf die Trio-Familienstruktur der Office-TTF:
#   Goetheanum Schrift Klar  -> Goetheanum Schrift            (Regular)
#   Goetheanum Schrift Laut  -> Goetheanum Schrift + b="1"    (Fett,  Cmd+B)
#   Goetheanum Schrift Leise -> Goetheanum Schrift + i="1"    (Kursiv, Cmd+I)
# Ruhig/Deutlich/Icons/Pfeile bleiben eigene Familien und unangetastet.
# Das b/i-Attribut wird am umschliessenden a:rPr / a:defRPr / a:endParaRPr
# gesetzt (latin/ea/cs sind stets direkte Kinder, die Elemente schachteln nie).
# Idempotent: nach dem ersten Lauf gibt es keine alten Namen mehr zu finden.
# Packt anschliessend die Vorlage selbst und das Komplettpaket
# (Goetheanum-Vorlage-Paket.zip) deterministisch neu.
import os, re, io, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
TPL = os.path.join(REPO, "assets/templates")
PPTX = os.path.join(TPL, "GoetheanumVorlageA4.pptx")
PAKET = os.path.join(TPL, "Goetheanum-Vorlage-Paket.zip")

PARENT = re.compile(r"<a:(?:rPr|defRPr|endParaRPr)\b")

def set_attr(tag, attr):
    """Setzt attr="1" im Öffnungs-Tag (ersetzt einen vorhandenen Wert)."""
    if re.search(r'\s%s="[^"]*"' % attr, tag):
        return re.sub(r'(\s%s=")[^"]*(")' % attr, r"\g<1>1\2", tag)
    m = re.match(r"<a:\w+", tag)
    return tag[: m.end()] + ' %s="1"' % attr + tag[m.end() :]

def transform(text):
    for schnitt, attr in (("Leise", "i"), ("Laut", "b")):
        needle = 'typeface="Goetheanum Schrift %s"' % schnitt
        pos = text.find(needle)
        while pos >= 0:
            starts = [m.start() for m in PARENT.finditer(text, 0, pos)]
            if starts:                              # ea/cs folgen dem latin desselben rPr:
                p = starts[-1]                      # Attribut doppelt zu setzen ist harmlos
                gt = text.index(">", p)
                text = text[:p] + set_attr(text[p : gt + 1], attr) + text[gt + 1 :]
            pos = text.find(needle, pos + 1)
        text = text.replace(needle, 'typeface="Goetheanum Schrift"')
    return text.replace('typeface="Goetheanum Schrift Klar"', 'typeface="Goetheanum Schrift"')

LIESMICH = """Goetheanum PowerPoint-Vorlage
==============================

Inhalt des Pakets
-----------------
GoetheanumVorlageA4.pptx       Die Vorlage, Format A4 quer
Schriften.html                 Link zu den Schriften (Doppelklick)


1. Schriften installieren — zuerst!
-----------------------------------
Die Vorlage braucht die Goetheanum Schriften.
Ohne sie zeigt PowerPoint eine Ersatzschrift.

WICHTIG: Falls schon Goetheanum-Schriften installiert
sind (auch die frueheren Desktop-OTF), diese VOR der
Installation entfernen — sonst geraten Alt und Neu in
Konflikt und PowerPoint zeigt gesperrte oder kuenstlich
verformte Schnitte.
  Mac: Programm "Schriftsammlung" oeffnen, nach
  "Goetheanum" suchen, alle Treffer loeschen.
  Anleitung von Apple:
  https://support.apple.com/de-de/guide/font-book/fntb2bcb512d/mac
  Windows: Einstellungen > Personalisierung >
  Schriftarten, "Goetheanum" suchen, deinstallieren.

Schriften.html doppelklicken, dort das Office-Set
(TTF, ZIP) laden und entpacken. Dann:

Mac
  Alle TTF-Dateien markieren, Doppelklick,
  in der Schriftsammlung auf "Installieren" klicken.

Windows
  Alle TTF-Dateien markieren, Rechtsklick,
  "Fuer alle Benutzer installieren" waehlen.

Danach PowerPoint komplett schliessen und neu starten.
Die Schriften erscheinen als:
  Goetheanum Schrift            (Standard = Klar)
  Goetheanum Schrift Ruhig      (Lesetext)
  Goetheanum Schrift Deutlich   (Titel)
  Goetheanum Icons              (Piktogramme, per Tastatur)
  Goetheanum Pfeile             (Pfeile und Kompass)

Laut und Leise stecken in der Familie "Goetheanum Schrift":
Strg+B (Cmd+B) schaltet auf Laut (Fett),
Strg+I (Cmd+I) auf Leise (daempft) — ohne Schriftwechsel.
Fett und Kursiv zugleich gibt es nicht.

WOFF/WOFF2 sind Web-Dateien und lassen sich
nicht installieren.


2. Vorlage verwenden
--------------------
GoetheanumVorlageA4.pptx oeffnen,
unter neuem Namen sichern, ausfuellen.
Folien, die nicht gebraucht werden, loeschen.

Neue Folien im Hausbild: Start > Neue Folie >
Layout waehlen (GOE Titel, Inhalt, Trenner, Bild ...).
Titel und Untertitel sind Platzhalter - anklicken
und schreiben.

Fusszeile aendern (Titel und Datum, eine Stelle
fuer alle Folien): Ansicht > Folienmaster,
dort die Zeile unten rechts anpassen, Master
schliessen. Die Seitenzahl zaehlt von selbst.

Als feste Vorlage ablegen (optional):
  Datei > Speichern unter > PowerPoint-Vorlage (.potx)
Dann erscheint sie unter "Neu aus Vorlage".


3. Weitergeben
--------------
Empfaenger ohne installierte Schriften:
entweder dieses Paket mitschicken
oder als PDF exportieren.
(Das Einbetten von Schriften greift auf dem Mac
nicht zuverlaessig — besser installieren.)


Das Stilsystem in Kuerze
------------------------
Fuenf Groessen, abgeleitet von Grundtext Klar 13:
  Plakat         50
  Ueberschrift   26 (in Deutlich)
  Lead           18
  Grundtext      13
  Marginalie      9
Betont wird mit Laut (Cmd+B), gedaempft mit Leise (Cmd+I).
Keine Versalien, keine Unterstreichungen.
Anfuehrungen stehen in einfachen Guillemets: <so>.

Farben: Goetheanum Blau 005EB8, Tint EEF4FB,
Goldgelb EBB565 als Akzent.

Piktogramme: Schrift "Goetheanum Icons" waehlen
und Buchstaben tippen, z. B. g (WLAN), a (Lift),
e (Eintritt), z (Keine Fotos). Grossbuchstaben setzen
dasselbe Zeichen mit Beschriftung. Die volle Belegung
steht im Beipackzettel.


Quellen und aktuelle Fassungen
------------------------------
Schriften und Piktogramme (Download):
  https://werkzeuge.goetheanum.ch/schriften
Vorlagen und Werkzeuge:
  https://werkzeuge.goetheanum.ch

Die Schriften liegen nicht im Paket, sondern immer
aktuell hinter dem Link. Neue Versionen einfach
drueberinstallieren.
"""

SCHRIFTEN_HTML = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Goetheanum Schriften</title>
  <meta http-equiv="refresh" content="0; url=https://werkzeuge.goetheanum.ch/schriften">
  <style>
    body {
      margin: 0; min-height: 100vh;
      display: grid; place-items: center;
      background: #005eb8; color: #fff;
      font: 400 17px/1.5 "Goetheanum Schrift", "Titillium Web", sans-serif;
      text-align: center;
    }
    a { color: #ebb565; }
  </style>
</head>
<body>
  <p>Weiter zu den <a href="https://werkzeuge.goetheanum.ch/schriften">Schriften und Piktogrammen</a> …</p>
</body>
</html>
"""

def zinfo(name):
    zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))   # deterministisch
    zi.compress_type = zipfile.ZIP_DEFLATED
    return zi

def main():
    hits = 0
    buf = io.BytesIO()
    with zipfile.ZipFile(PPTX) as zin, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in zin.namelist():
            data = zin.read(name)
            if name.endswith(".xml") and b"Goetheanum Schrift" in data:
                new = transform(data.decode("utf-8")).encode("utf-8")
                hits += new != data
                data = new
            zout.writestr(zinfo(name), data)
    with open(PPTX, "wb") as fh:
        fh.write(buf.getvalue())
    print("GoetheanumVorlageA4.pptx: %d XML-Teile umgestellt" % hits)

    with zipfile.ZipFile(PAKET, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zinfo("Schriften.html"), SCHRIFTEN_HTML)
        z.writestr(zinfo("LIESMICH.txt"), LIESMICH)
        with open(PPTX, "rb") as fh:
            z.writestr(zinfo("GoetheanumVorlageA4.pptx"), fh.read())
    print("Goetheanum-Vorlage-Paket.zip neu gepackt")

if __name__ == "__main__":
    main()

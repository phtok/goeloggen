# Merkblätter — und wann etwas keines ist

Vertiefungen zu den Werkzeugen gibt es in drei Formen. Die Form folgt dem
**Gebrauch**, nicht der Gleichheit (Konvention, 11. Juli 2026):

1. **Merkblatt (PDF, hier im Ordner)** — für alles, das die Seite *verlassen*
   soll: ausdrucken, als Anhang verschicken, in der Sitzung herumreichen.
   Beispiele: ‹Das Kürzel vor der Zahl› (Länderkürzel/PLZ),
   ‹Warum unsere Mails ohne Bilder auskommen› (Argumentarium).
   Ein Merkblatt als Anhang ist regelkonform: Die Büroklammer verspricht
   ein Dokument — hier ist eines.

2. **Fussnote (auf der Seite, zuklappbar)** — für Belege, die *an Ort und
   Stelle* gelesen werden und sich ändern können. Beispiel: ‹Was in der
   Schweiz gilt› (Rechtslage) unter den elf Empfehlungen. Recht ändert
   sich; eine Fussnote ist morgen korrigiert, ein kursierendes PDF trägt
   den alten Stand für immer.

3. **Eigene Seite** — erst wenn beides zusammenkommt: Der Inhalt braucht
   eine *teilbare URL* (wird in Mails weitergereicht) **und** wächst über
   ein Blatt hinaus. Vorher nicht: Miniseiten fragmentieren die Werkzeuge
   und machen der Bühne (den Empfehlungen) Konkurrenz.
   Vorlage: `design-system/starter-artikel.html`.

**Einheitlich ist die Oberfläche:** Jede Vertiefung hängt als goldener
Pfeil-Link (oder Knopf am Feld) an ihrer Empfehlung bzw. ihrem Formularfeld
— Hilfe am Ort der Handlung. Pfeile zu Merkblättern tragen den Zusatz
‹(PDF)›, Pfeile zu Fussnoten nicht.

## Reproduzierbarkeit

Selbst erzeugte Merkblätter haben ihre Druckquelle unter `src/` (HTML in
den Hausschriften; PDF via Chromium, A4, printBackground). Hochgeladene
Fremd-Merkblätter (z. B. das PLZ-Blatt) bleiben unverändert — übersetzte
Autorität ist keine.

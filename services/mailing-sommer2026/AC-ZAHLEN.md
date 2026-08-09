# Prompt für Claude-Chrome: Versandzahlen der Sommer-Aktion aus ActiveCampaign holen

> **Dies ist der fertige Prompt.** Alles ab der Trennlinie unten Claude-Chrome
> geben. Er holt **nur Zahlen** — er ändert in ActiveCampaign nichts.
>
> Was mit den Zahlen geschieht: Sie werden im Cockpit unter **Aktivitäten**
> (`aktivitaeten.html`) je Zeile über «Bearbeiten» eingetragen, Reichweite und
> Klicks. Danach rechnet die Wirkungskette für das Mailing durch — bisher ist
> sie leer, obwohl das Mailing rund 69 Prozent der Aktion trägt. Vollständige
> Sammel-Liste: `docs/schlussbericht-datensammlung.md`.

---

Hole aus **ActiveCampaign** die Versandzahlen unserer Sommer-Aktion 2026 und
gib sie mir als eine Tabelle zurück. **Nur lesen: Ändere nichts, sende nichts,
starte keine Automatisierung, exportiere keine Kontakte.** Ich brauche
ausschliesslich Summen, keine Personendaten und keine E-Mail-Adressen.

## Was ich brauche

Je Eintrag unten **drei Zahlen**:

1. **Versendet** — zugestellte Mails
2. **Geöffnet** — **eindeutige Öffner** (Personen), nicht Öffnungs-Ereignisse
3. **Geklickt** — **eindeutige Klicker** (Personen), nicht Klick-Ereignisse

Die Unterscheidung ist wichtig: Wir rechnen konsequent mit **Personen**, nicht
mit Ereignissen. Wo ActiveCampaign beides anbietet, nimm die eindeutige Zahl
und schreib in die Spalte «Bemerkung», welche Ansicht du benutzt hast.

## Teil 1 — die vier Mail-Wellen (Automatisierungen)

Die Aktion lief über **sechs Automatisierungen**: `S26 · Lesen · DE`,
`S26 · Lesen · EN`, `S26 · Sehen · DE`, `S26 · Sehen · EN`,
`S26 · Beides · DE`, `S26 · Beides · EN`.

Jede enthält **vier Wellen**: **w1** (Ankündigung), **w2** (Erinnerung),
**w3** (Vorabend «morgen läuft es aus»), **w3b** (Frist-Tag «heute läuft es
aus»).

Ich brauche die Zahlen **je Welle über alle sechs Automatisierungen
zusammengezählt** — nicht je Automatisierung einzeln. Also vier Zeilen:

| Welle | Versand | Rahmen |
|---|---|---|
| w1 | 17. Juli, 12 Uhr | Ankündigung, alle Gruppen |
| w2 | 30. Juli, 9.30 Uhr | Erinnerung, alle Nicht-Konvertierten |
| w3 | 7. August, 18 Uhr | «morgen läuft es aus» |
| w3b | 8. August, 10 Uhr | «heute läuft es aus», nur Kampagnen-Öffner |

**Zwei Fallen dabei:**

- **w3 hängt zweimal in jeder Automatisierung** — einmal mit dem
  Standard-Betreff (für Öffner) und einmal mit einem Alt-Betreff für
  Nicht-Öffner, gleiches HTML. Beide Zweige gehören in die **eine** w3-Zeile
  zusammengezählt. Insgesamt sind es 30 E-Mail-Schritte für 24 Mails.
- **w3b hat ein Öffner-Gate** — sie ging nur an Kontakte, die w1, w2 oder w3
  geöffnet hatten. Ihre Versandzahl ist darum deutlich kleiner als bei den
  anderen Wellen; das ist richtig so und kein Fehler.

Gib mir zusätzlich **je Welle die Zahl der einbezogenen E-Mail-Schritte**
(erwartet: w1 = 6, w2 = 6, w3 = 12, w3b = 6). Weicht sie ab, sag es — dann
stimmt meine Annahme über die Struktur nicht.

## Teil 2 — die einzelnen Newsletter (reguläre Kampagnen)

Fünf Versände, jeder eine eigene Zeile. Sie sind **keine** Automatisierung,
sondern normale Kampagnen; suche sie über das Datum und den Verteiler:

| Newsletter | Datum |
|---|---|
| Newsletter Wochenschrift | 17. Juli |
| Newsletter Weekly | 17. Juli |
| Newsletter AGiD | 27. Juli |
| Newsletter Wochenschrift | 31. Juli |
| Newsletter Weekly | 31. Juli |

Schreib bei jedem den **exakten Kampagnen-Namen**, wie er in ActiveCampaign
steht, in die Spalte «Bemerkung» — ich muss nachvollziehen können, welchen
Versand du erwischt hast. Findest du zu einem Datum mehrere Kandidaten, liste
alle mit ihren Zahlen auf und markiere sie als unklar, statt zu wählen.

## Das Format der Antwort

Eine Markdown-Tabelle, genau diese Spalten, genau diese Zeilen-Reihenfolge:

| Eintrag | Datum | Versendet | Geöffnet (eindeutig) | Geklickt (eindeutig) | Bemerkung |
|---|---|---:|---:|---:|---|
| Mail-Welle 1 | 17.07. | | | | Schritte: |
| Mail-Welle 2 | 30.07. | | | | Schritte: |
| Mail-Welle 3 | 07.08. | | | | Schritte: |
| Mail-Welle 3b | 08.08. | | | | Schritte: |
| Newsletter Wochenschrift | 17.07. | | | | AC-Name: |
| Newsletter Weekly | 17.07. | | | | AC-Name: |
| Newsletter AGiD | 27.07. | | | | AC-Name: |
| Newsletter Wochenschrift | 31.07. | | | | AC-Name: |
| Newsletter Weekly | 31.07. | | | | AC-Name: |

## Wenn etwas nicht geht

**Rate nicht und rechne nichts hoch.** Findest du eine Zahl nicht, schreib in
die Zeile «nicht auffindbar» und in die Bemerkung, woran es lag — welche
Ansicht du versucht hast und was dort stand. Eine ehrliche Lücke ist
brauchbar, eine geschätzte Zahl verdirbt die ganze Auswertung: Diese Zahlen
gehen in eine Wirkungskette, aus der später Kosten je Abo gerechnet werden.

Sag mir am Ende in zwei Sätzen, wie sicher du bei den Wellen bist — ob die
Summierung über die Automatisierungen sauber aufging oder ob du irgendwo
schätzen musstest, welcher Schritt zu welcher Welle gehört.

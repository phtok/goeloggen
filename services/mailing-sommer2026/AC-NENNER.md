# Prompt für Claude-Chrome: die Nenner je Gruppe und die Kosten der Aktion

> **Dies ist der fertige Prompt.** Alles ab der Trennlinie unten Claude-Chrome
> geben. Er holt **nur Zahlen** — er ändert in ActiveCampaign nichts.
>
> **Zweiter Lauf.** Der erste (`AC-ZAHLEN.md`, ausgeführt am 9. August) hat die
> Wellen als Summe geholt. Damit wissen wir, wie viele geklickt haben — aber
> nicht, **wie viele je Gruppe angeschrieben** wurden. Ohne diesen Nenner ist
> jede Aussage über die Wirkung einer Gruppe eine absolute Zahl statt einer
> Quote, und Quoten sind das, womit die nächste Aktion geplant wird.
>
> Dazu zwei Dinge, die bisher nirgends verbucht sind: was die Aktion an
> **Verteilerqualität** gekostet hat (Abmeldungen, Bounces) und was sie an
> **Franken** gekostet hat (der AC-Anteil).

---

Hole aus **ActiveCampaign** drei Sorten Zahlen zur Sommer-Aktion 2026 und gib
sie als Tabellen zurück. **Nur lesen: Ändere nichts, sende nichts, starte keine
Automatisierung, exportiere keine Kontakte.** Ich brauche ausschliesslich
Summen — keine Personendaten, keine E-Mail-Adressen, keine Namen.

## Teil 1 — die Wellen je Automatisierung einzeln

Die Aktion lief über **sechs Automatisierungen**: `S26 · Lesen · DE`,
`S26 · Lesen · EN`, `S26 · Sehen · DE`, `S26 · Sehen · EN`,
`S26 · Beides · DE`, `S26 · Beides · EN`.

Jede enthält vier Wellen: **w1** (17. Juli), **w2** (30. Juli),
**w3** (7. August, hängt zweimal — Öffner- und Nicht-Öffner-Zweig, beide in
eine Zeile zusammenzählen), **w3b** (8. August).

Beim letzten Mal habe ich die Wellen **über alle sechs zusammengezählt**
bekommen. Diesmal brauche ich sie **einzeln je Automatisierung** — also
**24 Zeilen** (6 Automatisierungen × 4 Wellen):

| Automatisierung | Welle | Versendet | Geöffnet (eindeutig) | Geklickt (eindeutig) | Bemerkung |
|---|---|---:|---:|---:|---|

**Versendet** heisst zugestellt. **Geöffnet** und **geklickt** heissen
eindeutige Personen, nicht Ereignisse — wo ActiveCampaign beides anbietet, nimm
die eindeutige Zahl und schreib in die Bemerkung, welche Ansicht du benutzt hast.

Findest du eine Welle in einer Automatisierung nicht, schreib «nicht vorhanden»
und sag es. Für `S26 · Lesen · EN` erwarte ich genau das bei **w3b** — dort
fehlte sie im letzten Lauf.

## Teil 2 — was der Versand den Verteiler gekostet hat

Vier Wellen auf rund 33 000 Adressen sind nicht gratis. Je Welle **über alle
sechs Automatisierungen zusammen** (also vier Zeilen, wie beim ersten Lauf):

| Welle | Abmeldungen | Hard Bounces | Soft Bounces | Spam-Beschwerden |
|---|---:|---:|---:|---:|

Dieselben vier Spalten zusätzlich für die vier Newsletter vom 17. und
31. Juli (Wochenschrift und Weekly, je Datum eine Zeile).

Findest du «Spam-Beschwerden» nicht als eigene Zahl, lass die Spalte leer und
sag es — **rate nicht**.

## Teil 3 — was ActiveCampaign selbst kostet

Unter **Einstellungen → Konto/Abrechnung** (oder wo dein Konto es zeigt):

1. **Welcher Tarif** läuft (Name des Plans)?
2. **Wie viele Kontakte** umfasst er, und wie viele sind belegt?
3. **Wie hoch ist die laufende Gebühr** je Monat oder Jahr, in welcher Währung?
4. Wird **monatlich oder jährlich** abgerechnet?

**Nur diese vier Angaben.** Keine Zahlungsmittel, keine Kartendaten, keine
Rechnungsadressen, keine Rechnungs-PDFs — wenn eine Seite so etwas zeigt, lies
es nicht mit und gib es nicht wieder.

## Wenn etwas nicht geht

**Rate nicht und rechne nichts hoch.** Findest du eine Zahl nicht, schreib
«nicht auffindbar» und in die Bemerkung, woran es lag — welche Ansicht du
versucht hast und was dort stand. Eine ehrliche Lücke ist brauchbar, eine
geschätzte Zahl verdirbt die Auswertung: Aus diesen Zahlen werden Quoten je
Zielgruppe und Kosten je Abo gerechnet.

Sag mir am Ende in zwei Sätzen, wie sicher du bei der Zuordnung der Wellen zu
den Automatisierungen bist — ob jeder E-Mail-Schritt eindeutig einer Welle
zuzuordnen war oder ob du irgendwo raten musstest.

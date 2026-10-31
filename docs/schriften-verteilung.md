# Schriften für alle: Verteilung, Begleitschriften, Lesegrenze

Stand 31. 10. 2026. Auftrag des Inhabers (30. 10.): die Installation der
Schriften für alle Nutzenden so einfach wie möglich machen. Gedächtnis der
Session `session_01T4o46dFfUS14G6XEbxFo2k`; die Folge-Sessions lesen hier.

## Erledigt

- **Installer-Skripte** (PR #722): `assets/fonts/goetheanum/Installer/`
  (`windows.ps1`, `mac.sh`, `README.md`). Entfernen jede alte
  Goetheanum-Schrift, installieren das Office-Set v2.8 inkl. Icons und Pfeile,
  die variable Schrift auf Wunsch. IT-Variante `-AlleBenutzer`/`--alle`.
  Getestet nur simuliert (pwsh unter Linux mit nachgebauter Registry, bash mit
  umgebogenen Ordnern), **nicht auf echtem Windows/Mac**.

## Entschieden (Inhaber, 30./31. 10.)

- Terminal-Einzeiler taugen **nicht** für die Mitarbeitenden. Sie kennen nur
  Knöpfe und Apps. Die Skripte bleiben Werkzeug der IT und Motor der Installer.
- **Weg 2: echte Installer** (Windows `.exe`, Mac `.pkg`), signiert, mit einer
  Seite auf werkzeuge.goetheanum.ch, die das System erkennt und einen Knopf
  zeigt. Mac-Signatur: ein Kollege hat ein Apple-Developer-Konto (Hinweis:
  zeigt seinen Namen als Entwickler, wenn es ein persönliches Konto ist).
  Windows-Signatur offen (Vorschlag: Microsoft Trusted Signing).
- **Weg 1 (M365 Brand Center) und Weg 3 (IT-Verteilung über MDM):** Der Inhaber
  fragt bei der EDV nach (Mail entworfen, 31. 10.). Einige Rechner werden eng
  betreut, andere gar nicht.
- **Variable Schrift** nicht im Standard, nur als Zusatz für die Gestaltung.
- **Source Sans 3 fest ins Paket**, damit die Vorlagen sie verwenden können.
  Statische Schnitte aus dem Netz holen: Adobe-Release `3.052R`
  (`TTF-source-sans-3.052R.zip` auf github.com/adobe-fonts/source-sans).
- **Kyrillisch und Arabisch zur Auswahl im Installer**, repariert und in unser
  Namenssystem eingebaut: **Goetheanum Kyrillisch** (aus Titillium Web [RUS]),
  **Goetheanum Arabisch** (aus Cairo, statisch instanziiert). Rechtlich ok:
  OFL, kein Reserved Font Name bei Titillium und Cairo, fsType 0; Copyright und
  Lizenz bleiben, Herkunft im Namens-Eintrag vermerken.

## Offen, wartet auf den Inhaber

- **Name von Source Sans 3:** Vorschlag, den Namen **unverändert** zu lassen
  (die Adobe-Dateien sind sauber; «Source» ist Reserved Font Name, eine
  Umbenennung wäre nur bei Änderung nötig). Der fremde Name hält sie davon ab,
  die Hausschrift zu ersetzen. Der Inhaber war bei «Goetheanum Info» unsicher.
- **Office-Regel** zur Freigabe (nicht eigenmächtig ins Regelwerk):
  «In Office-Dokumenten trägt die Goetheanum Schrift alles, was als Sprache
  gelesen wird: Titel, Lede, Fliesstext. Source Sans 3 steht nur, wo Text zu
  Daten wird: Tabellen, Formularfelder, Legenden, Fussnoten. Die Vorlagen geben
  das über Formatvorlagen vor.» Die genaue Fliesstext-Grenze liefert der
  Lesetest.

## Befunde

- Die Hausschrift deckt **kein** Griechisch (1/57), Kyrillisch, Hebräisch,
  Arabisch; Vietnamesisch nur 4/90. Source Sans 3 deckt Griechisch und
  Kyrillisch für den Lesetext.
- Titillium Web hat nur Latein; die einzige Erweiterung ist Kyrillisch
  (Daymarius). Für Hebräisch, Georgisch, Armenisch, Griechisch gibt es keine
  Titillium-Fassung.
- Landwirte-Vorlage `apps/lt-reader/vorlage/LT27-Reader.idml`: Chinesisch in
  PingFang HK/SC (49 Stellen, Apple-Systemschrift, fehlt auf Windows, nicht
  weitergebbar), Source Han Sans (2 Stellen). Empfehlung: **Source Han Sans**
  (Adobe, OFL, Schwester von Source Sans 3), im Installer zur Auswahl.

## In Arbeit (eigene Sessions, 31. 10.)

1. **Vergleichsseite Schriftsysteme** (Treibhaus) — **steht**, wartet auf die
   Wahl des Inhabers: https://werkzeuge.goetheanum.ch/begleitschriften.html
   Je Kandidat Titel (Schnitt nächst Deutlich 580) und Absatz, neben
   lateinischem Titel in der Hausschrift und Absatz in Source Sans 3.
   Subsets selbst gehostet unter `assets/fonts/schriftsysteme/` (Bau:
   `tools/schriftsysteme-probe.py`, nach Text-Änderung neu laufen lassen);
   Lizenz und Reserved Font Name je Kandidat in
   `assets/fonts/schriftsysteme/LIZENZEN.md`.

   | System | Kandidaten | Empfehlung (Session, 31. 10.) |
   |---|---|---|
   | Griechisch | Source Sans 3, Fira Sans, Commissioner, IBM Plex Sans | Titel **Fira Sans** (schmal, technisch, trägt wie die Hausschrift), Lesetext Source Sans 3 |
   | Hebräisch | Assistant, Heebo, IBM Plex Sans Hebrew, Noto Sans Hebrew | **Assistant** für Titel und Text (Latein = Source Sans); Heebo, falls der Titel kräftiger sein soll |
   | Georgisch | Noto Sans Georgian, FiraGO, Google Sans | **FiraGO** (eine Familie mit Fira Sans; Georgisch von Akaki Razmadze) |
   | Armenisch | Noto Sans Armenian, Mardoto, Google Sans | **Noto Sans Armenian** |
   | Chinesisch | Source Han Sans SC, Source Han Serif SC, ZCOOL XiaoWei | **Source Han Sans SC** |
   | Japanisch | Source Han Sans JP, Zen Kaku Gothic New, IBM Plex Sans JP, BIZ UDPGothic | **Source Han Sans JP**; BIZ UDPGothic, wenn proportionale Kana gewünscht |
   | Koreanisch | Source Han Sans KR, IBM Plex Sans KR, Gothic A1 | **Source Han Sans KR** |

   Begründungen und Vorbehalte:
   - Source Han Sans deckt alle drei CJK-Sprachen in einer Familie (als
     Super-OTC eine Datei) und ist die Schwester von Source Sans 3.
   - Google Sans ist OFL, trägt aber sichtbar Googles Markenbild — für das
     Goetheanum nur als Notlösung.
   - Mardoto (Apache 2.0, Roboto-Latein) zeichnet das grosse Հ wie Յ; von
     Armenisch-Lesenden prüfen lassen, bevor es infrage kommt.
   - ZCOOL XiaoWei hat nur einen Schnitt und setzt westliche Satzzeichen —
     Displayschrift, kein Lesetext.
   - Reserved Font Names: «Source» (Source Sans 3, Assistant, Source Han Sans
     SC/JP/KR), «Plex» (alle IBM Plex). Im Installer darum nur unveränderte
     Originaldateien; die Probe-Subsets heissen intern «Probe …».
   - **Mustertexte** (Übersetzung von ‹Goetheanum – Freie Hochschule für
     Geisteswissenschaft› und einem Satz über Sitz und Veranstaltungen) sind
     von der Session übersetzt, **nicht** von Muttersprachlern geprüft. Vor
     jeder Verwendung ausserhalb der Probe gegenlesen lassen, besonders
     Georgisch und Armenisch.
2. **Lesetest Hausschrift vs. Source Sans 3** (Treibhaus): gleiche Texte in vier
   Längen (≈80, 250, 600, 1500 Wörter), Lesezeit, Verständnisfragen,
   Anstrengung; jede Person liest beide Schriften, Reihenfolge wechselnd;
   20–30 Personen, auch ältere, Bildschirm und Papier. Ergebnis: die Länge, ab
   der Fliesstext in Source Sans 3 läuft.

## Nächste Schritte hier (Installer-Strang)

1. Source Sans 3 statisch, Goetheanum Kyrillisch, Goetheanum Arabisch bauen
   (Skript in `tools/goetheanum-fontfix/`), in die Installer-Skripte als
   Optionen.
2. Installer-Apps (Inno Setup / pkgbuild) über GitHub Actions, Signatur sobald
   Konten geklärt (Secrets-Konfiguration → vor Merge fragen).
3. Installationsseite mit einem Knopf je System.

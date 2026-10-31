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
2. **Lesetest Hausschrift vs. Source Sans 3** (Treibhaus, gebaut 31. 10.):
   `apps/lesetest/` – Test (`index.html`), Druckbogen (`druck.html`),
   Auswertung (`auswertung.html`, mit `?demo` Beispieldaten). Speicher:
   `services/lesetest/schema.sql` (Tabelle `lesetest_durchgang`, RPCs
   `lesetest_beginnen`/`_abgeben`/`_ergebnisse`), angewandt vom Workflow
   `lesetest-schema.yml`; Tabelle vom Inhaber freigegeben (31. 10.).
   - **Entscheid Inhaber (31. 10.):** Längen ≈80/250/500/1000 statt
     80/250/600/1500, damit es etwa zehn Minuten bleibt (sonst ≈15).
   - **Texte:** acht Kurzprosa-Stücke von Franz Kafka (gemeinfrei), je zwei
     pro Länge mit ähnlichem LIX (33–49): Kleine Fabel (76 Wörter) /
     Zerstreutes Hinausschaun (86); Der Fahrgast (232) / Eine kaiserliche
     Botschaft (320); Die Sorge des Hausvaters (472) / Vor dem Gesetz (585);
     Ein Besuch im Bergwerk (875) / Kinder auf der Landstraße (1071).
     Vorlagen Project Gutenberg (eBooks 21989, 23532) und Wikisource. Wortlaut
     und Schreibweise (ß) wie Vorlage, Anführung ‹…› und Striche nach G16/G18.
     Je Text drei Fragen; dazu ‹Kannte ich schon› (z. B. Vor dem Gesetz), die
     Auswertung lässt solche Texte wahlweise weg.
   - **Plan:** acht Gruppen (`plan.js`). Längen kurz → lang, je Person zwei
     Texte in jeder Schrift; jede Kombination Text × Schrift je Länge kommt
     über die Gruppen gleich oft vor. Bildschirm: die Datenbank gibt die
     am wenigsten belegte Gruppe. Papier: Bogennummer = Gruppe; die Person
     drückt am Telefon Start und Ende und beantwortet dort die Fragen.
   - **Gleich gemacht:** Grad `--t-body`, Zeilenhöhe `--lh-body`, Laufweite
     wie `body`; Gewicht Klar 440 ↔ Source 400 (Stamm 33 ↔ 34 px bei 400 px
     gemessen); x-Höhe gleich über `size-adjust` in `tokens.css`.
   - **Abweichung, Befund fürs Fundament:** gleiches Mass in **Zeichen**, nicht
     `--measure`. 62ch ergeben in der Hausschrift **89 Zeichen** je Zeile
     (ihre Null ist breit, `ch` misst die Null), in Source 70. Der Test setzt
     beide auf 70 Zeichen (Klar 29 em, Source 31.5 em). Folge fürs Haus:
     `--measure` ist für Fliesstext in der Hausschrift rund ein Viertel zu
     breit. Nicht geändert, wartet auf den Inhaber.
   - Auf dem Telefon füllen beide die Breite; dort fasst die Zeile in Klar
     etwa 50, in Source etwa 46 Zeichen.
   - **Ausschluss in der Auswertung:** unter 40 oder über 800 Wörter je
     Minute, oder mehr als ein Fünftel der Lesezeit im verborgenen Tab.
   - **Offen:** Einladung verschicken (Text im PR), Bogen 1–8 drucken für die
     Papiergruppe, nach 20–30 Durchgängen auswerten und dem Inhaber eine
     Regel «ab etwa N Wörtern Source Sans 3» vorschlagen (nicht ins
     Regelwerk ohne Freigabe).

## Nächste Schritte hier (Installer-Strang)

1. Source Sans 3 statisch, Goetheanum Kyrillisch, Goetheanum Arabisch bauen
   (Skript in `tools/goetheanum-fontfix/`), in die Installer-Skripte als
   Optionen.
2. Installer-Apps (Inno Setup / pkgbuild) über GitHub Actions, Signatur sobald
   Konten geklärt (Secrets-Konfiguration → vor Merge fragen).
3. Installationsseite mit einem Knopf je System.

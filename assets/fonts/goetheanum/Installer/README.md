# Installer der Goetheanum-Schriften

Zwei Skripte, die zuerst **jede frühere Goetheanum-Schrift und jede Kopie von
Source Sans 3 entfernen** und dann die aktuelle Fassung installieren. Alt und Neu tragen dieselben Namen;
nebeneinander geraten sie in Konflikt (Office zeigt gesperrte oder künstlich
verformte Schnitte).

| Was | Woher | Angabe |
|---|---|---|
| Goetheanum Schrift (Klar, Laut als Fett, Leise als Kursiv), Ruhig, Deutlich, Icons, Pfeile | `../Office` | Standard |
| Source Sans 3, Source Sans 3 Semibold (je mit Kursiv) | `../Begleitschriften`, Adobe 3.052R unverändert | Standard |
| Goetheanum Kyrillisch (Regular, Bold) | `../Begleitschriften` | `-Kyrillisch` / `--kyrillisch` |
| Goetheanum Arabisch (Regular, Bold) | `../Begleitschriften` | `-Arabisch` / `--arabisch` |
| Goetheanum Variabel | `../Variable` | `-Variabel` / `--variabel` |

- Kyrillisch und Arabisch, die schon installiert sind, kommen auch ohne Angabe
  wieder mit.
- Die variable Schrift gehört der Gestaltung (Flüstern bis Schreien); Office
  stellt die variable CFF2-Schrift nicht zuverlässig dar.
- Das Aufräumen erfasst auch die variable `SourceSans3-*.ttf` und alte
  OTF-Kopien, aber **nicht** Source Sans Pro.
- Ist Source Sans 3 schon für alle Benutzer installiert (etwa von der IT) und
  fehlen die Adminrechte, bleibt sie stehen und kommt nicht pro Benutzer dazu.

## Setup-Apps (für die Mitarbeitenden)

https://werkzeuge.goetheanum.ch/schriften-installieren.html – ein Knopf je
System. Beide Apps bringen die Schriften aus dem Repo-Stand mit und rufen
diese Skripte auf; gebaut und auf echtem Windows und macOS getestet von
`.github/workflows/schrift-installer.yml` (Quellen in `tools/schrift-installer/`),
ausgeliefert über das Release `schrift-installer`. Noch **unsigniert**.

| | Windows `.exe` (Inno Setup) | Mac `.pkg` (pkgbuild) |
|---|---|---|
| Installiert | pro Benutzer, ohne Adminrechte | für alle Benutzer, mit Passwort |
| Ruft auf | `windows.ps1 -OhneRueckfrage -Quelle …` | `mac.sh --alle --quelle …` |
| Zusätze | Häkchen Kyrillisch, Arabisch, Variabel | Auswahl unter ‹Installationstyp› |
| Still | `/VERYSILENT /TASKS="kyrillisch,arabisch"` | `installer -pkg … -target /` (Auswahl über `-applyChoiceChangesXML`) |

Offene Programme fragt die Windows-App vor dem Installieren ab; das Mac-Paket
installiert ohne Rückfrage.

## Für alle (pro Benutzer, ohne Adminrechte)

Windows, in PowerShell:

```powershell
irm https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/windows.ps1 | iex
```

Mac, im Terminal:

```bash
curl -fsSL https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/mac.sh | bash
```

Mit Zusätzen (hier Kyrillisch und Arabisch; `-Variabel` bzw. `--variabel`
ebenso):

```powershell
& ([scriptblock]::Create((irm https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/windows.ps1))) -Kyrillisch -Arabisch
```

```bash
curl -fsSL https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/mac.sh | bash -s -- --kyrillisch --arabisch
```

Über den kopierten Befehl gibt es keine Warnung von SmartScreen oder
Gatekeeper; ein heruntergeladenes, unsigniertes Skript würde sie auslösen.

## Für die IT (alle Benutzer eines Geräts)

Als Administrator bzw. root, auch über Intune oder Jamf:

```powershell
powershell -ExecutionPolicy Bypass -File windows.ps1 -AlleBenutzer [-Kyrillisch] [-Arabisch] [-Variabel] [-Quelle <Ordner>] [-OhneRueckfrage]
```

```bash
sudo bash mac.sh --alle [--kyrillisch] [--arabisch] [--variabel] [--quelle <Ordner>]
```

- `-AlleBenutzer`/`--alle` installiert in den Systemordner (Windows:
  `C:\Windows\Fonts`, Mac: `/Library/Fonts`) und räumt Kopien pro Benutzer in
  allen Profilen weg.
- `-Quelle`/`--quelle` nimmt die Dateien aus dem entpackten
  `Goetheanum-Schriften-v2.9.zip` statt aus dem Netz.
- `-OhneRueckfrage` (Windows) fragt nicht nach offenen Programmen; gesperrte
  Dateien enden mit Code 1. Ohne Fenster (Setup-App, Intune) nötig.

## Ablauf und Exit-Codes

1. Alle Dateien laden; scheitert das, bleibt alles unverändert.
2. Offene Programme (Word, PowerPoint, InDesign …) schliessen lassen, wenn
   jemand am Gerät sitzt.
3. Alles mit «Goetheanum», «SourceSans3» oder «Source Sans 3» im Namen aus
   den Schriftordnern entfernen, unter Windows samt Registry-Eintrag.
4. Neu installieren; unter Windows ohne Abmelden sofort verfügbar.

| Code | Bedeutung |
|---:|---|
| 0 | fertig |
| 1 | Fehler: Download, Datei gesperrt (Neustart, dann wiederholen) |
| 2 | alte Fassung für alle Benutzer gefunden, Adminrechte fehlen |

Bei einer neuen Fassung die Dateiliste und `Fassung`/`FASSUNG` in beiden
Skripten nachführen (CLAUDE-REF.md § Schnitt-System).

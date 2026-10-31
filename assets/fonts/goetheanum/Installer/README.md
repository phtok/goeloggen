# Installer der Goetheanum-Schriften

Zwei Skripte, die zuerst **jede frühere Goetheanum-Schrift entfernen** und dann
die aktuelle Fassung installieren. Alt und Neu tragen dieselben Namen;
nebeneinander geraten sie in Konflikt (Office zeigt gesperrte oder künstlich
verformte Schnitte).

Installiert wird das Office-Set aus `../Office`: Goetheanum Schrift (Klar,
Laut als Fett, Leise als Kursiv), Ruhig, Deutlich, Icons und Pfeile. Die
variable Schrift aus `../Variable` kommt nur auf Wunsch dazu (`-Variabel` bzw.
`--variabel`): Ihre Stufen Flüstern bis Schreien gehören der Gestaltung, und
Office stellt die variable CFF2-Schrift nicht zuverlässig dar.

## Für alle (pro Benutzer, ohne Adminrechte)

Windows, in PowerShell:

```powershell
irm https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/windows.ps1 | iex
```

Mac, im Terminal:

```bash
curl -fsSL https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/mac.sh | bash
```

Mit variabler Schrift:

```powershell
& ([scriptblock]::Create((irm https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/windows.ps1))) -Variabel
```

```bash
curl -fsSL https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/mac.sh | bash -s -- --variabel
```

Über den kopierten Befehl gibt es keine Warnung von SmartScreen oder
Gatekeeper; ein heruntergeladenes, unsigniertes Skript würde sie auslösen.

## Für die IT (alle Benutzer eines Geräts)

Als Administrator bzw. root, auch über Intune oder Jamf:

```powershell
powershell -ExecutionPolicy Bypass -File windows.ps1 -AlleBenutzer [-Variabel] [-Quelle <Ordner>]
```

```bash
sudo bash mac.sh --alle [--variabel] [--quelle <Ordner>]
```

- `-AlleBenutzer`/`--alle` installiert in den Systemordner (Windows:
  `C:\Windows\Fonts`, Mac: `/Library/Fonts`) und räumt Kopien pro Benutzer in
  allen Profilen weg.
- `-Quelle`/`--quelle` nimmt die Dateien aus dem entpackten
  `Goetheanum-Schriften-v2.8.zip` statt aus dem Netz.

## Ablauf und Exit-Codes

1. Alle Dateien laden; scheitert das, bleibt alles unverändert.
2. Offene Programme (Word, PowerPoint, InDesign …) schliessen lassen, wenn
   jemand am Gerät sitzt.
3. Alles mit «Goetheanum» im Namen aus den Schriftordnern entfernen,
   unter Windows samt Registry-Eintrag.
4. Neu installieren; unter Windows ohne Abmelden sofort verfügbar.

| Code | Bedeutung |
|---:|---|
| 0 | fertig |
| 1 | Fehler: Download, Datei gesperrt (Neustart, dann wiederholen) |
| 2 | alte Fassung für alle Benutzer gefunden, Adminrechte fehlen |

Bei einer neuen Fassung die Dateiliste und `Fassung`/`FASSUNG` in beiden
Skripten nachführen (CLAUDE-REF.md § Schnitt-System).

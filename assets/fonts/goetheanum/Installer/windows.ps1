# Goetheanum-Schriften installieren (Windows)
#
# Entfernt alle frueheren Goetheanum-Schriften und installiert die aktuelle
# Fassung: das Office-Set (Goetheanum Schrift, Ruhig, Deutlich, Icons, Pfeile),
# auf Wunsch dazu die variable Schrift fuer die Gestaltung.
#
# Fuer alle (pro Benutzer, ohne Adminrechte), in PowerShell:
#   irm https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/windows.ps1 | iex
# Mit variabler Schrift:
#   & ([scriptblock]::Create((irm https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum/Installer/windows.ps1))) -Variabel
#
# Fuer die IT (als Administrator, fuer alle Benutzer des Geraets):
#   .\windows.ps1 -AlleBenutzer [-Variabel] [-Quelle <entpackter Ordner Goetheanum-Schriften-v2.8>]
#
# Exit-Codes: 0 fertig - 1 Fehler (Download, Datei gesperrt) -
#             2 alte Fassung fuer alle Benutzer gefunden, braucht Adminrechte
#
# Die Dateiliste folgt assets/fonts/goetheanum/Office und Variable - bei neuer
# Fassung hier mitziehen (CLAUDE-REF.md Schnitt-System).

param(
  [switch]$Variabel,
  [switch]$AlleBenutzer,
  [string]$Quelle = ''
)

$ErrorActionPreference = 'Stop'
$Fassung = '2.8'
$Basis = 'https://werkzeuge.goetheanum.ch/assets/fonts/goetheanum'

# Datei -> Name im Schriftmenue (Registry-Eintrag)
$Schriften = [ordered]@{
  'Office/GoetheanumSchriftKlar.ttf'     = 'Goetheanum Schrift (TrueType)'
  'Office/GoetheanumSchriftLaut.ttf'     = 'Goetheanum Schrift Bold (TrueType)'
  'Office/GoetheanumSchriftLeise.ttf'    = 'Goetheanum Schrift Italic (TrueType)'
  'Office/GoetheanumSchriftRuhig.ttf'    = 'Goetheanum Schrift Ruhig (TrueType)'
  'Office/GoetheanumSchriftDeutlich.ttf' = 'Goetheanum Schrift Deutlich (TrueType)'
  'Office/GoetheanumIcons.ttf'           = 'Goetheanum Icons (TrueType)'
  'Office/GoetheanumPfeile.ttf'          = 'Goetheanum Pfeile (TrueType)'
}
if ($Variabel) {
  $Schriften["Variable/Goetheanum-Variabel-v$Fassung.otf"] = 'Goetheanum Variabel (OpenType)'
}

# Programme, die Schriftdateien sperren
$Programme = 'WINWORD','POWERPNT','EXCEL','OUTLOOK','ONENOTE','MSPUB','VISIO',
             'InDesign','Illustrator','Photoshop','AfterFX','Acrobat',
             'Designer','Photo','Publisher','Figma'

$NutzerOrdner = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
$SystemOrdner = Join-Path $env:WINDIR 'Fonts'
$NutzerReg = 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts'
$SystemReg = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'

function Melde([string]$text) { Write-Host "  $text" }
function Halt([string]$text) {
  Write-Host ''
  Write-Host "  $text" -ForegroundColor Red
  Write-Host ''
}

function Ist-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  (New-Object Security.Principal.WindowsPrincipal $id).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not ('Goetheanum.Gdi' -as [type])) {
  Add-Type -Namespace Goetheanum -Name Gdi -MemberDefinition @'
[DllImport("gdi32.dll", CharSet = CharSet.Unicode)]
public static extern int AddFontResource(string file);
[DllImport("gdi32.dll", CharSet = CharSet.Unicode)]
public static extern bool RemoveFontResource(string file);
[DllImport("user32.dll", CharSet = CharSet.Unicode)]
public static extern System.IntPtr SendMessageTimeout(System.IntPtr hWnd, uint Msg,
  System.UIntPtr wParam, System.IntPtr lParam, uint flags, uint timeout, out System.UIntPtr result);
'@
}

function Melde-Schriftwechsel {
  $r = [UIntPtr]::Zero
  [void][Goetheanum.Gdi]::SendMessageTimeout([IntPtr]0xffff, 0x001D,
    [UIntPtr]::Zero, [IntPtr]::Zero, 2, 1000, [ref]$r)
}

# Alte Goetheanum-Schriften in einem Bereich (Registry + Ordner) finden
function Finde-Alte([string]$reg, [string]$ordner) {
  $funde = @()
  if (Test-Path $reg) {
    $eintraege = Get-ItemProperty -Path $reg
    foreach ($p in $eintraege.PSObject.Properties) {
      if ($p.Name -like 'PS*') { continue }
      if ($p.Name -match 'Goetheanum' -or "$($p.Value)" -match 'Goetheanum') {
        $pfad = "$($p.Value)"
        if (-not [IO.Path]::IsPathRooted($pfad)) { $pfad = Join-Path $ordner $pfad }
        $funde += [pscustomobject]@{ Name = $p.Name; Pfad = $pfad; Reg = $reg }
      }
    }
  }
  if (Test-Path $ordner) {
    Get-ChildItem -Path $ordner -File -Filter '*oetheanum*' | ForEach-Object {
      $f = $_.FullName
      if (-not ($funde | Where-Object { $_.Pfad -eq $f })) {
        $funde += [pscustomobject]@{ Name = $null; Pfad = $f; Reg = $reg }
      }
    }
  }
  $funde
}

# IT-Fall: Kopien pro Benutzer in allen Profilen (Registry nur der geladenen Profile;
# verwaiste Eintraege ohne Datei uebergeht Windows)
function Finde-AlteProfile {
  $funde = @()
  Get-ChildItem -Path 'Registry::HKEY_USERS' -ErrorAction SilentlyContinue |
    Where-Object { $_.PSChildName -match '^S-1-5-21-[\d-]+$' } | ForEach-Object {
      $reg = "Registry::HKEY_USERS\$($_.PSChildName)\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
      $funde += @(Finde-Alte $reg $NutzerOrdner)
    }
  $benutzer = Join-Path $env:SystemDrive 'Users'
  Get-ChildItem -Path $benutzer -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $ordner = Join-Path $_.FullName 'AppData\Local\Microsoft\Windows\Fonts'
    if (Test-Path $ordner) {
      Get-ChildItem -Path $ordner -File -Filter '*oetheanum*' | ForEach-Object {
        $f = $_.FullName
        if (-not ($funde | Where-Object { $_.Pfad -eq $f })) {
          $funde += [pscustomobject]@{ Name = $null; Pfad = $f; Reg = $null }
        }
      }
    }
  }
  $funde
}

function Entferne($funde) {
  $gesperrt = @()
  foreach ($a in $funde) {
    if ($a.Pfad -and (Test-Path -LiteralPath $a.Pfad)) {
      [void][Goetheanum.Gdi]::RemoveFontResource($a.Pfad)
      try { Remove-Item -LiteralPath $a.Pfad -Force }
      catch { $gesperrt += $a.Pfad; continue }
    }
    if ($a.Name -and $a.Reg) { Remove-ItemProperty -Path $a.Reg -Name $a.Name -ErrorAction SilentlyContinue }
    Melde "entfernt: $(Split-Path $a.Pfad -Leaf)"
  }
  $gesperrt
}

function Installiere {
  Write-Host ''
  Write-Host "  Goetheanum-Schriften $Fassung installieren"
  Write-Host ''

  if ($AlleBenutzer -and -not (Ist-Admin)) {
    Halt 'Fuer alle Benutzer braucht es Adminrechte: PowerShell als Administrator starten.'
    return 1
  }

  # 1. Laden, bevor irgendetwas geloescht wird
  $tmp = Join-Path ([IO.Path]::GetTempPath()) ("goetheanum-" + [guid]::NewGuid())
  New-Item -ItemType Directory -Path $tmp | Out-Null
  try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor 3072
    foreach ($datei in $Schriften.Keys) {
      $ziel = Join-Path $tmp (Split-Path $datei -Leaf)
      if ($Quelle) {
        Copy-Item -LiteralPath (Join-Path $Quelle $datei) -Destination $ziel
      } else {
        Invoke-WebRequest -Uri "$Basis/$datei" -OutFile $ziel -UseBasicParsing
      }
      if ((Get-Item $ziel).Length -lt 1000) { throw "unvollstaendig: $datei" }
    }
  } catch {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Halt "Die Schriften liessen sich nicht laden ($($_.Exception.Message)). Nichts wurde veraendert."
    return 1
  }
  Melde 'Schriften geladen.'

  # 2. Offene Programme schliessen lassen
  $interaktiv = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected
  $offen = Get-Process -Name $Programme -ErrorAction SilentlyContinue
  while ($offen -and $interaktiv) {
    Write-Host ''
    Melde 'Bitte zuerst schliessen (sie halten die alten Schriften fest):'
    $offen | Select-Object -ExpandProperty ProcessName -Unique | ForEach-Object { Melde "  - $_" }
    [void](Read-Host '  Danach Enter druecken')
    $offen = Get-Process -Name $Programme -ErrorAction SilentlyContinue
  }

  # 3. Alte Fassungen entfernen
  $altSystem = @(Finde-Alte $SystemReg $SystemOrdner)
  if ($altSystem.Count -gt 0 -and -not (Ist-Admin)) {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Write-Host ''
    Melde 'Auf diesem Rechner ist eine alte Fassung fuer alle Benutzer installiert:'
    $altSystem | ForEach-Object { Melde "  - $(Split-Path $_.Pfad -Leaf)" }
    Halt ('Sie laesst sich nur mit Adminrechten entfernen. Bitte die IT fragen oder ' +
          'PowerShell als Administrator starten und den Befehl dort wiederholen. ' +
          'Nichts wurde veraendert.')
    return 2
  }
  $alt = @(Finde-Alte $NutzerReg $NutzerOrdner) + @($altSystem)
  if ($AlleBenutzer) { $alt += @(Finde-AlteProfile) }
  $gesperrt = @(Entferne $alt)
  if ($gesperrt.Count -gt 0) {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Melde 'Diese Dateien sind noch in Gebrauch:'
    $gesperrt | ForEach-Object { Melde "  - $(Split-Path $_ -Leaf)" }
    Halt 'Bitte den Rechner neu starten und den Befehl gleich danach wiederholen.'
    return 1
  }
  if ($alt.Count -eq 0) { Melde 'Keine alte Fassung gefunden.' }

  # 4. Neue Fassung installieren
  if ($AlleBenutzer) { $ordner = $SystemOrdner; $reg = $SystemReg }
  else { $ordner = $NutzerOrdner; $reg = $NutzerReg }
  New-Item -ItemType Directory -Force -Path $ordner | Out-Null
  if (-not (Test-Path $reg)) { New-Item -Path $reg -Force | Out-Null }

  foreach ($datei in $Schriften.Keys) {
    $name = Split-Path $datei -Leaf
    $ziel = Join-Path $ordner $name
    Copy-Item -LiteralPath (Join-Path $tmp $name) -Destination $ziel -Force
    $wert = if ($AlleBenutzer) { $name } else { $ziel }
    New-ItemProperty -Path $reg -Name $Schriften[$datei] -Value $wert -PropertyType String -Force | Out-Null
    [void][Goetheanum.Gdi]::AddFontResource($ziel)
    Melde "installiert: $name"
  }
  Melde-Schriftwechsel
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue

  Write-Host ''
  Write-Host "  Fertig: Goetheanum-Schriften $Fassung sind installiert." -ForegroundColor Green
  Write-Host '  Word, PowerPoint und Co. jetzt (neu) starten.'
  Write-Host ''
  return 0
}

# Als Datei (IT): Exit-Code. Ueber irm | iex: das Fenster bleibt offen.
$code = Installiere
if ($PSCommandPath) { exit $code }

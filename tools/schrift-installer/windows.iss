; Goetheanum-Schriften: Setup-App fuer Windows (Inno Setup 6)
;
; Bringt die Schriften aus dem Repo-Stand mit und ruft damit
; assets/fonts/goetheanum/Installer/windows.ps1 auf (-Quelle, -OhneRueckfrage).
; Das Skript entfernt alte Fassungen und installiert pro Benutzer, ohne
; Adminrechte. Gebaut von .github/workflows/schrift-installer.yml.
;
; Still (IT):  Goetheanum-Schriften-2.9-Windows.exe /VERYSILENT /TASKS="kyrillisch,arabisch"

#ifndef Fassung
  #define Fassung "2.9"
#endif
#define Wurzel "..\..\assets\fonts\goetheanum"

[Setup]
AppId=ch.goetheanum.schriften
AppName=Goetheanum-Schriften
AppVersion={#Fassung}
AppVerName=Goetheanum-Schriften {#Fassung}
AppPublisher=Goetheanum
AppPublisherURL=https://werkzeuge.goetheanum.ch/schriften-installieren.html
VersionInfoVersion={#Fassung}
OutputBaseFilename=Goetheanum-Schriften-{#Fassung}-Windows
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
CreateAppDir=no
Uninstallable=no
DisableProgramGroupPage=yes
DisableReadyPage=no
WizardStyle=modern
Compression=lzma2
SolidCompression=yes

[Languages]
Name: "de"; MessagesFile: "compiler:Languages\German.isl"

[Messages]
de.WizardSelectTasks=Zusätze wählen
de.SelectTasksDesc=Welche Schriften sollen dazukommen?
de.SelectTasksLabel2=Die Goetheanum Schrift und Source Sans 3 kommen immer. Alte Fassungen werden zuerst entfernt.
de.FinishedHeadingLabel=Fertig
de.FinishedLabelNoIcons=Die Goetheanum-Schriften {#Fassung} sind installiert. Word, PowerPoint und Co. jetzt (neu) starten.

[Tasks]
Name: "kyrillisch"; Description: "Goetheanum Kyrillisch"; Flags: unchecked
Name: "arabisch"; Description: "Goetheanum Arabisch"; Flags: unchecked
Name: "variabel"; Description: "Goetheanum Variabel (für die Gestaltung)"; Flags: unchecked

[Files]
Source: "{#Wurzel}\Office\*.ttf"; DestDir: "{tmp}\Office"
Source: "{#Wurzel}\Begleitschriften\*.ttf"; DestDir: "{tmp}\Begleitschriften"
Source: "{#Wurzel}\Variable\Goetheanum-Variabel-v{#Fassung}.otf"; DestDir: "{tmp}\Variable"
Source: "{#Wurzel}\Installer\windows.ps1"; DestDir: "{tmp}\Installer"

[Code]
var
  Fehler: String;

// Programme, die Schriftdateien sperren (wie $Programme in windows.ps1)
var
  Dateien, Namen: TArrayOfString;

procedure Programm(Datei, Name: String);
var
  n: Integer;
begin
  n := GetArrayLength(Dateien);
  SetArrayLength(Dateien, n + 1);
  SetArrayLength(Namen, n + 1);
  Dateien[n] := Datei;
  Namen[n] := Name;
end;

function InitializeSetup(): Boolean;
begin
  Programm('WINWORD.EXE', 'Word');
  Programm('POWERPNT.EXE', 'PowerPoint');
  Programm('EXCEL.EXE', 'Excel');
  Programm('OUTLOOK.EXE', 'Outlook');
  Programm('ONENOTE.EXE', 'OneNote');
  Programm('MSPUB.EXE', 'Publisher');
  Programm('VISIO.EXE', 'Visio');
  Programm('InDesign.exe', 'InDesign');
  Programm('Illustrator.exe', 'Illustrator');
  Programm('Photoshop.exe', 'Photoshop');
  Programm('AfterFX.exe', 'After Effects');
  Programm('Acrobat.exe', 'Acrobat');
  Programm('Designer.exe', 'Affinity Designer');
  Programm('Photo.exe', 'Affinity Photo');
  Programm('Publisher.exe', 'Affinity Publisher');
  Programm('Figma.exe', 'Figma');
  Result := True;
end;

function OffeneProgramme(): String;
var
  Locator, Dienst, Funde, Prozess: Variant;
  Abfrage, Name: String;
  i, j: Integer;
begin
  Result := '';
  Abfrage := '';
  for i := 0 to GetArrayLength(Dateien) - 1 do begin
    if Abfrage <> '' then Abfrage := Abfrage + ' OR ';
    Abfrage := Abfrage + 'Name=''' + Dateien[i] + '''';
  end;
  try
    Locator := CreateOleObject('WbemScripting.SWbemLocator');
    Dienst := Locator.ConnectServer('.', 'root\CIMV2');
    Funde := Dienst.ExecQuery('SELECT Name FROM Win32_Process WHERE ' + Abfrage);
    for j := 0 to Funde.Count - 1 do begin
      Prozess := Funde.ItemIndex(j);
      Name := Prozess.Name;
      for i := 0 to GetArrayLength(Dateien) - 1 do
        if (CompareText(Name, Dateien[i]) = 0) and (Pos('– ' + Namen[i] + #13#10, Result) = 0) then
          Result := Result + '– ' + Namen[i] + #13#10;
    end;
  except
    Result := '';
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Offen: String;
begin
  Result := True;
  if (CurPageID <> wpReady) or WizardSilent then exit;
  repeat
    Offen := OffeneProgramme();
    if Offen = '' then exit;
    if MsgBox('Bitte zuerst schliessen, sie halten die alten Schriften fest:' + #13#10#13#10 +
              Offen + #13#10 + 'Danach OK.', mbInformation, MB_OKCANCEL) = IDCANCEL then begin
      Result := False;
      exit;
    end;
  until False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Tmp, Protokoll, Angaben, Befehl: String;
  Inhalt: AnsiString;
  Code: Integer;
begin
  if CurStep <> ssPostInstall then exit;
  WizardForm.StatusLabel.Caption := 'Alte Fassungen entfernen, Schriften installieren …';
  Tmp := ExpandConstant('{tmp}');
  Protokoll := Tmp + '\protokoll.txt';
  Angaben := ' -OhneRueckfrage -Quelle "' + Tmp + '"';
  if WizardIsTaskSelected('kyrillisch') then Angaben := Angaben + ' -Kyrillisch';
  if WizardIsTaskSelected('arabisch') then Angaben := Angaben + ' -Arabisch';
  if WizardIsTaskSelected('variabel') then Angaben := Angaben + ' -Variabel';
  Befehl := '/C ""' + ExpandConstant('{sys}') + '\WindowsPowerShell\v1.0\powershell.exe"' +
            ' -NoProfile -ExecutionPolicy Bypass -File "' + Tmp + '\Installer\windows.ps1"' +
            Angaben + ' > "' + Protokoll + '" 2>&1"';
  if not Exec(ExpandConstant('{cmd}'), Befehl, Tmp, SW_HIDE, ewWaitUntilTerminated, Code) then
    Code := -1;
  if LoadStringFromFile(Protokoll, Inhalt) then Log(String(Inhalt));
  Log('windows.ps1 endete mit Code ' + IntToStr(Code));
  case Code of
    0: Fehler := '';
    2: Fehler := 'Auf diesem Rechner ist eine alte Fassung für alle Benutzer installiert. ' +
                 'Sie lässt sich nur mit Adminrechten entfernen. Bitte die IT fragen. Nichts wurde verändert.';
  else
    Fehler := 'Die Schriften liessen sich nicht vollständig installieren. ' +
              'Bitte den Rechner neu starten und die Installation gleich danach wiederholen.';
  end;
  if Fehler <> '' then SuppressibleMsgBox(Fehler, mbError, MB_OK, IDOK);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if (CurPageID = wpFinished) and (Fehler <> '') then begin
    WizardForm.FinishedHeadingLabel.Caption := 'Nicht installiert';
    WizardForm.FinishedLabel.Caption := Fehler;
  end;
end;

# Anfrage an die EDV: Logo unter der E-Mail-Signatur per Nachrichtenflussregel

**Umgesetzt:** Die EDV hat die Regel am 20. 10. 2026 eingebaut und
bestätigt. Das Logo erscheint unter der Text-Signatur; der Generator bietet
keine eigene Logo-Option mehr an.

Stand 18. 10. 2026. Hintergrund und Vergleich der Wege: `TESTING.md`,
Abschnitt «Recherche 18. 10. 2026». Der Text unten ist zum Kopieren gedacht.

---

## Anfrage (Text zum Kopieren)

Liebe EDV

Wir möchten das Goetheanum-Logo unter die E-Mail-Signaturen bringen, ohne
dass es beim Empfänger als Anhang (Büroklammer) erscheint. Die Signatur-
Editoren von Outlook neu, Outlook im Browser und Outlook für Mac betten
Bilder immer als Anhang ein. Darum soll das Logo nicht im Mailprogramm,
sondern vom Server angehängt werden: eine Nachrichtenflussregel in Exchange
Online (Aktion «Haftungsausschluss anfügen») mit einem verlinkten Bild.

Was die Regel tut:

- Sie hängt an jede **neue** Mail **nach aussen** ein kleines Logo (100 × 17 px,
  verlinkt auf goetheanum.ch) unten an. Das Bild liegt auf
  https://werkzeuge.goetheanum.ch/assets/logos/goetheanum-signatur-logo.png
  und wird vom Empfänger nachgeladen, kein Anhang.
- Antworten und Weiterleitungen bleiben unberührt (Ausnahme auf die
  Kopfzeile «In-Reply-To» und auf Betreffe mit AW/RE/WG/FW). Interne Mails
  ebenfalls.
- Steht das Logo schon im Text (Ausnahme auf den Dateinamen), hängt die Regel
  nichts an. So gibt es nie ein doppeltes Logo.
- Kann die Regel nicht einfügen (signierte oder verschlüsselte Mail), geht
  die Mail unverändert raus (Fallback «Ignore»).

Die Text-Signatur selbst bleibt Sache der Mitarbeitenden und kommt wie
bisher aus dem Signatur-Generator: https://werkzeuge.goetheanum.ch/signatur-generator.html

Zwei Fragen vorab:

1. Liegen alle Postfächer mit Goetheanum-Adresse in Exchange Online, oder
   laufen einige über Heinlein? (Das DNS zeigt MX bei Heinlein und
   Autodiscover bei Microsoft.) Die Regel greift nur für Mails, die über
   Exchange Online hinausgehen.
2. Könnt ihr die Regel zuerst im Testmodus anlegen und uns eine Testmail an
   eine externe Adresse schicken? Den fertigen PowerShell-Befehl und den
   HTML-Schnipsel hängen wir an. Wer lieber klickt: Exchange Admin Center →
   Nachrichtenfluss → Regeln → Regel hinzufügen → Haftungsausschlüsse
   anwenden, Werte wie unten.

Herzlichen Dank
Philipp

---

## HTML-Schnipsel (Inhalt des Haftungsausschlusses)

Unter 5000 Zeichen, alle Stile inline, kein `cid:`, kein Anhang. Masse wie
im Generator (das PNG hat 430 × 72 px, zweifach für scharfe Bildschirme).

```html
<div style="margin:14px 0 0 0;line-height:0;"><a href="https://goetheanum.ch" style="text-decoration:none;border:0;"><img src="https://werkzeuge.goetheanum.ch/assets/logos/goetheanum-signatur-logo.png" width="100" height="17" alt="Goetheanum" style="display:block;border:0;width:100px;height:17px;" /></a></div>
```

## PowerShell (Exchange Online, komplette Regel)

Zuerst im Testmodus (`-Mode Audit`), nach erfolgreicher Testmail auf
`-Mode Enforce` umstellen (`Set-TransportRule -Identity "Signatur-Logo" -Mode Enforce`).

```powershell
Connect-ExchangeOnline

$logoHtml = @'
<div style="margin:14px 0 0 0;line-height:0;"><a href="https://goetheanum.ch" style="text-decoration:none;border:0;"><img src="https://werkzeuge.goetheanum.ch/assets/logos/goetheanum-signatur-logo.png" width="100" height="17" alt="Goetheanum" style="display:block;border:0;width:100px;height:17px;" /></a></div>
'@

New-TransportRule -Name "Signatur-Logo" `
  -Comments "Logo unter der Signatur, nur neue Mails nach aussen. Bild verlinkt, kein Anhang. Kontakt: Kommunikation." `
  -FromScope InOrganization `
  -SentToScope NotInOrganization `
  -ExceptIfHeaderMatchesMessageHeader "In-Reply-To" `
  -ExceptIfHeaderMatchesPatterns "." `
  -ExceptIfSubjectMatchesPatterns "^\s*(AW|RE|WG|FW|Fwd|TR)\s*:" `
  -ExceptIfSubjectOrBodyContainsWords "goetheanum-signatur-logo.png" `
  -ApplyHtmlDisclaimerLocation Append `
  -ApplyHtmlDisclaimerText $logoHtml `
  -ApplyHtmlDisclaimerFallbackAction Ignore `
  -Mode Audit
```

## Dieselben Werte fürs Klicken (Exchange Admin Center)

| Feld | Wert |
|---|---|
| Name | Signatur-Logo |
| Regel anwenden, wenn | Der Absender befindet sich **innerhalb** der Organisation |
| und | Der Empfänger befindet sich **ausserhalb** der Organisation |
| Ausser wenn | Eine Nachrichtenkopfzeile entspricht Textmustern: Kopfzeile `In-Reply-To`, Muster `.` |
| oder | Der Betreff entspricht Textmustern: `^\s*(AW|RE|WG|FW|Fwd|TR)\s*:` |
| oder | Betreff oder Text enthält: `goetheanum-signatur-logo.png` |
| Aktion | Haftungsausschluss **anfügen**, Text = HTML-Schnipsel oben |
| Fallback | Ignorieren |
| Modus | zuerst **Testen ohne Richtlinientipps**, dann Erzwingen |

## Testen

1. Regel im Testmodus anlegen, Testmail von einer Goetheanum-Adresse an
   eine externe Adresse (Gmail, privates Outlook) schicken.
2. Prüfen: Logo unten sichtbar, **keine Büroklammer**, Link auf
   goetheanum.ch. Auf die Mail antworten: kein zweites Logo.
3. Dann auf Erzwingen umstellen.

## Folge im Repo

Ist die Regel aktiv, fliegt die Logo-Option aus dem Generator (eigener PR).
Das Logo kommt dann für alle vom Haus, die Signatur bleibt Text.

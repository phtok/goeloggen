# Signatur-Generator v2 — Test-Matrix

Das Tool erzeugt eine **reine Text-Signatur** (`div`/`<br>`, alle Stile inline,
kein Bild, keine Tabelle, kein `<style>`, keine Hintergrundfarbe). Ziel: übersteht
das Einfügen unverändert und bleibt **hell wie dunkel** lesbar.

E-Mail-HTML rendert je Client anders — vor grösseren Änderungen an
`buildSignature()` bitte real gegenprüfen: **echte Testmail an sich selbst**,
in den unten genannten Clients öffnen. Vorschau ≠ Realität.

## Akzeptanz je Client (einfügen + Testmail, hell UND dunkel)

| Client | Einfügen | Empfang Hell | Empfang Dunkel |
|---|---|---|---|
| Apple Mail (macOS) | ☐ | ☐ | ☐ |
| Mail (iOS/iPadOS) | ☐ | ☐ | ☐ |
| Outlook neu (Mac/Windows) | ☐ | ☐ | ☐ |
| Outlook klassisch (Windows) | ☐ | ☐ | ☐ |
| Outlook Web | ☐ | ☐ | ☐ |
| Gmail Web | ☐ | ☐ | ☐ |

Workflow: ‹Signatur kopieren› → im Client unter Einstellungen → Signaturen
einfügen. Apple Mail: ggf. ‹Standardschriftart für E-Mails verwenden› deaktivieren.

## Prüfpunkte

- [ ] **Kein Anhang-Symbol (Büroklammer)** beim Empfänger — d. h. wirklich kein Bild im Markup.
- [ ] **Fliesstext ohne feste Farbe:** Name/Funktion/Adresse erscheinen im Dark Mode hell, im Light Mode dunkel (erben Theme).
- [ ] **Keine Grautöne**, keine Trennlinie, keine Hintergrundfarbe.
- [ ] **‹Goetheanum›** ist selbst der Link zu goetheanum.ch (keine eigene Zeile goetheanum.ch mehr); im Klartext ‹Goetheanum · goetheanum.ch›.
- [ ] **Mail-Blau** (`#4183B4`) für ‹Goetheanum› und Web-Links — lesbar auf hellem UND dunklem Grund (Kontrast 4.09:1 / 4.07:1, im Code dokumentiert).
- [ ] **Hierarchie** über Grösse/Gewicht: Name in 600, Adresse eine Stufe kleiner.
- [ ] **Links** funktionieren: Website (`https`), Telefon/Mobil (`tel:`), PS-Link.
- [ ] **‹Nur Text kopieren›** liefert saubere Klartext-Fassung (Zeilenumbrüche, keine HTML-Reste).
- [ ] **PS-Modul:** 120-Zeichen-Zähler, Darstellung `PS: … — Link`, ‹Erinnerung in den Kalender› lädt eine `.ics`, die in Apple Kalender und Outlook korrekt öffnet; abgelaufenes PS zeigt beim Laden einen Hinweis.
- [ ] **Vorschau Hell/Dunkel** schaltet den Bühnen-Hintergrund; gerendert wird exakt das kopierte Markup.

## Funktion / Rollout

- [ ] `localStorage` (`goe-signatur-v4`): Eingaben überstehen ein Reload und führen direkt zu Schritt 3; ein v3-Stand wird übernommen (Sektions-/Bereichszeilen der Funktion werden zur Zugehörigkeit).
- [ ] Drei Schritte (Du · Zugehörigkeit · Signatur) sind jederzeit anwählbar; ‹ändern› an einer Zeile springt in ihren Schritt.
- [ ] Jede Zeile lässt sich ausblenden; ‹Minimal› = Name · Goetheanum, ‹Vollständig› = alle (Hochschule nur bei Sektion).
- [ ] Sprache Deutsch / Deutsch + English / English: Sektion, Hochschule, Gesellschaft und Funktion folgen.
- [ ] Query-Prefill: `?name=Test&role=Probe&unit=ms&lang=de-en` füllt die Felder.
- [ ] ‹Beispiel einfügen› (Schritt 1) / ‹Neu beginnen› (Schritt 3) funktionieren.
- [ ] Mehrzeilige Felder (Funktion, Eigene Angabe, Website, PS) wachsen mit dem Inhalt.
- [ ] Empfehlungen erscheinen als Textabschnitt unter dem Generator.

## Testpersonen (Aufbau prüfen)

Reihenfolge der Blöcke: wer (Name, Funktion, Sektion/Bereich, deren Websites)
· Telefon (eine Zeile) · Haus (Hochschule, Gesellschaft, Adresse) ·
‹Goetheanum› als Schluss (Schriftzug oder Logo). Zweisprachig stehen kurze
Paare auf einer Zeile (bis 56 Zeichen), lange untereinander.

| Person | Eingabe | Erwartet |
|---|---|---|
| Minimal | Name, ‹Minimal› | Name · Goetheanum |
| Sektionsleitung | Leiterin/Head, Bildende Künste, DE+EN, ein Telefon, sbk.goetheanum.org | ‹Leiterin · Head›, ‹Sektion für Bildende Künste · Visual Arts Section›, Hochschule an |
| Bereich, viel Kontakt | Kommunikation, DE+EN, Telefon + Mobil, zwei Websites | Telefone und Websites je auf einer Zeile, Websites im ersten Block |
| Nur Englisch | Medical Section, Coordinator | nur englische Zeilen |
| Lange Sektion | Heilpädagogik, DE+EN | Sektionsname auf zwei Zeilen |

## Logo (Backend-Versuch, nur Intern-Ansicht)

Das Logo steht an Stelle des Schriftzugs ‹Goetheanum› als Schlusszeile,
verlinkt, als **CSS-Hintergrund** (kein `<img>`). Klassisches Outlook (Windows)
liest die mso-Weiche und bekommt den Textlink.

### Befund 7. 10. 2026 (Apple Mail, macOS, Dunkelmodus)

| Variante | Dunkelmodus beim Empfang | Bilder gesperrt |
|---|---|---|
| `<img>` mit mso-Weiche und Stil | hell | ‹Goetheanum› als Text im Rahmen |
| `<img>` ohne mso-Weiche | hell | wie oben |
| `<img>` nackt | hell | wie oben |
| CSS-Hintergrund | **dunkel**, Logo sichtbar | Stelle leer |
| Schriftzug ohne Logo | dunkel | – |

Schluss: Jedes `<img>` schaltet Apple Mail auf hell, auch gesperrt. Gebaut
ist darum der Hintergrund. Keine Büroklammer in allen Varianten. Damit der
Name bei gesperrten Bildern nie fehlt, beginnt die Adresse mit Logo mit
**‹Goetheanum›** (halbfett, Textfarbe, verlinkt; Zeile dann nicht
ausblendbar). Abstand: eine Leerzeile vor der Adresse, zwei vor dem Logo.

### Befund 7. 10. 2026 (Gmail)

| Client | Logo sichtbar | Dunkelmodus | Adresse |
|---|---|---|---|
| Gmail Web (Chrome, hell) | ✅ | – | wurde zum blauen Maps-Link → selbst verlinkt in Textfarbe (#648); danach in Textfarbe ✅ (Web und iOS-App, hell und dunkel) |
| Gmail iOS | ✅ | ✅ dunkel, auch mit Logo | wie Web |

### Befund 7. 10. 2026 (Mail iOS)

| Client | Logo sichtbar | Dunkelmodus | Adresse |
|---|---|---|---|
| Mail (iOS) | ✅ | ✅ dunkel, auch mit Logo | ‹Goetheanum› halbfett ✅; Apples Datenerkennung setzt einen feinen Unterstrich in Textfarbe (vor #648 gesendet) |

### Befund 7. 10. 2026 (Outlook im Browser, goetheanum.ch)

| | ohne Logo | mit Logo |
|---|---|---|
| Adresse ruhig (Textfarbe) | ✅ | ✅ |
| ‹Goetheanum› sichtbar | ✅ blau am Schluss | ✅ halbfett in der Adresse |
| Logo | – | ❌ Hintergrundbild entfernt, kein Hinweis «Bilder anzeigen»; der Link bleibt als leere Fläche |

Schluss: In Outlook im Browser greift der Ersatz – der Name steht halbfett in
der Adresse, die Logo-Stelle bleibt leer. Nachladen lässt sich das Logo dort
nicht.

### Befund 7. 10. 2026 (Einfügen in Outlook im Browser)

Signatur in die Signatur-Einstellungen von Outlook im Browser eingefügt:
- Das Hintergrund-Logo wird beim Einfügen gelöscht; auch ein `<img>` kommt
  nicht durch. Bilder nimmt der Editor nur als hochgeladene Datei – die reist
  als eingebetteter Anhang mit (Büroklammer), was ‹Bildersturm?› ausschliesst.
- `color:inherit` an Links wird entfernt: verlinkte Adresse und ‹Goetheanum›
  werden blau. Darum ist die Adresse jetzt reiner Text; ein Wortverbinder
  (U+2060) in der Postleitzahl soll Gmails Karten-Link verhindern (☐ prüfen).

Beschluss: Standard für alle bleibt der blaue Schriftzug ‹Goetheanum›. Das
Logo bleibt eine Möglichkeit für Apple Mail und Gmail, nur zusammen mit der
Adresse (ohne Adresse – ‹Minimal› – schliesst der Schriftzug).

### Befund 7. 10. 2026 (Einfügen in Apple Mail, Gmail-Adresse)

- **Apple Mail:** Logo-Signatur aus dem Generator eingefügt und gesendet –
  Logo kommt an, Mail bleibt im Dunkelmodus dunkel, ‹Goetheanum› halbfett,
  Abstände stimmen. → Logo-Häkchen für alle freigegeben (‹Für Apple Mail›).
- **Gmail-Adresse:** Gmail macht eine Postadresse zum blauen Karten-Link. Nicht
  geholfen: Wortverbinder in der PLZ, geschützte Leerzeichen, unsichtbare
  Trenner in den Wörtern. Geholfen: jedes Wort in eigenem `<span>` (gebaut),
  oder selbst verlinkt (wird in Outlook blau, darum verworfen).

### Noch offen

| Client | Logo sichtbar | Dunkelmodus | Bilder gesperrt |
|---|---|---|---|
| Gmail, Mail iOS (Bilder gesperrt) | – | – | ☐ |
| Einfügen in Gmail-Einstellungen: Logo bleibt? | ☐ | – | – |
| Einfügen in Outlook im Browser: Adresse mit spans in Textfarbe? | – | – | ☐ |
| Outlook im Browser, Dunkelmodus | – | ☐ | – |
| Outlook klassisch (Windows) | – (Textlink) | ☐ | ☐ |

## Nicht-Ziele

- Kein Backend für die Signatur, keine Datenübertragung von Eingaben (nur anonyme, insert-only Nutzungsstatistik ohne Eingaben).
- Keine Mehrfach-/Kurzvariante, kein `.htm`-Download, kein Logo-/Bild-Upload.

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
- [ ] **Mail-Blau** (`#4183B4`) für ‹Goetheanum› und Web-Links — lesbar auf hellem UND dunklem Grund (Kontrast 4.09:1 / 4.07:1, im Code dokumentiert).
- [ ] **Hierarchie** über Grösse/Gewicht: Name in 600, Adresse eine Stufe kleiner.
- [ ] **Links** funktionieren: Website (`https`), Telefon/Mobil (`tel:`), PS-Link.
- [ ] **‹Nur Text kopieren›** liefert saubere Klartext-Fassung (Zeilenumbrüche, keine HTML-Reste).
- [ ] **PS-Modul:** 120-Zeichen-Zähler, Darstellung `PS: … — Link`, ‹Erinnerung in den Kalender› lädt eine `.ics`, die in Apple Kalender und Outlook korrekt öffnet; abgelaufenes PS zeigt beim Laden einen Hinweis.
- [ ] **Vorschau Hell/Dunkel** schaltet den Bühnen-Hintergrund; gerendert wird exakt das kopierte Markup.

## Funktion / Rollout

- [ ] `localStorage` (`goe-signatur-v3`): Eingaben überstehen ein Reload; alte Versionen erzeugen keinen kaputten Zustand.
- [ ] Query-Prefill: `?name=Test&role=Probe` füllt die Felder.
- [ ] ‹Beispiel einfügen› / ‹Felder leeren› funktionieren.
- [ ] Mehrzeilige Felder (Funktion, Website, PS) wachsen mit dem Inhalt.
- [ ] Empfehlungen erscheinen als Textabschnitt unter dem Generator.

## Nicht-Ziele

- Kein Backend für die Signatur, keine Datenübertragung von Eingaben (nur anonyme, insert-only Nutzungsstatistik ohne Eingaben).
- Keine Mehrfach-/Kurzvariante, kein `.htm`-Download, kein Logo-/Bild-Upload.

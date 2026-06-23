# Signatur-Generator — Test-Matrix

Das Tool verspricht: funktioniert in Outlook (Windows/Mac), Apple Mail und Gmail.
Diese Datei deckt das ab. E-Mail-HTML rendert in jedem Client anders — vor
grösseren Änderungen am Signatur-Output (`buildSignature()`) bitte real gegenprüfen.

Kurz testen heisst: **echte E-Mail an sich selbst senden** und in den unten
genannten Clients öffnen. Vorschau im Generator ≠ Realität im Client.

## Clients (Minimal-Matrix)

| # | Client | Engine | Priorität |
|---|--------|--------|-----------|
| 1 | Outlook 365 **Windows** | Word | **kritisch** (häufigste Brüche) |
| 2 | Outlook **Mac** | WebKit | hoch |
| 3 | Apple Mail (macOS) | WebKit | hoch |
| 4 | Gmail **Web** | eigenes Sanitizing | hoch |
| 5 | Gmail **App** (iOS/Android) | — | mittel |
| 6 | iOS Mail | WebKit | mittel |

## Workflow pro Client

1. ‹Signatur kopieren› klicken.
2. In den Signatur-Einstellungen des Clients einfügen
   (Outlook Win alternativ: ‹.htm laden› → Datei nach
   `%APPDATA%\Microsoft\Signatures`).
3. Neue Mail + Antwort erstellen, an sich selbst senden, im Zielclient öffnen.

## Prüfpunkte (das sind die bekannten Outlook-Bruchstellen)

- [ ] **Layout**: Person links (Name → Funktion → Kontakt), Organisation rechts
      (Goetheanum → Gesellschaft → Adresse), dazwischen der blaue Trennbalken.
- [ ] **Blauer Trennbalken** ist sichtbar, durchgehend, 2px, klappt nicht weg
      (Spacer-Zelle, nicht `border`).
- [ ] **Abstände** (Funktion → Kontakt) stimmen
      (Spacer-Zeilen, nicht `<br><br>` — Word staucht/dehnt sonst).
- [ ] **Spaltenbreiten** stabil, kein Umbruch/Verrutschen, keine ungewollte
      Volldehnung über die Mailbreite.
- [ ] **Eine Grösse**: Arial 10.5pt durchgängig, **kein** Fett, **kein**
      Goetheanum-Webfont im Output.
- [ ] **Farben** (einziges Auszeichnungsmittel): Name dunkel, Funktion/Adresse grau,
      Kontakt-Links **und** Organisations-Hauptzeile (Goetheanum) im Goetheanum-Blau.
- [ ] **Links** funktionieren: `mailto:`, Website, `tel:` (auf Mobile).
- [ ] **Lang- und Kurz-Variante** je einzeln prüfen.
- [ ] **Dark Mode** des Clients: Signatur bleibt lesbar (Apple Mail/iOS invertieren gern).
- [ ] **Antwort/Weiterleitung**: Signatur bleibt intakt (Outlook reflowt Tabellen).

## Funktion / Rollout

- [ ] `localStorage`: Eingaben überstehen ein Reload.
- [ ] Query-Prefill: `?name=Test&role=Probe` füllt die Felder.
- [ ] ‹Beispiel einfügen› / ‹Felder leeren› funktionieren.
- [ ] E-Mail-Validierung markiert offensichtlich falsche Adressen.

## Bekannte Grenzen

- **Responsive** ist bewusst kein Ziel (Clients ignorieren `@media` weitgehend).
- `.htm`-Download ist **klassisches** Outlook (Windows) spezifisch; das *neue* Outlook nutzt
  den Signatures-Ordner nicht. Für neues Outlook, Apple Mail, Gmail: ‹Signatur kopieren›.

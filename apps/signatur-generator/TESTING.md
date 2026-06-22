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

- [ ] **Blauer Trennbalken** ist sichtbar, durchgehend, 2px, klappt nicht weg
      (Spacer-Zelle, nicht `border`).
- [ ] **Abstände** zwischen Person/Organisation bzw. Adresse/Kontakt stimmen
      (Spacer-Zeilen, nicht `<br><br>` — Word staucht/dehnt sonst).
- [ ] **Spaltenbreiten** stabil, kein Umbruch/Verrutschen, keine ungewollte
      Volldehnung über die Mailbreite.
- [ ] **Schrift** = Arial 10pt, **kein** Goetheanum-Webfont im Output.
- [ ] **Farben**: Name dunkel, Funktion grau, Kontakt-Links Goetheanum-Blau.
- [ ] **Links** funktionieren: `mailto:`, Website, `tel:` (auf Mobile).
- [ ] **Lang- und Kurz-Variante** je einzeln prüfen.
- [ ] **Dark Mode** des Clients: Signatur bleibt lesbar (Apple Mail/iOS invertieren gern).
- [ ] **Antwort/Weiterleitung**: Signatur bleibt intakt (Outlook reflowt Tabellen).

## PNG-Ausgabe

- [ ] Logo-Wortmarke + Sektionsname in korrekter Farbe (aus `goetheanum-orgs.js`).
- [ ] Transparenter Hintergrund sauber (kariert in der Vorschau = transparent).
- [ ] Schrift scharf (3×-Auflösung), Webfont geladen.

## Funktion / Rollout

- [ ] `localStorage`: Eingaben überstehen ein Reload.
- [ ] Query-Prefill: `?name=Test&roleDe=Probe` füllt die Felder.
- [ ] ‹Beispiel einfügen› / ‹Felder leeren› funktionieren.
- [ ] E-Mail-Validierung markiert offensichtlich falsche Adressen.

## Bekannte Grenzen

- **Responsive** ist bewusst kein Ziel (Clients ignorieren `@media` weitgehend).
- `.htm`-Download ist Outlook-Windows-spezifisch; für Apple Mail ‹Signatur kopieren› nutzen.

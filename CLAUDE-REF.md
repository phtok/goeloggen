# CLAUDE-REF — kaltes Nachschlagewissen (nur bei Bedarf lesen)

Ausgelagert aus `CLAUDE.md` (Token-Sparsamkeit, 9. 8. 2026): Was hier
steht, gilt unverändert — es wird nur nicht mehr in jeder Session
geladen. `CLAUDE.md` verweist je Abschnitt hierher.

## § Seite anschauen — kopierfertiges Playwright-Rezept

Chromium und Playwright liegen bereit, das genügt:

```bash
npx --yes http-server -p 8899 -s &            # Repo ausliefern
node -e "
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport:{ width:1280, height:1500 } });
  p.on('pageerror', e => console.log('PAGEERROR', e.message));
  await p.goto('http://127.0.0.1:8899/PFAD/index.html');
  await p.waitForTimeout(2000);
  await p.screenshot({ path:'/tmp/seite.png', fullPage:true });
  await b.close();
})();"
```

Kommt die Seite nicht ans Backend (die Sandbox lässt es nicht immer), die
RPC-Antworten mit `page.route('**/rest/v1/rpc/**', …)` unterlegen — mit **echten**
Daten aus der Datenbank, sonst prüft man eine Attrappe.

## § Schnitt-System (Stand v2.9, Paketstruktur Trio)

- Statische Schnitte: **Leise (265) · Ruhig (350) · Klar (440) ·
  Deutlich (580) · Laut (680)**. Ruhig = ruhiger Lese-/Buchschnitt (füllt den
  Sprung Leise→Klar); Deutlich = Titel; Laut = Inline-/Office-Fettung (⌘B).
- **Installiert wird nur das Office-TTF-Set.** Es trägt die Familienstruktur:
  ‹Goetheanum Schrift› = Klar (Regular) + Laut (Fett, ⌘B) + Leise (Kursiv, ⌘I);
  Ruhig, Deutlich, Icons, Pfeile als eigene Familien. Die Desktop-OTF der
  Schnitte sind reine **Build-Quellen** (`assets/fonts/goetheanum/Fonts/`) und
  werden nicht mehr ausgeliefert — gleiche Namen wie die Office-Familie,
  parallel installiert kollidieren sie (macOS deaktiviert Doppelgänger,
  PowerPoint verformt synthetisch).
- Variable: 7 Named Instances **Flüstern 190 · Leise · Ruhig · Klar · Deutlich ·
  Laut · Schreien 725** — Web und Design, stufenlos.

Bei Änderungen an der Schnittzahl **alle** Beschreibungen mitziehen
(schriften.html, schrift-webfont.html, README, tools.json, Beipackzettel).
Bei neuer Fassung oder geänderten Dateinamen auch die Installer nachführen
(`assets/fonts/goetheanum/Installer/windows.ps1` und `mac.sh`: Dateiliste und
Fassungsnummer).

## § Werkzeug-Schutz (Supabase-RPCs, Stand 5. 11. 2026)

**Beschluss des Inhabers (5. 11. 2026): Die Werkzeuge bleiben ohne Schlüssel
zugänglich.** Schlüssel wirken wie Passwörter und häufen sich, und ein zu
kompliziertes Werkzeug wird nicht benutzt. Die RPCs sind darum für anon offen;
geschützt wird durch **Umkehrbarkeit** (`services/werkzeug-schluessel/umkehrbar.sql`):

| Werkzeug | Schutz | Zurückholen (SQL, als Service-Rolle) |
|---|---|---|
| Folder | Trigger hält vor jedem Überschreiben eine Fassung fest (höchstens alle 10 Min., bei Export immer; je Folder die letzten 60) in `folder_fassung` | `update folder_archiv set stand = (select stand from folder_fassung where id = …) where id = '…';` |
| Kurzlinks (QR, UTM) | Gelöschtes samt Zählung in `kurzlink_geloescht`; ein Link auf eine noch nie verwendete Domain schickt eine Mail (Edge Function `kurzlink-melden`, Quelle `services/qr-generator/kurzlink-melden/`, Konfiguration in `kurzlink_config`) | Zeile aus `kurzlink_geloescht.zeile` zurück einfügen, `hits` nach `link_hits` |
| Sommer-Zähler | Ändern und Löschen in `sommer2026_kosten`, `_massnahmen`, `_multiplikatoren`, `_multi_kontakte` landet in `sommer2026_protokoll` | alte Zeile aus `protokoll.alt` |
| LT-Reader | hatte schon `reader_fassung` | – |

- Öffentlich lesbar bleiben auch Einnahmen-Summen und Stundensätze (für das
  Dashboard entscheidend, Beschluss 5. 11. 2026). Eine Zugangsregelung für
  das ganze Projekt («nur bestimmte Nutzende») kommt mit der nächsten
  Überarbeitung.
- **Geschichte:** Am 3. 11. 2026 kurz mit Schlüssel je Werkzeug gebaut (#754,
  `schema.sql`), am 5. 11. zurückgebaut (#761, `rueckbau.sql`). Schon am
  6. 7. 2026 war ein Kurzlink-Schlüssel als «zu kompliziert» entfernt worden.
  **Nicht wieder einführen**, ohne den Inhaber zu fragen.
- **Übrig vom Schlüssel-Bau:** nur `succow26_*`. Dessen Token steht nicht mehr
  im Klartext im Funktionsrumpf, sondern als Hash in `werkzeug_schluessel`
  (geprüft von `werkzeug_tor`). Der Token selbst ist gleich geblieben.
- **Offen:** `sommer2026_multi_pw_ok` lässt sich für anon ohne Bremse
  durchprobieren (Passwort klein geschrieben, ungesalzen).

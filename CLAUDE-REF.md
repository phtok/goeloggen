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

## § Schnitt-System (Stand v2.7, Paketstruktur Trio)

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

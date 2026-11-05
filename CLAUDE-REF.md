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

## § Werkzeug-Schlüssel (Supabase-RPCs, seit 3. 11. 2026)

Schreibende und heikle lesende RPCs der Werkzeuge verlangen einen Schlüssel
je Werkzeug. Bauart und Migration: `services/werkzeug-schluessel/schema.sql`;
Browser-Seite: `design-system/schluessel.js` (`GoeSchluessel.rpc(werkzeug,
name, body)` – fragt einmal je Gerät, prüft sofort, merkt in localStorage).

| Werkzeug | RPCs | Aufrufer |
|---|---|---|
| `kurzlinks` | `qr_link_anlegen/loeschen`, `sommer2026_link_anlegen/loeschen` (Parameter heisst dort `p_schluessel`) | qr-generator, utm-generator |
| `folder` | `folder_liste/holen/sichern` | folder, programmheft (live, zz-zusammen), folder-archiv |
| `reader` | alle `reader_*` | lt-reader |
| `zaehler` | `sommer2026_kosten_*`, `_massnahme_eintragen/aendern`, `_multi_anlegen`, `_multi_kontakt_anlegen`, `_multi_protokoll`, `_einnahmen` | sommer-zaehler |
| `lesetest` | `lesetest_ergebnisse` (Teilnehmen bleibt offen) | lesetest/auswertung |
| `succow26` | `succow26_list/upsert` (Token unverändert, nur noch als Hash) | ausserhalb dieses Repos |

- **Bauart:** Die alte Funktion liegt unverändert in `werkzeug_intern` (für
  anon zu), in `public` steht eine Hülle mit `p_key text default null`, die
  `werkzeug_tor()` fragt. Rümpfe ändern heisst: die Funktion in
  `werkzeug_intern` ersetzen, nicht die Hülle.
- **Phasen:** `werkzeug_schluessel.pflicht = false` lässt Aufrufe ohne
  Schlüssel noch durch (ein falscher scheitert immer). Verbindlich machen:
  `update public.werkzeug_schluessel set pflicht = true where werkzeug = '…';`
  – ohne Deploy, sofort wirksam.
- **Antwort bei falschem/fehlendem Schlüssel:** HTTP 403, Code `28000`,
  Meldung `schluessel_falsch`. Prüfen ohne Wirkung: RPC `werkzeug_key_ok`.
- **Schlüssel wechseln:** neuen erzeugen, Hash setzen (Formel im Kopf der
  Schema-Datei; normalisiert = klein, nur a–z/0–9). Geräte mit dem alten
  bekommen 403 und werden neu gefragt. Klartext nie in Datei, Commit, Log.
- **Fallen:** Ein Werkzeug ohne Zeile in `werkzeug_schluessel` ist zu (auch
  ohne Schlüssel). Interne Aufrufe ohne Anfrage-Rolle und `service_role`
  gehen durch. Wer im Dialog abbricht, wird bis zum Neuladen nicht mehr
  gefragt; der Zähler zeigt dann die geschützten Zahlen nicht.
  Der Kurzlink-Schlüssel war am 6. 7. 2026 schon einmal ausgebaut worden
  («zu kompliziert»); darum merkt sich das Gerät ihn jetzt.
- **Bewusst offen gelassen:** `*_comment_erledigt` (Kommentare sind dort für
  anon ohnehin les- und schreibbar), `sommer2026_multi_liste` und
  `_massnahmen_public` (nur Aliasse bzw. Massnahmen ohne Personen),
  öffentliche Zähler (`qr_stats_*`, `sommer2026_stats` …). Die
  Kurzlink-Auflösung läuft über die Edge Function `go` (Service-Role).
- **Offen:** `sommer2026_multi_pw_ok` ist für anon ein Ratespiel ohne Bremse
  (Passwort klein geschrieben, ungesalzen) – bei Gelegenheit auf einen
  Zufallsschlüssel umstellen.

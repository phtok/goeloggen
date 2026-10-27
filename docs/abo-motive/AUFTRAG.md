# Auftrag: Kampagnenseite «Abo-Motive»

*Für eine neue Claude-Code-Session in `phtok/goeloggen`. Selbsttragend, setzt
kein Wissen aus früheren Sitzungen voraus. Stand: 27. Oktober 2026.*

## Ziel

Eine interne Werkzeugseite in der Rubrik **Kampagne**, die drei Befunde zu den
Abo-Motiven, die vertiefte Frage «Gratis oder bezahlt?» und den Plan der
Weihnachtsaktion zeigt. Im Fuss sind die vollen Dossiers aufrufbar. Die Seite
dient der Marketingsitzung und soll die Geschäftsführung überzeugen, dass die
Gratisprobe getestet statt fortgeschrieben wird.

## Was in diesem Ordner liegt

| Datei | Inhalt |
|---|---|
| `seitentext.md` | **Fertiger Seitentext**, Reihenfolge = Seite. Nichts dazuerfinden. |

Die beiden Dossiers (Kurzanalyse und Marketingdossier samt Quellwerten) sind
**intern** und liegen bewusst **nicht** im öffentlichen Repo, sondern im
Google-Drive-Ordner «Abo-Motive 2026 · Dossiers»:
https://drive.google.com/drive/folders/1HiX0_yfIG-IWy0IvIrc5J_oe2GBssPoW

Gestaltete Vorlage (Sitzungsblatt, gleicher Inhalt ohne Gratis-Abschnitt):
https://claude.ai/artifact/J5zJMZ7rvHwtJKejFYN4ZX

## Bauen

1. **Ort:** `apps/abo-motive/index.html`, vom Starter
   `design-system/starter.html` aus. `tokens.css`, `base.css`, `nav.css`
   einbinden wie `apps/kampagnen-drehbuch/index.html` (Vorbild für Aufbau,
   `noindex`, Kopf und Navigation).
2. **Registrieren** in `tools.json`, gleich wie `kampagnen-drehbuch`:
   `"cat": "kampagne"`, `"status": "intern"`, `"slug": "abo-motive"`,
   `"href": "apps/abo-motive/"`, Titel «Abo-Motive». Danach
   `python3 tools/build_tool_aliases.py .`.
3. **Abschnitte** in der Reihenfolge von `seitentext.md`: Kopf · Drei Befunde ·
   Gratis oder bezahlt? · Weihnachtsaktion · Offen · Fuss.
4. **Fuss:** ein Link «Volle Dossiers (intern, Google Drive)» auf den
   Drive-Ordner oben. Den Inhalt der Dossiers **nicht** ins Repo kopieren.
   Dazu die drei Repo-Belege (`einnahmen-perspektive-10-08.md`,
   `probeabo-kosten-12-08.md`, `kampagnen-drehbuch.md`), relativ verlinkt wie
   im Drehbuch (`../../docs/...`).

## Gestalt (Regeln mit ID nennen)

- **Drei Befunde gleich gross** (CLAUDE.md § «Die Maschine prüft die Regel, das
  Auge prüft das Gewicht»): drei gleiche Karten, Leitzahlen in gleichem Grad,
  Source Sans 3, tabellarische Ziffern (G25).
- **Gratis-Abschnitt:** «Fünf Belege» als nummerierte Liste (echte Reihenfolge
  der Argumentation), «Was dagegen spricht» gleichwertig daneben oder darunter,
  nicht kleiner und nicht in Grau versteckt. Die Geschäftsführung soll sehen,
  dass ihre Einwände ernst genommen sind. Das Rechenbeispiel als eigener
  kurzer Block.
- **Betonung** mit Laut, nie Versalien, Sperren, Unterstreichen (G01, G05).
  Kicker normal (G05).
- **Weiss auf Farbe**, keine dunkle Schrift auf Farbfläche (B01). Grössen nach
  B03, Fingerziele B04, Flächen aus Tokens (B05).
- **Umbrüche:** Titel `text-wrap: balance`, Fliesstext `pretty`; festes
  Leerzeichen zwischen Zahl und Einheit (`89&nbsp;%`, `CHF&nbsp;270`,
  `29.&nbsp;November`).
- **Werkzeuge zeigen, das Repo erklärt:** Herleitung und Methodik bleiben in
  den Dossiers; die Seite trägt nur Befund, Beleg, Plan.

## Optional: lebende Zahlen

Die TV-Quote (21 %), die Kündigungsverteilung und die Länderwerte kommen aus
dem Supabase-Backend der Sommer-Aktion (RPCs `sommer2026_kohorten`,
`sommer2026_kuendigungen`, `sommer2026_stats`; Lesemuster in
`apps/sommer-zaehler/campaign.js`). Wenn das einfach geht: diese Zahlen live
laden, mit Stand-Datum, und den Text aus `seitentext.md` als Rückfall stehen
lassen. Sonst statisch mit «Stand 27. Oktober 2026».

## Abnahme

- `tools/typo-check.py` und `tools/ds-lint.py --staged` grün (Hook).
- `node tools/barrierefreiheit.mjs --seite apps/abo-motive/index.html` ohne Fund.
- Seite ansehen (Rezept `CLAUDE-REF.md` § Seite anschauen): 420 und 1280 px,
  hell und dunkel. Leitzahlen per `getComputedStyle` gleich gross.
- PR nicht als Draft, nach grünen Prüfmaschinen Squash-Merge (CLAUDE.md
  § Pull Requests).
- Live-URL melden: https://werkzeuge.goetheanum.ch/apps/abo-motive/

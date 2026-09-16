#!/usr/bin/env node
// DS08 · Barrierefreiheit — was das Handbuch verspricht, wird hier gemessen.
//
// Die Hausregeln B01–B05 stehen seit je in CLAUDE.md: kein dunkler Text auf
// farbigem Grund, Lesetext ≥ 4.5:1, Mindestgrössen, Fingerziele ≥ 44 px,
// Hell/Dunkel allein aus den Tokens. Geprüft hat sie bisher niemand am
// fertigen Blatt — ds-lint liest den Quelltext, und ob ein Kontrast trägt,
// entscheidet sich erst im Browser. Diese Maschine schliesst die Lücke.
//
//   node tools/barrierefreiheit.mjs [--seite <pfad>] [--check] [--spur]
//                                   [--alles] [--regel <id>]
//
// Ohne --check ist es ein Bericht, mit --check ein Tor: ein Verstoss beendet
// den Lauf mit 1. --alles nimmt zusätzlich die Empfehlungen auf, die über die
// Norm hinausgehen (axe nennt sie best-practice) — die zählen nie fürs Tor.
// --regel zeigt nur eine Regelsorte, für die Arbeit an einem Fund.
//
// Was eine Maschine nicht sieht: ob eine Beschriftung das Richtige sagt, ob
// die Reihenfolge dem Sinn folgt, ob eine Bewegung stört. Rund ein Drittel
// der Kriterien ist überhaupt automatisierbar. Ein grüner Lauf heisst «keine
// der prüfbaren Regeln verletzt» — nicht «zugänglich».
//
// Erwartet playwright-core und @axe-core/playwright (tools/package.json) und
// einen Chromium unter CHROMIUM_PATH oder /opt/pw-browsers/chromium.

import { chromium } from 'playwright-core'
import axePaket from '@axe-core/playwright'
import { readFileSync, existsSync, statSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { createServer } from 'node:http'
import { join, extname, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

// Das Paket kommt als CommonJS; je nach Auflösung liegt die Klasse eine
// Ebene tiefer. Beide Fälle abfangen, statt auf einen zu wetten.
const AxeBuilder = axePaket?.default ?? axePaket

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const KONTRAKT = JSON.parse(readFileSync(join(ROOT, 'design-system/contract.json'), 'utf8'))
const REGEL = KONTRAKT.barrierefreiheit ?? {}

// Die normativen Kriterien, nicht die Empfehlungen. Was axe unter
// best-practice führt, ist Rat — guter Rat, aber kein Gesetz, und ein Tor
// darf sich nur auf Gesetz stützen.
const NORM = REGEL.stufen ?? ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22a', 'wcag22aa']
const RAT = ['best-practice']

// Zwei Achsen: nur zwei Kriterien der Norm hängen überhaupt an der
// Fensterbreite — die Grösse der Fingerziele (2.5.8) und der Umbruch ohne
// Querscrollen (1.4.10). Beide entscheiden sich zwischen Telefon und
// Schreibtisch.
const ACHSEN = [{ tag: 'schmal', width: 390, height: 844 },
                { tag: 'weit', width: 1440, height: 1000 }]

const TYPEN = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
                '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
                '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml',
                '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.webp': 'image/webp', '.ico': 'image/x-icon', '.woff2': 'font/woff2',
                '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf',
                '.avif': 'image/avif', '.txt': 'text/plain; charset=utf-8',
                '.yaml': 'text/plain; charset=utf-8', '.yml': 'text/plain; charset=utf-8' }

// Derselbe Geltungsbereich wie ds-lint: versionierte Seiten mit eigenem
// Körper, ohne die ausgenommenen Pfade, ohne reine Weiterleitungen. Wer hier
// abweicht, prüft ein anderes Haus als der Rest der Maschinen.
function seiten () {
  const g = KONTRAKT.geltungsbereich
  const verzeichnet = execFileSync('git', ['ls-files', '*.html'], { cwd: ROOT, encoding: 'utf8' })
    .split('\n').map(l => l.trim()).filter(Boolean)
  const artefakt = REGEL.artefakt_dateien ?? []
  const liste = []
  for (const pfad of verzeichnet) {
    const p = '/' + pfad.replace(/^\.?\//, '')
    if (g.ausgenommen_substr.some(s => p.includes(s))) continue
    if (g.ausgenommen_dateien.includes(pfad)) continue
    const text = readFileSync(join(ROOT, pfad), 'utf8')
    if (!text.toLowerCase().includes('<body')) continue           // kein eigener Körper
    if (/http-equiv\s*=\s*["']?refresh/i.test(text)) continue     // reine Weiterleitung
    liste.push({ pfad, artefakt: artefakt.some(a => pfad === a || pfad.startsWith(a)) })
  }
  return liste.sort((a, b) => a.pfad.localeCompare(b.pfad))
}

// Ein Server auf der Repo-Wurzel: die Seiten adressieren ihre Anhänge
// absolut (/design-system/tokens.css), wie auf den Seiten von GitHub Pages.
function serviere (wurzel) {
  return new Promise(fertig => {
    const s = createServer((req, res) => {
      let p = decodeURIComponent(req.url.split('?')[0])
      if (p.endsWith('/')) p += 'index.html'
      const datei = join(wurzel, p)
      if (!datei.startsWith(wurzel) || !existsSync(datei) || statSync(datei).isDirectory()) {
        res.writeHead(404).end('')
        return
      }
      res.writeHead(200, { 'content-type': TYPEN[extname(datei)] || 'application/octet-stream' })
      res.end(readFileSync(datei))
    })
    s.listen(0, '127.0.0.1', () => fertig({ port: s.address().port, zu: () => s.close() }))
  })
}

// Einmal durch die Seite blättern, bevor gemessen wird. Blätter, die ihre
// Abschnitte erst beim Herankommen einblenden, zeigen sonst Schrift in
// Grundfarbe auf Grund — und der Lauf meldet Kontrast-Verstösse, die kein
// Mensch je zu sehen bekommt. Also wird gelesen wie von einer Leserin, dann
// gemessen.
async function durchblaettern (seite) {
  await seite.evaluate(async () => {
    const schritt = window.innerHeight * 0.8
    const ende = document.documentElement.scrollHeight
    for (let y = 0; y < ende; y += schritt) {
      window.scrollTo(0, y)
      await new Promise(r => setTimeout(r, 60))
    }
    window.scrollTo(0, 0)
  })
  await seite.waitForTimeout(700)
}

const args = process.argv.slice(2)
const check = args.includes('--check')
const spur = args.includes('--spur')
const alles = args.includes('--alles')
const nur = args.includes('--seite') ? args[args.indexOf('--seite') + 1] : null
const nurRegel = args.includes('--regel') ? args[args.indexOf('--regel') + 1] : null
const browserPfad = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium'

const browser = await chromium.launch(
  existsSync(browserPfad) ? { executablePath: browserPfad } : {})
const server = await serviere(ROOT)
let gemessen = 0
const alle = []
const nachRegel = new Map()
const fortgegangen = new Set()   // Brücken-Seiten, die sich selbst weiterschicken

for (const { pfad, artefakt } of seiten()) {
  if (nur && pfad !== nur) continue
  if (spur) console.error(`— ${pfad}`)
  for (const achse of ACHSEN) {
    // Eigener Kontext statt browser.newPage(): axe legt für seine Prüfung
    // eine zweite Seite an, und ein von newPage() erzeugter Kontext lässt
    // genau das nicht zu.
    const kontext = await browser.newContext(
      { viewport: { width: achse.width, height: achse.height } })
    const seite = await kontext.newPage()
    seite.setDefaultTimeout(15000)
    // Was von aussen kommt, wird abgewiesen statt abgewartet: gemessen wird
    // das Blatt, nicht die Leitung.
    await seite.route('**/*', r => {
      const ziel = r.request().url()
      return ziel.startsWith(`http://127.0.0.1:${server.port}`) || ziel.startsWith('data:')
        ? r.continue() : r.abort()
    })
    try {
      await seite.goto(`http://127.0.0.1:${server.port}/${pfad}`,
                       { waitUntil: 'domcontentloaded', timeout: 15000 })
      await seite.waitForTimeout(400)   // Schriften und Nachladungen setzen lassen

      // Manche Blätter sind Brücken: sie lesen den Pfad und schicken weiter
      // (die Kurzlink-404 etwa). Ihr Ziel liegt ausserhalb, wird abgewiesen,
      // und Chromium malt an ihrer Stelle seine eigene Fehlerseite — die dann
      // gemessen würde. Gemessen wird aber das Haus, nicht der Browser: wer
      // fortgeht, wird gezählt und übersprungen.
      if (!seite.url().startsWith(`http://127.0.0.1:${server.port}`)) {
        fortgegangen.add(pfad)
        if (spur) console.error(`  ${achse.tag}\tleitet weiter`)
        continue
      }
      await durchblaettern(seite)

      const bau = new AxeBuilder({ page: seite }).withTags(alles ? [...NORM, ...RAT] : NORM)
      // Physische Farben sind keine Bildschirmflächen: eine gedruckte Karte
      // ist weiss, weil das Papier weiss ist. Solche Blätter stehen im
      // Kontrakt und werden von der Kontrastprüfung ausgenommen — von
      // nichts sonst.
      if (artefakt) bau.disableRules(['color-contrast'])
      const ergebnis = await bau.analyze()
      gemessen++

      const funde = ergebnis.violations
        .filter(v => !nurRegel || v.id === nurRegel)
        .map(v => ({
          id: v.id,
          norm: !v.tags.includes('best-practice'),
          schwere: v.impact || 'unbekannt',
          was: v.help,
          kriterien: v.tags.filter(t => /^wcag\d/.test(t)),
          stellen: v.nodes.map(n => n.target.join(' ')),
          probe: v.nodes[0]?.html?.replace(/\s+/g, ' ').slice(0, 72) || ''
        }))
        .sort((a, b) => b.stellen.length - a.stellen.length)

      for (const f of funde) nachRegel.set(f.id, (nachRegel.get(f.id) || 0) + f.stellen.length)
      if (funde.length) alle.push({ pfad, achse: achse.tag, funde })
      if (spur) console.error(`  ${achse.tag}\t${funde.length || '·'}`)
    } catch (e) {
      alle.push({ pfad, achse: achse.tag,
                  funde: [{ id: 'lädt nicht', norm: true, schwere: 'kritisch',
                            was: e.message.split('\n')[0], kriterien: [], stellen: [], probe: '' }] })
    } finally {
      await kontext.close().catch(() => {})
    }
  }
}
server.zu()
await browser.close()

for (const s of alle) {
  console.log(`!!  ${s.pfad}  (${s.achse})`)
  for (const f of s.funde) {
    const marke = f.norm ? f.schwere : 'rat'
    const kr = f.kriterien.length ? `  [${f.kriterien.join(' ')}]` : ''
    console.log(`        ${f.id}  (${marke}, ${f.stellen.length}×)${kr}`)
    console.log(`            ${f.was}`)
    if (f.stellen.length) console.log(`            ${f.stellen.slice(0, 3).join('  ·  ')}`)
    if (f.probe) console.log(`            «${f.probe}»`)
  }
}

const verstoesse = alle.reduce((s, x) => s + x.funde.filter(f => f.norm).length, 0)
const rat = alle.reduce((s, x) => s + x.funde.filter(f => !f.norm).length, 0)

if (fortgegangen.size) {
  console.log(`\nÜbersprungen, weil sie weiterleiten: ${[...fortgegangen].join(', ')}`)
}

if (nachRegel.size) {
  console.log('\nnach Regel:')
  for (const [id, n] of [...nachRegel.entries()].sort((a, b) => b[1] - a[1])) {
    console.log(`        ${String(n).padStart(4)}×  ${id}`)
  }
}

if (verstoesse) {
  console.log(`\n${verstoesse} Verstoss/Verstösse gegen WCAG 2.2 AA` +
              (rat ? ` (und ${rat} Empfehlung(en))` : '') +
              ` bei ${gemessen} Messungen.`)
  if (check) process.exit(1)
} else {
  console.log(`\nKein Verstoss gegen WCAG 2.2 AA` +
              (rat ? ` (${rat} Empfehlung(en) genannt)` : '') +
              ` bei ${gemessen} Messungen.`)
}

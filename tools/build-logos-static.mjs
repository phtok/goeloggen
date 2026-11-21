// Alle Logos als feste Dateien erzeugen und in einer Liste beschreiben (logos.json).
//
// Der Logo-Generator baut die Sektions-, Bereichs- und Allgemein-Logos erst im Browser
// (apps/logos/engine.js, braucht getBBox). Damit Entwickler und Werkzeuge sie unter
// festen Adressen holen können, rendert dieses Skript sie einmal in Chromium und
// schreibt sie als SVG nach <ziel>/<org>/<form>-<sprache>-<farbe>.svg.
//
// Aufruf:  node tools/build-logos-static.mjs <ziel>   (Standard: _site/assets/logos/alle)
// Läuft im Deploy (deploy-pages.yml), die Dateien liegen nicht im Repo.
import { chromium } from 'playwright-core'
import { mkdirSync, writeFileSync, existsSync } from 'node:fs'
import { join, resolve, dirname } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const wurzel = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const ziel = resolve(process.argv[2] || join(wurzel, '_site/assets/logos/alle'))
const browserPfad = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium'
const SPRACHEN = ['de', 'en', 'fr', 'es']
const FORMEN = { desktop: 'lang', mobile: 'kurz', icon: 'icon', point: 'kreis', square: 'quadrat' }
const MIT_TEXT = new Set(['desktop', 'mobile'])
const FARBEN = { original: 'farbe', white: 'weiss', black: 'schwarz' }

const browser = await chromium.launch(existsSync(browserPfad) ? { executablePath: browserPfad } : {})
const seite = await browser.newPage()
seite.on('pageerror', e => { console.error('Seitenfehler:', e.message); process.exitCode = 1 })
await seite.goto(pathToFileURL(join(wurzel, 'apps/logos/index.html')).href)
await seite.waitForFunction(() => window.LogoEngine && typeof GCI_ORGS !== 'undefined')

const orgs = await seite.evaluate(() => {
  const katVon = {}
  Object.entries(GCI_CATS).forEach(([k, c]) => (c.items || []).forEach(o => { katVon[o] = k }))
  return Object.entries(GCI_ORGS).map(([key, o]) => ({ key, kat: katVon[key] || 'bereiche', ...o }))
})

let anzahl = 0
const liste = {}
for (const o of orgs) {
  const dateien = {}
  const verz = join(ziel, o.key); mkdirSync(verz, { recursive: true })
  for (const [form, formName] of Object.entries(FORMEN)) {
    for (const [modus, farbName] of Object.entries(FARBEN)) {
      for (const sprache of (MIT_TEXT.has(form) ? SPRACHEN : [null])) {
        const svg = await seite.evaluate(({ kat, org, layout, lang, mode }) =>
          window.LogoEngine.svg({ cat: kat === 'allgemein' ? 'allgemein' : kat, org, layout, lang: lang || 'de', mode, txt: '', scale: 2.635 }),
          { kat: o.kat, org: o.key, layout: form, lang: sprache, mode: modus })
        const name = [formName, sprache, farbName].filter(Boolean).join('-') + '.svg'
        writeFileSync(join(verz, name), svg)
        ;(dateien[formName] ||= {})[[sprache || '-', farbName].join('/')] = `${o.key}/${name}`
        anzahl++
      }
    }
  }
  liste[o.key] = { name: { de: o.name_de, en: o.name_en, fr: o.name_fr, es: o.name_es }, kategorie: o.kat, farbe: o.color, dateien }
}
await browser.close()

const basis = 'https://werkzeuge.goetheanum.ch/assets/logos/alle/'
writeFileSync(join(ziel, '..', 'logos.json'), JSON.stringify({
  beschreibung: 'Alle Logos des Goetheanum als feste Dateien (SVG). Adresse = basis + Pfad aus dateien. Die Medien-Logos (Wochenschrift, Videos, my.goetheanum u. a.) stehen mit PNG und JPG in medien/manifest.json.',
  stand: new Date().toISOString().slice(0, 10),
  basis,
  formen: FORMEN, farben: FARBEN, sprachen: SPRACHEN,
  medien: 'https://werkzeuge.goetheanum.ch/assets/logos/medien/manifest.json',
  logos: liste
}, null, 1))
console.log(`${anzahl} Logos von ${orgs.length} Einheiten nach ${ziel}`)

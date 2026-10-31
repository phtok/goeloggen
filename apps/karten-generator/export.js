"use strict";

/* Vektor-Export des Kartentools.
   PDF: jsPDF + svg2pdf (vendor/, lokal) — Text bleibt Text (Goetheanum-
   Schrift v2.7 als TTF eingebettet), Karte und Marker bleiben Pfade.
   Beschnitt (3 mm) und Schnittmarkenzone (5 mm) sind finale Millimeter,
   das A3-Format ist die √2-Skalierung derselben Szene. */

const MM_ZU_PT = 72 / 25.4;
const BESCHNITT_MM = 3;
const MARKEN_MM = 5;

const FORMATE = {
  a4: { breite: 297, hoehe: 210 },
  a3: { breite: 420, hoehe: 297 }
};

const PDF_SCHRIFTEN = [
  ["GoetheanumDeutlich", "../../assets/fonts/goetheanum/Office/GoetheanumSchriftDeutlich.ttf"],
  ["GoetheanumLaut", "../../assets/fonts/goetheanum/Office/GoetheanumSchriftLaut.ttf"],
  ["SourceSans3Semibold", "assets/fonts/SourceSans3-SemiBold.ttf"]
];

function exportGeometrie() {
  const format = FORMATE[state.format] || FORMATE.a4;
  const skala = format.breite / SZENE.breite;
  const beschnitt = state.beschnitt ? BESCHNITT_MM : 0;
  const marken = state.beschnitt && state.marken;
  const rand = beschnitt + (marken ? MARKEN_MM : 0);
  return {
    trimBreite: format.breite,
    trimHoehe: format.hoehe,
    skala, beschnitt, marken, rand,
    seiteBreite: format.breite + 2 * rand,
    seiteHoehe: format.hoehe + 2 * rand
  };
}

// Campuskarte_<Titel>_A4.<endung>: Titel wie getippt, Umlaute aufgelöst,
// Wörter mit Bindestrich, nur Buchstaben, Ziffern und Bindestrich.
function dateiname(endung) {
  const titel = state.titel.trim()
    .replace(/Ä/g, "Ae").replace(/Ö/g, "Oe").replace(/Ü/g, "Ue")
    .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^A-Za-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  const teile = ["Campuskarte", titel, state.format.toUpperCase()].filter(Boolean);
  return `${teile.join("_")}.${endung}`;
}

function exportSvgString(fontCss) {
  const g = exportGeometrie();
  const marken = g.marken
    ? `<g transform="translate(${g.rand} ${g.rand})">`
      + schnittmarkenMarkup(g.trimBreite, g.trimHoehe, BESCHNITT_MM, MARKEN_MM)
      + "</g>"
    : "";
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${g.seiteBreite}mm" height="${g.seiteHoehe}mm" viewBox="0 0 ${g.seiteBreite} ${g.seiteHoehe}">
${fontCss || ""}
<rect width="${g.seiteBreite}" height="${g.seiteHoehe}" fill="#ffffff" />
<g transform="translate(${g.rand} ${g.rand}) scale(${g.skala})">
${szeneMarkup(g.beschnitt / g.skala)}
</g>
${marken}
</svg>`;
}

/* ---------- Hilfen ---------- */

async function dateiAlsBase64(pfad) {
  const antwort = await fetch(pfad);
  if (!antwort.ok) throw new Error(`${pfad}: ${antwort.status}`);
  const bytes = new Uint8Array(await antwort.arrayBuffer());
  let binaer = "";
  const block = 0x8000;
  for (let i = 0; i < bytes.length; i += block) {
    binaer += String.fromCharCode.apply(null, bytes.subarray(i, i + block));
  }
  return btoa(binaer);
}

function herunterladen(name, inhalt, typ) {
  const blob = inhalt instanceof Blob ? inhalt : new Blob([inhalt], { type: typ });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/* ---------- SVG-Download (Webfonts eingebettet) ---------- */

let svgFontCssPromise = null;

function svgFontCss() {
  if (!svgFontCssPromise) {
    svgFontCssPromise = (async () => {
      const [deutlich, laut, wert] = await Promise.all([
        dateiAlsBase64("../../assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.9-Deutlich.woff2"),
        dateiAlsBase64("../../assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.9-Laut.woff2"),
        dateiAlsBase64("../../assets/fonts/goetheanum/Fallback/SourceSans3-SemiBold.woff2")
      ]);
      return `<defs><style>
@font-face { font-family: "GoetheanumDeutlich"; src: url('data:font/woff2;base64,${deutlich}') format('woff2'); }
@font-face { font-family: "GoetheanumLaut"; src: url('data:font/woff2;base64,${laut}') format('woff2'); }
@font-face { font-family: "SourceSans3Semibold"; src: url('data:font/woff2;base64,${wert}') format('woff2'); }
</style></defs>`;
    })().catch((fehler) => {
      console.warn("Schrift nicht einbettbar, SVG ohne Schrift-Einbettung:", fehler);
      svgFontCssPromise = null;
      return "";
    });
  }
  return svgFontCssPromise;
}

/* ---------- PDF: Trim- und Bleed-Box nachtragen ---------- */

// jsPDF kennt nur die MediaBox. Für die Druckerei tragen wir Trim- und
// Bleed-Box im Seiten-Wörterbuch nach und korrigieren die xref-Tabelle
// um den eingefügten Versatz. Alles rein auf Byte-Ebene — die Datei
// enthält komprimierte Binär-Streams, die kein Textdecoder anfassen darf.
function bytesSuchen(bytes, ascii, von, rueckwaerts) {
  const muster = Array.from(ascii, (z) => z.charCodeAt(0));
  const passt = (i) => muster.every((wert, k) => bytes[i + k] === wert);
  if (rueckwaerts) {
    for (let i = Math.min(von, bytes.length - muster.length); i >= 0; i -= 1) {
      if (passt(i)) return i;
    }
  } else {
    for (let i = von; i <= bytes.length - muster.length; i += 1) {
      if (passt(i)) return i;
    }
  }
  return -1;
}

function asciiBytes(text) {
  return Uint8Array.from(text, (z) => z.charCodeAt(0));
}

function druckboxenEinsetzen(bytes, geometrie) {
  const g = geometrie;
  if (!g.rand) return bytes;
  const mediaIndex = bytesSuchen(bytes, "/MediaBox", 0, false);
  if (mediaIndex < 0) return bytes;
  const endeIndex = bytesSuchen(bytes, "]", mediaIndex, false);
  if (endeIndex < 0) return bytes;
  const einfuegePos = endeIndex + 1;

  const zahl = (mm) => (mm * MM_ZU_PT).toFixed(2);
  const anschnitt = g.rand - g.beschnitt;
  const einschub = asciiBytes(
    ` /TrimBox [${zahl(g.rand)} ${zahl(g.rand)} ${zahl(g.seiteBreite - g.rand)} ${zahl(g.seiteHoehe - g.rand)}]`
    + ` /BleedBox [${zahl(anschnitt)} ${zahl(anschnitt)} ${zahl(g.seiteBreite - anschnitt)} ${zahl(g.seiteHoehe - anschnitt)}]`
  );
  const delta = einschub.length;

  const neu = new Uint8Array(bytes.length + delta);
  neu.set(bytes.subarray(0, einfuegePos), 0);
  neu.set(einschub, einfuegePos);
  neu.set(bytes.subarray(einfuegePos), einfuegePos + delta);

  // xref-Tabelle und startxref (reines ASCII am Dateiende) nachziehen.
  const startxrefIndex = bytesSuchen(neu, "startxref", neu.length - 1, true);
  const xrefIndex = startxrefIndex < 0 ? -1 : bytesSuchen(neu, "xref", startxrefIndex - 1, true);
  if (xrefIndex >= 0 && startxrefIndex > xrefIndex) {
    let ende = String.fromCharCode.apply(null, neu.subarray(xrefIndex));
    ende = ende.replace(/(^|\n)(\d{10}) (\d{5}) n/g, (voll, kopf, versatz, generation) => {
      const wert = parseInt(versatz, 10);
      const korrigiert = wert > einfuegePos ? wert + delta : wert;
      return `${kopf}${String(korrigiert).padStart(10, "0")} ${generation} n`;
    });
    ende = ende.replace(/startxref\s+(\d+)/, (voll, wert) => {
      const zahlwert = parseInt(wert, 10);
      return `startxref\n${zahlwert > einfuegePos ? zahlwert + delta : zahlwert}`;
    });
    const endeBytes = asciiBytes(ende);
    const ausgabe = new Uint8Array(xrefIndex + endeBytes.length);
    ausgabe.set(neu.subarray(0, xrefIndex), 0);
    ausgabe.set(endeBytes, xrefIndex);
    return ausgabe;
  }
  return neu;
}

/* ---------- PDF-Export ---------- */

// Das gemalte Blatt geht als Datei-Verweis ins PDF, nicht als Data-URI.
// Befund vom 30. August 2026: svg2pdf zerlegt Data-URIs mit einem Ausdruck,
// dessen Alternative-in-Schleife an der rund 670 000 Zeichen langen Kette
// in manchen Regex-Maschinen (Safari) aussteigt. Greift der Ausdruck nicht,
// hält svg2pdf die Zeichenkette für eine Adresse, rät das Bildformat aus
// ihrer Endung und reicht jsPDF ein verstümmeltes ‹data:image/…› weiter.
// jsPDF wirft ‹files of type UNKNOWN›, svg2pdf fängt den Wurf selbst ab —
// und das Blatt kommt ohne Aquarell heraus, ohne dass jemand etwas merkt.
// Die kurze Datei-Adresse nimmt den Ausdruck aus dem Spiel: das Format
// kommt aus der Endung, die Bytes holt svg2pdf selbst. Der SVG-Export
// behält die Data-URI — dort muss die Datei für sich allein stehen.
function rasterAufDatei(svgElement) {
  const bilder = Array.from(svgElement.querySelectorAll("image"));
  bilder.forEach((bild) => {
    const quelle = bild.getAttribute("href") || bild.getAttribute("xlink:href");
    if (!quelle || !quelle.startsWith("data:image/")) return;
    bild.removeAttribute("xlink:href");
    bild.setAttribute("href", new URL(AQUARELL.datei, document.baseURI).href);
  });
  return bilder.length;
}

let pdfSchriftenPromise = null;

function pdfSchriftenLaden() {
  if (!pdfSchriftenPromise) {
    pdfSchriftenPromise = Promise.all(
      PDF_SCHRIFTEN.map(async ([name, pfad]) => [name, await dateiAlsBase64(pfad)])
    ).catch((fehler) => {
      pdfSchriftenPromise = null;
      throw fehler;
    });
  }
  return pdfSchriftenPromise;
}

// SVG-Text als PDF-Bytes (Blattgrösse in mm). Schriften nur, wo Text im
// SVG steht; die Gegenprobe des Aquarells gilt für jedes Blatt.
async function svgAlsPdfBytes(svgText, breiteMm, hoeheMm, schriften) {
  const svgElement = new DOMParser()
    .parseFromString(svgText, "image/svg+xml").documentElement;
  const raster = rasterAufDatei(svgElement);

  const doc = new jspdf.jsPDF({
    unit: "pt",
    format: [breiteMm * MM_ZU_PT, hoeheMm * MM_ZU_PT],
    orientation: breiteMm >= hoeheMm ? "landscape" : "portrait",
    compress: true
  });
  (schriften || []).forEach(([name, base64]) => {
    doc.addFileToVFS(`${name}.ttf`, base64);
    doc.addFont(`${name}.ttf`, name, "normal");
  });

  await doc.svg(svgElement, {
    x: 0, y: 0,
    width: breiteMm * MM_ZU_PT,
    height: hoeheMm * MM_ZU_PT
  });

  const bytes = new Uint8Array(doc.output("arraybuffer"));
  // Gegenprobe statt Vertrauen: svg2pdf verschluckt einen gescheiterten
  // Bildeinbau lautlos. Trägt die Szene ein Raster, muss das PDF ein
  // Bild-XObject führen — sonst lieber gar keine Datei als ein Blatt
  // ohne Grundkarte.
  if (raster && bytesSuchen(bytes, "/Subtype /Image", 0, false) < 0) {
    throw new Error("Aquarell-Blatt nicht ins PDF übernommen");
  }
  return bytes;
}

async function exportPdf() {
  const g = exportGeometrie();
  const schriften = await pdfSchriftenLaden();
  let bytes = await svgAlsPdfBytes(exportSvgString(""), g.seiteBreite, g.seiteHoehe, schriften);
  bytes = druckboxenEinsetzen(bytes, g);
  herunterladen(dateiname("pdf"), new Blob([bytes], { type: "application/pdf" }), "application/pdf");
}

/* ---------- Grundkarte allein (IDML-Verknüpfung) ----------
   Nur Gelände, Aquarell und Kompass — ohne Marken, Text, Legende, Logo
   und Schnittmarken. Blatt = Endformat plus Beschnitt; die Schnittmarken
   zeichnet InDesign beim Export selbst. */
async function grundkartePdfBytes() {
  const g = exportGeometrie();
  const breite = g.trimBreite + 2 * g.beschnitt;
  const hoehe = g.trimHoehe + 2 * g.beschnitt;
  const svgText = `<svg xmlns="http://www.w3.org/2000/svg" width="${breite}mm" height="${hoehe}mm" viewBox="0 0 ${breite} ${hoehe}">
<g transform="translate(${g.beschnitt} ${g.beschnitt}) scale(${g.skala})">
${grundkarteSzeneMarkup(g.beschnitt / g.skala)}
</g>
</svg>`;
  return { name: "grundkarte.pdf", bytes: await svgAlsPdfBytes(svgText, breite, hoehe), breite, hoehe };
}

/* ---------- IDML (InDesign) ----------
   Grundkarte, Logo und Sonderlogo als verknüpfte PDFs, alles Übrige nativ
   aus szeneModell() — gebaut in idml.js (Modul, erst beim Klick geladen). */

// Stand der Export-Bausteine: bei jeder Änderung an idml.js erhöhen,
// sonst mischt der Browser-Cache alt und neu.
const IDML_BAU = "2026-10-31";

// Die Hausschrift reist mit (SIL OFL, Lizenz liegt bei).
const IDML_SCHRIFTEN = [
  ["Goetheanum-Variabel-v2.9.otf", "../../assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.9.otf"],
  ["OFL.txt", "../../assets/fonts/goetheanum/OFL.txt"]
];

async function dateiBytes(pfad) {
  const antwort = await fetch(pfad);
  if (!antwort.ok) throw new Error(`${pfad}: ${antwort.status}`);
  return new Uint8Array(await antwort.arrayBuffer());
}

const FARB_NAMEN = { rot: "Rot", blau: "Blau", gruen: "Grün", grau: "Grau", gold: "Gold" };

function idmlFarbnamen() {
  const familie = aquarellMarkerStil() ? MARKER_FARBEN_AQUARELL : MARKER_FARBEN;
  const namen = { [TINTE]: "Tinte", [TINTE_LEISE]: "Tinte leise" };
  Object.entries(familie).forEach(([schluessel, hex]) => {
    namen[hex.toLowerCase()] = `Marke ${FARB_NAMEN[schluessel] || schluessel}`;
  });
  return namen;
}

// Breite in Blatt-mm: Laut-Ziffern aus der Vorschubtabelle, Sprache wie
// bei der Zentrierung der Schriftzüge.
function idmlTextBreite(text, schrift, groesse) {
  const zeichen = String(text).split("");
  if (schrift === SCHRIFT_ZAHL && zeichen.every((z) => LAUT_VORSCHUB[z] != null)) {
    return zeichen.reduce((summe, z) => summe + LAUT_VORSCHUB[z], 0) * groesse;
  }
  return textBreiteMm(text, schrift, groesse);
}

// Ein Logo (reine Pfade) als PDF in seiner Endgrösse.
async function logoPdf(name, markup, viewBox, lage, skala) {
  const breite = lage.breite * skala, hoehe = lage.hoehe * skala;
  const svgText = `<svg xmlns="http://www.w3.org/2000/svg" width="${breite}mm" height="${hoehe}mm" viewBox="${viewBox}">${markup}</svg>`;
  return { name, bytes: await svgAlsPdfBytes(svgText, breite, hoehe), breite, hoehe };
}

// Alles, was idml.js für die Karte braucht (Modell, Geometrie, verknüpfte
// PDFs, Farbnamen, Textbreite) – für den eigenen Export und für einbettende
// Werkzeuge (Tagungs-Reader, window.Kartentool.idmlTeile). namen steht vor
// den Farbfeldnamen, damit sie in einer fremden Vorlage nicht kollidieren.
async function idmlTeile(namen = "") {
  const g = exportGeometrie();
  const modell = szeneModell();
  const links = { grundkarte: await grundkartePdfBytes() };
  if (modell.logo) {
    links.logo = await logoPdf("logo.pdf", logoInhalt.markup,
      `0 0 ${logoInhalt.breite} ${logoInhalt.hoehe}`, modell.logo, g.skala);
  }
  if (modell.titelLogo) {
    const l = state.titelLogo;
    links.titellogo = await logoPdf("titellogo.pdf", l.markup,
      `${l.vbX || 0} ${l.vbY || 0} ${l.vbBreite} ${l.vbHoehe}`, modell.titelLogo, g.skala);
  }
  const farbnamen = Object.fromEntries(Object.entries(idmlFarbnamen()).map(([hex, name]) => [hex, namen + name]));
  return {
    modell, geometrie: g, links, farbnamen,
    immerFarben: [TINTE, TINTE_LEISE],
    textBreite: idmlTextBreite,
    schriften: IDML_SCHRIFTEN.map(([name, pfad]) => ({ name, url: new URL(pfad, document.baseURI).href }))
  };
}

async function exportIdml() {
  const teile = await idmlTeile();
  const schriften = await Promise.all(teile.schriften.map(async ({ name, url }) => ({ name, bytes: await dateiBytes(url) })));
  const { baueIdml } = await import(`./idml.js?v=${IDML_BAU}`);
  const zip = await baueIdml({ ...teile, schriften, dateiname: dateiname("idml") });
  herunterladen(dateiname("zip"), new Blob([zip], { type: "application/zip" }), "application/zip");
}

/* ---------- Knöpfe ---------- */

document.getElementById("download-pdf").addEventListener("click", async () => {
  const knopf = document.getElementById("download-pdf");
  const beschriftung = knopf.textContent;
  knopf.disabled = true;
  knopf.textContent = "PDF wird erzeugt …";
  try {
    await exportPdf();
    varianteAblegen();  // Download legt den Stand unter seinem Titel ab
  } catch (fehler) {
    console.error(fehler);
    window.alert("PDF-Export fehlgeschlagen. Bitte Konsole prüfen oder SVG exportieren.");
  } finally {
    knopf.disabled = false;
    knopf.textContent = beschriftung;
  }
});

document.getElementById("download-svg").addEventListener("click", async () => {
  const knopf = document.getElementById("download-svg");
  knopf.disabled = true;
  try {
    const fontCss = await svgFontCss();
    herunterladen(dateiname("svg"), exportSvgString(fontCss), "image/svg+xml");
    varianteAblegen();  // Download legt den Stand unter seinem Titel ab
  } finally {
    knopf.disabled = false;
  }
});

document.getElementById("download-idml").addEventListener("click", async () => {
  const knopf = document.getElementById("download-idml");
  const beschriftung = knopf.textContent;
  knopf.disabled = true;
  knopf.textContent = "IDML wird gepackt …";
  try {
    await exportIdml();
    varianteAblegen();  // Download legt den Stand unter seinem Titel ab
  } catch (fehler) {
    console.error(fehler);
    window.alert("IDML-Export fehlgeschlagen. Bitte Konsole prüfen oder PDF exportieren.");
  } finally {
    knopf.disabled = false;
    knopf.textContent = beschriftung;
  }
});

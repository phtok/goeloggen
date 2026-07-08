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
  ["GoetheanumKlar", "../../assets/fonts/goetheanum/Office/GoetheanumSchriftKlar.ttf"],
  ["GoetheanumDeutlich", "../../assets/fonts/goetheanum/Office/GoetheanumSchriftDeutlich.ttf"]
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

function dateiname(endung) {
  const g = exportGeometrie();
  const teile = ["goetheanum-campuskarte", state.format, "quer"];
  if (g.beschnitt) teile.push("3mm");
  if (g.marken) teile.push("marken");
  return `${teile.join("-")}.${endung}`;
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
      const [deutlich, klar] = await Promise.all([
        dateiAlsBase64("../../assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.7-Deutlich.woff2"),
        dateiAlsBase64("../../assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.7-Klar.woff2")
      ]);
      return `<defs><style>
@font-face { font-family: "GoetheanumDeutlich"; src: url('data:font/woff2;base64,${deutlich}') format('woff2'); }
@font-face { font-family: "GoetheanumKlar"; src: url('data:font/woff2;base64,${klar}') format('woff2'); }
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

async function exportPdf() {
  const g = exportGeometrie();
  const schriften = await pdfSchriftenLaden();
  const svgText = exportSvgString("");
  const svgElement = new DOMParser()
    .parseFromString(svgText, "image/svg+xml").documentElement;

  const doc = new jspdf.jsPDF({
    unit: "pt",
    format: [g.seiteBreite * MM_ZU_PT, g.seiteHoehe * MM_ZU_PT],
    orientation: "landscape",
    compress: true
  });
  schriften.forEach(([name, base64]) => {
    doc.addFileToVFS(`${name}.ttf`, base64);
    doc.addFont(`${name}.ttf`, name, "normal");
  });

  await doc.svg(svgElement, {
    x: 0, y: 0,
    width: g.seiteBreite * MM_ZU_PT,
    height: g.seiteHoehe * MM_ZU_PT
  });

  let bytes = new Uint8Array(doc.output("arraybuffer"));
  bytes = druckboxenEinsetzen(bytes, g);
  herunterladen(dateiname("pdf"), new Blob([bytes], { type: "application/pdf" }), "application/pdf");
}

/* ---------- Knöpfe ---------- */

document.getElementById("download-pdf").addEventListener("click", async () => {
  const knopf = document.getElementById("download-pdf");
  const beschriftung = knopf.textContent;
  knopf.disabled = true;
  knopf.textContent = "PDF wird erzeugt …";
  try {
    await exportPdf();
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
  } finally {
    knopf.disabled = false;
  }
});

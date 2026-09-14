"use strict";

/* PDF des Campusplans — Vektor, wie im Kartentool (jsPDF + svg2pdf, Schrift
   als TTF eingebettet). Blatt 1: Karte links, nummerierte Legende rechts.
   Blatt 2 (und weitere): die Stationen mit Einzeiler, Zugang und Zeiten,
   dazu Link und QR-Code. Nur das Gelände läuft durch svg2pdf; Marken,
   Legende und Text zeichnet jsPDF selbst — so sitzen die Ziffern mittig
   (svg2pdf misst Textbreiten mit fremden Metriken, Learnings § 2).

   Kein Beschnitt, keine Schnittmarken: das Blatt ist für den Drucker
   zuhause, A4 quer. */

const PDF_MM_ZU_PT = 72 / 25.4;
const PDF_SEITE = { b: 297, h: 210 };
const PDF_RAND = 12;
const PDF_SCHRIFTEN_PLAN = [
  ["GoetheanumDeutlich", "../../assets/fonts/goetheanum/Office/GoetheanumSchriftDeutlich.ttf"],
  ["GoetheanumLaut", "../../assets/fonts/goetheanum/Office/GoetheanumSchriftLaut.ttf"],
  ["SourceSans3", "../../assets/fonts/goetheanum/Fallback/SourceSans3-Regular.ttf"],
  ["SourceSans3Semibold", "../karten-generator/assets/fonts/SourceSans3-SemiBold.ttf"]
];
// Druckfarben: Tinte und leise Tinte wie im Kartentool (Learnings § 3),
// Marken im dunklen Gold (Weiss darauf 4.55:1), Anreise im Markenblau.
const PDF_FARBEN = { tinte: "#4e4f4a", leise: "#6e6f6a", marke: "#94702e", anreise: "#0061a9", weiss: "#ffffff" };

let pdfSchriftenVersprechen = null;

async function pdfDateiAlsBase64(pfad) {
  const antwort = await fetch(pfad);
  if (!antwort.ok) throw new Error(`${pfad}: ${antwort.status}`);
  const bytes = new Uint8Array(await antwort.arrayBuffer());
  let binaer = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binaer += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  }
  return btoa(binaer);
}

function pdfSchriften() {
  if (!pdfSchriftenVersprechen) {
    pdfSchriftenVersprechen = Promise.all(
      PDF_SCHRIFTEN_PLAN.map(async ([name, pfad]) => [name, await pdfDateiAlsBase64(pfad)])
    ).catch((fehler) => { pdfSchriftenVersprechen = null; throw fehler; });
  }
  return pdfSchriftenVersprechen;
}

/* Gelände für den Druck: Klassen werden zu Füllungen (svg2pdf liest kein
   CSS), aktive Gebäude tragen das Goetheanum-Blau, jede Fläche eine
   Eigenkontur in Füllfarbe gegen Rasterfugen (Learnings § 5). */
function pdfGelaende(aktiveBauten) {
  const f = (farbe) => `fill="${farbe}" stroke="${farbe}" stroke-width="0.35"`;
  let inhalt = gelaendeInhalt.replace(/<style>[\s\S]*?<\/style>/, "");
  inhalt = inhalt.replace(/class="k-parkflaeche" id="parkflaeche-(\d+)"/g, (voll, nr) => `${f(PALETTE.parkflaeche)} id="parkflaeche-${nr}"`);
  inhalt = inhalt.replace(/class="k-wiese" id="wiese-(klein|gross)"/g, (voll, name) => `${f(PALETTE.campus)} id="wiese-${name}"`);
  inhalt = inhalt.replace(/data-wiese-strich="(klein|gross)"/g, () => `stroke="${PALETTE.campus}"`);
  inhalt = inhalt.replace(
    /<path id="(campusbau-\d+)"([^>]*?)class="k-(goetheanum|gebaeude-campus|akzent)"/g,
    (voll, bauId, mitte) => `<path id="${bauId}"${mitte}${f(aktiveBauten.has(bauId) ? PALETTE.goetheanum : PALETTE["gebaeude-campus"])}`
  );
  inhalt = inhalt.replace(/class="k-([a-z-]+)"/g, (voll, rolle) => f(PALETTE[rolle] || "#cccccc"));
  inhalt = inhalt.replace(/data-ks="([a-z-]+)"/g, (voll, rolle) => `stroke="${PALETTE[rolle] || "#cccccc"}"`);
  return inhalt;
}

function pdfAusschnitt(ids, kastenB, kastenH) {
  // Alle Marken des Plans plus Rand, auf das Seitenverhältnis des Kastens.
  let minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
  ids.forEach((id) => {
    const [x, y] = ortPosition(id);
    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y);
  });
  if (minX > maxX) { minX = 0; minY = 0; maxX = BLATT.breite; maxY = BLATT.hoehe; }
  const rand = 14;
  let b = Math.max(80, maxX - minX + 2 * rand);
  let h = Math.max(60, maxY - minY + 2 * rand);
  const seite = kastenB / kastenH;
  if (b / h < seite) b = h * seite; else h = b / seite;
  return { x: (minX + maxX) / 2 - b / 2, y: (minY + maxY) / 2 - h / 2, b, h, skala: kastenB / b };
}

function pdfDatumText(iso, sprache) {
  if (!iso) return "";
  const [j, m, t] = iso.split("-").map(Number);
  const d = new Date(j, m - 1, t);
  return d.toLocaleDateString(sprache === "en" ? "en-GB" : "de-CH", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}

function pdfQrMalen(doc, text, x, y, groesse) {
  if (typeof qrcode !== "function") return;
  const q = qrcode(0, "M");
  q.addData(text);
  q.make();
  const n = q.getModuleCount();
  const m = groesse / n;
  doc.setFillColor(0, 0, 0);
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (q.isDark(r, c)) doc.rect(x + c * m, y + r * m, m, m, "F");
}

function pdfMarke(doc, x, y, r, text, farbe) {
  doc.setFillColor(farbe);
  doc.setDrawColor(PDF_FARBEN.weiss);
  doc.setLineWidth(0.3);
  doc.circle(x, y, r, "FD");
  doc.setTextColor(PDF_FARBEN.weiss);
  doc.setFont("GoetheanumLaut", "normal");
  doc.setFontSize(r * 1.0 * PDF_MM_ZU_PT);
  doc.text(String(text), x, y + r * 0.02, { align: "center", baseline: "middle" });
}

async function planPdf() {
  const schriften = await pdfSchriften();
  const doc = new jspdf.jsPDF({ unit: "mm", format: "a4", orientation: "landscape", compress: true });
  schriften.forEach(([name, base64]) => {
    doc.addFileToVFS(`${name}.ttf`, base64);
    doc.addFont(`${name}.ttf`, name, "normal");
  });

  const { nummeriert, anreise } = stationen();
  const alleIds = nummeriert.concat(anreise).map((g) => g.id);
  const datum = pdfDatumText(state.datum, state.sprache);
  const titel = state.modus === "plan" ? ui("besuch") : ui("titel");
  const link = planLink();

  /* ---------- Blatt 1: Karte und Legende ---------- */
  const kopfH = 14;
  const kasten = { x: PDF_RAND, y: PDF_RAND + kopfH, b: 178, h: PDF_SEITE.h - PDF_RAND - kopfH - PDF_RAND };
  doc.setTextColor(PDF_FARBEN.tinte);
  doc.setFont("GoetheanumDeutlich", "normal");
  doc.setFontSize(20);
  doc.text(titel, PDF_RAND, PDF_RAND + 7);
  doc.setFont("SourceSans3", "normal");
  doc.setFontSize(10);
  doc.setTextColor(PDF_FARBEN.leise);
  const unter = [datum, `${nummeriert.length} ${ui("stationen")} · ${ui("etwa")} ${dauerText(planMinuten())}`].filter(Boolean).join(" · ");
  doc.text(unter, PDF_RAND, PDF_RAND + 12.5);

  // Gelände als Vektor, auf den Ausschnitt geclippt.
  const aktiveBauten = new Set();
  alleIds.forEach((id) => ortGebaeude(id).forEach((b) => aktiveBauten.add(b)));
  const a = pdfAusschnitt(alleIds, kasten.b, kasten.h);
  const gSkala = KARTE.gelaende.breite / gelaendeMasse.breite;
  const svgText = `<svg xmlns="http://www.w3.org/2000/svg" width="${kasten.b}mm" height="${kasten.h}mm" viewBox="${a.x} ${a.y} ${a.b} ${a.h}">` +
    `<defs><clipPath id="plan-clip"><rect x="${a.x}" y="${a.y}" width="${a.b}" height="${a.h}"/></clipPath></defs>` +
    `<g clip-path="url(#plan-clip)"><rect x="${a.x - 50}" y="${a.y - 50}" width="${a.b + 100}" height="${a.h + 100}" fill="${PALETTE.umgebung}"/>` +
    `<g transform="translate(${KARTE.gelaende.x} ${KARTE.gelaende.y}) scale(${gSkala})">${pdfGelaende(aktiveBauten)}</g></g></svg>`;
  const svgElement = new DOMParser().parseFromString(svgText, "image/svg+xml").documentElement;
  await doc.svg(svgElement, { x: kasten.x, y: kasten.y, width: kasten.b, height: kasten.h });
  doc.setDrawColor(PDF_FARBEN.leise);
  doc.setLineWidth(0.2);
  doc.rect(kasten.x, kasten.y, kasten.b, kasten.h, "S");

  // Marken auf dem Blatt (Blatt-mm → Seiten-mm über den Ausschnitt).
  const aufSeite = (id) => { const [x, y] = ortPosition(id); return [kasten.x + (x - a.x) * a.skala, kasten.y + (y - a.y) * a.skala]; };
  const r = Math.max(2.4, Math.min(3.6, 3.2 * a.skala));
  anreise.forEach((g) => { const [x, y] = aufSeite(g.id); pdfMarke(doc, x, y, r, ortMarker(g.id) || "·", PDF_FARBEN.anreise); });
  nummeriert.forEach((g, i) => { const [x, y] = aufSeite(g.id); pdfMarke(doc, x, y, r, i + 1, PDF_FARBEN.marke); });

  // Legende rechts: Nummer und Name; bei vielen Stationen enger gesetzt,
  // was nicht mehr passt, steht vollständig auf Blatt 2.
  const legX = kasten.x + kasten.b + 8;
  const legB = PDF_SEITE.b - PDF_RAND - legX;
  let zeileH = nummeriert.length > 22 ? 5.2 : 6.6;
  const legStart = kasten.y + 2;
  let y = legStart;
  const legMax = kasten.y + kasten.h;
  const kreisR = zeileH > 6 ? 2.6 : 2.1;
  let uebrig = 0;
  nummeriert.forEach((g, i) => {
    if (y + zeileH > legMax) { uebrig += 1; return; }
    pdfMarke(doc, legX + kreisR, y + zeileH / 2, kreisR, i + 1, PDF_FARBEN.marke);
    doc.setTextColor(PDF_FARBEN.tinte);
    doc.setFont("GoetheanumDeutlich", "normal");
    doc.setFontSize(zeileH > 6 ? 10.5 : 9);
    const name = ortName(g.id);
    const zeilen = doc.splitTextToSize(name, legB - kreisR * 2 - 4);
    doc.text(zeilen[0] + (zeilen.length > 1 ? " …" : ""), legX + kreisR * 2 + 3, y + zeileH / 2, { baseline: "middle" });
    y += zeileH;
  });
  if (anreise.length && y + zeileH * 1.5 < legMax) {
    y += 2;
    doc.setFont("SourceSans3", "normal"); doc.setFontSize(8.5); doc.setTextColor(PDF_FARBEN.leise);
    doc.text(ui("anreise"), legX, y + 3);
    y += 5;
    anreise.forEach((g) => {
      if (y + 5.2 > legMax) return;
      pdfMarke(doc, legX + 2.1, y + 2.6, 2.1, ortMarker(g.id) || "·", PDF_FARBEN.anreise);
      doc.setTextColor(PDF_FARBEN.tinte); doc.setFont("SourceSans3", "normal"); doc.setFontSize(9);
      doc.text(g.id === "wc-goetheanum" ? ui("wc") : ortName(g.id), legX + 7.2, y + 2.6, { baseline: "middle" });
      y += 5.2;
    });
  }
  if (uebrig) {
    doc.setFont("SourceSans3", "normal"); doc.setFontSize(8.5); doc.setTextColor(PDF_FARBEN.leise);
    doc.text(`+ ${uebrig} → ${ui("blatt")} 2`, legX, legMax - 1);
  }
  doc.setFont("SourceSans3", "normal"); doc.setFontSize(7.5); doc.setTextColor(PDF_FARBEN.leise);
  doc.text(link, PDF_RAND, PDF_SEITE.h - 5, { maxWidth: PDF_SEITE.b - 2 * PDF_RAND });

  /* ---------- Blatt 2 ff.: die Stationen ---------- */
  doc.addPage();
  const spalteB = (PDF_SEITE.b - 2 * PDF_RAND - 10) / 2;
  const spalten = [PDF_RAND, PDF_RAND + spalteB + 10];
  let spalte = 0;
  y = PDF_RAND;
  const untenMax = PDF_SEITE.h - PDF_RAND - 30; // Platz für QR und Link unten
  doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(14); doc.setTextColor(PDF_FARBEN.tinte);
  doc.text(`${titel} · ${ui("stationen-titel")}`, PDF_RAND, y + 5);
  y += 12;
  const spaltenStart = y;
  const eintrag = (g, nummer) => {
    const x = spalten[spalte];
    const textX = x + 9;
    const textB = spalteB - 9;
    const name = g.id === "wc-goetheanum" ? ui("wc") : ortName(g.id);
    doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(11);
    const nameZeilen = doc.splitTextToSize(name, textB);
    doc.setFont("SourceSans3", "normal"); doc.setFontSize(9.5);
    const einZeilen = g.einzeiler ? doc.splitTextToSize(t(g.einzeiler), textB) : [];
    const meta = [g.zugang ? t(ZUGANG[g.zugang]) : "", g.dauer ? dauerText(g.dauer) : "", g.zeiten ? t(g.zeiten) : ""].filter(Boolean).join(" · ");
    const geschlossen = state.datum && ortGeschlossenAm(g, state.datum);
    doc.setFontSize(8.5);
    const metaZeilen = meta ? doc.splitTextToSize(meta + (geschlossen ? ` · ${ui("geschlossen-am")}` : ""), textB) : [];
    const hoehe = nameZeilen.length * 4.6 + einZeilen.length * 4.1 + metaZeilen.length * 3.8 + 4;
    if (y + hoehe > untenMax) {
      if (spalte === 0) { spalte = 1; y = spaltenStart; }
      else { doc.addPage(); spalte = 0; y = PDF_RAND; }
    }
    const xx = spalten[spalte], tx = xx + 9;
    if (nummer) pdfMarke(doc, xx + 3, y + 2.6, 2.6, nummer, PDF_FARBEN.marke);
    else pdfMarke(doc, xx + 3, y + 2.6, 2.4, ortMarker(g.id) || "·", PDF_FARBEN.anreise);
    doc.setTextColor(PDF_FARBEN.tinte); doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(11);
    doc.text(nameZeilen, tx, y + 3.6);
    let yy = y + nameZeilen.length * 4.6;
    if (einZeilen.length) {
      doc.setFont("SourceSans3", "normal"); doc.setFontSize(9.5); doc.setTextColor(PDF_FARBEN.tinte);
      doc.text(einZeilen, tx, yy + 2.6);
      yy += einZeilen.length * 4.1;
    }
    if (metaZeilen.length) {
      doc.setFont("SourceSans3", "normal"); doc.setFontSize(8.5); doc.setTextColor(PDF_FARBEN.leise);
      doc.text(metaZeilen, tx, yy + 2.4);
      yy += metaZeilen.length * 3.8;
    }
    y = yy + 4;
  };
  nummeriert.forEach((g, i) => eintrag(g, i + 1));
  anreise.forEach((g) => eintrag(g, 0));

  // Link und QR unten auf dem letzten Blatt.
  const qrG = 22;
  const qrX = PDF_SEITE.b - PDF_RAND - qrG, qrY = PDF_SEITE.h - PDF_RAND - qrG;
  pdfQrMalen(doc, link, qrX, qrY, qrG);
  doc.setFont("SourceSans3", "normal"); doc.setFontSize(8); doc.setTextColor(PDF_FARBEN.leise);
  doc.text(ui("pdf-link-hint"), PDF_RAND, qrY + 4, { maxWidth: qrX - PDF_RAND - 6 });
  doc.setFontSize(7.5);
  doc.text(link, PDF_RAND, qrY + 9, { maxWidth: qrX - PDF_RAND - 6 });

  const name = `campusplan${state.datum ? "-" + state.datum : ""}.pdf`;
  doc.save(name);
}

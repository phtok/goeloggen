"use strict";

/* PDF des Campusplans — Vektor, wie im Kartentool (jsPDF + svg2pdf, Schrift
   als TTF eingebettet). Blatt 1: die Karte des Kartentools selbst (karte.js),
   mit den Orten des Plans in Gehfolge, Titel, Legende und Logo.
   Blatt 2 (und weitere): die Stationen mit Einzeiler, Zugang und Zeiten,
   dazu Link und QR-Code; die Marken dort tragen die Farben der Karte.

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
// Druckfarben: Tinte und leise Tinte wie im Kartentool (Learnings § 3).
// marke/anreise gelten nur, falls das Kartentool für einen Ort keine Farbe
// liefert — sonst führt Blatt 2 die Markenfarbe der Karte.
const PDF_FARBEN = { tinte: "#4e4f4a", leise: "#6e6f6a", marke: "#7a5a20", anreise: "#0061a9", weiss: "#ffffff" };

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

// Wortverbinder und schmale Leerzeichen der Bildschirmfassung kennen die
// PDF-Schriften nicht: Verbinder fällt weg, das schmale wird ein normales.
function pdfText(text) {
  return String(text).replace(/\u2060/g, "").replace(/\u202f/g, " ");
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

  const { nummeriert, anreise, plan } = stationen();
  const datum = pdfDatumText(state.datum, state.sprache);
  const titel = ui("besuch");
  const link = planLink();

  /* ---------- Blatt 1: die Karte des Kartentools ---------- */
  // Dieselbe Blattszene wie im Kartentool (Gebäudenamen, Kompass, Legende,
  // Logo), nur mit den Orten des Plans in Gehfolge — ganz durch svg2pdf.
  const spanne = plan && plan.eintraege.length
    ? spanneText({ von: plan.eintraege[0].von, bis: plan.ende })
    : `${ui("etwa")} ${dauerText(planMinuten())}`;
  const untertitel = [datum, `${nummeriert.length} ${ui("stationen")} · ${spanne}`].filter(Boolean).join(" · ");
  const szene = await kartenSzene({ nummeriert, anreise, titel: ui("besuch"), untertitel: pdfText(untertitel) });
  const farbe = (id, ersatz) => szene.farben[id] || ersatz;
  const svgText = `<svg xmlns="http://www.w3.org/2000/svg" width="${PDF_SEITE.b}mm" height="${PDF_SEITE.h}mm" viewBox="0 0 ${szene.breite} ${szene.hoehe}">${szene.markup}</svg>`;
  const svgElement = new DOMParser().parseFromString(svgText, "image/svg+xml").documentElement;
  await doc.svg(svgElement, { x: 0, y: 0, width: PDF_SEITE.b, height: PDF_SEITE.h });
  let y;

  /* ---------- Blatt 2 ff.: die Stationen ---------- */
  doc.addPage();
  const spalteB = (PDF_SEITE.b - 2 * PDF_RAND - 10) / 2;
  const spalten = [PDF_RAND, PDF_RAND + spalteB + 10];
  let spalte = 0;
  y = PDF_RAND;
  const untenMax = PDF_SEITE.h - PDF_RAND - 30; // Platz für QR und Link unten
  doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(14); doc.setTextColor(PDF_FARBEN.tinte);
  doc.text(`${titel} · ${plan ? ui("zeitplan") : ui("stationen-titel")}`, PDF_RAND, y + 5);
  y += 12;
  const spaltenStart = y;
  // Mit Zeitplan steht die Uhrzeit rechts in der Namenszeile (tabellarisch,
  // G25), Pausen als eigene leise Zeile dazwischen.
  const pausen = {};
  if (plan) plan.eintraege.forEach((e, i) => { const n = plan.eintraege[i + 1]; if (e.pause && n) pausen[n.id] = e; });
  const eintrag = (g, nummer) => {
    const termin = zeitplanVon(plan, g.id);
    const zeitB = termin ? 30 : 0;
    const textB = spalteB - 9;
    const name = ortName(g.id);
    doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(11);
    const nameZeilen = doc.splitTextToSize(name, textB - zeitB);
    doc.setFont("SourceSans3", "normal"); doc.setFontSize(9.5);
    const einZeilen = g.einzeiler ? doc.splitTextToSize(t(g.einzeiler), textB) : [];
    const meta = [g.zugang ? t(ZUGANG[g.zugang]) : "", g.dauer ? dauerText(g.dauer) : "", zeitenText(g)].filter(Boolean).join(" · ");
    const tag = planTag();
    const geschlossen = tag && ortGeschlossenAm(g, tag);
    const live = ausnahmeAm(g, tag);
    const zusatz = (geschlossen ? ` · ${ui("geschlossen-am")}` : "") + (live && !live.zu ? ` · ${ui("an-diesem-tag")} ${live.text}` : "")
      + (plan && plan.ausserhalb.includes(g.id) ? ` · ${ui("ausserhalb")}` : "");
    doc.setFontSize(8.5);
    const metaZeilen = meta || zusatz ? doc.splitTextToSize(pdfText(meta + zusatz), textB) : [];
    const pause = pausen[g.id];
    const hoehe = (pause ? 5 : 0) + nameZeilen.length * 4.6 + einZeilen.length * 4.1 + metaZeilen.length * 3.8 + 4;
    if (y + hoehe > untenMax) {
      if (spalte === 0) { spalte = 1; y = spaltenStart; }
      else { doc.addPage(); spalte = 0; y = PDF_RAND; }
    }
    const xx = spalten[spalte], tx = xx + 9;
    if (pause) {
      doc.setFont("SourceSans3", "normal"); doc.setFontSize(8.5); doc.setTextColor(PDF_FARBEN.leise);
      doc.text(pdfText(`${ui("pause-bis")} ${uhrZeit(pause.bis)}`), tx, y + 2.6);
      y += 5;
    }
    if (nummer) pdfMarke(doc, xx + 3, y + 2.6, 2.6, nummer, farbe(g.id, PDF_FARBEN.marke));
    else pdfMarke(doc, xx + 3, y + 2.6, 2.4, ortMarker(g.id) || "·", farbe(g.id, PDF_FARBEN.anreise));
    doc.setTextColor(PDF_FARBEN.tinte); doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(11);
    doc.text(nameZeilen, tx, y + 3.6);
    if (termin) {
      doc.setFont("SourceSans3Semibold", "normal"); doc.setFontSize(9.5);
      doc.text(pdfText(spanneText(termin)), xx + spalteB, y + 3.6, { align: "right" });
    }
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

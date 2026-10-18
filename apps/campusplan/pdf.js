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

  /* ---------- Blatt 2 ff.: die Stationen ---------- */
  // Drei Spalten. Erst wird jeder Eintrag vermessen, dann verteilt und
  // ausgeglichen (Einträge brechen nie über Spalten).
  // Mit Zeitplan steht die Uhrzeit als eigene Zeile über dem Namen,
  // Pausen als leise Zeile darüber.
  const SPALTEN = 3, ABSTAND = 14;
  const spalteB = (PDF_SEITE.b - 2 * PDF_RAND - (SPALTEN - 1) * ABSTAND) / SPALTEN;
  const spaltenX = Array.from({ length: SPALTEN }, (_, i) => PDF_RAND + i * (spalteB + ABSTAND));
  const kopfY = PDF_RAND + 12;                       // unter dem Titel
  const spalteH = PDF_SEITE.h - PDF_RAND - kopfY;
  const pausen = {};
  if (plan) plan.eintraege.forEach((e, i) => { const n = plan.eintraege[i + 1]; if (e.pause && n) pausen[n.id] = e; });

  const vermessen = (g, nummer) => {
    const termin = zeitplanVon(plan, g.id);
    const textB = spalteB - 9;
    doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(11);
    const nameZeilen = doc.splitTextToSize(ortName(g.id), textB);
    doc.setFont("SourceSans3", "normal"); doc.setFontSize(9.5);
    const einZeilen = einzeilerText(g) ? doc.splitTextToSize(einzeilerText(g), textB) : [];
    const meta = [g.zugang ? t(ZUGANG[g.zugang]) : "", g.dauer ? dauerText(g.dauer) : "", zeitenText(g)].filter(Boolean).join(" · ");
    const tag = planTag();
    const geschlossen = tag && ortGeschlossenAm(g, tag);
    const live = ausnahmeAm(g, tag);
    const zusatz = (geschlossen ? ` · ${ui("geschlossen-am")}` : "") + (live && !live.zu ? ` · ${ui("an-diesem-tag")} ${live.text}` : "")
      + (plan && plan.ausserhalb.includes(g.id) ? ` · ${ui("ausserhalb")}` : "")
      + (zeitenBestaetigt(g) === false ? ` · ${ui("nicht-bestaetigt")}, ${ui("pruefen")}` : "");
    doc.setFontSize(8.5);
    const metaZeilen = meta || zusatz ? doc.splitTextToSize(pdfText(meta + zusatz), textB) : [];
    const pause = pausen[g.id];
    const hoehe = (pause ? 5 : 0) + (termin ? 4.4 : 0) + nameZeilen.length * 4.6 + einZeilen.length * 4.1 + metaZeilen.length * 3.8 + 4;
    return { g, nummer, termin, pause, nameZeilen, einZeilen, metaZeilen, hoehe };
  };

  // Der Weg aufs Telefon gehört nicht zur Liste: er steht fest unten rechts
  // auf dem letzten Blatt — QR-Code an der rechten Kante, Hinweis und Link
  // links daneben. Die letzte Spalte endet darüber.
  const QR_G = 20;
  const qrX = PDF_SEITE.b - PDF_RAND - QR_G, qrY = PDF_SEITE.h - PDF_RAND - QR_G;
  const telefonX = spaltenX[SPALTEN - 1], telefonB = qrX - 4 - telefonX;
  doc.setFont("SourceSans3", "normal"); doc.setFontSize(8);
  const telefonHinweis = doc.splitTextToSize(ui("pdf-link-hint"), telefonB);
  doc.setFontSize(7.5);
  const telefonAdresse = doc.splitTextToSize(link, telefonB);
  const telefonH = Math.max(QR_G, telefonHinweis.length * 3.6 + 2 + telefonAdresse.length * 3.3);
  const telefonOben = PDF_SEITE.h - PDF_RAND - telefonH;
  const telefonZeichnen = () => {
    pdfQrMalen(doc, link, qrX, qrY, QR_G);
    doc.setFont("SourceSans3", "normal"); doc.setFontSize(8); doc.setTextColor(PDF_FARBEN.leise);
    doc.text(telefonHinweis, telefonX, telefonOben + 2.6);
    doc.setFontSize(7.5);
    doc.text(telefonAdresse, telefonX, telefonOben + 2.6 + telefonHinweis.length * 3.6 + 2);
  };

  const zeichnen = (e, xx, y) => {
    const tx = xx + 9;
    if (e.pause) {
      doc.setFont("SourceSans3", "normal"); doc.setFontSize(8.5); doc.setTextColor(PDF_FARBEN.leise);
      doc.text(pdfText(`${ui("pause-bis")} ${uhrZeit(e.pause.bis)}`), tx, y + 2.6);
      y += 5;
    }
    if (e.termin) {
      // Uhrzeit als eigene Zeile über dem Namen, auf der Textkante — wie am Telefon.
      doc.setFont("SourceSans3Semibold", "normal"); doc.setFontSize(9); doc.setTextColor(PDF_FARBEN.tinte);
      doc.text(pdfText(spanneText(e.termin)), tx, y + 2.9);
      y += 4.4;
    }
    if (e.nummer) pdfMarke(doc, xx + 3, y + 2.6, 2.6, e.nummer, farbe(e.g.id, PDF_FARBEN.marke));
    else pdfMarke(doc, xx + 3, y + 2.6, 2.4, ortMarker(e.g.id) || "·", farbe(e.g.id, PDF_FARBEN.anreise));
    doc.setTextColor(PDF_FARBEN.tinte); doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(11);
    doc.text(e.nameZeilen, tx, y + 3.6);
    let yy = y + e.nameZeilen.length * 4.6;
    if (e.einZeilen.length) {
      doc.setFont("SourceSans3", "normal"); doc.setFontSize(9.5); doc.setTextColor(PDF_FARBEN.tinte);
      doc.text(e.einZeilen, tx, yy + 2.6);
      yy += e.einZeilen.length * 4.1;
    }
    if (e.metaZeilen.length) {
      doc.setFont("SourceSans3", "normal"); doc.setFontSize(8.5); doc.setTextColor(PDF_FARBEN.leise);
      doc.text(e.metaZeilen, tx, yy + 2.4);
    }
  };

  // Spalten bei Höchsthöhe h der Reihe nach füllen; die letzte Spalte des
  // letzten Blatts (Index `letzte`) endet über dem Telefon-Block.
  const letzteKap = telefonOben - 6 - kopfY;
  const packen = (liste, h, letzte) => {
    const spalten = [[]];
    let belegt = 0;
    const kap = () => (spalten.length - 1 === letzte ? Math.min(h, letzteKap) : h);
    liste.forEach((e) => {
      if (belegt + e.hoehe > kap() && spalten[spalten.length - 1].length) { spalten.push([]); belegt = 0; }
      spalten[spalten.length - 1].push(e);
      belegt += e.hoehe;
    });
    return spalten;
  };

  const eintraege = nummeriert.map((g, i) => vermessen(g, i + 1)).concat(anreise.map((g) => vermessen(g, 0)));
  // So wenige Blätter wie nötig, und über alle gleichmässig: die kleinste
  // Spaltenhöhe, mit der alles in 3 × Blattzahl Spalten passt.
  const passt = (h, n) => packen(eintraege, h, SPALTEN * n - 1).length <= SPALTEN * n;
  let blattzahl = Math.max(1, Math.ceil(packen(eintraege, spalteH, -1).length / SPALTEN));
  while (!passt(spalteH, blattzahl)) blattzahl += 1;
  let lo = Math.max(...eintraege.map((e) => e.hoehe)), hi = spalteH;
  while (hi - lo > 0.5) {
    const mitte = (lo + hi) / 2;
    if (passt(mitte, blattzahl)) hi = mitte; else lo = mitte;
  }
  const alleSpalten = packen(eintraege, hi, SPALTEN * blattzahl - 1);
  const blaetter = [];
  for (let i = 0; i < alleSpalten.length; i += SPALTEN) blaetter.push(alleSpalten.slice(i, i + SPALTEN));

  blaetter.forEach((spalten, b) => {
    doc.addPage();
    if (b === 0) {
      doc.setFont("GoetheanumDeutlich", "normal"); doc.setFontSize(14); doc.setTextColor(PDF_FARBEN.tinte);
      doc.text(`${titel} · ${plan ? ui("zeitplan") : ui("stationen-titel")}`, PDF_RAND, PDF_RAND + 5);
    }
    spalten.forEach((spalte, i) => {
      let y = kopfY;
      spalte.forEach((e) => { zeichnen(e, spaltenX[i], y); y += e.hoehe; });
    });
    if (b === blaetter.length - 1) telefonZeichnen();
  });

  const name = `campusplan${state.datum ? "-" + state.datum : ""}.pdf`;
  doc.save(name);
}

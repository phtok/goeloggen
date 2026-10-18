"use strict";

/* Die Karte des Campusplans ist die Karte des Kartentools — nicht nachgebaut,
   sondern dort gezeichnet. Das Kartentool läuft unsichtbar im Hintergrund
   (?einbett, wie im Tagungs-Reader apps/lt-reader/) und liefert über seine
   Schnittstelle window.Kartentool die Blattszene als SVG (mm, 297 × 210).
   Der Campusplan gibt nur vor, was darauf steht: die Orte des Plans, ihre
   Folge auf dem Rundweg (Nummern und Legende) und den Titel. */

let kartentoolVersprechen = null;

/* Lagen, die der Gästeplan anders setzt als der Katalog des Kartentools
   (Blatt-mm). Toiletten: die Pille liegt im Katalog auf dem Grossen Saal; im
   Gästeplan stehen beide oft zugleich, die Pille rückt darum unter den
   Schriftzug. Korrekturen, die überall gelten, gehören in den Katalog
   (tools/karten/extract-marker-positionen.py, KORREKTUREN). */
const KATALOG_LAGEN = {
  "wc-goetheanum": [197.24, 121.0]
};

function kartentoolLaden() {
  if (!kartentoolVersprechen) {
    kartentoolVersprechen = new Promise((loesen, ablehnen) => {
      const f = document.createElement("iframe");
      f.src = "../karten-generator/?einbett=1";
      f.title = "Kartentool";
      f.setAttribute("aria-hidden", "true");
      f.tabIndex = -1;
      f.style.cssText = "position:absolute;left:-9999px;top:0;width:1200px;height:900px;visibility:hidden";
      f.addEventListener("load", async () => {
        try { loesen(await f.contentWindow.Kartentool.bereit); }
        catch (fehler) { ablehnen(fehler); }
      }, { once: true });
      document.body.appendChild(f);
    }).catch((fehler) => { kartentoolVersprechen = null; throw fehler; });
  }
  return kartentoolVersprechen;
}

/* Stand für das Kartentool aus dem Plan: Katalog-Orte über ‹an›, Orte, die
   es nur im Gästeplan gibt (NEUE_ORTE), als eigene Marken; die nummerierten
   Stationen in Gehfolge als ‹folge›. Geteilte Katalog-Orte zeigen nur den
   ersten Teil — wie die Liste des Plans. */
function kartenStand(plan) {
  const katalog = new Set(ORTE.map((o) => o.id));
  // Orte mit Kartentool-Zeichen (karte) stehen mit diesen Katalog-Orten auf
  // der Karte statt mit einer eigenen Marke.
  const ids = plan.nummeriert.concat(plan.anreise).flatMap((g) => g.karte || [g.id]);
  const teileAus = {};
  const gebaeudeAn = [];
  const labels = {};
  ids.forEach((id) => {
    const o = ort(id);
    if (o && o.teile) {
      teileAus[id] = {};
      o.teile.forEach((_, i) => { if (i) teileAus[id][i] = true; });
    }
    const g = gast(id);
    if (g && g.gebaeude) gebaeudeAn.push(...g.gebaeude);
    if (g && g.name) labels[id] = t(g.name);   // Name im Gästeplan (z. B. Galerie statt Nordgalerie)
  });
  const eigene = NEUE_ORTE.filter((o) => ids.includes(o.id)).map((o) => ({
    id: o.id, label: t(o.label), farbe: o.farbe || "blau", x: o.positionen[0][0], y: o.positionen[0][1], marker: "0"
  }));
  NEUE_ORTE.forEach((o) => { if (ids.includes(o.id) && o.gebaeude) gebaeudeAn.push(o.gebaeude); });
  return {
    titel: plan.titel || "", untertitel: plan.untertitel || "",
    sprache: state.sprache, format: "a4", beschnitt: false, marken: false,
    an: ids.filter((id) => katalog.has(id)).concat(eigene.map((e) => e.id)),
    eigene, teileAus, notizenAus: {}, labels, markerFarben: {},
    positionen: KATALOG_LAGEN,
    gebaeudeAn, gebaeudeAus: [],
    folge: plan.nummeriert.flatMap((g) => g.karte || [g.id]),
    legende: plan.legende !== false,
    festeNummern: false, kompakt: false, preset: "gedeckt", basiskarte: "vektor",
    ausschnitt: { skala: 1, dx: 0, dy: 0 }
  };
}

/* Blattszene des Plans. Passt die Legende nicht, setzt das Kartentool sie
   kompakt (kleinerer Grad, engere Zeilen). Liefert das SVG-Markup ohne
   Wurzel, die Markenfarben je Ort (für Liste und Stationenblatt) und die
   Lage jeder Marke in Blatt-mm (für Zoom und Abhak-Zeichen am Telefon). */
async function kartenSzene(plan) {
  const K = await kartentoolLaden();
  const stand = kartenStand(plan);
  K.anwenden(stand);
  let markup = K.szene(0);
  if (stand.legende && K.ueberlauf()) {
    K.anwenden({ ...stand, kompakt: true });
    markup = K.szene(0);
  }
  const farben = {};
  stand.an.forEach((id) => { farben[id] = K.markenFarbe(id); });
  const lagen = {};
  stand.an.forEach((id) => {
    const o = ORTE.find((x) => x.id === id) || NEUE_ORTE.find((x) => x.id === id);
    const p = stand.positionen[id] || (o && o.positionen && o.positionen[0]);
    if (p) lagen[id] = p;
  });
  // Orte mit Kartentool-Zeichen: Farbe ihres ersten Zeichens, Lage aus
  // NEUE_ORTE (für Zoom und Abhaken am Telefon).
  plan.nummeriert.filter((g) => g.karte).forEach((g) => {
    farben[g.id] = K.markenFarbe(g.karte[0]);
    const o = NEUE_ORTE.find((x) => x.id === g.id);
    if (o) lagen[g.id] = o.positionen[0];
  });
  return { markup, farben, lagen, breite: K.masse.blatt.breite, hoehe: K.masse.blatt.hoehe };
}

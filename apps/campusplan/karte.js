"use strict";

/* Die Karte des Campusplans ist die Karte des Kartentools — nicht nachgebaut,
   sondern dort gezeichnet. Das Kartentool läuft unsichtbar im Hintergrund
   (?einbett, wie im Tagungs-Reader apps/lt-reader/) und liefert über seine
   Schnittstelle window.Kartentool die Blattszene als SVG (mm, 297 × 210).
   Der Campusplan gibt nur vor, was darauf steht: die Orte des Plans, ihre
   Folge auf dem Rundweg (Nummern und Legende) und den Titel. */

let kartentoolVersprechen = null;

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
  const ids = plan.nummeriert.concat(plan.anreise).map((g) => g.id);
  const teileAus = {};
  const gebaeudeAn = [];
  ids.forEach((id) => {
    const o = ort(id);
    if (o && o.teile) {
      teileAus[id] = {};
      o.teile.forEach((_, i) => { if (i) teileAus[id][i] = true; });
    }
    const g = gast(id);
    if (g && g.gebaeude) gebaeudeAn.push(...g.gebaeude);
  });
  const eigene = NEUE_ORTE.filter((o) => ids.includes(o.id)).map((o) => ({
    id: o.id, label: t(o.label), farbe: "blau", x: o.positionen[0][0], y: o.positionen[0][1], marker: "0"
  }));
  NEUE_ORTE.forEach((o) => { if (ids.includes(o.id) && o.gebaeude) gebaeudeAn.push(o.gebaeude); });
  return {
    titel: plan.titel || "", untertitel: plan.untertitel || "",
    sprache: state.sprache, format: "a4", beschnitt: false, marken: false,
    an: ids.filter((id) => katalog.has(id)).concat(eigene.map((e) => e.id)),
    // Die Toiletten-Pille liegt im Katalog genau auf dem Grossen Saal; im
    // Gästeplan stehen beide oft zugleich — die Pille rückt darum in den
    // freien Teil des Baus darunter (beide bleiben im Goetheanum).
    eigene, teileAus, notizenAus: {}, labels: {}, markerFarben: {},
    positionen: { "wc-goetheanum": [197.24, 134.5] },
    gebaeudeAn, gebaeudeAus: [],
    folge: plan.nummeriert.map((g) => g.id),
    festeNummern: false, kompakt: false, preset: "gedeckt", basiskarte: "vektor",
    ausschnitt: { skala: 1, dx: 0, dy: 0 }
  };
}

/* Blattszene des Plans. Passt die Legende nicht, setzt das Kartentool sie
   kompakt (kleinerer Grad, engere Zeilen). Liefert das SVG-Markup ohne
   Wurzel und die Markenfarben je Ort (für Liste und Stationenblatt). */
async function kartenSzene(plan) {
  const K = await kartentoolLaden();
  const stand = kartenStand(plan);
  K.anwenden(stand);
  let markup = K.szene(0);
  if (K.ueberlauf()) {
    K.anwenden({ ...stand, kompakt: true });
    markup = K.szene(0);
  }
  const farben = {};
  stand.an.forEach((id) => { farben[id] = K.markenFarbe(id); });
  return { markup, farben, breite: K.masse.blatt.breite, hoehe: K.masse.blatt.hoehe };
}

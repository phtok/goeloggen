// Wirkungs-Lesart der Sommer-Aktion – Stand 8. August 2026, letzter Fristtag.
// Verteilt die Anmeldungen OHNE UTM-Spur (352 von 926) auf die Gebiete.
// Methode wie am 7. August, nur mit einem Fenster mehr (die Fristtage):
//   1) Grundlinie – die Tage vor der ersten Mail-Welle geben die Rate der
//      spurlosen Anmeldungen je Tag; sie wird auf jedes Fenster fortgeschrieben.
//   2) Ueberschuss eines Fensters -> nach den GEMESSENEN Anteilen desselben
//      Fensters verteilt (was im Hellen dominiert, dominiert auch im Dunkeln).
//   3) Grundlinien-Block -> nach der Selbstauskunft verteilt (61 Antworten).
// Aufruf: node docs/wirkungs-lesart-08-08.js

// Fenster: Tage, Anmeldungen ohne Spur, gemessene Anteile im selben Fenster.
const FENSTER = [
  { name:'Grundlinie · 3.–16. Juli',   tage:14, dunkel: 52, anzeigeLief:false,
    gemessen:{ social:7, mailing:4, organik:2 } },
  { name:'Welle 1 · 17.–23. Juli',     tage: 7, dunkel: 69, anzeigeLief:true,
    gemessen:{ mailing:80, newsletter:4, organik:2, social:2, bezahlt:1 } },
  { name:'Zwischenfeld · 24.–29. Juli',tage: 6, dunkel: 42, anzeigeLief:true,
    gemessen:{ mailing:13, newsletter:6, social:1, organik:1 } },
  { name:'Welle 2 · 30. Juli–6. Aug.', tage: 8, dunkel: 89, anzeigeLief:false,
    gemessen:{ mailing:138, popup:18, newsletter:8, social:4, bezahlt:2, organik:1 } },
  { name:'Fristtage · 7.–8. Aug.',     tage: 2, dunkel:100, anzeigeLief:false,
    gemessen:{ mailing:234, newsletter:20, popup:17, social:5, organik:4 } }
];

// Selbstauskunft der dunklen Anmeldungen (61 Antworten, 58 einordenbar).
// Traegt den Grundlinien-Block; «mail» heisst dort Newsletter, denn in der
// Grundlinie lief kein Mailer – nur die beiden Eroeffnungs-Newsletter.
const SELBST = { newsletter:22, organik:14, empfehlung:15, social:3, print:2, bezahlt:2 };

// Die bezahlte Anzeige wird NICHT als Anteil gerechnet, sondern als feste Zahl.
// Grund: Sie ist seit dem 24. Juli aus (letzter Klick 26. Juli). Ihr Beitrag
// steht damit absolut fest und darf nicht schrumpfen, nur weil das Dunkelfeld
// durch die Mail-Wellen gewachsen ist – ein Anteil taete genau das. Die Zahl
// stammt aus der Abschalt-Probe: rund 8–12 Abos insgesamt, davon 3 gemessen
// (docs/abschaltprobe-anzeige-27-07.md).
const BEZAHLT_DUNKEL = 6;

const summe = o => Object.values(o).reduce((a, b) => a + b, 0);
const rate  = FENSTER[0].dunkel / FENSTER[0].tage;

const out = {};
const add = (k, v) => { out[k] = (out[k] || 0) + v; };

// Selbstauskunft-Schluessel, einmal ohne «bezahlt» (fuer Fenster ohne Anzeige).
const selbstAnteile = (mitBezahlt) => {
  const s = { ...SELBST };
  if (!mitBezahlt){ s.organik += s.bezahlt; s.bezahlt = 0; }
  const g = summe(s);
  return Object.fromEntries(Object.entries(s).map(([k, v]) => [k, v / g]));
};

for (const f of FENSTER){
  const grund = Math.min(f.dunkel, rate * f.tage);
  const ueber = f.dunkel - grund;

  const sa = selbstAnteile(f.anzeigeLief);
  for (const [k, a] of Object.entries(sa)) add(k, grund * a);

  const g = summe(f.gemessen);
  if (ueber > 0 && g > 0){
    for (const [k, n] of Object.entries(f.gemessen)) add(k, ueber * n / g);
  }
}

// Anzeige auf die feste Zahl setzen; die Differenz traegt das groesste Gebiet.
{
  const diff = (out.bezahlt || 0) - BEZAHLT_DUNKEL;
  out.bezahlt = BEZAHLT_DUNKEL;
  const groesstes = Object.keys(out).filter(k => k !== 'bezahlt')
    .sort((a, b) => out[b] - out[a])[0];
  out[groesstes] += diff;
}

const DUNKEL = FENSTER.reduce((s, f) => s + f.dunkel, 0);

// Dieselbe Rundung wie dunkelVerteilen() im Cockpit: je Gebiet kaufmaennisch
// runden, den Rest dem groessten Gebiet geben. Ohne diese Angleichung stuenden
// im Dokument andere Zahlen als auf der Seite – genau die Drift, die eine
// datierte Lesart verhindern soll.
const ANTEILE_ROH = {};
{
  const anteile = Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v / DUNKEL]));
  for (const [k, a] of Object.entries(anteile)) ANTEILE_ROH[k] = Math.round(a * 1000) / 1000;
  let verteilt = 0, groesstes = null, max = -1;
  for (const [k, a] of Object.entries(anteile)){
    const n = Math.round(DUNKEL * Math.round(a * 1000) / 1000);
    out[k] = n; verteilt += n;
    if (a > max){ max = a; groesstes = k; }
  }
  if (groesstes && verteilt !== DUNKEL) out[groesstes] += (DUNKEL - verteilt);
}
// Gemessenes Feld ueber alle Fenster – fuer die Spalte «dazu gemessen».
const GEMESSEN = {};
FENSTER.forEach(f => Object.entries(f.gemessen).forEach(([k, n]) => GEMESSEN[k] = (GEMESSEN[k] || 0) + n));

console.log('Grundlinie:', rate.toFixed(2), 'Anmeldungen ohne Spur je Tag');
console.log('Dunkelfeld gesamt:', DUNKEL, '· gemessen:', summe(GEMESSEN),
            '· Aktion:', DUNKEL + summe(GEMESSEN), '\n');

const zeilen = Object.entries(out).sort((a, b) => b[1] - a[1]);
let anteilSumme = 0, dunkelSumme = 0;
console.log('Gebiet          dunkel  Anteil   gemessen   gesamt');
for (const [k, v] of zeilen){
  const anteil = v / DUNKEL;
  const d = Math.round(v);
  anteilSumme += Math.round(anteil * 1000) / 1000; dunkelSumme += d;
  console.log(k.padEnd(14),
    String(d).padStart(6),
    (anteil * 100).toFixed(1).padStart(7) + ' %',
    String(GEMESSEN[k] || 0).padStart(8),
    String(d + (GEMESSEN[k] || 0)).padStart(8));
}
console.log('\nProbe · Anteile:', anteilSumme.toFixed(3), '· verteilt:', dunkelSumme, 'von', DUNKEL);
// Diese Anteile stehen in CONFIG.dunkel.anteile im Cockpit. Die Restzuteilung
// oben laesst die gerundeten Stueckzahlen exakt aufgehen – deshalb ergeben die
// Anteile hier nicht in jedem Fall wieder genau die Zeilen der Tabelle.
console.log('\nAnteile fuer CONFIG.dunkel.anteile (Summe ' +
  Object.values(ANTEILE_ROH).reduce((a, b) => a + b, 0).toFixed(3) + '):');
console.log(ANTEILE_ROH);

// Einnahmen-Perspektive Sommer-Aktion 2026 – Stand 8. August (letzter Fristtag)
// Preise aus CONFIG.preise (echt, Stand 17.7.), Kurs eurChf 0.93.
var EURCHF = 0.93;

// [produkt, format, waehrung, intervall, aktive Abos, Preis je Periode]
var SEG = [
  ['gtv', 'stream',  'eur', 'jaehrlich',  74, 149.0],   // 73 standard + 1 ermaessigt (Fallback Standardpreis)
  ['gtv', 'stream',  'eur', 'monatlich', 475,  14.9],
  ['wos', 'digital', 'chf', 'jaehrlich',   1, 109.0],
  ['wos', 'digital', 'chf', 'monatlich',  15,  10.9],
  ['wos', 'digital', 'eur', 'jaehrlich',  21,  99.0],
  ['wos', 'digital', 'eur', 'monatlich', 210,   9.9],
  ['wos', 'papier',  'chf', 'jaehrlich',   8, 149.0],
  ['wos', 'papier',  'chf', 'monatlich',  12,  14.9],
  ['wos', 'papier',  'eur', 'jaehrlich',  16, 139.0],
  ['wos', 'papier',  'eur', 'monatlich',  70,  13.9]
];

var SZENARIEN = [
  { name: 'Vorsichtig', gtv: 0.35, wos: 0.55, monate: 7  },
  { name: 'Erwartet',   gtv: 0.50, wos: 0.70, monate: 9  },
  { name: 'Gut',        gtv: 0.65, wos: 0.85, monate: 11 }
];

function chf(eur, waehrung){ return waehrung === 'eur' ? eur * EURCHF : eur; }
function f(n){ return Math.round(n).toLocaleString('de-CH'); }

// Decke: alle bleiben, monatliche zahlen volle 12 Monate.
var decke = 0, decken = 0;
SEG.forEach(function(s){
  var jahr = s[3] === 'jaehrlich' ? s[5] : s[5] * 12;
  decke += chf(jahr * s[4], s[2]); decken += s[4];
});
console.log('Decke (100 %, volle 12 Monate): CHF ' + f(decke) + ' aus ' + decken + ' Abos\n');

SZENARIEN.forEach(function(sz){
  var sum = 0, bleiben = 0, jeProdukt = { gtv: 0, wos: 0 };
  SEG.forEach(function(s){
    var quote = s[0] === 'gtv' ? sz.gtv : sz.wos;
    var n = s[4] * quote;
    var jahr = s[3] === 'jaehrlich' ? s[5] : s[5] * sz.monate;
    var betrag = chf(jahr * n, s[2]);
    sum += betrag; bleiben += n; jeProdukt[s[0]] += betrag;
  });
  console.log(sz.name.padEnd(11) +
    ' | bleiben ' + String(Math.round(bleiben)).padStart(3) +
    ' | CHF ' + f(sum).padStart(7) +
    ' | gtv ' + f(jeProdukt.gtv).padStart(6) +
    ' | wos ' + f(jeProdukt.wos).padStart(6) +
    ' | je Abo ' + f(sum / bleiben));
});

// Empfindlichkeit: nur der Monats-Faktor, Quoten des Erwartet-Falls.
console.log('\nEmpfindlichkeit (Quoten wie «Erwartet», nur Monate variiert):');
[6, 8, 9, 10, 12].forEach(function(m){
  var sum = 0;
  SEG.forEach(function(s){
    var quote = s[0] === 'gtv' ? 0.50 : 0.70;
    var jahr = s[3] === 'jaehrlich' ? s[5] : s[5] * m;
    sum += chf(jahr * s[4] * quote, s[2]);
  });
  console.log('  ' + m + ' Monate: CHF ' + f(sum));
});

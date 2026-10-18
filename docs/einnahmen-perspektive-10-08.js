// Einnahmen-Perspektive Sommer-Aktion 2026 – Stand 10. August (nach Aktionsende).
// Preise aus CONFIG.preise (echt, Stand 17.7.), Kurs eurChf 0.93.
// Basis: sommer2026_stats, Status «gekuendigt» zaehlt nicht mit.
// Gegenueber dem 8. August hat sich allein die MENGE geaendert: die Zaehlregel
// «Verlaengerungen zaehlen nicht» (View sommer2026_neuabos) nimmt bei
// goetheanum.tv 40 Zeilen weg und traegt 11 nach, die Schlusstage bringen bei
// der Wochenschrift zu. Quoten, Monats-Faktoren und Methode sind unveraendert.
var EURCHF = 0.93;

// [produkt, format, waehrung, intervall, aktive Abos, Preis je Periode]
var SEG = [
  ['gtv', 'stream',  'eur', 'jaehrlich',  81, 149.0],   // 80 standard + 1 ermaessigt (Fallback Standardpreis)
  ['gtv', 'stream',  'eur', 'monatlich', 532,  14.9],
  ['wos', 'digital', 'chf', 'jaehrlich',   1, 109.0],
  ['wos', 'digital', 'chf', 'monatlich',  17,  10.9],
  ['wos', 'digital', 'eur', 'jaehrlich',  25,  99.0],
  ['wos', 'digital', 'eur', 'monatlich', 249,   9.9],
  ['wos', 'papier',  'chf', 'jaehrlich',   9, 149.0],
  ['wos', 'papier',  'chf', 'monatlich',  12,  14.9],
  ['wos', 'papier',  'eur', 'jaehrlich',  17, 139.0],
  ['wos', 'papier',  'eur', 'monatlich',  76,  13.9]
];

var SZENARIEN = [
  { name: 'Vorsichtig', gtv: 0.35, wos: 0.55, monate: 7  },
  { name: 'Erwartet',   gtv: 0.50, wos: 0.70, monate: 9  },
  { name: 'Gut',        gtv: 0.65, wos: 0.85, monate: 11 }
];

function chf(eur, waehrung){ return waehrung === 'eur' ? eur * EURCHF : eur; }
function f(n){ return Math.round(n).toLocaleString('de-CH'); }

// Mengen zur Kontrolle: je Produkt, je Intervall.
var jeProdukt = {}, monatlich = 0, jaehrlich = 0, papier = 0;
SEG.forEach(function(s){
  jeProdukt[s[0]] = (jeProdukt[s[0]] || 0) + s[4];
  if (s[3] === 'monatlich') monatlich += s[4]; else jaehrlich += s[4];
  if (s[1] === 'papier') papier += s[4];
});
console.log('Aktive Abos: ' + (jeProdukt.gtv + jeProdukt.wos) +
  ' (gtv ' + jeProdukt.gtv + ', wos ' + jeProdukt.wos + ')');
console.log('davon monatlich ' + monatlich + ', jaehrlich ' + jaehrlich +
  ' (' + (jaehrlich / (monatlich + jaehrlich) * 100).toFixed(1) + ' %), Papier ' + papier + '\n');

// Decke: alle bleiben, monatliche zahlen volle 12 Monate.
var decke = 0, decken = 0;
SEG.forEach(function(s){
  var jahr = s[3] === 'jaehrlich' ? s[5] : s[5] * 12;
  decke += chf(jahr * s[4], s[2]); decken += s[4];
});
console.log('Decke (100 %, volle 12 Monate): CHF ' + f(decke) + ' aus ' + decken + ' Abos\n');

SZENARIEN.forEach(function(sz){
  var sum = 0, bleiben = 0, je = { gtv: 0, wos: 0 };
  SEG.forEach(function(s){
    var quote = s[0] === 'gtv' ? sz.gtv : sz.wos;
    var n = s[4] * quote;
    var jahr = s[3] === 'jaehrlich' ? s[5] : s[5] * sz.monate;
    var betrag = chf(jahr * n, s[2]);
    sum += betrag; bleiben += n; je[s[0]] += betrag;
  });
  console.log(sz.name.padEnd(11) +
    ' | bleiben ' + String(Math.round(bleiben)).padStart(4) +
    ' | CHF ' + f(sum).padStart(7) +
    ' | gtv ' + f(je.gtv).padStart(6) +
    ' | wos ' + f(je.wos).padStart(6) +
    ' | je Abo ' + f(sum / bleiben));
});

// Empfindlichkeit: nur der Monats-Faktor, Quoten des Erwartet-Falls.
console.log('\nEmpfindlichkeit (Quoten wie «Erwartet», nur Monate variiert):');
var vor = null;
[6, 8, 9, 10, 12].forEach(function(m){
  var sum = 0;
  SEG.forEach(function(s){
    var quote = s[0] === 'gtv' ? 0.50 : 0.70;
    var jahr = s[3] === 'jaehrlich' ? s[5] : s[5] * m;
    sum += chf(jahr * s[4] * quote, s[2]);
  });
  console.log('  ' + m + ' Monate: CHF ' + f(sum));
  if (m === 8) vor = sum; else if (m === 9) console.log('  → ein Monat mehr: CHF ' + f(sum - vor));
});

// Kosten je Abo und Rueckfluss – erst vollstaendig, wenn die internen Stunden
// eingetragen sind. Erfasst am 10. August: CHF 769.70.
var KOSTEN = 769.70;
var alle = decken;
console.log('\nKosten erfasst CHF ' + KOSTEN.toFixed(2) + ' auf ' + (alle) + ' aktive Abos' +
  ' (1042 Anmeldungen insgesamt): CHF ' + (KOSTEN / 1042).toFixed(2) + ' je Anmeldung.');

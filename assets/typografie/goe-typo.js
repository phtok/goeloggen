/* =============================================================================
   goe-typo.js – Typografie-Engine der Hausregeln, wiederverwendbar.
   -----------------------------------------------------------------------------
   Quelle der Wahrheit bleibt assets/typografie/typo-regeln.yaml. Diese Datei
   liest nichts Eigenes hinein, sie führt nur aus: laden() holt die Regeln,
   pruefeFehler() behebt Eindeutiges automatisch, findeEmpfehlungen() markiert
   Urteilsfragen. Kein Rendering, kein DOM – das bleibt Sache der Seite, die
   diese Bibliothek einbindet (z. B. apps/editor/).
   ============================================================================= */
(function (root) {
  "use strict";

  function scalar(v) {
    v = v.trim();
    if (v.length >= 2 && v[0] === v[v.length - 1] && (v[0] === "'" || v[0] === '"')) {
      var inner = v.slice(1, -1);
      return v[0] === "'" ? inner.split("''").join("'") : inner;
    }
    return v;
  }

  // Mini-Parser für die flache Regelliste – spiegelt tools/typo-check.py, damit
  // beide Seiten (Hook und Browser) exakt dieselbe Datei ohne Bibliothek lesen.
  function parseYaml(text) {
    var lines = text.split(/\r?\n/), rules = [], cur = null;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (/^\s*#/.test(line) || !line.trim()) continue;
      var m = line.match(/^-\s+(\w+):\s*(.*)$/);
      if (m) {
        if (cur) rules.push(cur);
        cur = {};
        cur[m[1]] = scalar(m[2]);
        continue;
      }
      m = line.match(/^\s+(\w+):\s*(.*)$/);
      if (m && cur) cur[m[1]] = scalar(m[2]);
    }
    if (cur) rules.push(cur);
    return rules;
  }

  function laden(url) {
    return fetch(url).then(function (r) { return r.text(); }).then(parseYaml);
  }

  // Wendet eine einzelne Regel auf einen bereits gefundenen Treffer an –
  // dieselbe Regex noch einmal auf den Treffer selbst, damit $1/$2 stimmen.
  function korrigiereTreffer(rule, treffer) {
    return treffer.replace(new RegExp(rule.erkennen), rule.korrektur);
  }

  // Umgebung eines Treffers fürs Verständnis in der Marginalspalte – der Treffer
  // selbst bleibt exakt (er wird programmatisch ersetzt), nur die Anzeige bekommt
  // ein paar Zeichen mehr Satz drumherum, an der nächsten Wortgrenze gekappt.
  var KONTEXT_PAD = 18;
  function kontext(text, start, end) {
    var vor = text.slice(Math.max(0, start - KONTEXT_PAD), start);
    var nach = text.slice(end, Math.min(text.length, end + KONTEXT_PAD));
    if (start - KONTEXT_PAD > 0) vor = "…" + vor.replace(/^\S*\s?/, "");
    if (end + KONTEXT_PAD < text.length) nach = nach.replace(/\s?\S*$/, "") + "…";
    return { vor: vor, nach: nach };
  }

  // Behebt alle ‹fehler›-Regeln automatisch, protokolliert jede Änderung mit Kontext.
  function pruefeFehler(text, rules) {
    var log = [], out = text;
    rules.filter(function (r) { return r.schwere === "fehler" && r.erkennen && r.korrektur; })
      .forEach(function (rule) {
        var re = new RegExp(rule.erkennen, "g"), m, stueckchen = [], pos = 0;
        while ((m = re.exec(out))) {
          if (m[0].length === 0) { re.lastIndex++; continue; }
          var korrigiert = korrigiereTreffer(rule, m[0]);
          if (korrigiert !== m[0]) {
            var k = kontext(out, m.index, m.index + m[0].length);
            log.push({ ruleId: rule.id, regel: rule.regel, vorher: m[0], nachher: korrigiert, kontextVor: k.vor, kontextNach: k.nach });
          }
          stueckchen.push(out.slice(pos, m.index), korrigiert);
          pos = m.index + m[0].length;
        }
        stueckchen.push(out.slice(pos));
        out = stueckchen.join("");
      });
    return { text: out, log: log };
  }

  // Findet ‹empfehlung›-Regeln als offene Fragen (nicht automatisch verändert).
  // Überlappende Treffer verschiedener Regeln: der frühere gewinnt.
  function findeEmpfehlungen(text, rules) {
    var funde = [];
    rules.filter(function (r) { return r.schwere === "empfehlung" && r.erkennen && r.korrektur; })
      .forEach(function (rule) {
        var re = new RegExp(rule.erkennen, "g"), m;
        while ((m = re.exec(text))) {
          if (m[0].length === 0) { re.lastIndex++; continue; }
          var korrektur = korrigiereTreffer(rule, m[0]);
          if (korrektur !== m[0]) {
            var k = kontext(text, m.index, m.index + m[0].length);
            funde.push({ ruleId: rule.id, regel: rule.regel, start: m.index, end: m.index + m[0].length, original: m[0], korrektur: korrektur, kontextVor: k.vor, kontextNach: k.nach });
          }
        }
      });
    funde.sort(function (a, b) { return a.start - b.start; });
    var kept = [], lastEnd = -1;
    funde.forEach(function (f) {
      if (f.start >= lastEnd) { kept.push(f); lastEnd = f.end; }
    });
    return kept;
  }

  // Urteils-Regeln (pruefung: lm) – (noch) kein Regex, brauchen ein Sprachmodell.
  function lmRegeln(rules) {
    return rules.filter(function (r) { return r.pruefung === "lm"; });
  }

  function zeichenzahl(text) {
    var ohneLeerzeichen = text.replace(/\s/g, "").length;
    var woerter = (text.trim().match(/\S+/g) || []).length;
    return { zeichen: text.length, ohneLeerzeichen: ohneLeerzeichen, woerter: woerter };
  }

  root.GoeTypo = { laden: laden, parseYaml: parseYaml, pruefeFehler: pruefeFehler, findeEmpfehlungen: findeEmpfehlungen, lmRegeln: lmRegeln, zeichenzahl: zeichenzahl };
})(window);

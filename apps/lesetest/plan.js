/* Lesetest · Zuteilung (geteilt von Test, Druckbogen und Auswertung).
   Acht Gruppen. Reihenfolge der Längen fest (kurz → lang). Je Länge zwei
   Texte (A/B) und zwei Schriften (G = Goetheanum Klar, S = Source Sans 3).
   Über die acht Gruppen kommt jede Kombination aus Text und Schrift je Länge
   genau zweimal vor; jede Person liest zwei Texte in jeder Schrift, und jede
   Schrift steht gleich oft an jeder Stelle. */
(function () {
  const SCHRIFTEN = ["GSGS", "SGSG", "GSSG", "SGGS"];
  const TEXTE = ["ABAB", "BABA"];
  function plan(gruppe) {
    const s = SCHRIFTEN[gruppe % 4], t = TEXTE[gruppe < 4 ? 0 : 1];
    return [1, 2, 3, 4].map((laenge, i) => {
      const text = window.LESETEXTE.find((x) => x.laenge === laenge && x.set === t[i]);
      return { pos: i + 1, laenge, text, schrift: s[i] };
    });
  }
  window.LESEPLAN = { plan, gruppen: 8 };
  window.LESEBACKEND = {
    url: "https://dagcsnfrlbpxcmdimnrw.supabase.co",
    key: "sb_publishable_SXhY0mrhXjdTnjbJ5Uobtg_zAXW_xGY",
    async rpc(name, body) {
      const r = await fetch(`${this.url}/rest/v1/rpc/${name}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", apikey: this.key, Authorization: `Bearer ${this.key}` },
        body: JSON.stringify(body || {}),
      });
      if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
      const t = await r.text();
      return t ? JSON.parse(t) : null;
    },
  };
})();

/* =============================================================================
   Goetheanum – Begriffe & gängige Übersetzungen (eine Quelle der Wahrheit)
   -----------------------------------------------------------------------------
   Wiederkehrende institutionelle Begriffe, die auf Karten, Signaturen, Titeln
   und Seiten identisch erscheinen müssen. Vier Sprachen wie goe-orgs.js.

   status:
     'fest'   – in den Werkzeugen bestätigt / unstrittig (de & en).
     'pruefen'– fr/es sind Vorschläge der gebräuchlichen offiziellen Namen und
                vom Auftraggeber zu RATIFIZIEREN (Maschine schlägt vor, Mensch
                ratifiziert). Nach Prüfung auf 'fest' setzen.

   Korrigieren = diese Datei bearbeiten. Werkzeuge sollen sie EINBINDEN, nicht
   kopieren (sonst driftet das Bild – vgl. die abgewichene Sektions-Kopie).
   ============================================================================= */
const GOE_TERMS = {
  "goetheanum": {
    de: "Goetheanum", en: "Goetheanum", fr: "Goetheanum", es: "Goetheanum",
    status: "fest", note: "Eigenname – in allen Sprachen gleich."
  },
  "aag": {
    de: "Allgemeine Anthroposophische Gesellschaft",
    en: "General Anthroposophical Society",
    fr: "Société anthroposophique universelle",
    es: "Sociedad Antroposófica General",
    status: "pruefen", note: "de/en aus den Werkzeugen bestätigt; fr/es offizielle Namen – prüfen."
  },
  "hochschule": {
    de: "Freie Hochschule für Geisteswissenschaft",
    en: "School of Spiritual Science",
    fr: "École de science de l’esprit",
    es: "Escuela de Ciencia Espiritual",
    status: "pruefen", note: "de/en bestätigt; fr/es prüfen."
  },
  "geisteswissenschaft": {
    de: "Geisteswissenschaft",
    en: "Spiritual Science",
    fr: "Science de l’esprit",
    es: "Ciencia Espiritual",
    status: "pruefen", note: "de/en bestätigt; fr/es prüfen."
  },
  "sektion": {
    de: "Sektion", en: "Section", fr: "Section", es: "Sección",
    status: "fest"
  },
  "vorstand": {
    de: "Vorstand", en: "Executive Board", fr: "Comité directeur", es: "Junta directiva",
    status: "pruefen", note: "en aus goe-orgs bestätigt; fr/es prüfen."
  },
  "leiter": {
    de: "Leiter / Leiterin", en: "Leader",
    fr: "Responsable", es: "Responsable",
    status: "pruefen", note: "Rollen-Präfix (‹Leiter der … Sektion›); fr/es prüfen."
  },
  "am-goetheanum": {
    de: "am Goetheanum", en: "at the Goetheanum",
    fr: "au Goetheanum", es: "en el Goetheanum",
    status: "pruefen", note: "Ortsangabe-Zusatz; prüfen."
  },
  "schweiz": {
    de: "Schweiz", en: "Switzerland", fr: "Suisse", es: "Suiza",
    status: "fest", note: "Land (Dornach, CH)."
  }
};

if (typeof window !== "undefined") window.GOE_TERMS = GOE_TERMS;

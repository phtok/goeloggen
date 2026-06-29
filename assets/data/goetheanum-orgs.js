/*
 * Goetheanum – Organisationen (Sektionen, Bereiche, Teilbereiche).
 * EINZIGE QUELLE DER WAHRHEIT für Logo-Namen und -Farben.
 * Geladen von Logo-Generator UND Signatur-Generator.
 *
 * Neuen Eintrag hinzufügen:
 *   1) in ORGS einen Schlüssel mit name_de/name_en/short_de/short_en/color ergänzen
 *   2) den Schlüssel in CATS unter der passenden Kategorie (items) listen
 * Farbe der allgemeinen/administrativen Einträge: Goetheanum-Blau #0061a9.
 */
var ORGS={
  "it": {
    "name_de": "IT-Abteilung",
    "name_en": "IT Department",
    "name_fr": "Département informatique",
    "name_es": "Departamento de TI",
    "short_de": "IT",
    "short_en": "IT",
    "short_fr": "IT",
    "short_es": "IT",
    "color": "#0061a9"
  },
  "goetheanum": {
    "name_de": "Goetheanum",
    "name_en": "Goetheanum",
    "name_fr": "Goetheanum",
    "name_es": "Goetheanum",
    "short_de": "Goetheanum",
    "short_en": "Goetheanum",
    "short_fr": "Goetheanum",
    "short_es": "Goetheanum",
    "color": "#0061a9"
  },
  "aas": {
    "name_de": "Allgemeine Anthroposophische Sektion",
    "name_en": "General Anthroposophical Section",
    "name_fr": "Section d'anthroposophie générale",
    "name_es": "Sección Antroposófica General",
    "short_de": "Allgemeine Anthroposophie",
    "short_en": "General Anthroposophy",
    "short_fr": "Anthroposophie générale",
    "short_es": "Antroposofía General",
    "color": "#a24f8a"
  },
  "ps": {
    "name_de": "Pädagogische Sektion",
    "name_en": "Pedagogical Section",
    "name_fr": "Section pédagogique",
    "name_es": "Sección Pedagógica",
    "short_de": "Pädagogik",
    "short_en": "Pedagogy",
    "short_fr": "Pédagogie",
    "short_es": "Pedagogía",
    "color": "#3b4881"
  },
  "ms": {
    "name_de": "Medizinische Sektion",
    "name_en": "Medical Section",
    "name_fr": "Section médicale",
    "name_es": "Sección médica",
    "short_de": "Medizin",
    "short_en": "Medicine",
    "short_fr": "Médecine",
    "short_es": "Medicina",
    "color": "#5f5599"
  },
  "nws": {
    "name_de": "Naturwissenschaftliche Sektion",
    "name_en": "Natural Science Section",
    "name_fr": "Section des sciences naturelles",
    "name_es": "Sección de Ciencias Naturales",
    "short_de": "Naturwissenschaften",
    "short_en": "Natural Science",
    "short_fr": "Sciences naturelles",
    "short_es": "Ciencias Naturales",
    "color": "#1e7b6e"
  },
  "lws": {
    "name_de": "Sektion für Landwirtschaft",
    "name_en": "Section for Agriculture",
    "name_fr": "Section d'agriculture",
    "name_es": "Sección de Agricultura",
    "short_de": "Landwirtschaft",
    "short_en": "Agriculture",
    "short_fr": "Agriculture",
    "short_es": "Agricultura",
    "color": "#63b145"
  },
  "sbk": {
    "name_de": "Sektion für Bildende Künste",
    "name_en": "Visual Arts Section",
    "name_fr": "Section des arts plastiques",
    "name_es": "Sección de Artes Plásticas",
    "short_de": "Bildende Künste",
    "short_en": "Visual Arts",
    "short_fr": "Arts plastiques",
    "short_es": "Artes Plásticas",
    "color": "#d072a0"
  },
  "ssw": {
    "name_de": "Sektion für Schöne Wissenschaften",
    "name_en": "Section for the Literary Arts and Humanities",
    "name_fr": "Belles-Lettres",
    "name_es": "Sección de Bellas Artes",
    "short_de": "Schöne Wissenschaften",
    "short_en": "Literary Arts and Humanities",
    "short_fr": "Belles-Lettres",
    "short_es": "Bellas Artes",
    "color": "#5168c0"
  },
  "szw": {
    "name_de": "Sektion für Sozialwissenschaften",
    "name_en": "Section for Social Sciences",
    "name_fr": "Section des sciences sociales",
    "name_es": "Sección de Ciencias Sociales",
    "short_de": "Sozialwissenschaften",
    "short_en": "Social Sciences",
    "short_fr": "Sciences sociales",
    "short_es": "Ciencias Sociales",
    "color": "#df4164"
  },
  "js": {
    "name_de": "Jugendsektion",
    "name_en": "Youth Section",
    "name_fr": "Section jeunesse",
    "name_es": "Sección de Jóvenes",
    "short_de": "Jugendsektion",
    "short_en": "Youth Section",
    "short_fr": "Section jeunesse",
    "short_es": "Jóvenes",
    "color": "#ff675d"
  },
  "srmk": {
    "name_de": "Sektion für Redende und Musizierende Künste",
    "name_en": "Section for the Performing Arts",
    "name_fr": "Art de la parole et de la musique",
    "name_es": "Sección de Artes de la Palabra y Música",
    "short_de": "Redende und Musizierende Künste",
    "short_en": "Performing Arts",
    "short_fr": "Arts de la parole et musique",
    "short_es": "Artes de la Palabra y Música",
    "color": "#598ddc"
  },
  "mas": {
    "name_de": "Mathematisch-Astronomische Sektion",
    "name_en": "Section for Mathematics and Astronomy",
    "name_fr": "Section mathématique-astronomie",
    "name_es": "Sección Matemático-Astronómica",
    "short_de": "Mathematik und Astronomie",
    "short_en": "Mathematics and Astronomy",
    "short_fr": "Mathématique-astronomie",
    "short_es": "Matemático-Astronómica",
    "color": "#2e54a4"
  },
  "hpise": {
    "name_de": "Sektion für Heilpädagogik und inklusive soziale Entwicklung",
    "name_en": "Section for Inclusive Social Development",
    "short_de": "Heilpädagogik und inklusive soziale Entwicklung",
    "short_en": "Inclusive Social Development",
    "color": "#f98a3c",
    "name_fr": "Pédagogie spécialisée et développement social inclusif",
    "name_es": "Sección para el Desarrollo Social Inclusivo",
    "short_fr": "Développement social inclusif",
    "short_es": "Desarrollo Social Inclusivo"
  },
  "bauadmin": {
    "name_de": "Bau-Administration",
    "name_en": "Building Administration",
    "name_fr": "Administration des bâtiments",
    "name_es": "Administración de edificios",
    "short_de": "Bau-Administration",
    "short_en": "Building Administration",
    "short_fr": "Administration des bâtiments",
    "short_es": "Administración de edificios",
    "color": "#b15359"
  },
  "buehne": {
    "name_de": "Bühne",
    "name_en": "Stage",
    "name_fr": "Scène",
    "name_es": "Goetheanum Escenario",
    "short_de": "Bühne",
    "short_en": "Stage",
    "short_fr": "Scène",
    "short_es": "Escenario",
    "color": "#968250"
  },
  "dokumentation": {
    "name_de": "Dokumentation",
    "name_en": "Documentation",
    "name_fr": "Documentation",
    "name_es": "Documentación",
    "short_de": "Dokumentation",
    "short_en": "Documentation",
    "short_fr": "Documentation",
    "short_es": "Documentación",
    "color": "#0061a9"
  },
  "empfang": {
    "name_de": "Empfang",
    "name_en": "Reception",
    "name_fr": "Réception",
    "name_es": "Recepción",
    "short_de": "Empfang",
    "short_en": "Reception",
    "short_fr": "Réception",
    "short_es": "Recepción",
    "color": "#0061a9"
  },
  "kommunikation": {
    "name_de": "Kommunikation",
    "name_en": "Communication",
    "name_fr": "Communication",
    "name_es": "Comunicación",
    "short_de": "Kommunikation",
    "short_en": "Communication",
    "short_fr": "Communication",
    "short_es": "Comunicación",
    "color": "#0061a9"
  },
  "studium": {
    "name_de": "Studium",
    "name_en": "Studies",
    "name_fr": "Études",
    "name_es": "Estudios",
    "short_de": "Studium",
    "short_en": "Studies",
    "short_fr": "Études",
    "short_es": "Estudios",
    "color": "#0061a9"
  },
  "campus": {
    "name_de": "Campus",
    "name_en": "Campus",
    "name_fr": "Campus",
    "name_es": "Campus",
    "short_de": "Campus",
    "short_en": "Campus",
    "short_fr": "Campus",
    "short_es": "Campus",
    "color": "#0061a9"
  },
  "archiv": {
    "name_de": "Archiv",
    "name_en": "Archive",
    "name_fr": "Archives",
    "name_es": "Archivo",
    "short_de": "Archiv",
    "short_en": "Archive",
    "short_fr": "Archives",
    "short_es": "Archivo",
    "color": "#0061a9"
  },
  "personalwesen": {
    "name_de": "Personalwesen",
    "name_en": "Human Resources",
    "name_fr": "Ressources humaines",
    "name_es": "Recursos Humanos",
    "short_de": "Personalwesen",
    "short_en": "Human Resources",
    "short_fr": "Ressources humaines",
    "short_es": "Recursos Humanos",
    "color": "#0061a9"
  },
  "kunstsammlung": {
    "name_de": "Kunstsammlung",
    "name_en": "Art Collection",
    "name_fr": "Collection d'art",
    "name_es": "Colección de arte",
    "short_de": "Kunstsammlung",
    "short_en": "Art Collection",
    "short_fr": "Collection d'art",
    "short_es": "Colección de arte",
    "color": "#0061a9"
  },
  "finanzwesen": {
    "name_de": "Finanzwesen",
    "name_en": "Finance",
    "name_fr": "Finances",
    "name_es": "Finanzas",
    "short_de": "Finanzwesen",
    "short_en": "Finance",
    "short_fr": "Finances",
    "short_es": "Finanzas",
    "color": "#0061a9"
  },
  "betriebsdienst": {
    "name_de": "Betriebsdienst",
    "name_en": "Operations",
    "name_fr": "Services opérationnels",
    "name_es": "Servicios operativos",
    "short_de": "Betriebsdienst",
    "short_en": "Operations",
    "short_fr": "Services opérationnels",
    "short_es": "Servicios operativos",
    "color": "#0061a9"
  },
  "bibliothek": {
    "name_de": "Bibliothek",
    "name_en": "Library",
    "name_fr": "Bibliothèque",
    "name_es": "Biblioteca",
    "short_de": "Bibliothek",
    "short_en": "Library",
    "short_fr": "Bibliothèque",
    "short_es": "Biblioteca",
    "color": "#0061a9"
  },
  "gaertnerei": {
    "name_de": "Gärtnerei",
    "name_en": "Gardens",
    "name_fr": "Jardins",
    "name_es": "Jardín del Goetheanum",
    "short_de": "Gärtnerei",
    "short_en": "Gardens",
    "short_fr": "Jardins",
    "short_es": "Jardín",
    "color": "#63b145"
  },
  "saaldienst": {
    "name_de": "Saaldienst",
    "name_en": "Hall Service",
    "name_fr": "Service de salle",
    "name_es": "Servicio de sala",
    "short_de": "Saaldienst",
    "short_en": "Hall Service",
    "short_fr": "Service de salle",
    "short_es": "Servicio de sala",
    "color": "#0061a9"
  },
  "freiwilligenarbeit": {
    "name_de": "Freiwilligenarbeit",
    "name_en": "Volunteer Work",
    "name_fr": "Bénévolat",
    "name_es": "Trabajo Voluntario",
    "short_de": "Freiwilligenarbeit",
    "short_en": "Volunteer Work",
    "short_fr": "Bénévolat",
    "short_es": "Trabajo Voluntario",
    "color": "#0061a9"
  },
  "leitung": {
    "name_de": "Leitung",
    "name_en": "Management",
    "name_fr": "Direction",
    "name_es": "Dirección",
    "short_de": "Leitung",
    "short_en": "Management",
    "short_fr": "Direction",
    "short_es": "Dirección",
    "color": "#0061a9"
  },
  "vorstand": {
    "name_de": "Vorstand",
    "name_en": "Executive Board",
    "name_fr": "Conseil d'administration",
    "name_es": "Junta Directiva",
    "short_de": "Vorstand",
    "short_en": "Executive Board",
    "short_fr": "Conseil d'administration",
    "short_es": "Junta Directiva",
    "color": "#0061a9"
  },
  "betriebsleitung": {
    "name_de": "Betriebsleitung",
    "name_en": "Operations Management",
    "name_fr": "Direction des opérations",
    "name_es": "Dirección de operaciones",
    "short_de": "Betriebsleitung",
    "short_en": "Operations Management",
    "short_fr": "Direction des opérations",
    "short_es": "Dirección de operaciones",
    "color": "#0061a9"
  },
  "medienarbeit": {
    "name_de": "Medienarbeit",
    "name_en": "Media Work",
    "name_fr": "Travail médiatique",
    "name_es": "Relaciones con los medios de comunicación",
    "short_de": "Medienarbeit",
    "short_en": "Media Work",
    "short_fr": "Travail médiatique",
    "short_es": "Relaciones con los medios",
    "color": "#0061a9"
  },
  "mitgliedersekretariat": {
    "name_de": "Mitgliedersekretariat",
    "name_en": "Membership Office",
    "name_fr": "Secrétariat des membres",
    "name_es": "Secretaría de miembros",
    "short_de": "Mitgliedersekretariat",
    "short_en": "Membership Office",
    "short_fr": "Secrétariat des membres",
    "short_es": "Secretaría de miembros",
    "color": "#0061a9"
  },
  "raumplanung": {
    "name_de": "Raumplanung",
    "name_en": "Space Planning",
    "name_fr": "Planification spatiale",
    "name_es": "Planificación espacial",
    "short_de": "Raumplanung",
    "short_en": "Space Planning",
    "short_fr": "Planification spatiale",
    "short_es": "Planificación espacial",
    "color": "#0061a9"
  },
  "studio": {
    "name_de": "Studio",
    "name_en": "Studio",
    "name_fr": "Studio",
    "name_es": "Estudio",
    "short_de": "Studio",
    "short_en": "Studio",
    "short_fr": "Studio",
    "short_es": "Estudio",
    "color": "#0061a9"
  },
  "subscriptions": {
    "name_de": "Abos · Subscriptions",
    "name_en": "Abos · Subscriptions",
    "name_fr": "Abos · Subscriptions",
    "name_es": "Abos · Subscriptions",
    "short_de": "Subscriptions",
    "short_en": "Subscriptions",
    "short_fr": "Subscriptions",
    "short_es": "Subscriptions",
    "color": "#0061a9"
  }
};

var CATS={
  "allgemein": {
    "label_de": "Allgemein",
    "label_en": "General",
    "items": [
      "goetheanum",
      "buehne"
    ]
  },
  "sektionen": {
    "label_de": "Sektionen",
    "label_en": "Sections",
    "items": [
      "aas",
      "js",
      "mas",
      "ms",
      "nws",
      "ps",
      "sbk",
      "hpise",
      "lws",
      "srmk",
      "ssw",
      "szw"
    ]
  },
  "bereiche": {
    "label_de": "Bereiche",
    "label_en": "Divisions",
    "items": [
      "bauadmin",
      "dokumentation",
      "empfang",
      "gaertnerei",
      "kommunikation",
      "studium"
    ]
  },
  "teilbereiche": {
    "label_de": "Teilbereiche",
    "label_en": "Subdivisions",
    "items": [
      "archiv",
      "betriebsdienst",
      "betriebsleitung",
      "bibliothek",
      "campus",
      "finanzwesen",
      "freiwilligenarbeit",
      "it",
      "kunstsammlung",
      "leitung",
      "medienarbeit",
      "mitgliedersekretariat",
      "personalwesen",
      "raumplanung",
      "saaldienst",
      "studio",
      "subscriptions",
      "vorstand"
    ]
  }
};

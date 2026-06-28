# Goetheanum Grafik – Strategieblatt & Wesensanalyse

*Arbeitsstand. Grundlage: Bestandsaufnahme der vorhandenen Konzepte, ein
Strategie-Interview sowie gründliche Recherche zu Marty Neumeiers Markenstrategie
und zu vergleichbaren „Design-System-durch-Alltagswerkzeug"-Ansätzen
(öffentliche Design-Systeme, Design-Tokens, Universitäts-Generatoren, Vorlagen-Tools).*

---

## 1. Strategieblatt nach Neumeier (eine Seite)

Aufgebaut auf Neumeiers **Strategischer Pyramide** (Purpose → Mission/Vision →
Ziele, dazu Werte) und seiner **Brand-Commitment-Matrix** (Kunde ↔ Organisation),
mit dem **Onliness-Statement** als Herzstück.

### Purpose — warum es uns gibt (ändert sich nie)
> Damit das Goetheanum nach außen so **klar, würdig und unverwechselbar** erscheint,
> wie es im Innern gemeint ist – getragen von allen, die für es schreiben, gestalten
> und sprechen.

### Onliness-Statement — das ZAG (Herzstück)
> Die **Goetheanum-Werkzeugkiste** ist die **EINZIGE** Hausgrafik-Umgebung, die die
> Corporate Identity des Goetheanum nicht als Regelwerk *beschreibt*, sondern sie in
> **einfachen Alltagswerkzeugen verkörpert** – sodass **jede mitarbeitende Person ohne
> Designkenntnis** in **Minuten** markenkonformes Material erzeugt, in einer Zeit, in
> der Identität sonst in Wildwuchs und Beliebigkeit zerfällt.

*(Raster: WAS = Hausgrafik-Umgebung · WIE = CI verkörpert statt beschrieben · WER =
Mitarbeitende ohne Designkenntnis · WO = Goetheanum/AAG · WARUM = korrektes Material
in Minuten · WANN = Zeit der gestalterischen Beliebigkeit.)*

### Vision — Bild des Gelingens
> In wenigen Jahren entsteht **alles, was das Goetheanum nach außen gibt** – Signaturen,
> Karten, Briefe, Plakate, Programme, Folder, Schilder – durch diese Werkzeuge. Es ist
> auf einen Blick „Goetheanum", und die Menschen benutzen die Werkzeuge **gern**, weil
> sie schneller zu einem schöneren Ergebnis kommen als auf jedem anderen Weg.

### Mission — der Plan, Wert zu schaffen
> Ein **gemeinsames Fundament** (Schrift, Farben, Logo-Aufbau, Typografie-Regeln als
> eine Quelle) und eine **wachsende Reihe von Werkzeugen mit Leitplanken** bereitstellen,
> die den markenkonformen Weg zum **einfachsten** Weg machen – und die selbst Vorbild der
> CI sind, die sie durchsetzen.

### Werte — wie wir arbeiten
- **Klarheit** – wenige Mittel, präzise gesetzt.
- **Würde & Sorgfalt** – das Erscheinungsbild ist Ausdruck einer Haltung.
- **Einfachheit/Zugänglichkeit** – kein Login-Hürdenlauf, kein Handbuch nötig.
- **Eigenständigkeit** – Mitarbeitende werden befähigt, nicht abhängig gemacht.
- **Offenheit** – ein lebendes System, transparent gepflegt.
- **Datensparsamkeit** – anonym, kein Tracking von Personen.

### Brand-Commitment-Matrix (Ausrichtung Mensch ↔ Haus)
| Ebene | Mitarbeitende (Kunde) | Goetheanum Grafik (wir) |
|---|---|---|
| Identität ↔ Purpose | „Ich vertrete das Goetheanum und will es nicht falsch darstellen." | Würdiges, einheitliches Außenbild |
| Bedürfnis ↔ Onliness | „Ich brauche schnell korrektes Material, ohne Designer." | Die einzige Umgebung, die CI in Alltagswerkzeugen verkörpert |
| Haltung ↔ Werte | Sorgfalt, Zugehörigkeit, Freude am guten Ergebnis | Klarheit, Würde, Einfachheit, Eigenständigkeit |

### Ziele (kurzfristig, 1–3)
1. **Fundament fertigstellen** und die drei laufenden Werkzeuge sichtbar darauf heben.
2. **Öffnen** für die Mitarbeitendenschaft mit einem ersten, freudvollen Satz.
3. **Annahme** belegen (anonyme Nutzungszahlen) und daraus die nächsten Werkzeuge ableiten.

> *Hinweis zu Zeithorizonten:* Neumeiers Pyramide ordnet Purpose (nie) → Mission/Vision
> (langfristig) → Ziele (1–5 J.). Die exakten Jahreszahlen sind in der Literatur
> uneinheitlich; hier bewusst als Größenordnung, nicht als feste Zahl.

---

## 2. Wesensanalyse – was tragend ist, was wir mitnehmen, was wir fallen lassen

### Das Wesensfundament (darauf baut alles, jetzt und für jedes weitere Werkzeug)
1. **Organisations- & Farbsystem** – `assets/data/goetheanum-orgs.js`: 34 Organisationen,
   je Hausfarbe, Namen in 4 Sprachen. **Die** Datenwurzel. Wird von Logo- und
   Signatur-Generator genutzt; jedes weitere Werkzeug zieht daraus.
2. **Hausschrift v2.6** + Reparatur-Pipeline (`tools/goetheanum-fontfix/`) + Fallbacks.
   Auditiert, reproduzierbar, als Webfont gehostet. Die typografische Grundlage.
3. **Design-Tokens** – `design-system/tokens.css` + `tokens.json` (DTCG). Eine Quelle
   für Farben, Typo, Abstände, Radien.
4. **Logo-Aufbau als abrufbarer Baustein** – *aktuell dupliziert* in Logo-Generator
   und GTV-Naming. **Schlüssel-Refactor:** in ein gemeinsames Modul („Logo-Engine")
   herausziehen, das aus Org + Variante + Sprache ein korrektes Lockup als SVG liefert –
   **abrufbar für jedes Werkzeug** (Visitenkarten, Briefe, Plakate, Folder, Programme, Schilder).
5. **Typografie-Regelwerk** – `typografie.html` als Regeln + maschinenlesbare Tokens/Checks.
6. **Komponenten-Schicht** – `design-system/base.css` (Kopf/Fuß, Karten, Knöpfe, Felder).
7. **Manifest + Übersicht** – `tools.json` + `start/` (selbstrendernd, wachstumsfähig).
8. **Anonyme Statistik** – Supabase-Muster (insert-only) + Privacy-Haltung.

### Mitnehmen & weiterbetreiben (laufende Tools, schrittweise aufs Fundament heben)
- **Logo-Generator** (live), **Visitenkarten** (live), **Signatur** (live, reifstes Tool),
  **GTV-Naming** (beta), **Schriften-Übersicht** (live).

### Parken (gute Konzepte, aber nicht jetzt – sie binden Kraft)
- **Campus-Kartentool** – sehr gut spezifiziert (`docs/specs/`), aber großer Bau. Später.
- **Brand-Portrait-Generator** (KI/GPU) – durchdacht, aber eigener Schwerpunkt mit
  Infrastruktur-Abhängigkeiten (`reference/material/`). Klar abgegrenzt halten, später.
- **Jahrgaenge-Sammlung**, **gtv-subs** – nicht Teil der CI-Werkzeugkiste.

### Aus dem Mitarbeitenden-Produkt heraushalten (≠ wegwerfen)
- **Werkstatt-/Font-Entwicklungstools** (proof, kerning, ineinander, zuordnen,
  ligvorschau, werkzeug): wichtig für die *Pflege der Schrift*, aber **kein**
  Mitarbeitendenwerkzeug. In einen internen „Werkstatt"-Bereich, nicht in den
  geöffneten Satz.
- **Alt-Einstiege/Doppelungen** konsolidieren (Redirect-Aliasse behalten).

---

## 3. Architektur – ein gemeinsamer Kern, viele Werkzeuge

Damit jedes Werkzeug die CI *trägt und ist*, bauen alle auf demselben Kern auf
(„dogfooding": die Werkzeuge selbst sind im Hausbild gestaltet).

```
core/  (gemeinsamer Kern – einmal, von allen genutzt)
  brand-data   Organisationen, Farben, Sprachen        (heute goetheanum-orgs.js)
  tokens       Farben/Typo/Abstände/Radien + Hausschrift (tokens.css/.json)
  logo         Logo-Aufbau → SVG (Org + Variante + Sprache)  ← ENTDUPLIZIEREN
  components    Kopf/Fuß, Felder, Knöpfe, Export-Leiste   (base.css + Web-Components)
  export        SVG / PNG / PDF, Druck mit Beschnitt+Marken (aus Kartentool-Spec)
  analytics     anonyme Statistik (Supabase, insert-only)

tools/ (Editoren & Generatoren, komponieren den Kern)
  logo · visitenkarten · signatur · brief · plakat · folder · programm · schild …
```

**Prinzip:** Neue Werkzeuge entstehen durch **Komposition** des Kerns + Eintrag in
`tools.json`. Wachstum kostet wenig, Konsistenz ist eingebaut.

---

## 4. Was wir von anderen übernehmen (Recherche-Essenz)

**Aus erfolgreichen Design-Systemen (GOV.UK, USWDS, Carbon, Material, Atlassian, Polaris):**
- Durchsetzung gelingt **nicht über Verbote, sondern weil der konforme Weg der
  einfachste ist** (Selbstbedienung statt Rücksprache).
- **Tokens als einzige Quelle der Wahrheit** verbinden Design und Code; eine Änderung
  propagiert überall (Skalierungs-Hebel).
- **Reifegradmodell statt Big-Bang:** stufenweise Adoption (erst Farben/Typo, dann
  Komponenten) senkt Widerstand.
- **Konformität einbacken**, nicht prüfen: Werkzeuge, die *nur* korrekten Output
  erzeugen können, ersetzen manuelle Kontrolle.
- **Winziges Kernteam + transparente Governance** (offener Backlog, klare Kriterien)
  reicht für ein großes System.
- **Verlässliche Versionierung/Deprecation** schafft Vertrauen.

**Aus Institutions-Generatoren (UW–Madison, Boise State, Berkeley, Marq an Unis):**
- **Element-Lock:** Logo/Schrift/Farbe/Layout sperren, nur Text-/Bildzonen öffnen –
  „kaputt machen" wird unmöglich. (Deckt sich mit der Entscheidung *strenge Leitplanken*.)
- **Ein zentrales Lockup-System** statt vieler Insel-Logos.
- **Feste Export-/Druckformate** vorgeben (verhindert Auflösungs-/Farbraum-Fehler).
- Optionaler **kurzer Freigabe-Schritt** vor Druck als letzte Leitplanke.

**Aus Vorlagen-Tools (Canva, Adobe Express, Marq, Venngage):**
- **Balance entscheidet über Akzeptanz:** „zu starr → abgelehnt, zu frei → Marke
  verwässert." Das Markenkritische sperren, den Rest großzügig öffnen.
- **Markenkonform = bequemster Startpunkt** (vorbefüllte Beispiele, gute Defaults).
- **Leitplanken schaffen Selbstvertrauen → Freude → Nutzung** statt Abhängigkeit.
- Eingaben **minimal** halten (wenige klare Felder, Sofort-Vorschau, Ein-Klick-Export).

**Typische Fallen (vermeiden):** reines Richtlinien-PDF ohne Werkzeug; Big-Bang-Migration;
zu viele Optionen; unklare Pflege/Verantwortung; brechende Updates; Login-Hürden, die
Nutzung abwürgen.

---

## 5. Fahrplan – sicher und zügig öffnen

Entscheidung aus dem Interview: **Fundament zuerst**, dafür aber **zeitlich knapp** –
dann öffnen. Strenge Leitplanken. Zielgruppe breit (Sektionen/Bereiche, Sekretariate,
interne Grafik, externe Dienstleister).

**Phase 0 – Sicherung (sofort, erledigt/laufend)**
- Deploy-Konflikt gelöst (ein Workflow). Wurzel bleibt Weiterleitung zum Logo-Generator.
- Baustelle (`start/`, `design-system/`, `tools.json`) live unter `…/goeloggen/start/`.

**Phase 1 – Fundament festziehen (das „zuerst", knapp halten)**
- **Logo-Engine entduplizieren** → `core/logo`, von Logo-Generator & GTV-Naming genutzt.
- `goetheanum-orgs.js` → `core/brand-data` als gemeinsame Datenwurzel bestätigen.
- Typografie-Regeln → Tokens + saubere Referenzseite.
- Die 3 laufenden Werkzeuge **sichtbar aufs Design-System heben** (Parität, alte URLs bleiben).

**Phase 2 – Öffnen (der erste freudvolle Wurf)**
- Übersicht als Eingangstür; Werkzeuge mit Beispiel-Vorbelegung, Sofort-Vorschau,
  Ein-Klick-Export. Status `live/beta/entwurf` ehrlich ausgewiesen.
- Kurze, einladende Einführung für Mitarbeitende (kein Handbuch).
- Erst wenn stimmig: **Wurzel auf die Übersicht umlegen** (Aliasse behalten).

**Phase 3 – Wachsen (entlang des Bedarfs)**
- Nächste Alltagswerkzeuge aus dem Kern: **Brief**, **Plakat**, **Programm**, **Folder**,
  **Schild** – je nach Nutzungszahlen priorisiert.
- Leichte Governance: kleines Kernteam, offener Backlog (`tools.json` + Issues),
  klare Aufnahme-Kriterien.

---

## 6. Getroffene Entscheidungen (2. Interview)
- **Verhältnis zur bestehenden grafik.goetheanum.ch:** *mittelfristig ablösen* – unser
  Frontend wird das Ziel-Portal (alles an einem Ort, eine Technik, ein Hausbild).
  Heute verlinkt das offizielle Portal bereits in unsere Tools (Logo-Download,
  Schriften, Signatur → `phtok.github.io/goeloggen/`).
- **Zwei Oberflächen, ein Manifest:** *Front door* (`/`, bewusst **minimal**: nur
  Generatoren + Schriften) für Mitarbeitende; *interner Hub* (`start/`, reichhaltig:
  alle Werkzeuge, geparkte Projekte, Konzeptdokumente) für die Pflege. Beide speisen
  sich aus `tools.json` (Pfade root-relativ, Basis je Oberfläche aufgelöst).
- **Nächste zu entwickelnde Funktionen:** (1) Farben & Icons (Elemente vervollständigen),
  (2) Brief/Briefbogen, (3) Social Media & PowerPoint.

### Funktions-Landkarte aus grafik.goetheanum.ch (integrieren/übernehmen/entwickeln)
| Rubrik | Status bei uns | To-do |
|---|---|---|
| Logos, Schriften, Signatur | ✅ live | bereits verlinkt; Logo-Pakete aus Generator statt logopackage.app |
| Zeichen | 🟡 in Logo-Engine | Referenzseite |
| Icons, Farben | 🟡 Assets da | Icon-Browser + Farben-Seite **(nächste Schritte)** |
| Social Media, PowerPoint, Wallpaper, Mailer | ❌ | Generatoren/Vorlagen mit Leitplanken |
| Videoreihen | 🟡 Cover-Generator (Entwurf) | fertigstellen |
| Briefpapier | 🟡 Briefschaften (Entwurf) | Brief/Briefbogen **(nächster Schritt)** |
| Leitsystem | ❌ | Schilder-Generator |
| Kartierung | 🅿️ geparkt | Pflichtenheft liegt vor |
| Druckauftrag (VK/Grusskarten/Couverts/Hausdruckerei) | 🟡 VK live + Mail-Worker | Grusskarten/Couverts; Druckanfrage-Anbindung |
| Gestaltende/Übersetzungen/Anfragen | ❌ | Info-/Intake-Seiten |
| Werkstatt | ✅ intern | aus Frontend heraushalten |

### Weiter offen
- **Zugang**: offen im Web vs. sanfter Schutz für Schreib-/Export-Rechte (später).
- **Technikstufe** der gemeinsamen Schicht (Vanilla vs. statisches Framework) – vertagt.
- **Stichtag/Anlass** für die Öffnung – keiner genannt.
- **Wurzel-Umlegung live:** Front door ersetzt erst beim Merge die bisherige
  Weiterleitung; Deep-Links (`/logo-generator.html` etc.) bleiben unverändert.

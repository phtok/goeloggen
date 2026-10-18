# Gestaltungsspielraum — Entwurf zur Entscheidung

Stand: 10. Juli 2026 · Status: **Entwurf, vom Auftraggeber zu ratifizieren.**
Zwei Fragen aus dem Feedback zur Webfamilie: *Welche Bilder trägt das Haus?*
und *Wie viel Varianz erlaubt das System, bevor alles gleich aussieht?*
Dieses Blatt schlägt vor — beschlossen wird hier nichts.

---

## Teil 1 · Foto-Richtlinie: drei mögliche Richtungen

Was immer gilt (unabhängig von der Richtung, bereits im Fundament):
Text steht auf Bildern nur über dem gerechneten Schleier (`hero-bild`, B01/B02);
jedes inhaltstragende Bild hat einen Alt-Text (WCAG 1.1.1) und, wo es erklärt,
eine Bildunterschrift (`.cap`, ≥14px, B03); kein Bild als Dekoration ohne
Aussage (G03 sinngemäss: was entfallen kann, entfällt); Quellen sind die
eigenen: Haus-Fotografie, Bühne, Kunstsammlung, Archiv — keine Stock-Motive.

### Richtung A — «Das Haus als Zeuge» (dokumentarisch)
- **Motivwelt:** echte Menschen bei echter Arbeit — proben, forschen, lehren,
  gärtnern; der Bau als wiederkehrender Anker (aussen wie innen); Veranstaltungen
  so, wie sie waren.
- **Licht & Farbe:** vorhandenes Licht, natürliche Farben, keine Filter,
  keine Beauty-Retusche. Warm, aber ungeschminkt.
- **Beschnitt & Form:** ruhige, gerade Kadrierung; Menschen nie angeschnitten
  entwürdigend; Formate aus den Rollen (21:9 Hero, 4:3 Karte, 16:9 Kachel).
- **Stärke:** Glaubwürdigkeit — passt zur Sprache des Hauses (klar, unverstellt).
  Die heutige goetheanum.ch-Fotografie liegt nah an dieser Richtung.
- **Risiko:** braucht laufende, gute Fotografie; schwache Reportage wirkt beliebig.

### Richtung B — «Bühne und Licht» (inszeniert, atmosphärisch)
- **Motivwelt:** von der Bühne her gedacht — Eurythmie in Bewegung, Lichträume,
  der Grosse Saal, Faust; Menschen als Gestalten im Raum, nicht als Porträt-Raster.
- **Licht & Farbe:** dramatisches Licht, tiefe Schatten; Farbklang darf sich an
  den Sektionsfarben orientieren; für Flächen mit Text eine definierte dunkle
  Ton-Variante (verwandt mit `--stage-*`).
- **Beschnitt & Form:** grosszügig, auch radikal (Ausschnitt, Unschärfe,
  Bewegung); Bilder dürfen Fläche sein.
- **Stärke:** Emotion und Unverwechselbarkeit; trägt goetheanum.tv und die
  Bühnen-Kommunikation von selbst.
- **Risiko:** auf Verwaltungs- und Service-Seiten schnell zu viel Pathos;
  braucht die Trennung ‹Bühne dort, Dokument hier›.

### Richtung C — «Goethes Blick» (Form, Natur, Detail)
- **Motivwelt:** Metamorphose — Pflanze, Hand, Material, die Beton-Formen des
  Baus im Detail; dazu die Kunstsammlung und das Archiv als gleichberechtigte
  Bildquellen (Gemälde, Skizzen, historische Aufnahmen).
- **Licht & Farbe:** grosse Ruhe, viel Weissraum, reduzierte Paletten; das Bild
  als kontemplatives Fenster, nicht als Reportage.
- **Beschnitt & Form:** streng und knapp; ein Motiv je Bild; Serien statt
  Einzelbilder (dreimal dieselbe Pflanze im Wandel).
- **Stärke:** unverwechselbar goetheanisch, altert nicht, funktioniert auch mit
  kleinem Foto-Budget (Sammlung + Detailfotografie).
- **Risiko:** wenig Menschen — allein eingesetzt wirkt das Haus entvölkert.

**Empfehlung (zur Diskussion):** A als Grundton für die Webfamilie, B als
ausgewiesener Dialekt der Bühne/goetheanum.tv, C als Vertiefungsebene für
Sektionen, Hochschule und Publikationen. Entscheid → dann wird die gewählte
Fassung als `assets/typografie`-Nachbar (`foto-richtlinie.md` + Beispiele im
Schaufenster) Teil des Fundaments, mit Bild-Checks in `ds-lint`
(Alt-Text-Pflicht, Text-auf-Bild nur in `hero-bild`).

---

## Teil 2 · Erlaubte Varianz: vier Ansätze

Der Befund: Alles atmet im selben Rhythmus (`shead` → Karten → `shead` →
Karten). Einheit soll aus Tokens und Regeln kommen — nicht aus Gleichförmigkeit
der Komposition. Vier Ansätze, kombinierbar:

### Ansatz 1 — Dialekte je Welt
Jede ‹Welt› bekommt ein dokumentiertes Profil auf denselben Tokens:
**Magazin** (Wochenschrift: Bild-Hero, lange Ledes, Serifen-Ruhe im `.prose`),
**Haus** (goetheanum.ch: Kalender-Dichte, Sieben-Block-Footer),
**Bühne** (dunkel, `--stage-*`, Bild als Fläche),
**Werkzeug/Portal** (dicht, funktional, App-Schale).
Technisch: ein `data-welt`-Attribut am `<html>`, das Gewichtungen schaltet
(Grundgrad, Heroform, Dichte) — die Bühne existiert schon als Beweis, dass
das im Token-System geht. *Varianz zwischen Welten, Einheit innerhalb.*

### Ansatz 2 — Freiheitsgrade je Rolle
Jede Rolle dokumentiert im Schaufenster zwei Spalten: **fest** (Schrift,
Kontrast, Mindestgrössen, Abstände-Skala — prüft die Maschine) und **frei**
(Spaltenzahl, Bildseitenverhältnis, mit/ohne Bild, Reihenfolge, Dichte —
entscheidet die Seite). Damit ist Varianz nicht Regelbruch, sondern
ausgewiesener Spielraum. `ds-lint` prüft weiterhin nur die feste Spalte.

### Ansatz 3 — Dramaturgie-Budget je Seite
Komposition folgt einem kleinen Budget statt einem Raster: **ein** Hero,
**eine** Primärhandlung je Blick, höchstens **eine** Akzentfläche je
Viewport — dafür grosse Sprünge (Riesengrad neben Kleingrad, volle Breite
neben schmaler Spalte, Dichte neben Leere). Das erzeugt Spannung mit
denselben Werten. Maschinell teilweise prüfbar (Hero vorhanden? mehr als
eine Primärhandlung?) — als Hinweis, nicht als Fehler.

### Ansatz 4 — Varianz durch den Atem (schon vorhanden, ernster nehmen)
Jede Abweichung beginnt als ratifizierte Ausnahme (`# ds-ok`) an **einer**
Seite. Bewährt sie sich, wird sie Dialekt (Ansatz 1) oder Freiheitsgrad
(Ansatz 2) — dokumentiert im Ledger. Nicht bewährt → `ds-fix` löst sie auf.
Das System hat diesen Mechanismus bereits; er braucht nur die ausdrückliche
Erlaubnis, auch für *Gestalt-Experimente* benutzt zu werden, nicht nur für
Artefakt-Farben.

**Empfehlung (zur Diskussion):** 2 sofort (reine Dokumentation im
Schaufenster, kein Risiko), 1 als nächster Ausbau (die Welten existieren
faktisch schon), 3 als Gestaltungs-Leitsatz im Schaufenster, 4 als gelebte
Praxis weiterführen.

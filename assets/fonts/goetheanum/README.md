# Goetheanum Schriften — `v2.7`

Reparierte und optimierte Fassung des offiziellen Schriftpakets der Goetheanum
Kommunikation (basierend auf der originalen v1.4.43, abgeleitet aus Titillium,
SIL OFL). Reparaturen und Begründung siehe
[`AUDIT.md`](./AUDIT.md); reproduzierbare Build-Pipeline unter
[`tools/goetheanum-fontfix/`](../../../tools/goetheanum-fontfix/).

## Schnitte

| Schnitt | Gewicht | Einsatz (laut Beipackzettel) |
|--------|---------|------------------------------|
| **Leise** | 265 | Leise Auszeichnung, Gegenstimme — nicht für Fließtext-Mengen — Office-Kursiv (⌘I) von Klar |
| **Ruhig** | 350 | Ruhiger Lese- und Lauftext — die Buch-Zwischenstimme zwischen Leise und Klar |
| **Klar**  | 440 | Standard: Korrespondenz, Formulare, Lauftext |
| **Deutlich** | 580 | Titel und Header — die ruhige Auszeichnung |
| **Laut**  | 680 | Titel, **Wegleitung, Signaletik**, Hervorhebungen — Office-Fett (⌘B) von Klar |
| **Icons** | — | Piktogramme & Logos (Tastatur-Belegung im Beipackzettel) |
| **Variabel** | 190–725 | Gewichtsachse `wght` – inkl. der Extreme **Flüstern**/**Schreien** (nur hier, der Grafik vorbehalten) |

## Verwendung im Web

```css
@font-face {
  font-family: "Goetheanum Schrift";
  src: url("Webfonts/woff2/Goetheanum-Schrift-v2.7-Klar.woff2") format("woff2");
  font-weight: 440; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Goetheanum Schrift";
  src: url("Webfonts/woff2/Goetheanum-Schrift-v2.7-Laut.woff2") format("woff2");
  font-weight: 680; font-style: normal; font-display: swap;
}
```

Für Signaletik (z. B. das Kartentool) ist **Laut** der richtige Schnitt.

## Neu in v2.7

- **Siebter Schnitt „Ruhig" (wght 350).** Er füllt den grössten Sprung der
  Leiter – zwischen Leise (265) und Klar (440) – als ruhige Buch-Zwischenstimme:
  fester als die leise Nebenstimme, zurückgenommener als die volle Lesestimme
  (I-Stamm 67 gegenüber 50 bei Leise und 82 bei Klar). Installierbar als
  statischer Schnitt, im Variable Font als benannte Stufe **Ruhig** und im
  Office-Paket als eigene TrueType. Die übrige Familie bleibt unverändert.
- **Schlummernde Null (`zero`) gesäubert.** In den statischen Schnitten lag der
  Schrägstrich als roh überlappende Kontur über dem Oval; an den Überschneidungen
  entstanden an kleinen Graden Knoten. Die Konturen sind jetzt überschneidungsfrei
  vereinigt – die Silhouette bleibt, die Kerbe an der Schräg-Spitze ist weg.
- **Vertikale Metriken geradegezogen.** Eine kaputte Glyphe hatte `usWinAscent`
  auf 1722 aufgebläht (2.17× Zeilenhöhe in Apps ohne `USE_TYPO_METRICS`). Jetzt
  `win` = echte Tintengrenzen (1114/306), `USE_TYPO_METRICS` an → 1.0× em in
  konformen Apps, 1.43× in Legacy-Apps.
- **Ǻ (U+01FA) repariert.** Die Akzente waren in Leise/Ruhig/Klar/Variabel
  verrissen (Konturen bis y 1722). Ǻ ist neu und gewichtsrichtig aus dem gesunden
  Å und dem Akut zusammengesetzt – statisch je Schnitt und geblendet in der Variable.
  Ebenso die **Kapitälchen-Variante** (smcp/c2sc): in Leise war sie verrissen (der
  letzte Metrik-Ausreisser), jetzt aus dem Kapitälchen-Å + Akut sauber gesetzt.
  Danach trägt keine Glyphe mehr über die Tintengrenzen hinaus (win 1126 → 1114).

## Neu in v2.6

- **Typografische Leerzeichen** in den Schnitten Leise/Klar/Laut: Geviert/En
  (U+2003/2002), Drittel-/Viertel-/Sechstelgeviert (U+2004/2005/2006),
  Schmalspatium (U+2009), Haarspatie (U+200A), Ziffernspatie (U+2007),
  Punktspatie (U+2008), das **schmale geschützte Leerzeichen** (U+202F, 125 =
  1/8 em, Hausnorm), Wortfuge (U+2060) und Nullbreite (U+200B). Zuvor trug die
  Familie nur Wortzwischenraum und NBSP.
- **Geschützter Bindestrich** U+2011 (Form des Bindestrichs, bricht nie um).
- **Ziffern-Features:** Grundton bleibt dicktengleich (`tnum`/`lnum`); neu
  `pnum` (proportional) und `onum` (kurze Ziffern auf x-Höhe). Echte
  Mediävalziffern mit Ranging sind gezeichnete Formen und bleiben ausstehend.
  Die Variable und die Icons sind unverändert.

## Versionshistorie (grob)

Zum Unterscheiden der Fassungen – welche Datei welchen Stand trägt:

| Version | Kurz |
|---------|------|
| **v2.7** | Siebter Schnitt **Ruhig** (wght 350), die Buch-Zwischenstimme zwischen Leise und Klar. Schlummernde Null (`zero`) in den Überschneidungen gesäubert. |
| **v2.6** | **Versaleszett ẞ**; typografische Spatien + geschützter Bindestrich (U+2011); Ziffern **proportional** (`pnum`) und Kurzziffern (`onum`), volle Ziffern-Parität; **f-Ligaturen** und **Kapitälchen** (smcp/c2sc). Versionssprung 2.5 → 2.6. |
| **v2.5** | Titel-/Auszeichnungsschnitt **Deutlich** (wght 580). |
| **v2.4.1** | Grundreparatur aus der Original-v1.4.43: Zeichensatz, Kerning, Maßzeichen (Prime/Doppelprime, Striche, schlummernde Null). |

Der jeweils aktuelle Stand steht als **`Neu in …`** oben; im Beipackzettel (PDF)
sind Zeichensatz und Funktionen der aktuellen Fassung abgebildet.

## Dateien
- `Fonts/` — OTF (Desktop): Leise, Ruhig, Klar, Deutlich, Laut, Icons
- Office-Verknüpfung: Klar=Regular, Laut=Fett (⌘B), Leise=Kursiv (⌘I) – eine Familie „Goetheanum Schrift"
- `Variable/` — variable OTF (CFF2)
- `Webfonts/woff` und `Webfonts/woff2` — Web
- `OFL.txt` — Lizenz · `Beipackzettel-…pdf` — Original-Beipackzettel

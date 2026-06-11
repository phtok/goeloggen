# Goetheanum Schriften — `v2.3.1`

Reparierte und optimierte Fassung des offiziellen Schriftpakets der Goetheanum
Kommunikation (basierend auf der originalen v1.4.43, abgeleitet aus Titillium,
SIL OFL). Reparaturen und Begründung siehe
[`AUDIT.md`](./AUDIT.md); reproduzierbare Build-Pipeline unter
[`tools/goetheanum-fontfix/`](../../../tools/goetheanum-fontfix/).

## Schnitte

| Schnitt | Gewicht | Einsatz (laut Beipackzettel) |
|--------|---------|------------------------------|
| **Leise** | 265 | Titel, Gegenstimme — nicht für Fließtext-Mengen |
| **Klar**  | 440 | Standard: Korrespondenz, Formulare, Lauftext |
| **Laut**  | 680 | Titel, **Wegleitung, Signaletik**, Hervorhebungen — Office-Fett (⌘B) von Klar |
| **Icons** | — | Piktogramme & Logos (Tastatur-Belegung im Beipackzettel) |
| **Variabel** | 190–725 | Gewichtsachse `wght` – inkl. der Extreme **Flüstern**/**Schreien** (nur hier, der Grafik vorbehalten) |

## Verwendung im Web

```css
@font-face {
  font-family: "Goetheanum Schrift";
  src: url("Webfonts/woff2/Goetheanum-Schrift-v2.3.1-Klar.woff2") format("woff2");
  font-weight: 440; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Goetheanum Schrift";
  src: url("Webfonts/woff2/Goetheanum-Schrift-v2.3.1-Laut.woff2") format("woff2");
  font-weight: 680; font-style: normal; font-display: swap;
}
```

Für Signaletik (z. B. das Kartentool) ist **Laut** der richtige Schnitt.

## Dateien
- `Fonts/` — OTF (Desktop): Leise, Klar, Laut, Icons
- Office-Verknüpfung: Klar=Regular, Laut=Fett (⌘B), Leise=Kursiv (⌘I) – eine Familie „Goetheanum Schrift"
- `Variable/` — variable OTF (CFF2)
- `Webfonts/woff` und `Webfonts/woff2` — Web
- `OFL.txt` — Lizenz · `Beipackzettel-…pdf` — Original-Beipackzettel

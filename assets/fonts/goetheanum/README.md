# Goetheanum Schriften — `v2.0.0`

Reparierte und optimierte Fassung des offiziellen Schriftpakets der Goetheanum
Kommunikation (basierend auf der originalen v1.4.43, abgeleitet aus Titillium,
SIL OFL). Reparaturen und Begründung siehe
[`AUDIT.md`](./AUDIT.md); reproduzierbare Build-Pipeline unter
[`tools/goetheanum-fontfix/`](../../../tools/goetheanum-fontfix/).

## Schnitte

| Schnitt | Gewicht | Einsatz (laut Beipackzettel) |
|--------|---------|------------------------------|
| **Leise** | 280 | Titel, Gegenstimme — nicht für Fließtext-Mengen |
| **Klar**  | 450 | Standard: Korrespondenz, Formulare, Lauftext |
| **Laut**  | 600 | Titel, **Wegleitung, Signaletik**, Hervorhebungen |
| **Icons** | — | Piktogramme & Logos (Tastatur-Belegung im Beipackzettel) |
| **Variabel** | 280–600 | Gewichtsachse `wght`, nur für Profis |

## Verwendung im Web

```css
@font-face {
  font-family: "Goetheanum Schrift";
  src: url("Webfonts/woff2/Goetheanum-Schrift-v2.0.0-Klar.woff2") format("woff2");
  font-weight: 450; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Goetheanum Schrift";
  src: url("Webfonts/woff2/Goetheanum-Schrift-v2.0.0-Laut.woff2") format("woff2");
  font-weight: 600; font-style: normal; font-display: swap;
}
```

Für Signaletik (z. B. das Kartentool) ist **Laut** der richtige Schnitt.

## Dateien
- `Fonts/` — OTF (Desktop): Leise, Klar, Laut, Icons
- `Variable/` — variable OTF (CFF2)
- `Webfonts/woff` und `Webfonts/woff2` — Web
- `OFL.txt` — Lizenz · `Beipackzettel-…pdf` — Original-Beipackzettel

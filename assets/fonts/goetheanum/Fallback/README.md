# Fallback-Schriften für Nicht-Latein

Die Goetheanum-Schriften decken **Latein** ab (Basic + Extended-A). Für
andere Schriftsysteme braucht es einen Fallback. Dieser Ordner enthält den
**kyrillischen** Fallback gebündelt; für Griechisch und Arabisch sind die
empfohlenen Schriften unten verlinkt (alle **SIL OFL**, dieselbe Rechtslage).

Leitgedanke: möglichst nah an der Titillium-Basis der Goetheanum-Schrift bleiben.

| Schriftsystem | Empfehlung | Bezug zur Titillium-Basis |
|---|---|---|
| **Kyrillisch** | **Titillium Web [RUS]** (hier gebündelt) | direkte Kyrillisierung von Titillium (Daymarius) |
| **Arabisch** | **Cairo** (Mohamed Gaber) | erweitert Titillium Web um Arabisch (Kufi-Duktus) |
| **Griechisch** | **Source Sans 3** | humanistische Grotesk, nah an Titillium; bereits im Web-Stack |

## Gebündelt: Titillium Web [RUS]
Kyrillische Erweiterung von Titillium Web durch **Daymarius**, Version 1.002
(2018), SIL OFL 1.1. Vier Schnitte: Light (300), Regular (400), SemiBold (600),
Bold (700). Nur Kyrillisch + Latein, statisch — als Fallback ausreichend.

## Nicht gebündelt (Download bei Bedarf)
- **Cairo** — https://fonts.google.com/specimen/Cairo (OFL)
- **Source Sans 3** — https://fonts.google.com/specimen/Source+Sans+3 (OFL)

## Einbindung (Web)
Siehe `fallback.css`: zuerst die Goetheanum-Schrift, dann pro Schriftsystem
der Fallback. Der Browser wählt je Zeichen automatisch die passende Schrift.

```css
font-family: "Goetheanum Klar", "Titillium RUS", "Cairo", "Source Sans 3", sans-serif;
```

## Lizenz
Alle genannten Schriften stehen unter der SIL Open Font License 1.1 und dürfen
frei weitergegeben werden. Die OFL der Goetheanum-Schriften liegt unter
`../OFL.txt`; die OFL der Fallback-Schriften ist in den jeweiligen Font-Dateien
(name table) hinterlegt.

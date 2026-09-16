# Begleitschrift & Nicht-Latein-Fallback

Die Goetheanum-Schriften decken **Latein** ab (Display + Auszeichnung). Für
**langen Mengentext** und für **andere Schriftsysteme** kommen hier zwei Dinge
zusammen — alle **SIL OFL**, alle **selbst gehostet** (woff2), keine CDN-Abhängigkeit.

## Begleit-Grotesk (entschieden): Source Sans 3
Die gesetzte **Lese-/Begleitschrift** für langen Mengentext. Humanistische
Grotesk, ruhig im Satz, echte Kursive; deckt **Latein + Griechisch + Kyrillisch**.
goetheanum.ch nutzt sie (als Source Sans Pro) bereits als Textschrift – die
Mischung Goetheanum-Display + Source-Text ist gelebte Praxis.
Dateien: `SourceSans3-Regular/-SemiBold/-Italic.woff2` (Web) · `SourceSans3-Variable.ttf` + `-Italic.ttf` (Desktop).

## Script-Fallback (Titillium-nah)
| Schriftsystem | Schrift | Rolle |
|---|---|---|
| **Kyrillisch** | **Titillium Web [RUS]** (Daymarius) | Display-Fallback für Titel in Hausschrift-Optik (Titillium-DNA) |
| **Arabisch** | **Cairo** (Mohamed Gaber) | direkte Titillium-Erweiterung um Arabisch |

Kyrillischer und griechischer **Mengentext** läuft in Source Sans 3 selbst;
Titillium RUS ist für **Display/Titel** gedacht, wo die Hausschrift-Anmutung
gewünscht ist. Arabisch deckt Cairo (Mengentext wie Titel).

## Einbindung (Web)
`fallback.css` einbinden – enthält alle `@font-face` (lokal) und die Stacks:
```css
--goe-text:    "Source Sans 3", "Cairo", system-ui, sans-serif;          /* Lesetext */
--goe-display: "Goetheanum Klar", "Titillium RUS", "Cairo", sans-serif;  /* Titel + Fallback */
```

## Lizenz
Alle Schriften stehen unter der **SIL Open Font License 1.1** und dürfen frei
weitergegeben werden – siehe `OFL-FALLBACK.txt` (Quellen/Autoren) und die
`name`-Tabellen der Font-Dateien.

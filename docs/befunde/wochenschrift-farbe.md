# Befund: Farbe des Wochenschrift-Logos (#333548)

Stand 21. 11. 2026. Anlass: Frage von Joe (Design-Assistent von Louis Defèche), ob
#333548 die offizielle Farbe ist.

## Im Repo
`#333548` steht nur in zwei Dateien: `assets/logos/medien/wochenschrift/full/farbe/web.svg`
und `…/short/farbe/web.svg`. Keine Regel, kein Token, kein Ledger-Eintrag nennt es.

## Gemessen an der Quelle
Live-Seite https://dasgoetheanum.com (abgerufen 21. 11. 2026):

| Fundstelle | Farbe |
|---|---|
| Wochenschrift-Logo `logo_800_WP_mobil.png` (Pixelwert, einzige Farbe) | `#373949` |
| Logo `logo_360.png` (häufigste Pixel) | `#373949` |
| Titel und Überschriften (CSS) | `#373947` |
| Kopf, Navigation, Knöpfe (CSS) | `#373948` |

Die Webfarbe der Wochenschrift liegt bei `#373947`–`#373949`. `#333548` kommt dort
nirgends vor; der Unterschied ist klein (R 4, G 4, B 1 Stufe), aber er ist da.

## Befund
Das Repo-Logo trägt eine Farbe, die weder in der Live-Quelle noch in einem Beschluss
steht. Die belegte Farbe ist `#373949` (Logo) beziehungsweise `#373947` (Webtext).
Quelle der Wahrheit wäre das Logopaket der Wochenschrift; es lag hier nicht vor.

## Zur Entscheidung
Empfehlung: die zwei SVG auf `#373949` setzen (Pixelwert des veröffentlichten Logos)
und als Token `wochenschrift` festhalten. Ein Eintrag im Logopaket der Redaktion
bestätigt oder widerlegt das.

## Nachtrag 21. 11. 2026: neues Logo
Das Logo der Wochenschrift wird erneuert (Bildmarke und «Das Goetheanum» in der Hausschrift,
Wochenschrift-Website, Klasse `.brand-mark`, Variable `--logo`). Gemessen: Farbe `#373949`,
Weiss im Dunkel. Entscheid des Inhabers: Token `--wochenschrift` (`#373949`) in
`design-system/tokens.css` und `tokens.json`; neue Form «Weblogo» im Logo-Generator
(`assets/logos/medien/wochenschrift/weblogo/`, gebaut von `tools/build_wochenschrift_logo.py`).
Die alten Formen «Voll» und «Kurz» tragen noch `#333548`.

# Entwurf: Pfeil-Schrift in der Form der Textschrift (25. 11. 2026)

Auftrag des Inhabers (25. 11.): ‹ja, ich möchte die Entwürfe sehen› – der
offene Punkt aus `docs/befunde/pfeile-textschrift-2026-11-02.md`: die
‹Goetheanum Pfeile› auf die Form der Textschrift-Pfeile heben (ihre dünnen
Pfeile sind leichter als Flüstern). **Nur Entwurf und Bild, kein Paket,**
keine Schriftdatei geändert.

![Pfeil-Schrift heute (dünn, fett) und Entwurf in vier Hausgewichten, darunter im Satz](pfeile-schrift-entwurf-2026-11-25.png) <!-- typo-ok -->

- Bild: https://github.com/phtok/goeloggen/blob/main/docs/befunde/pfeile-schrift-entwurf-2026-11-25.png
  (Tafel als SVG: `pfeile-schrift-entwurf-2026-11-25.svg`)
- Bau: `tools/goetheanum-fontfix/entwurf_pfeile_textform.py` (zeichnet mit
  `kopf`/`pfeil` aus `build_v29_pfeile.py`, schreibt nur Bilder)

## Was der Entwurf tut

- **Form der Textschrift:** Arm 50° zum Schaft, stumpfe Spitze, Strich wird
  zum Ende schlanker (0,71 / 0,85 / 0,72), Kopf 0,27 × Länge + 0,9 × Strich –
  dieselbe Konstruktion wie → in der Textschrift.
- **Kasten der Pfeil-Schrift bleibt:** Länge 820, Mitte 500, Vorschub 1250,
  Belegung (6 t u h, 2 0 q e o ü s ö) unverändert.
- **Gewicht = Hausschnitt:** Strich = Minus des Schnitts, Ruhig 60 · Klar 74
  · Deutlich 97 · Laut 113. Heute: dünn 24, fett 58.
- **Gebogene Pfeile 1–8:** Mittellinie wie heute (senkrecht, Bogen, Spitze
  in 40°), Kopf und Verlauf der Textschrift. Die sieben anderen sind
  Spiegelungen und Drehungen von Nr. 1, wie in der heutigen Schrift (geprüft:
  100 von 100 Punkten). Mit wachsendem Strich rückt der Bogen tiefer und
  breiter, damit er offen bleibt (bei Laut 370 statt 236 breit).
- **Kompass 1–4:** nicht angefasst (Piktogramm mit Beschriftung).

## Beobachtet

- Im Satz bei gleichem Grad ist der Pfeil der Pfeil-Schrift **19 % länger**
  als → der Textschrift (820 gegen 691) und steht mit breitem Abstand
  (Vorschub 1250). Der Entwurf behält beides; erst so bleibt die Belegung
  austauschbar. Wer den Pfeil im Text will, nimmt ohnehin → der Textschrift.
- Klar (74) liegt im Satz neben Klar-Text im selben Gewicht; Ruhig (60) ist
  dem heutigen fett (58) am nächsten.

## Zu entscheiden

1. **Weiterbauen?** Empfehlung: **ja, zwei Gewichte Klar und Laut** – dünn
   wird Klar, fett wird Laut (Umschalt bleibt ‹fett›), gebogene Pfeile in
   beiden. Alternative: Ruhig und Deutlich, näher am heutigen Bild.
2. Bei ja: als Fassung der Pfeil-Schrift bauen (Dateiname bleibt, Version
   höher), Beipackzettel S. 5 nachziehen. Das ist ein Paket-Schritt; die
   Schwester-Session ‹Hausschrift 2.93› berührt dieselben Pakete – nach ihr.

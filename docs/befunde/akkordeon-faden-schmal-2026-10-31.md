# Befund Akkordeon, Kleid Faden, schmal, offenes Feld (31. 10. 2026)

Screenshot des Auftraggebers vom Telefon (`akkordeon-faden-schmal-2026-10-31.jpg`,
Frage 16 auf akkordeon.html), zwei Markierungen:

1. **Links (Kreis):** Die Antwort hängt direkt unter dem getönten Band der
   Frage, zu nah am Faden (12 px statt --s4) und ohne Luft zum Band.
   «Die Schrift klebt am Rahmen.»
2. **Rechts (Pfeil auf/ab):** Das getönte Band der Frage bleibt nach dem
   Tippen stehen und läuft bis an den rechten Rand, die Antwort darunter
   nicht – der Übergang Band → Antwort ist unruhig. Lesart: der Hover-Hauch
   (`.faden summary:hover`) klebt auf Touch-Geräten nach dem Tippen
   (Sticky Hover) und müsste hinter `@media (hover:hover)` liegen; das
   offene Feld braucht einen eigenen, ruhigen Zustand ohne Tönung oder
   mit einer Tönung, die Frage UND Antwort trägt.

Gemessen (goetheanum.io, 420 px, Faden offen): Antwort 12 px vom Faden,
8 px vom rechten Rand, 24 px unter dem Band; breit 16 px vom Faden.

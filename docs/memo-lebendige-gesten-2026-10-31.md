# Memo des Auftraggebers: Gesten des Lebendigen (31. 10. 2026)

Wortlaut (Auftraggeber, im Zusammenhang mit dem Spendenformular und der
ersten Anwendung des Akkordeons auf goetheanum.io):

> Die Goetheanum-Sprache soll Gesten des Lebendigen tragen: Wiederholungen,
> Polaritäten, Steigerungen, Reduktionen, Übergänge. Das ist vielleicht das
> Wichtigste: Übergänge gestalten. Weich, flüssig, eins ins andere
> übergehend. Wie die Bloom-Menüs. Was können wir davon lernen und
> implementieren? Weiche wie klare Animationen. Etwas wächst oder verwelkt.
> Eins geht aus dem anderen hervor. Jedes Teil enthält das Ganze.

## Lesart (zur Prüfung, nicht beschlossen)

Das Memo benennt einen Kandidaten für ein siebtes Prinzip neben P1–P6 in
`docs/gestaltungsprinzipien-entwurf.md`: **P7 · Lebendig** – die Gestalt
bewegt sich wie Gewachsenes, nicht wie Geschaltetes. Die fünf Gesten sind
Goethes Begriffe aus der Metamorphosenlehre (Polarität und Steigerung als
«die zwei grossen Triebräder aller Natur»), hier als Gestaltungsmittel:

| Geste | Im Satz und in der Fläche | In der Bewegung |
|---|---|---|
| Wiederholung | Rhythmus der Zeilen, Raster, gleiche Marke an gleicher Stelle | dieselbe Kurve überall (`--acc-kurve`, Bloom) |
| Polarität | Klar/Laut, hell/dunkel, offen/geschlossen | auf und zu sind ein Paar, nicht zwei Effekte |
| Steigerung | Stufen 15 / 18 / 20 / 23, ein Merkmal je Stufe (G01) | etwas wächst: Höhe, Fläche, Farbe nehmen zu |
| Reduktion | Weglassen (G03, P2) | etwas verwelkt: kürzer, leiser, dann weg (220 ms zu gegen 280 ms auf) |
| Übergang | Nichts springt: Hauch → Band → Fläche, Papier → Hauch | eins geht aus dem anderen hervor (Morph, View Transitions), nie Schnitt |

«Jedes Teil enthält das Ganze»: ein Baustein trägt die Tokens, die Kurve,
die Stimme des Hauses in sich – wer das Akkordeon sieht, sieht das Haus.
Das ist technisch schon P5 (aus einer Quelle), hier als Gestalt-Forderung.

Was bereits so gebaut ist: die Bloom-Kurve `cubic-bezier(.32,.08,.24,1)`
des Hauptmenüs im Akkordeon (280 ms auf, 220 ms zu, `prefers-reduced-motion`
auf 0 s), die Reihe der Gründe von schwer nach leicht (Ledger 1.21.2), die
Flächen-Übergänge Hauch → Band. Was fehlt: ein Bewegungs-Vokabular im
Fundament (Dauer- und Kurven-Tokens, Ein- und Austritt als Paar, Übergang
zwischen Zuständen eines Formulars), damit die nächste Seite nicht ihre
eigene Bewegung erfindet.

## Offen (Auftraggeber entscheidet)

1. P7 in den Prinzipien-Entwurf aufnehmen?
2. Bewegungs-Tokens ins Fundament (`tokens.css`: Kurve, Dauer auf/zu) als
   erste Umsetzung – Anwendungsfall Spendenformular (Betrag wählen, Felder
   erscheinen, Dank wächst aus dem Knopf)?

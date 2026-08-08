# Wirkungs-Lesart der Sommer-Aktion — Stand 7. August 2026

> **Abgelöst am 8. August 2026 durch `wirkungs-lesart-08-08.md`.** Diese Fassung
> bleibt als Historie stehen — die Zahlen darin sind der Stand vom 7. August.

Dieses Dokument ordnet die Anmeldungen **ohne UTM-Spur** («ohne UTM» im
Cockpit) den Aktivitäten der Kampagne zu. Es ist eine **Lesart, keine
Messung**: Alle mit ≈ markierten Zahlen sind Schätzungen (±30 %). Die
Datenbank bleibt unangetastet — dort stehen nur harte Zuordnungen. Die
Anteile daraus stehen im Cockpit (`CONFIG.dunkel.anteile`) und werden dort
auf den jeweils aktuellen Stand angewandt.

Diese Fassung löst `wirkungs-lesart-24-07.md` ab (die bleibt als Historie
liegen). Sie widerspricht ihr nicht — sie schreibt sie auf die letzten zwei
Wochen fort, in denen zwei Mail-Wellen, das Popup und der Schlussspurt
dazugekommen sind.

Grundlage am Stichtag (7. August, vier Tage vor dem verlängerten Aktionsende
am 11. August): **636 Anmeldungen**, davon **358 mit UTM** und **278 ohne**. Das Dunkelfeld ist
damit von 54 % (24. Juli) auf **44 %** gesunken — nicht, weil weniger dunkel
hereinkommt, sondern weil das Mailing mit sauberer Spur so viel dazugelegt
hat.

## Was sich gegenüber dem 24. Juli ändert

1. **Das Mailing trägt die Aktion.** Am 24. Juli war es eine von mehreren
   Kräften; heute stellt es mit 282 gemessenen Abschlüssen **79 % des
   gemessenen Feldes**. Beide Wellen sind als Sprung in der Tageskurve
   sichtbar (18. Juli: 56 Abos, 30. Juli: 60).
2. **Die bezahlte Anzeige ist aus** — seit dem 24. Juli, letzter Einzelklick
   am 26. Juli (`abschaltprobe-anzeige-27-07.md`). Ihr Anteil bleibt bei den
   dort belegten ≈9 Abos und wächst nicht mehr. Damit fällt auch die
   Vorsichtsklausel der alten Lesart weg: das Klick-Log wird **nicht mehr**
   von einem einzelnen Weg beherrscht.
3. **Zwei neue Gebiete im Dunkelfeld:** **Popup** (seit 25. Juli auf den
   Webseiten, 21 gemessene Abschlüsse) und **Empfehlung** (persönliches
   Umfeld, Praxen, Schulen, Tagungen — in den Selbstauskünften der
   zweitgrösste Block, im gemessenen Feld strukturell unsichtbar, weil er nie
   einen Link trägt).

## Wie gerechnet wurde

Drei Anker, wie am 24. Juli — der schwächste (vermutete Herkunft aus dem
zeitnächsten Klick) bleibt aussen vor.

### Anker 1 · Die Tageskurve (Grundlinie und Überschuss)

Vor der ersten Mail-Welle lief die Aktion 14 Tage ohne Mailer und ohne
Anzeige. Das Dunkelfeld dieser Tage ist die **Grundlinie**: 52 Anmeldungen
ohne Spur, **3,7 pro Tag**. Diese Rate wird auf jedes spätere Fenster
fortgeschrieben; was darüber liegt, ist der **Überschuss** des Fensters.

| Fenster | Tage | dunkel | Grundlinie | Überschuss |
|---|---:|---:|---:|---:|
| 3.–16. Juli (vor dem Mailing) | 14 | 52 | 52 | — |
| 17.–23. Juli (Welle 1) | 7 | 69 | 26 | **+43** |
| 24.–29. Juli (Zwischenfeld) | 6 | 42 | 22 | +20 |
| 30. Juli–6. Aug. (Welle 2) | 8 | 89 | 30 | **+59** |
| 7. August (Welle 3, Frist) | 1 | 26 | 4 | **+22** |
| **Summe** | 36 | **278** | | |

### Anker 2 · Die gemessenen Anteile desselben Fensters

Der Überschuss eines Fensters wird nach den **gemessenen** Anteilen
**dieses Fensters** verteilt — was im Hellen dominiert, dominiert auch im
Dunkeln, denn es sind dieselben Wege mit derselben Landingpage.

| Fenster | gemessen (ohne dunkel) |
|---|---|
| Welle 1 | Mailing 81 · Newsletter 4 · Social 2 · Organik 2 · Bezahlt 1 |
| Zwischenfeld | Mailing 13 · Newsletter 6 · Organik 1 · Social 1 |
| Welle 2 | Mailing 139 · Popup 18 · Newsletter 8 · Social 4 · Bezahlt 2 |
| Welle 3 | Mailing 49 · Newsletter 6 · Popup 4 · Social 3 · Organik 1 |

Die **Grundlinie** trägt diesen Schlüssel nicht: In ihr wurde fast nichts
gemessen (7 Social, 4 Mailing, 2 Organik). Sie wird darum nach Anker 3
verteilt.

### Anker 3 · Die Selbstauskunft

42 der 278 dunklen Anmeldungen beantworten «Wie sind Sie auf uns aufmerksam
geworden?». Von 40 einordenbaren Antworten:

| Antwort-Gruppe | Anzahl | Anteil |
|---|---:|---:|
| E-Mail, Newsletter, Verteiler | 15 | 37,5 % |
| Direkt, Suche, Bestand («kenne es schon lange») | 10 | 25,0 % |
| Empfehlung, Praxis, Schule, Tagung | 9 | 22,5 % |
| Print, Stand, Flyer | 2 | 5,0 % |
| Social | 2 | 5,0 % |
| Anzeige, Werbung | 2 | 5,0 % |

Die Selbstauskunft kann **Mailing und Newsletter nicht trennen** — für den
Empfänger ist beides «eine Mail». Diese Trennung leistet Anker 2. Umgekehrt
ist die Selbstauskunft der **einzige** Beleg für Empfehlung: Dieser Weg
trägt nie einen Link und ist im gemessenen Feld notwendig eine Null.

## Das Ergebnis

Die 278 Anmeldungen ohne Spur, verteilt (Grundlinie nach Anker 3, jeder
Überschuss nach Anker 2, die Anzeige gedeckelt durch die Abschalt-Probe):

| Gebiet | ≈ dunkel | Anteil | dazu gemessen | ≈ gesamt |
|---|---:|---:|---:|---:|
| Mailing | 111 | 39,9 % | 282 | **393** |
| Newsletter | 64 | 23,0 % | 28 | 92 |
| Organik · Direkt · Bestand | 39 | 14,0 % | 7 | 46 |
| Empfehlung | 31 | 11,2 % | 0 | 31 |
| Social organisch | 12 | 4,3 % | 17 | 29 |
| Popup | 8 | 2,9 % | 21 | 29 |
| Print · Stand · Inserat | 7 | 2,5 % | 0 | 7 |
| Bezahlt · Anzeige | 6 | 2,2 % | 3 | **9** |
| **Summe** | **278** | **100 %** | **358** | **636** |

**Die eine Aussage:** Rund **62 % der ganzen Aktion** gehen auf die drei
Mail-Wellen an den eigenen Verteiler zurück, weitere 14 % auf die
Newsletter. Die Aktion ist damit im Kern **keine Gewinnung neuer
Öffentlichkeit, sondern eine Aktivierung des eigenen Umfelds** — was die
Zielmarke erreicht hat (636 von 500, übertroffen am 5. August), aber für die
nächste Aktion die entscheidende Frage stellt.

**Die Anzeige** bleibt bei ≈9 Abos aus rund 965 gemessenen Klicks und
131 000 erreichten Personen. Diese Zahl ist seit dem 24. Juli dreifach
gestützt: Placebo-Probe, Abschalt-Probe und jetzt die Fensterrechnung, in
der die Anzeige-Fenster keinen eigenen Überschuss zeigen.

## Wo diese Lesart schwach ist

- **Grundlinie als Konstante.** Sie unterstellt, dass die organische
  Nachfrage über 36 Tage gleich bleibt. In der Schlusswoche stimmt das
  vermutlich nicht: Die Frist selbst erzeugt Direktverkehr, der hier dem
  Mailing zugeschlagen wird. Der Mailing-Anteil ist darum eher eine
  Obergrenze.
- **Die Aktion ist nach diesem Stichtag um drei Tage verlängert worden**
  (neues Ende: 11. August), und zwar **still**: keine Ankündigung, keine Mail,
  kein neues Datum auf den Aktionsseiten (Beschluss 7. August). Der 7. August
  ist damit nicht mehr der Schlusstag, sondern ein Zwischenstand. Die
  kommunizierte Frist bleibt der 8. August — die Mail-Wellen 3 und 3b nennen
  ihn —, der gemessene Zeitraum endet drei Tage später.

  Wer diese Lesart nach dem 11. August fortschreibt, rechnet die Tage **9. bis
  11. August als eigenes Fenster**: Hinter ihnen steht kein Versand, sondern
  nur die offene Tür, und für die Empfänger war die Frist bereits abgelaufen.
  Beides zieht die Zahlen nach unten. Die Methode oben trägt hier nicht — der
  Schlüssel «Überschuss nach gemessenen Anteilen» setzt einen Impuls voraus,
  den es in diesem Fenster nicht gibt. Diese Tage gehören darum in der
  Grundlinie gerechnet, nicht im Schlussspurt.
- **Newsletter gegen Mailing.** Beide fallen auf dieselben Tage (17. Juli,
  31. Juli). Anker 2 trennt sie nach dem gemessenen Verhältnis; sind die
  Newsletter schlechter ausgezeichnet als der Mailer, ist ihr Anteil zu
  klein geraten.
- **Empfehlung** steht allein auf 9 Selbstauskünften. Die Grössenordnung ist
  belegt, die Zahl nicht.

Bei neuer Auswertung: `CONFIG.dunkel` (stand / doc / anteile) im Cockpit
nachziehen, sonst nichts.

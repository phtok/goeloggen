# Welche Gruppe hat wie reagiert — Auswertung mit Nennern, 10. August 2026

Der zweite ActiveCampaign-Lauf (`services/mailing-sommer2026/AC-NENNER.md`) hat
geliefert, was gefehlt hat: **wie viele Menschen je Gruppe angeschrieben
wurden**. Erst damit wird aus einer absoluten Zahl eine Quote — und die Quote
ist das, womit die nächste Aktion geplant wird.

Drei Gruppen, nach dem, was die Person schon hatte:

| Gruppe | hatte | bekam angeboten | angeschrieben |
|---|---|---|---:|
| **Lesen** | Wochenschrift | goetheanum.tv | 922 |
| **Sehen** | goetheanum.tv | Wochenschrift | 3 839 |
| **Beides** | nichts | beides | 28 948 |
| | | **Summe** | **33 709** |

## Der Befund: die kleinste Gruppe ist die stärkste

| Gruppe | angeschrieben | Klicker | Abos (mit Spur) | Abo je Angeschriebenem | **Abo je Klicker** |
|---|---:|---:|---:|---:|---:|
| **Lesen** | 922 | 193 | 103 | **11,2 %** | **53,4 %** |
| Beides | 28 948 | 4 385 | 399 | 1,38 % | 9,1 % |
| Sehen | 3 839 | 930 | 35 | 0,91 % | 3,8 % |

**Von den Wochenschrift-Lesern, die geklickt haben, hat jeder zweite ein
TV-Abo gelöst.** Bei den TV-Abonnenten, denen die Wochenschrift angeboten
wurde, war es jeder sechsundzwanzigste.

Gemessen an der Gruppengrösse ist der Abstand noch grösser: Die Gruppe «Lesen»
war **31 Mal kleiner** als «Beides» und hat pro angeschriebener Person **acht
Mal so oft** zu einem Abo geführt. Sie war die einzige Gruppe im zweistelligen
Bereich.

### Warum «Sehen» so schlecht abschneidet — und warum das kein Nebenbefund ist

«Sehen» hat die **höchste Klickrate aller Gruppen** (24,2 % der
Angeschriebenen, gegen 20,9 % bei Lesen und 15,1 % bei Beides). Das Interesse
war also da, und zwar überdurchschnittlich. Verloren gegangen ist es **nach**
dem Klick: 930 Menschen sind auf die Wochenschrift-Seite gegangen, 35 haben
abgeschlossen.

Das passt zum Kassen-Befund bei goetheanum.tv (268 Abbrüche ohne Rückkehr,
`docs/uscreen-abgleich-10-08.md`) und schärft ihn: **Nicht das Angebot war das
Problem, sondern der Weg zum Abschluss.** Bei der Wochenschrift führt er über
ein Paperform-Formular, bei goetheanum.tv über die Uscreen-Kasse — gemessen ist
bisher keiner von beiden.

### Nachtrag am selben Tag: drei Ursachen sind ausgeschlossen

Der erste Verdacht — der Anmeldeweg der Wochenschrift sei der Engpass — **hält
der Prüfung nicht stand.** Drei Tests, alle aus vorhandenen Daten:

1. **Das Formular ist es nicht.** Innerhalb der Gruppe «Beides» — dieselben
   Menschen, dieselbe Mail, beide Angebote nebeneinander — gewann die
   Wochenschrift: **211 Abschlüsse gegen 188** bei goetheanum.tv. Wer die Wahl
   hatte, nahm eher das Heft. Ein kaputter Weg sieht anders aus.
2. **Das Papier ist es nicht.** Die Formatwahl ist in beiden Gruppen praktisch
   identisch: 76 % digital bei «Beides», 77 % bei «Sehen». Die Adresseingabe
   schreckt nicht ab, weil kaum jemand sie überhaupt erreicht.
3. **Ein Ablenkungsklick ist es nicht.** Das Link-Register zeigt für jede Gruppe
   genau **eine** Zielseite (plus denselben Link als Weiterempfehlung). Die
   Sehen-Gruppe konnte gar nichts anderes anklicken als die Wochenschrift.

**Nachtrag 13. August — die vierte Ursache ist geprüft, nicht mehr offen.**
Die Betreffzeilen aller 24 Mail-Schritte stehen bereits im Repo
(`services/mailing-sommer2026/AC-AUTOMATION.md`, Tabelle «S26 · NurTV→WS» —
das ist die Sehen-Automation) — ein Blick genügte, keine neue Abfrage nötig.

Der Vergleich der acht Betreffzeilen gegen die acht der Gegenrichtung
(«S26 · NurWS→TV», Lesen-Automation, dasselbe Muster in derselben Aktion)
**widerlegt die Hypothese, statt sie zu bestätigen:**

| Welle | Sehen → WS (Betreff nennt Produkt?) | Lesen → TV (Betreff nennt Produkt?) |
|---|---|---|
| w1 DE/EN | ja («Wochenschrift», «weekly») | ja («goetheanum.tv») |
| w2 DE/EN | **nein** («Ihr kostenloser Zugang …») | **nein** — identischer Betreff |
| w3 DE | ja («… gratis lesen») | ja («… goetheanum.tv gratis») |
| w3 EN | **nein** («three months free») | ja («… of goetheanum.tv») |
| w3b DE/EN | ja («… gratis lesen» / «free reading») | ja («… goetheanum.tv») |

Die einzige Zeile ohne Produktnamen, die **nur** die Sehen-Automation trifft,
ist **w3 EN** — eine von acht. Die w2-Lücke («Ihr kostenloser Zugang») steht
in **beiden** Richtungen identisch und kann darum den Unterschied zwischen
11,2 % und 0,91 % nicht erklären: Wäre unklare Betreffzeile die Ursache, würde
sie die Lesen-Gruppe genauso treffen — tut sie aber nachweislich nicht.

**Die Hypothese vom letzten Eintrag ist damit widerlegt, nicht offen.** Es
gibt keinen Textfehler, der sich in fünf Minuten beheben liesse — die Mails
sind zu über 90 % strukturell identisch zur erfolgreichen Gegenrichtung.
Was bleibt, ist eine Erklärung ohne billige Lösung: Der Wechsel vom Sehen zum
Lesen scheint **dem Medium nach** ein grösserer Schritt zu sein als der
umgekehrte — ein zusätzliches Leseabo zu beginnen, ist ein anderes
Commitment als ein Video anzuklicken, unabhängig davon, wie klar das Angebot
formuliert ist. Das ist eine Erkenntnis über die Werbung von Video- zu
Lese-Publikum, keine Korrektur an dieser Kampagne.

## Sprachen

| | angeschrieben | Klicker | Klickrate |
|---|---:|---:|---:|
| Beides · DE | 12 231 | 2 123 | 17,4 % |
| Beides · EN | 16 717 | 2 262 | 13,5 % |
| Sehen · DE | 1 858 | 511 | 27,5 % |
| Sehen · EN | 1 981 | 419 | 21,2 % |
| Lesen · DE | 377 | 91 | 24,1 % |
| Lesen · EN | 545 | 102 | 18,7 % |

**Deutsch klickt in jeder Gruppe besser als Englisch** — durchweg um vier bis
sechs Prozentpunkte. Der englische Verteiler ist grösser (19 243 gegen 14 466)
und reagiert schwächer. Bei den Abschlüssen verstärkt sich das: 422 der 539
Abos mit Mailing-Spur tragen Deutsch.

## Was der Versand den Verteiler gekostet hat

Bisher stand das nirgends. Vier Wellen auf 33 709 Adressen:

| Welle | Abmeldungen | Hard Bounces | Soft Bounces |
|---|---:|---:|---:|
| w1 · 17. Juli | 163 | 10 | 25 |
| w2 · 30. Juli | 180 | 4 | 23 |
| w3 · 7. August | 103 | 2 | 24 |
| w3b · 8. August | 42 | 0 | 3 |
| **Summe Wellen** | **488** | **16** | **75** |
| vier Newsletter | 61 | 30 | 43 |
| **Gesamt** | **549** | **46** | **118** |

**549 Menschen haben den Verteiler verlassen**, gegen 1 042 gewonnene Abos —
auf zwei gewonnene Abonnements kommt ein verlorener Kontakt. Das ist kein
Alarm: 1,45 % Abmeldungen in fünf Wochen bei vier Wellen ist ein normaler,
niedriger Wert. Aber es ist eine Kostenseite, die eine Kampagne hat und die
bisher in keiner Rechnung stand.

Auffällig ist die **zweite** Welle: Sie kostete mehr Abmeldungen (180) als die
erste (163), obwohl sie an weniger Menschen ging. Die dritte und vierte kosteten
deutlich weniger — w3b, die schärfste Frist-Mail, am wenigsten von allen. Wer
bis dahin geblieben war, hat sich von der Erinnerung nicht mehr gestört gefühlt.

**Spam-Beschwerden:** ActiveCampaign führt dafür kein eigenes Feld. Die Spalte
bleibt leer statt geraten.

## Zwei Fehler in der Mail-Strecke

1. **`S26 · Lesen · EN`, Welle w3b ging am 15. Juli** — drei Tage **vor** der
   Ankündigung. 197 englische Wochenschrift-Leser haben «heute läuft es aus»
   erhalten, als die Aktion noch gar nicht begonnen hatte. Sie haben trotzdem
   ordentlich reagiert (97 Öffner, 9 Klicker), aber die Nachricht war zu diesem
   Zeitpunkt sinnlos. Damit hat die englische «Lesen»-Gruppe als einzige **keine
   echte Frist-Mail am Fristtag** bekommen.
2. **Das Link-Tracking der beiden Wochenschrift-Newsletter war aus**
   (`tracklinks:none`, Befund vom 9. August). Ihre Klicks sind nicht messbar.

Beides ist derselbe Fehlertyp: Die Strecke wurde gebaut und nicht vor dem
Scharfschalten durchgesehen. Für das Drehbuch: **eine Abnahme der ganzen
Automatisierung vor dem Start** — Versanddatum je Schritt, Link-Tracking an,
Zielgruppe je Zweig.

## Was ActiveCampaign kostet: eine Verteilung, keine Rechnung

Der Tarifpreis war nicht auffindbar — die Abrechnung liegt bei
ActiveCampaign beim Konto-Inhaber in einem eigenen Portal. Gefunden wurde das
Kontingent:

- **100 000 Kontakte**, davon 86 477 belegt
- **1 200 000 Sendungen** im Abrechnungszeitraum, im laufenden noch unverbraucht

Damit lässt sich der Aktionsanteil sauber ableiten, ohne den Preis zu kennen:
Die vier Wellen verbrauchten **113 074 Sendungen** — das sind **9,4 % des
Sendekontingents**. Die Newsletter zählen nicht dazu, die wären ohnehin gelaufen.

**Empfehlung: den Versandanteil ansetzen, nicht den Zeitanteil.** ActiveCampaign
läuft ohnehin und trägt den ganzen Newsletter-Betrieb; die Aktion hat kein Abo
ausgelöst, sondern zusätzliches Volumen erzeugt. Ein Zeitanteil (5,5 Wochen
Grundgebühr) wäre zehnmal so hoch und würde der Aktion etwas anlasten, das auch
ohne sie bezahlt worden wäre.

**Nachtrag 13. August — als Schätzung eingetragen, auf Wunsch des Auftraggebers
statt weiter nachzufragen.** Angenommene Grundgebühr CHF 1'000/Monat (Grössen­
ordnung für ~100 000 Kontakte mit den hier genutzten bedingten Automatisierungen,
ungeprüft) × 9,4 % Versandanteil = **CHF 95**, als Posten «Infrastruktur» in der
Kosten-Maske erfasst. Kommt die echte Gebühr je einmal ans Licht, ersetzt sie
diesen Posten — bis dahin ist er als Schätzung markiert (Posten-Text in der
Kosten-Tabelle), nicht als Messung.

## Nachhaken bei den Abspringern — geprüft, Entscheid: nicht jetzt

Drei Gruppen wären namentlich bekannt und erreichbar gewesen — Kassenabbrecher
bei goetheanum.tv (268, mit Zeitstempel bei Uscreen) und Klicker ohne
Abschluss in beiden Mail-Gruppen (~4 900, in ActiveCampaign). Die 268 wären
der günstigste Hebel gewesen: Konto angelegt, Kasse erreicht, ein Schritt
gefehlt — Uscreen bringt die Abandoned-Checkout-Mail für genau diesen Fall
serienmässig mit.

**Entscheid vom 13. August: kein Nachfassen.** Der Auftraggeber hat sich
bewusst dagegen ausgesprochen. Festgehalten, damit es nicht als vergessener
Punkt wiederkehrt: Die Analyse steht, die Zahl ist bekannt, die Handlung ist
unterblieben — nicht aus Unwissen, sondern aus Entscheid. Für die nächste
Aktion bleibt die Erkenntnis gültig: Ein Kassenabbrecher mit Zeitstempel ist
der billigste erreichbare Rest einer Kampagne, sollte es beim nächsten Mal
anders entschieden werden.

## Was daraus für die nächste Aktion folgt

1. **Die eigenen Leute zuerst.** Die Gruppe «Lesen» war 2,7 % des Verteilers und
   brachte 19 % der Abos mit Mailing-Spur. Wer schon etwas vom Haus hat, nimmt
   das zweite Angebot an. Eine Aktion, die nur diese Gruppe anspricht, wäre um
   ein Vielfaches günstiger und kaum weniger wirksam.
2. **Vom Sehen zum Lesen ist ein grösserer Schritt als umgekehrt — einplanen,
   nicht wegtexten.** Formular, Papierformat, Ablenkung und Betreff sind
   geprüft und ausgeschlossen; «Sehen» wandelt trotzdem nur ein Zwölftel der
   Rate von «Lesen». Eine gute Anzeigen-Klickrate bei dieser Zielgruppe ist
   kein Signal für ähnliche Abschlusszahlen wie bei «Lesen» — die Erwartung
   für eine nächste Aktion muss das schon vorher berücksichtigen, nicht erst
   im Nachhinein erklären.
3. **Deutsch und Englisch getrennt planen.** Der englische Verteiler ist grösser
   und reagiert schwächer — mit denselben Texten, nur übersetzt. Das ist eine
   Frage an die Ansprache, nicht an die Zustellung.
4. **Die Strecke vor dem Start abnehmen.** Zwei von sechs Automatisierungen
   trugen einen Fehler, den niemand vor dem Versand gesehen hat.

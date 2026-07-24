# Wirkungs-Lesart der Sommer-Aktion — Stand 22. Juli 2026

Dieses Dokument ordnet die Anmeldungen **ohne UTM-Spur** («ohne UTM» im
Cockpit) den Aktivitäten der Kampagne zu. Es ist eine **Lesart, keine
Messung**: Alle mit ≈ markierten Zahlen sind Schätzungen (±30 %). Die
Datenbank bleibt unangetastet — dort stehen nur harte Zuordnungen. Im Cockpit
wirkt diese Lesart in der Spalte «≈ mit Dunkelfeld» der Gebiete-Liste; die
Herleitung steht dort unter Belege → «Dunkelfeld».

Diese Fassung löst `wirkungs-lesart-18-07.md` ab (die bleibt als Historie
liegen). Neu gegenüber dem 18. Juli: ein Live-Anker mehr — die **vermutete
Herkunft** je dunkler Anmeldung (zeitnächster Kurzlink-Klick, RPC
`sommer2026_ereignisse`) deckt inzwischen **72 der 84** dunklen Anmeldungen
der letzten 14 Tage ab. Die Schätzung steht damit auf deutlich festerem
Grund als am 18. Juli.

Grundlage am Stichtag: **109 Anmeldungen ohne UTM** von insgesamt **216**
(mit UTM: 107). Der Dunkel-Anteil ist von **60 %** (18. Juli: 84 von 139)
auf **50 %** gefallen — die Attributions-Reparaturen vom 18. Juli greifen:
von den 77 seither hinzugekommenen Anmeldungen tragen gut zwei Drittel eine
Spur.

## Warum kommen überhaupt so viele ohne UTM an?

Die Frage aus dem Auftrag, mit den Zahlen dahinter. Von den 84 dunklen
Anmeldungen der letzten 14 Tage sind **58 goetheanum.tv (Uscreen)** und
**26 Wochenschrift (Paperform)**. Das ist der Kern:

1. **goetheanum.tv / Uscreen ist das strukturelle Leck (58 von 84).** Die
   Attribution von goetheanum.tv hängt an **einem** Faden: dem
   `user_created`-Event, das Uscreen aus seiner eigenen Session-Erfassung
   mit `utm_params` schickt. Kommt dieses Event ohne `utm_params` (In-App-
   Browser aus Instagram/Facebook, verlorene Cookies, Weiterleitungsketten),
   ist die Anmeldung dunkel — der Uscreen-Checkout selbst trägt keine
   Landingpage und keine UTM in die Subscription. Darum steht bei allen 58
   `landing_path = NULL`.
2. **Die bezahlte Meta-Anzeige ist der grösste einzelne Dunkel-Treiber.**
   Der Link `story_statisch` sammelt **rund 600 Kurzlink-Klicks** (377 EN +
   220 DE), aber nur **eine** hart zugeordnete Anmeldung. Die restlichen
   Abschlüsse dieser Anzeige landen im Dunkelfeld: **43 der 84** dunklen
   Anmeldungen tragen einen zeitnahen Klick genau auf diese Anzeige. Grund
   ist Punkt 1 — die Anzeige führt auf goetheanum.tv, und die Spur überlebt
   den Uscreen-Checkout nicht. Klicks werden serverseitig gezählt (link_hits
   je Kurzcode), der Abschluss danach nicht.
3. **Paperform / Wochenschrift (26 von 84).** Hier soll die Spur über
   versteckte Prefill-Felder **und** `device.utm` ankommen. 26 dunkle von
   ~55 WoS zeigen: auf einzelnen Wegen reicht die Landingpage die `?utm_*`
   noch nicht ans Formular weiter, oder es sind echte Direkt-/Organik-
   Zugänge (getippte URL, Lesezeichen — die tragen nie Parameter).

## Die vier belegten Anker (Stand 22. Juli)

1. **Vermutete Herkunft (neu, halb-hart):** je dunkler Anmeldung der
   zeitlich nächste Kurzlink-Klick (≤ 90 Min. davor) auf einen zum Produkt
   passenden Kampagnen-Link. Deckt 72 der 84 dunklen der letzten 14 Tage.
   Verteilung: `meta-anzeige/story_statisch` 43 · `tv-weekly*/nl-tv phase1`
   15 · Instagram/Facebook (story, reel_wolfgang, karussell) 11 · LinkedIn 1
   · `inserat_rsv` 1 · `mailing/newsletter_agid` 1.
2. **Kurzlink-Klicks (link_hits):** je Link automatisch gezählt. Grosse
   Treiber: Meta-Anzeige ~600, `otter-2` (tv-weekly Übersicht) 73, `spinne`
   (Instagram-Story) 32, `biber-4` (nl-tv) 27, `rabbit` (tv-weekly-abo EN)
   26. Die Inserat-Kurzlinks: einstellig (`dachs-2` 8, `zebra` 0).
3. **Quelle/Produkt der dunklen Anmeldungen:** 58 Uscreen (goetheanum.tv),
   26 Paperform (Wochenschrift) in den letzten 14 Tagen — der Rest ohne
   zeitnahen Klick (12) ist echte Direkt-/Organik-Anmeldung.
4. **Frühphase 3.–7. Juli (~25 Anmeldungen ausserhalb des 14-Tage-
   Fensters):** die löchrige Startwoche — AC-Newsletter «Sommerfestivals»
   (4.7.), Hinweis-Newsletter AWW (3.7.), Bestandskonten und Organik. Für
   diese greift die Vermutungs-Logik nicht mehr (Klick-Log rollt); sie
   bleiben die weichste Ecke der Schätzung (wie schon am 18. Juli).

## Kampagnenweite Rangfolge (gemessen + geschätzt)

| Rang | Aktivität | gemessen | ≈ dazu (dunkel) | ≈ gesamt |
|---|---|---|---|---|
| 1 | Mailing (Welle 1) | 79 | ≈1 | **≈80** |
| 2 | Meta-Anzeige (bezahlt) | 0 | ≈44 | **≈44** |
| 3 | Organik · Bestand · Direkt | 8 | ≈25 | **≈33** |
| 4 | Social organisch (Reels · Stories · Karussell) | 9 | ≈14 | **≈23** |
| 5 | goetheanum.tv-Newsletter (TV-Weekly) | 5 | ≈17 | **≈22** |
| 6 | Haus-/AC-Newsletter (Frühphase) | 5 | ≈7 | **≈12** |
| 7 | Inserat · Print | 0 | ≈1 | **≈1** |
| 8 | Empfehlung | 1 | ≈0 | **≈1** |
| | **Summe** | **107** | **109** | **216** |

Die Spalte «gemessen» sind harte UTM-Zuordnungen (RPC
`sommer2026_kanaele` / `sommer2026_attribution`). «≈ dazu» verteilt das
Dunkelfeld (109) nach den vier Ankern oben; die Summen sind mit den
Live-Zahlen abgeglichen (107 mit UTM, 109 ohne, 216 gesamt).

Drei Sätze dazu: **Das Mailing trägt die Aktion weiter** — eine Welle, gut
ein Drittel aller Abos, fast alles messbar. **Die bezahlte Meta-Anzeige ist
der neue grosse Posten** und läuft fast vollständig dunkel — hier liegt der
grösste Attributions-Gewinn, wenn das Uscreen-Leck geschlossen wird.
**Print/Inserat trägt weiter kaum etwas** (Kurzlinks einstellig) — der
ehrlichste Einzelbefund bleibt.

## Was sich verbessern lässt (nach Hebel)

1. **Grösster Hebel — die goetheanum.tv-Spur bis in den Uscreen-Checkout
   tragen.** Heute reicht die Landingpage `tv-sommer2026…` die `?utm_*` nicht
   sicher an den Uscreen-Checkout weiter; darum hängt alles am
   `user_created`-Event. Zwei Wege, am besten beide:
   - Auf der TV-Landingpage die eingehenden `?utm_*` an den «3 Monate
     gratis»-Button hängen (an die Checkout-URL), damit Uscreen sie in der
     Session sicher aufnimmt — analog zur Paperform-Weiterreichung.
   - Bezahlte und soziale TV-Wege **über den Kurzlink** (`/s/<code>`, Function
     `go`) führen: 302 mit voller UTM-URL, robuster gegen In-App-Browser als
     ein direkt geteilter Roh-Link. Details in `services/sommer-zaehler/
     utm-ablauf.md` → «Sonderfall goetheanum.tv / Uscreen».
2. **Meta-Anzeige zuerst umstellen** (grösster Einzelposten). Sobald die
   Anzeige über den Kurzlink läuft und die Landingpage die Spur weiterreicht,
   wandern ~44 Anmeldungen von dunkel nach gemessen — der Dunkel-Anteil
   fiele auf einen Schlag Richtung 30 %.
3. **Paperform gegenprüfen (26 dunkel).** Auf allen vier Formularen die vier
   versteckten Prefill-Felder (`utm_source/medium/campaign/content`) und die
   Weiterreichung Landingpage → Formular verifizieren; ein Testlink je
   Formular durchschicken (siehe utm-ablauf.md → «Test»).
4. **Optionaler Backend-Ausbau (nicht deployt, zur Entscheidung):** das
   Vermutungs-Fenster in `sommer2026_ereignisse` von 90 Minuten auf die
   Sitzungsdauer erweitern und für Paperform zusätzlich über `landing_path`
   ankern — dann bekämen auch die 12 hint-losen dunklen eine Lesart. Erst
   nach Freigabe, weil es die Auslegung (nicht die Messung) verschiebt.

## Wie das Cockpit diese Lesart benutzt (seit dem Umbau vom 24. Juli)

Die Zuordnung liegt im Cockpit nicht mehr als feste Zeilenliste, sondern als
**Anteile** in `CONFIG.dunkel.anteile` (`apps/sommer-zaehler/campaign.js`):

| Gebiet | Anteil |
|---|--:|
| Bezahlt · Anzeige (Meta über den Uscreen-Checkout) | 40,4 % |
| Organik · Direkt · Bestand | 22,9 % |
| Newsletter (TV-Weekly und Haus-Newsletter) | 22,0 % |
| Social organisch | 12,8 % |
| Mailing | 0,9 % |
| Print · Stand · Inserat | 0,9 % |

Diese Anteile stammen aus der Verteilung oben (109 dunkle Anmeldungen am
22. Juli) und werden auf den **jeweils aktuellen** Stand der Anmeldungen ohne
Spur angewandt. Damit bleibt die Einordnung stimmig, während die Zahlen
weiterlaufen – ohne dass jemand die Tabelle täglich nachrechnen müsste. Der
Rundungsrest geht an das grösste Gebiet, damit die Summe exakt aufgeht.

**Bei einer neuen Auswertung** genügt es, `stand`, `doc` und `anteile` dort
nachzuziehen; die Gebiete-Liste und die Belege-Tabelle rechnen unverändert
weiter. Ändert sich die Struktur der Kampagne grundlegend (neuer Kanal, das
Uscreen-Leck geschlossen), gehört eine frische Lesart her – nicht eine
Fortschreibung der alten.

## Pflege

Die Lesart ist datiert und wird **nicht** automatisch nachgeführt. Bei einer
neuen Auswertung: Kopie mit neuem Datum anlegen, `CONFIG.dunkelLesart` in
`apps/sommer-zaehler/campaign.js` nachziehen (Stand-Datum + Zeilen), Cockpit
zeigt sie dann automatisch. Das Live-Aggregat «vermutete Herkunft» im
Cockpit atmet ohnehin mit — es zieht sich jede Minute frisch aus den
Ereignissen. Seit dem 18. Juli entsteht immer weniger dunkler Bestand;
künftige Auswertungen brauchen immer weniger Schätzung.

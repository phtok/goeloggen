# Public Secrets: Analyse, Empfehlungen und Umbauplan

Stand: 2026-03-18

## Backup der aktuellen Version

Vor dem Umbau wurde der aktuelle Stand als Git-Tag gesichert:

- `backup/public-secrets-pre-socialmedia-2026-03-18`

Wiederherstellung des gesicherten Standes:

```bash
git switch --detach backup/public-secrets-pre-socialmedia-2026-03-18
```

Neuen Arbeitszweig von diesem Stand aus anlegen:

```bash
git switch -c relaunch-from-backup backup/public-secrets-pre-socialmedia-2026-03-18
```

## 1. Kurzfazit zur neuen Richtung

Die neue Richtung ist **deutlich klarer als Social-Produkt** und zugleich wesentlich skalierbarer als die bisherige Ensemble-Website.

Der stärkste Gedanke darin ist nicht mehr die reine Präsentation des Ensembles, sondern ein **sozialer Kreislauf von Fragen**:

1. ich werde gefragt,
2. ich frage andere,
3. ich formuliere neue Fragen.

Damit wird aus einem redaktionell kuratierten Frage-Archiv eine **fragebasierte Netzwerk-App**.

## 2. Vergleich mit dem aktuellen Stand

### Was die aktuelle Web-App bereits gut vorbereitet

- Ein klarer Fokus auf Fragen als zentrales Format.
- Eine reduzierte Startseite mit großer Typografie.
- Interaktionen an Fragen sind bereits vorhanden.
- Es gibt bereits Login- und Mitgliederbereiche.
- Mitglieder können schon Profil, Fragen, Initiativen und Termine pflegen.
- Einzelne Datenbereiche sind im Backend bereits getrennt modelliert.

### Was konzeptionell nicht mehr zur neuen Richtung passt

- Das Ensemble ist derzeit weiterhin das tragende Ordnungsprinzip.
- Navigation und Inhalte sind auf **Menschen / Initiativen / Momente** ausgerichtet.
- Es existieren gemeinsame Kalender- und Initiativen-Bereiche, die laut neuer Idee entfallen sollen.
- Die aktuelle Interaktion ist vor allem **Bewertung + Kommentar**, nicht **Weitergabe / Antwort / soziale Zirkulation**.
- Es gibt noch keine echte öffentliche Nutzerlogik mit frei anlegbaren Profilen.
- Es gibt noch keine Frage-Detailseiten mit eigenem, stabilen Link pro Frage.
- Direktadressierung an andere Nutzer ist bislang nicht modelliert.

## 3. Produkt-Einschätzung zu den neuen Ideen

## 3.1 Sehr stark: die drei Grundaktionen

Die drei Grundaktionen ergeben bereits eine gute Produktlogik:

- **Antworten** auf eine an mich gerichtete Frage,
- **Weiterstellen** einer bestehenden Frage,
- **eigene Frage formulieren**.

Das ist stark, weil dadurch dieselbe Frage auf mehreren Ebenen leben kann:

- als Original,
- als soziale Weitergabe,
- als Anlass für neue Antworten,
- als wachsendes Interaktionsobjekt.

Empfehlung: Diese drei Aktionen sollten zur **primären Informationsarchitektur** werden.

## 3.2 Direktnachrichten nur sehr vorsichtig einführen

Die Idee mit Direktnachrichten ist verständlich, aber für ein frühes Produkt riskant, weil sie sofort viele Folgeprobleme erzeugt:

- Zustellbarkeit,
- Benachrichtigungen,
- Missbrauch / Spam,
- Blockieren / Melden,
- Moderation,
- Datenschutz,
- Lesestatus und Inbox-Logik.

Empfehlung für Phase 1:

- **keine vollwertige Chat-Funktion**,
- stattdessen **Frage an Nutzer senden**,
- Zustellung zunächst über **E-Mail-Benachrichtigung mit Link**,
- im Produkt selbst nur eine einfache Ansicht **„An mich gestellt“ / „Von mir gestellt“**.

So bleibt die Kernhandlung erhalten, ohne sofort ein Messaging-System bauen zu müssen.

## 3.3 Fragebewertung über „Aktivierung“ ist besser als reine Sterne

Die Abkehr von Sternbewertungen ist sinnvoll. Für dieses Produkt ist **soziale Aktivierung** aussagekräftiger als abstrakte Qualität.

Sinnvolle Signale:

- Anzahl Antworten,
- Anzahl Weiterstellungen,
- Anzahl Herzen,
- Anzahl Profilaufrufe oder Detailaufrufe optional erst später.

Empfehlung:

- in Phase 1 nur **Antworten + Weiterstellungen + Herzen** zählen,
- eine transparente Kennzahl anzeigen, z. B.:
  - `Aktivierung: 12` oder
  - `3 Antworten · 5 Weitergaben · 4 Herzen`.

Wichtig: Die zusammengesetzte Punktzahl intern nutzbar machen, aber öffentlich lieber die **einzelnen Zähler** zeigen. Das ist verständlicher.

## 3.4 Eigene Fragenseite pro Frage ist absolut richtig

Das ist ein zentraler Baustein für die neue App.

Jede Frage braucht:

- eine stabile URL,
- den Originaltext,
- die Urheberin oder den Urheber,
- Sichtbarkeit aller Antworten,
- Sichtbarkeit aller Weitergaben,
- Sichtbarkeit der Herzen,
- klare Handlungen: **antworten**, **weiterstellen**, **herzen**.

Das wird die eigentliche soziale Einheit der Plattform.

## 3.5 Startseite: Scroll-Flow vs. Tinder

### Variante A: vertikaler Scroll-Flow

Vorteile:

- ruhiger,
- typografisch stärker,
- passt besser zur bisherigen Ästhetik,
- niedrigere Interaktionshürde,
- leichter technisch umzusetzen,
- besser für Desktop und Links auf einzelne Fragen.

Nachteile:

- weniger spielerisch,
- schwächere Vorselektion.

### Variante B: Fragen-Tinder

Vorteile:

- hohe Aktivierung,
- klare Sammelbewegung: erst wählen, dann beantworten,
- stärkeres App-Gefühl.

Nachteile:

- deutlich höhere UX- und Implementierungskomplexität,
- Gefahr von Spielmechanik ohne inhaltliche Tiefe,
- Swipes können Fragen zu schnell oberflächlich machen,
- schwieriger bei langen, komplexen Fragen.

### Empfehlung

Für Phase 1 zuerst **Variante A (Scroll-Flow)** umsetzen.

Warum:

- sie bewahrt die vorhandene Stärke der Website,
- sie ist näher am aktuellen Bestand,
- sie macht die neue Produktlogik verständlich,
- sie liefert schneller echte Nutzungsdaten.

Die Tinder-Variante würde ich als **spätere Experimentfunktion** behandeln, sobald genügend Fragen und aktive Nutzer vorhanden sind.

## 4. Wichtige Produktentscheidungen vor dem Umbau

Vor der Implementierung sollten diese Punkte gemeinsam entschieden werden:

### 4.1 Wer darf was sehen?

Mögliche Regeln:

- Profile öffentlich, Antworten öffentlich.
- Profile öffentlich, Antworten teilweise privat.
- Fragen öffentlich, Nutzerprofile nur eingeschränkt öffentlich.

Empfehlung:

- Fragen öffentlich,
- Profile mit Name, Kurztext, Fragen und Antworten öffentlich,
- E-Mail-Adressen niemals öffentlich,
- Kontakt nur über Systemhandlung oder E-Mail-Relay.

### 4.2 Muss jede Frage an jemanden adressiert sein?

Hier braucht es zwei Modi:

- **offene Frage** an die Öffentlichkeit,
- **gerichtete Frage** an eine bestimmte Person.

Beide sollten im Datenmodell vorkommen.

### 4.3 Was genau ist eine „Antwort“?

Zu klären:

- eine freie Textantwort,
- optional Medien später,
- eine Antwort kann öffentlich sichtbar sein,
- eine nicht beantwortete Weitergabe bleibt trotzdem als Ereignis sichtbar.

Empfehlung: Antworten in Phase 1 nur als **Textantworten**.

### 4.4 Was passiert bei Missbrauch?

Sobald Nutzer einander Fragen schicken können, braucht ihr mindestens:

- Melden,
- Blockieren optional später,
- Moderationsstatus,
- Limits gegen Massenversand.

Empfehlung für MVP:

- Rate-Limits,
- einfache Moderationsflags,
- Versand nur an bestätigte Accounts,
- E-Mail-Relay statt direkter Offenlegung von Adressen.

## 5. Technische Einschätzung zum aktuellen Codebestand

Der aktuelle Bestand ist für einen Umbau **brauchbar als Prototyp-Basis**, aber nicht als endgültige Architektur für eine offene Social-App.

### Positiv

- Frontend und Backend sind überschaubar.
- Das Node-Backend ist einfach genug, um schnell umzubauen.
- Fragen, Kommentare, Personen, Initiativen und Termine liegen schon getrennt vor.
- Login-/Mitgliederlogik existiert bereits.

### Kritisch für die neue Richtung

- Persistenz in JSON-Dateien ist für eine Social-App nur begrenzt tragfähig.
- Beziehungen wie „Frage wurde von A an B weitergestellt“ fehlen strukturell.
- Es gibt kein echtes Ereignismodell für Aktivität.
- Rollen und Rechte sind noch auf Redaktion/Mitglied zugeschnitten, nicht auf offene Nutzerkonten.
- Kalender- und Initiativenlogik würde beim Umbau Ballast werden.

### Empfehlung zur Technik

- **Für Konzepttest / MVP-Prototyp**: bestehendes Node-Projekt weiterverwenden.
- **Spätestens vor öffentlicher Öffnung**: auf SQLite oder PostgreSQL umstellen.

Wenn ihr schnell lernen wollt, ist der jetzige Stack gut genug für Phase 1. Wenn ihr echte Community-Dynamik erwartet, sollte die Datenhaltung früh stabilisiert werden.

## 6. Empfohlenes neues Datenmodell

## 6.1 Nutzer

- id
- slug
- name
- email
- bio
- avatar
- visibility
- createdAt
- status

## 6.2 Frage

- id
- text
- authorUserId
- createdAt
- visibility
- status
- sourceQuestionId optional für Ableitungen

## 6.3 Frageweitergabe

- id
- questionId
- fromUserId
- toUserId optional
- toEmail optional
- message optional
- createdAt
- deliveryStatus

## 6.4 Antwort

- id
- questionId
- userId
- text
- createdAt
- visibility

## 6.5 Herz

- id
- questionId
- userId
- createdAt

## 6.6 Aktivitätsereignis

Optional, aber sehr hilfreich:

- id
- type (`question_created`, `question_forwarded`, `question_answered`, `question_liked`)
- actorUserId
- questionId
- targetUserId optional
- createdAt

Damit können Feed, Detailseiten und Auswertungen viel leichter gebaut werden.

## 7. Empfohlene neue Informationsarchitektur

## Hauptmenü

- **Fragen**
- **Login**

Optional später:

- Profil
- Benachrichtigungen

## Startseite / Fragenfeed

Die Startseite sollte direkt der Fragenfeed sein.

Mögliche Tabs innerhalb von „Fragen“:

- Neu
- Aktiv
- An mich
- Von mir
- Gemerkt optional später

## Frage-Detailseite

Elemente:

- Fragetext
- Autorprofil
- Aktivierungszahlen
- Antworten
- Weiterstellungen
- Herzen
- CTA: beantworten
- CTA: weiterstellen
- CTA: eigene Frage davon ausgehend formulieren optional später

## Profilseite

Elemente:

- Name
- Bio
- eigene Fragen
- gegebene Antworten
- gestartete Weitergaben
- sichtbare Initiativen/Ereignisse nur falls später als Profil-Posts neu gedacht

## 8. Empfohlener Umsetzungsplan

## Phase 0 – Sicherung und Produktklärung

1. Backup-Tag beibehalten und dokumentieren.
2. Kalender und Initiativen als auslaufende Bereiche markieren.
3. 60- bis 90-minütigen Entscheidungsworkshop machen.
4. Die Kernbegriffe final festlegen:
   - Frage,
   - Antwort,
   - Weiterstellen,
   - Herz,
   - Profil.

## Phase 1 – Informationsarchitektur und UI-Konzept

1. Navigation auf **Fragen / Login** reduzieren.
2. Startseite als Fragenfeed neu skizzieren.
3. Frage-Detailseite wireframen.
4. Profilseite wireframen.
5. Zustände definieren:
   - nicht eingeloggt,
   - eingeloggt,
   - Frage an mich gestellt,
   - Frage weiterstellen,
   - eigene Frage erstellen.

## Phase 2 – Backend-Umbau im bestehenden Stack

1. Neue Datenmodelle für Antworten, Herzen und Weiterstellungen einführen.
2. Frage-Detailroute und API-Endpunkte ergänzen.
3. E-Mail-Relay für Frageweitergabe bauen.
4. Aktivierungsmetriken serverseitig berechnen.
5. Erste Moderations- und Rate-Limit-Regeln ergänzen.

## Phase 3 – Frontend-Umbau

1. Ensemble-/Initiativen-/Momente-Navigation entfernen.
2. Fragenfeed als Default-Ansicht bauen.
3. Fragekarten oder Vollseiten-Flow mit CTA bauen.
4. Eigene Seite je Frage einführen.
5. Profilseiten auf Nutzeraktivität statt Ensemble-Darstellung umstellen.

## Phase 4 – Migration der Altinhalte

1. Bestehende Ensemble-Mitglieder als erste Nutzer behandeln.
2. Bestehende Fragen übernehmen.
3. Initiativen und Termine entweder:
   - ganz archivieren,
   - oder als historische Inhalte außerhalb des Hauptprodukts ablegen.
4. Alte Links prüfen und nötige Weiterleitungen definieren.

## Phase 5 – Experimentieren und Lernen

1. Nutzungsdaten für Scroll-Feed sammeln.
2. Erst danach Tinder-Prototyp testen.
3. Prüfen, welche Fragen wirklich weitergestellt werden.
4. Auf Basis echter Nutzung Benachrichtigungen und Messaging erweitern.

## 9. Konkrete Tipps für den Start

- Beginnt nicht mit Chat.
- Beginnt nicht mit zu vielen öffentlichen Bereichen.
- Baut zuerst den **Fragekreislauf** stabil.
- Führt Fragen als **soziale Objekte mit eigener URL** ein.
- Nutzt E-Mail zuerst nur als Zustellmechanik.
- Trennt früh zwischen **öffentlicher Ansicht** und **Account-Aktionen**.
- Lasst die Tinder-Idee als optionalen zweiten Einstieg offen, aber nicht als erste Hauptlogik.

## 10. Meine klare Empfehlung

Wenn ihr jetzt umbaut, dann in dieser Reihenfolge:

1. **Backup sichern**,
2. **Navigation radikal vereinfachen**,
3. **Frage-Detailseite einführen**,
4. **Antworten / Weiterstellen / Herzen** technisch modellieren,
5. **Profile als Nutzerprofile statt Ensembleprofile** umbauen,
6. erst danach über echte Direktnachrichten oder Swipe-Logik entscheiden.

So bleibt der Umbau kontrollierbar, und ihr könnt die neue Idee testen, ohne die gesamte App auf einmal neu zu erfinden.

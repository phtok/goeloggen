# Auftrag für Claude im Chrome: Selbstauskunft in die Paperform-Formulare

Ziel: Auch die Wochenschrift-Anmeldungen sollen eine Selbstauskunft tragen
(«Wie sind Sie auf uns aufmerksam geworden?») — das Backend
(`ingest-paperform`) liest sie über den Custom-Key `selbstauskunft` und nutzt
sie als Kanal-Fallback, wenn keine UTM-Spur mitkommt. Nebenbei wird die
Pre-fill-Kür aus dem Übergabe-Brief erledigt (Custom-IDs der versteckten
UTM-Felder).

Den folgenden Block Claude im Chrome geben (eingeloggt bei paperform.co):

---

Du bist im Paperform-Konto der Goetheanum-Sommer-Aktion eingeloggt. Wir
ergänzen in den Aktions-Formularen ein Selbstauskunfts-Feld und prüfen die
versteckten UTM-Felder. Es geht um die Formulare der Sommer-Aktion 2026 —
erkennbar am Titel «Abonnieren … (Sommerangebot 2026)» bzw. an den URLs
`sommer2026-chf-de`, `sommer2026-eur-de`, `sommer2026-eur-en` und (falls
vorhanden) `sommer2026-chf-en`.

Regeln: Nichts löschen, keine Felder umsortieren, keine Fragen umformulieren.
Nach jeder Formular-Änderung publishen. Keine Secrets in den Chat.

Je Formular zwei Dinge:

**A) Neues Feld «Selbstauskunft» (sichtbar, optional)**
1. Ein kurzes Textfeld anlegen, NICHT als Pflichtfeld, sinnvoll platziert
   (vor dem Absenden-Bereich):
   - Deutsche Formulare: «Wie sind Sie auf uns aufmerksam geworden?»
   - Englisches Formular: «How did you hear about us?»
2. In der Feld-Konfiguration ganz unten die **Custom ID** exakt auf
   `selbstauskunft` setzen (klein, ein Wort). Das ist entscheidend — das
   Backend erkennt das Feld nur an diesem Key (Fallback: Beschriftung mit
   «aufmerksam»/«hear about»).

**B) Versteckte UTM-Felder prüfen (Pre-fill)**
Jedes Formular soll vier versteckte Felder haben, deren **Custom ID** exakt
`utm_source`, `utm_medium`, `utm_campaign`, `utm_content` heisst. Bekannter
Altstand: im EN-Formular tragen sie zufällige IDs (`75kij`, `eb0qb`, `qdmh`,
`7c5la`) — diese Custom IDs auf die vier exakten Namen umstellen. In den
anderen Formularen nur verifizieren und abweichende IDs ebenso korrigieren.

**Abschlussbericht** in dieser Gliederung:
1. Je Formular: Selbstauskunfts-Feld angelegt (ja/neu/existierte) + Custom ID
2. Je Formular: Zustand der vier UTM-Custom-IDs (korrekt / korrigiert von …)
3. Publiziert: ja/nein je Formular
4. Auffälligkeiten (z. B. ein viertes Formular, das anders heisst)

---

## Backend-Stand dazu

- `ingest-paperform/index.ts` liest `selbstauskunft` (Custom-Key oder
  Beschriftung), redigiert E-Mail-Angaben und nutzt die Antwort als
  Kanal-Fallback («über den Newsletter» → newsletter statt ohne UTM).
  **Muss nach dem Repo-Stand deployt werden** (gleicher Weg wie
  ingest-uscreen).
- Test danach: Formular über einen Generator-Link mit UTM öffnen, mit einer
  `hao.bu`-Adresse absenden (zählt nie, landet nur im Roh-Log) und im Log
  prüfen, dass `selbstauskunft` ankommt.

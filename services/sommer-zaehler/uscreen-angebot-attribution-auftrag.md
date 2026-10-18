# Auftrag für Claude im Chrome: eigenes Uscreen-Angebot je bezahltem Weg

*Stand 24. Juli 2026. Vorgeschichte und Zahlen: `docs/wirkungs-lesart-24-07.md`.
Vorläufer-Auftrag (Custom-Feld, Webhooks, API, Snippets):
`uscreen-attribution-auftrag.md` — dort steht, was im Konto bereits eingerichtet
ist.*

## Warum dieser Auftrag

Die Browser-Kette (Landingpage → Checkout → `user_created` mit `utm_params`)
ist geprüft und trägt. Sie hat aber eine Grenze: sie überlebt nur, solange
Uscreen die Spur in seiner eigenen Session mitführt. Für Wege, deren Wirkung
wir **hart** kennen müssen — bezahlte Anzeigen, Partner, Inserate —, brauchen
wir einen Träger, der nicht am Browser hängt.

Den gibt es: der Checkout läuft über `goetheanum.tv/checkout/new?o=<offer_id>`,
und das Webhook-Ereignis `order_paid` liefert **`offer_id`** und **`coupon`**
serverseitig mit. Beides ist im Roh-Log belegt (u. a. `84317` Standard-Abo
Monatlich, `84322` Standard-Abo Jährlich; Coupon-Werte wie `LEGEN12` kommen
an). Ein eigenes Angebot je bezahltem Weg macht dessen Abschlüsse damit
zählbar — an Cookies, In-App-Browsern und Weiterleitungen vorbei.

**Vorher entscheiden:** Dieser Auftrag ändert Produkt-Einstellungen im
laufenden Verkauf. Er wird erst ausgeführt, wenn feststeht, dass die bezahlte
Anzeige weiterläuft. Die günstigere Reihenfolge ist: zuerst die Abschalt-Probe
(3–4 Tage aussetzen, Anmeldungen vergleichen), dann erst instrumentieren.

## Regeln für diesen Auftrag

- Nichts löschen, nichts abschalten, keine Preise ändern. Nur **duplizieren**,
  prüfen und dokumentieren.
- Keine Aktion, die Mails an Kundinnen oder Kunden auslöst.
- Geheimnisse (Webhook-URLs mit `?key=…`, Tokens) nie in den Chat schreiben
  und nicht in Screenshots zeigen — nur bestätigen, DASS sie existieren.
- Das neue Angebot muss für die Kundin **gleich** aussehen: gleicher Name,
  gleicher Preis, gleiche Gratis-Frist wie `84317`. Es ist ein Mess-Duplikat,
  kein neues Produkt.
- Wenn eine Einstellung anders heisst oder fehlt: nicht improvisieren,
  sondern notieren, wie der Bereich wirklich heisst, und im Bericht melden.

## Die Schritte

**Schritt 1 — Bestandsaufnahme.** Öffne die Angebots-/Plan-Verwaltung
(Offers bzw. Plans). Notiere für `84317` (Standard-Abo Monatlich): Preis,
Währung, Abrechnungsintervall, Gratis-Frist (Trial), Zugriffsrechte und ob
das Angebot öffentlich gelistet oder nur per Link erreichbar ist.

**Schritt 2 — Duplikat anlegen.** Lege ein Duplikat von `84317` an, intern
benannt `Standard-Abo Monatlich · Kampagne bezahlt` (der intern sichtbare
Name darf sich unterscheiden, der für Kundinnen sichtbare nicht). Alle Werte
aus Schritt 1 übernehmen. Falls wählbar: **nicht** öffentlich listen, nur
per Link erreichbar. Notiere die neue `offer_id` und die vollständige
Checkout-URL (`…/checkout/new?o=<neue_id>`).

**Schritt 3 — Gegenprobe Coupon.** Prüfe, ob die Checkout-URL einen Coupon
vorbelegen kann (Parameter am Link oder Einstellung am Angebot) und ob sich
ein Coupon anlegen lässt, der **keinen** zusätzlichen Rabatt gibt, sondern
nur als Kennung mitläuft. Das wäre der Ersatzweg, falls das Duplikat
Nebenwirkungen hat. Nur prüfen und berichten, noch nichts anlegen.

**Schritt 4 — Sichtprüfung.** Öffne die neue Checkout-URL in einem privaten
Fenster (nicht abschliessen) und prüfe: gleicher Name, gleicher Preis,
gleiche Gratis-Frist wie beim bestehenden Weg. Screenshot ohne Personendaten.

**Schritt 5 — Bericht.** Kompakt in dieser Gliederung:
1. `84317` — Preis, Intervall, Gratis-Frist, Sichtbarkeit
2. neue `offer_id` + vollständige Checkout-URL
3. Coupon-Weg: möglich ja/nein, wie genau
4. Sichtprüfung: stimmt die Kundenansicht überein?
5. Auffälligkeiten, besonders alles, was Bestandskunden berühren könnte

## Was danach bei uns passiert (Backend-Seite)

1. **Mapping eintragen.** In `sommer2026_config` eine Zeile
   `angebot_<offer_id>` mit dem UTM-Tupel des Weges, z. B.
   `meta-anzeige|social|summer26_trial|story_statisch`.
2. **Ingestion erweitern** (`ingest-uscreen/index.ts`): trägt eine Anmeldung
   keine Spur, aber eine bekannte `offer_id`, wird das hinterlegte Tupel
   gesetzt. Reihenfolge: echte UTM schlägt Angebots-Mapping, Angebots-Mapping
   schlägt `user_created`-Fallback. Der Coupon-Wert wird analog gelesen
   (`coupon` steht bereits im Payload).
3. **Link umstellen:** die Ziel-URL des Kurzlinks der Anzeige zeigt auf die
   TV-Landing, deren Knopf auf die neue Checkout-URL führen muss — das ist
   eine Lovable-Änderung an der TV-Landing (Knopf-Ziel je nach `utm_source`).
   Ohne diesen Schritt greift das Mapping nicht.
4. **Prüfen:** eine Test-Anmeldung mit einer `hao.bu`-Adresse läuft ins
   Roh-Protokoll, ohne als Abo zu zählen — damit lässt sich die Kette
   gefahrlos verifizieren.

## Was dieser Weg nicht leistet

Er misst den **Abschluss**, nicht die Wirkung auf Meta-Seite. Wer die Anzeige
im Werbekonto optimieren will (Gebote, Zielgruppen), braucht zusätzlich ein
Konversions-Ereignis im Post-purchase-Snippet — also Meta-Pixel und damit
eine Datenschutz-Entscheidung. Die ist ausdrücklich **nicht** Teil dieses
Auftrags und wird vom Auftraggeber getroffen.

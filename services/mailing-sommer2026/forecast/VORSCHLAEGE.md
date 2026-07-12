# Textvorschläge & Kontroll-Liste — Sommer-Aktion 2026

Grundregel bei allem: die Frist (8. August) ist echt, darum darf man sie nennen.
Keine erfundene Knappheit, kein Druck, kündigen bleibt einfach.

> **✓ Stand: eingebaut in die Mail-Quelle (`heroes.json`, DE + EN):**
> - **Mail 2** neu: «Drei Monate Lesestoff, geschenkt zu Ihrem Abo»
> - **Mail 3** neu: Betreff «Bis Samstag: drei Monate mitlesen, geschenkt» + der
>   neue Text (siehe Punkt 2)
> - **Mail 1** unverändert (schon stark).
> - Der Nicht-Öffner-Betreff von Mail 3 («Was Sie sehen, jetzt auch lesen — bis
>   Samstag») **bleibt** — sonst bekämen Öffner und Nicht-Öffner denselben Betreff.
>
> **Zwei bewusste Abweichungen** von dem, was ich vorhin genannt habe, mit Grund:
> Mail 2 wurde **nicht** «Was Sie sehen, jetzt auch lesen — bis 8. August», weil
> das die Zeile aus Mail 1 fast wörtlich wiederholt (liest sich wie kopiert).
> Mail 3 wurde **nicht** «Bis Samstag: was Sie sehen, jetzt auch lesen», weil das
> exakt der Nicht-Öffner-Betreff ist — dann wäre die Unterscheidung weg. Beide
> Alternativen bleiben wählbar; ein Wort, und ich tausche.
>
> **Vor dem Versand von Mail 3** einmal `build_editor.py --publish` laufen lassen,
> damit der neue Mail-3-Text auch im HTML steht (die Betreffe wirken schon über
> die AC-Tabelle).

---

## 1 · Bessere Betreffzeilen (deutsche «Lesen»-Mails)

Die «Lesen»-Mails werden gut geöffnet, aber selten geklickt. Betreff-Alternativen,
falls Du eine gegen die aktuelle testen willst:

**Mail 1 (Ankündigung)**
- Aktuell: «Was Sie sehen, jetzt auch lesen — 3 Monate gratis»  ← schon stark
- Variante: «Jede Woche denkt jemand vor Ihnen laut — 3 Monate gratis»
- Variante: «Diesen Sommer mitlesen — drei Monate geschenkt»
- *Warum:* Die aktuelle ist die beste (sie sagt sofort, worum es geht). Die erste
  Variante nennt den konkreten Reiz.

**Mail 2 (Erinnerung)** — hier wird am wenigsten geklickt
- Aktuell: «Ihr Sommer hat noch Seiten frei»
- Variante: «Was Sie sehen, jetzt auch lesen — noch bis 8. August»
- Variante: «Drei Monate Lesestoff, geschenkt zu Ihrem Abo»
- *Warum:* Die aktuelle ist hübsch, aber unkonkret — man weiss nicht, was man
  anklicken soll. Die Varianten sagen klar, was drin ist, und nennen die Frist.

**Mail 3 (Schluss)**
- Aktuell: «Nur noch bis Samstag: drei Monate gratis»
- Variante: «Bis Samstag: was Sie sehen, jetzt auch lesen»
- Variante: «Am Samstag endet die Sommer-Aktion — drei Monate gratis»
- *Warum:* Die erste Variante verbindet die echte Frist mit dem Reiz («jetzt auch
  lesen») — genau das hat bei der TV-Aktion gezogen. Die zweite sagt ehrlich, was
  endet: die Aktion, nicht Ihr Zugang.

---

## 2 · Die letzte Erinnerung, die zieht (Mail 3 «Lesen»)

Bei der TV-Aktion zog die Schluss-Mail, bei der Lese-Aktion nicht. Der Grund ist
nicht mehr Druck, sondern: **klar sagen, was man bekommt, und die echte Frist
nennen.** So würde ich Mail 3 umschreiben:

| | Aktuell | Vorschlag |
|---|---|---|
| **Betreff** | Nur noch bis Samstag: drei Monate gratis | Bis Samstag: was Sie sehen, jetzt auch lesen |
| **Vorschau-Zeile** | Eine Minute für drei Monate Lesezeit: die Wochenschrift gratis zu Ihrem Abo — bis Samstag. | Drei Gratis-Monate zum Mitlesen — nur noch bis Samstag, 8. August. |
| **Text** | Noch ein paar Sommertage lang: die Wochenschrift, drei Monate gratis zu Ihrem Abo. Wenn sie Ihnen nicht ans Herz wächst, kündigen Sie einfach. | Diese Woche endet die Sommer-Aktion. Bis Samstag lesen Sie die Wochenschrift drei Monate gratis zu Ihrem Abo — und kommen mit anderen Augen in Ihre Woche zurück. Gefällt es nicht, kündigen Sie mit einem Klick. |

Für Leute, die die ersten Mails **nicht** geöffnet haben, bleibt der andere Betreff
«Was Sie sehen, jetzt auch lesen — bis Samstag» (die sehen die Brücke zum ersten
Mal). Das ist schon so eingerichtet — gut.

---

## 3 · Nachfass-Mails nach dem Gratis-Start (neu — das Wichtigste)

Drei kurze Mails an jede Person, die den Gratis-Test startet. Ziel: dass aus
Gratis-Testern zahlende Leser:innen werden — freundlich, ohne Druck. Unten die
Wochenschrift-Fassung; für goetheanum.tv läuft dieselbe Strecke mit «sehen» statt
«lesen» (schreibe ich, sobald diese hier steht).

### Mail A — Willkommen (sofort nach dem Start)

**DE**
- Betreff: «Willkommen — Ihre erste Woche zum Mitlesen»
- Vorschau: «Drei Monate Wochenschrift, geschenkt. So finden Sie hinein.»
- Text: «Schön, dass Sie dabei sind. Die Wochenschrift erscheint jede Woche — Sie
  müssen nichts nachholen, fangen Sie einfach mit der aktuellen Ausgabe an. Ein
  Vorschlag für den Anfang: [aktueller Beitrag]. Lesen Sie, wo der Sommer Sie
  hinträgt.»
- Knopf: «Zur aktuellen Ausgabe»

**EN**
- Betreff: «Welcome — your first week of reading»
- Vorschau: «Three months of the weekly, as a gift. Here’s how to begin.»
- Text: «Glad you’re here. The weekly comes out every week — there’s nothing to
  catch up on, simply start with the current issue. A suggestion to begin:
  [current piece]. Read wherever summer takes you.»
- Knopf: «Read the current issue»

### Mail B — Anstoss nach der Hälfte (~6 Wochen später)

**DE**
- Betreff: «Haben Sie diese Woche schon gelesen?»
- Vorschau: «Ein Stück, das nachklingt — mitten in Ihren drei Gratis-Monaten.»
- Text: «Die Hälfte Ihrer drei Monate ist um. Falls die Woche voll war — hier ist
  ein Beitrag, der sich lohnt: [Empfehlung]. Ein paar Minuten, die anders
  weiterdenken lassen.»
- Knopf: «Jetzt lesen»

**EN**
- Betreff: «Have you read this week yet?»
- Vorschau: «A piece that stays with you — halfway through your free months.»
- Text: «You’re halfway through your three months. If the week was full — here’s
  one worth your time: [recommendation]. A few minutes that keep working in you.»
- Knopf: «Read now»

### Mail C — Erinnerung vor dem Ende (~2 Wochen vor Ablauf)

**DE**
- Betreff: «In zwei Wochen endet Ihre Gratis-Zeit»
- Vorschau: «Was danach passiert — und wie Sie entscheiden.»
- Text: «Ihre drei Gratis-Monate der Wochenschrift enden am [Datum]. Danach läuft
  Ihr Abo regulär weiter — wenn Sie mögen. Wenn nicht, kündigen Sie bis dahin mit
  einem Klick, ohne Angabe von Gründen. Und falls Sie geblieben sind, weil es
  Ihnen etwas gibt: schön, dass Sie mitlesen.»
- Knopf: «Abo ansehen»

**EN**
- Betreff: «Your free time ends in two weeks»
- Vorschau: «What happens next — and how you decide.»
- Text: «Your three free months of the weekly end on [date]. After that your
  subscription simply continues — if you’d like. If not, cancel before then in one
  click, no reasons needed. And if you stayed because it gives you something:
  we’re glad you’re reading.»
- Knopf: «View subscription»

*So ist es gebaut:* Die Mails hängen am Abo-Start (Tag 0 · ~Tag 45 · ~Tag 75).
Ehrlich nach eurem Kündigungsmodell (läuft weiter, wenn man nichts tut; kündigen
jederzeit einfach). Die [Platzhalter] fülle ich mit echten Beiträgen/Daten, sobald
Du die Strecke freigibst.

---

## 4 · Kontroll-Liste: Läuft die Aktion?

Ein bis zwei Tage nach jeder Mail auf drei Zahlen schauen — mehr braucht es nicht:

1. **Wie viele haben geöffnet?**  Gut: etwa 4 von 10. Unter 3 von 10 → Betreff
   oder Absender prüfen.
2. **Wie viele haben geklickt?**  Normal: 1–2 von 100. Das ist die wackelige
   Stelle — hier geht’s um den Knopf und das Angebot in der Mail.
3. **Wie viele haben sich angemeldet?**  Steht bei den neuen Gratis-Tests im
   Cockpit.

**Ampel:**
- **Grün:** Anmeldungen tröpfeln stetig herein, Abmeldungen bleiben unter 1 von 100.
- **Gelb:** Viele öffnen, fast keiner klickt → der Knopf/das Angebot ist unklar.
- **Rot:** Abmeldungen über 1 von 100, **oder** die Anmelde-Seite verliert Leute
  zwischen Klick und Formular → Seite prüfen (der häufigste stille Verlust).

**Die wichtigste Zahl kommt nach der Aktion:** Wie viele der Gratis-Tester bleiben
zahlend? Das entscheidet, ob sich alles gelohnt hat — und genau dafür sind die
Nachfass-Mails aus Punkt 3 da.

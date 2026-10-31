# Recherche: UX und UI von Spendenformularen (31. 10. 2026)

Grundlage für Review und Neugestaltung des Formulars auf
https://goetheanum.io/de/spenden. Vorarbeit: Befund und Memo auf dem Branch
`spenden-befund` (PR https://github.com/phtok/goeloggen/pull/723).

**Methode.** Nur lesend im Web (Suche und Abruf von Seiten), drei
Teilrecherchen, zusammengeführt. Jede Zeile nennt Quelle, Aussage, Methode
und die Folgerung für das Goetheanum-Formular. Belegtiefe: **geöffnet** =
Seite selbst abgerufen (der Abruf wurde von einem kleinen Modell
zusammengefasst, Zitate sind daher sinngemäss); **Suche** = nur in
Suchtreffern gesehen; **Erfahrungswert** = nicht belegt. Beinahe alle
Experimente stammen aus den USA; Übertragbarkeit auf Dornach und CHF ist
nirgends belegt. Rechtsangaben geben den Stand der Quelle wieder, keine
Rechtsberatung. Nicht lesbar waren Unicef Schweiz und Pro Natura (HTTP 403);
dazu steht nichts Erfundenes.

## 1. Formular-Grundlagen

| Quelle | Aussage | Methode | Folgerung für das Goetheanum-Formular |
|---|---|---|---|
| GOV.UK, Error summary und Error message: https://design-system.service.gov.uk/components/error-summary/ · https://design-system.service.gov.uk/components/error-message/ | Bei jedem Fehler eine Zusammenfassung oben, Fokus darauf, jeder Eintrag verlinkt das Feld, gleicher Text wie am Feld; Meldung sagt, was falsch ist und wie es sich beheben lässt; «This field is required» gilt als zu vage; Eingaben bleiben erhalten. | Designsystem-Doku | Fehlerzusammenfassung mit Sprunglinks; konkrete Sätze («Geben Sie Ihre E-Mail-Adresse ein»); Betrag und Adresse bleiben nach Fehler stehen. |
| GOV.UK, Question pages: https://design-system.service.gov.uk/patterns/question-pages/ | Eine Frage je Seite (Fokus, Screenreader); verwandte Fragen dürfen gruppiert werden, wenn Forschung es stützt. | Doku, keine Zahlen | Drei Gruppen (Betrag · Angaben · Zahlung) sind vertretbar; «eine Frage je Seite» steigert Spenden nirgends belegt. |
| GOV.UK, Text input: https://design-system.service.gov.uk/components/text-input/ | Label sichtbar über dem Feld; Platzhalter nie als Label, Hinweis oder Beispiel; `autocomplete` setzen; `inputmode` statt `type="number"`; Währung auch im Label nennen. | Doku | Betragsfeld mit `inputmode="decimal"` und «CHF» im Label; PLZ-Feld schmal. |
| GOV.UK, Radios: https://design-system.service.gov.uk/components/radios/ | Nicht vorauswählen: Nutzer übersehen die Frage oder senden die falsche Antwort. | Doku | Vorauswahl von Betrag oder «monatlich» ist ein offen zu führender Gestaltungsentscheid; Wirkung auf die Spendenhöhe nicht belegt. |
| NN/g, Platzhalter: https://www.nngroup.com/articles/form-design-placeholders/ | Sieben Nachteile (Gedächtnis, Fehlerkorrektur, schwacher Kontrast, gefüllt wirkende Felder, Screenreader). | Usability-Tests, Stichprobe nicht genannt | Sichtbare Labels; Platzhalter höchstens für ein Formatbeispiel. |
| NN/g, Fehler in Formularen: https://www.nngroup.com/articles/errors-forms-design-guidelines/ | Prüfung, sobald das Feld verlassen wird, nicht beim Tippen; Meldung am Feld; Zusammenfassung nie als einziger Hinweis. | Richtlinie, keine Studie | Prüfung beim Verlassen des Felds; Zielkonflikt: GOV.UK ist bei Inline-Prüfung zurückhaltender. |
| NN/g, Pflichtfelder: https://www.nngroup.com/videos/required-fields-forms/ | Stern für Pflichtfelder verbessere die Bedienbarkeit. Gegenmeinung: https://digitalcommunications.wp.st-andrews.ac.uk/2020/10/27/how-to-indicate-required-and-optional-fields-in-forms/ (Suche) | Video, keine Zahlen | Pflicht und freiwillig sichtbar trennen; Pflichtfelder auf das Nötige kürzen. Welche Kennzeichnung besser konvertiert: nicht belegt. |
| NN/g, Touch Target Size: https://www.nngroup.com/articles/touch-target-size/ | Mindestens 1 cm × 1 cm; Quelle Parhi, Karlson, Bederson 2006. Apple 44 pt, Material 48 dp (nur über Sekundärquellen, Suche). | Literaturverweis | 44 px (Haus B04) ist gedeckt; die heutigen 39 und 42 px liegen darunter. |
| Baymard, Zahl der Felder: https://baymard.com/blog/checkout-flow-average-form-fields | Durchschnitt 11,3 Felder im Checkout (2024); «most sites need only 8»; die Feldzahl wirke stärker als die Schrittzahl. | Benchmark, Online-Shops | Das Spendenformular hat 11 Felder und Kästchen; kürzen. Übertragbarkeit auf Spenden: Erfahrungswert. |
| Wroblewski, «Web Form Design» (2008), Folien: https://static.lukew.com/WebForms_LukeW_101209.pdf (Suche) | Label über dem Feld erlaubt, Label und Feld in einer Augenbewegung zu erfassen. Die oft zitierte Zahl «doppelt so schnell» ist nicht verifiziert. | Eyetracking Penzo 2006, Stichprobe unbekannt | Label oben, einspaltig; die Zahl nicht zitieren. |
| Jarrett/Gaffney, «Forms that Work» (2008): https://shop.elsevier.com/books/forms-that-work/jarrett/978-1-55860-710-1 · Silver, «Form Design Patterns» (2018) | Drei Schichten: Beziehung, Gespräch, Erscheinung. Silvers Buchtext nicht gelesen. | Verlagsangabe | Zweck, Datenverwendung und Bescheinigung vor dem Feld klären. Einzelaussagen beider Bücher: Erfahrungswert. |
| iOS-Zoom: https://docs.squirrelscan.com/rules/mobile/input-zoom (Suche) | iOS Safari zoomt bei Feldschrift unter 16 px; Zoom nie sperren. | Entwicklerdoku, keine Apple-Primärquelle | Felder ≥16 px (Haus B03); heute 15.2 px. |

## 2. Spendenseiten im Besonderen

Evidenz: **Experiment** (A/B-Test), **Benchmark** (Erhebung), **Meinung**
(Anbieter-Blog).

| Quelle | Aussage | Stichprobe/Methode | Folgerung |
|---|---|---|---|
| M+R Benchmarks 2026: https://mrbenchmarks.com/fundraising/ | Monatsspenden = 27 % des Online-Umsatzes 2025 (klein: 22 %, sehr gross: 37 %); 81 % der Dauerspendenden nach 7 Monaten noch dabei, 71 % nach einem Jahr. | 180 Non-Profits, USA, Selbstauskunft (Benchmark) | Monatsoption ist Standard; ein kleines Haus rechnet eher mit etwa 20 %. |
| M+R 2026 über Anedot: https://www.anedot.com/blog/year-end-donation-page-checklist | Spendenseite 11 % Desktop, 8 % mobil; mobil 52 % des Verkehrs, aber 28 % des Umsatzes. | Sekundär (Benchmark) | Mobil zuerst bauen; kleine Organisationen 4 % mobil als Massstab. |
| NextAfter, CaringBridge: https://www.nextafter.com/experiments/how-adding-suggested-gift-amounts-affects-donor-conversion/ | 4 gegen 6 Betragskacheln: 0,96 % → 2,0 % (+104 %, 98,7 %); Ø Gabe −4 $ (nicht signifikant). | A/B, n = 4 159, 2015 (Experiment) | Mehr und tiefere Stufen testen; heute vier Kacheln. |
| NextAfter, Jerusalem Prayer Team: https://www.nextafter.com/experiments/how-increasing-the-lowest-gift-amount-affects-donation-revenue/ | Tiefste Stufe 3 $ → 9 $: Umsatz je Besucher 4,14 → 6,64 $ (+60,6 %, 96,0 %). | A/B, Stichprobe nicht genannt | Tiefste Kachel wirkt als Anker; 25 CHF prüfen, nicht unter 10 CHF. |
| NextAfter, Leadership Institute: https://www.nextafter.com/experiments/how-more-donation-options-with-a-lower-initial-ask-affects-recurring-donations/ | Monatsstufen mit tieferem Einstieg: Abschluss 6,3 % → 14,3 % (+125 %). | n = 445, klein | Monatsoption braucht eigene, tiefere Stufen. |
| NextAfter, Monatsstandard 2025: https://www.nextafter.com/experiments/how-defaulting-a-form-to-monthly-adding-a-monthly-callout-affects-donor-conversion/ | Standard monatlich plus Hinweis: Quote 0,33 % → 0,96 %; Umsatz +214 %; **Einmalspenden −34,2 %** (99,9 %). | n = 7 734, 10 Tage, Social-Media-Verkehr | Monatsstandard bringt viele Dauerspendende, kostet Einmalspenden; Lebenswert nicht gemessen. |
| NextAfter, Focus on the Family: https://www.nextafter.com/experiments/how-defaulting-to-recurring-gift-on-an-acquisition-donation-page-impacts-recurring-donor-conversion/ | Monatsstandard: Monatsspenden 13 gegen 3, aber alle Transaktionen −22 %, Umsatz je Besucher −50 %. | n = 2 530; Seite enthält interne Widersprüche | Gegenstück zum vorigen Test: kein sicherer Gewinn. |
| NextAfter, Formularaufbau (Fund for American Studies): https://www.nextafter.com/experiments/how-form-formatting-improved-donor-conversion-rate/ | Betrag zuerst, grössere Knöpfe, Abschnitte: 0 % → 4,1 %. | n = 244, 5 Spenden | Zu schwach für eine Zahl; Reihenfolge Betrag, dann Angaben ist plausibel. |
| NextAfter, Care Net, Dallas Theological Seminary, Buckner (nur Suchtreffer): https://www.nextafter.com/experiments/how-reducing-donation-form-friction-affects-conversion/ · https://www.nextafter.com/experiments/how-embedding-a-donation-form-impacts-donations-2/ · https://www.nextafter.com/experiments/how-removing-unnecessary-elements-on-a-donation-page-impacts-donor-conversion/ | Weniger Felder +107 %; Formular eingebettet statt hinter Knopf +36,9 %; aber Buckner: optionale Felder entfernt −24 % bei nur 83,5 % Konfidenz. | Stichproben nicht erfasst | Weniger Felder und sichtbares Formular helfen meist, nicht immer: als Hypothese testen. |
| Baymard, Checkout 2025: https://baymard.com/research-articles/current-state-of-checkout-ux | 18 % der US-Käufer brachen ab, weil sie ein Konto anlegen sollten; über 70 % zögern bei der Telefonnummer; optionale Felder kosten 5–30 % Zeit; 61 % der Seiten trennen Pflicht und optional nicht. | Umfrage n = 1 026, Usability-Tests; Online-Handel | Spende ohne Konto; keine Telefonnummer; «Adresse nur bei Bedarf» liefert Baymard keine Zahl. |
| Altmann u. a. 2019, «Defaults and Donations»: https://econpapers.repec.org/RePEc:tpr:restat:v:101:y:2019:i:5:p:808-826 | Voreinstellung lenkt das Einzelverhalten stark, der Gesamtbetrag bleibt aber unverändert. | Feldexperiment, Abstract gelesen | Standardbetrag verschiebt die Verteilung, hebt die Summe nicht sicher. |
| charity: water über Optimizely: https://www.optimizely.com/field-notes/customer-stories/charity-water | Höherer Standardbetrag (60 $): Durchschnitt stieg, Konversion sank nicht; weniger Angaben bei Kampagnenanmeldung +34 %. | Herstellerbericht, Signifikanz nicht genannt | Höheren Standardbetrag und weniger Felder testen. |
| Qgiv über NextAfter: https://www.qgiv.com/blog/use-recurring-upgrade-prompts-to-grow-your-fundraising/ | Upgrade-Hinweis +64 % Dauerspenden; nur 10 % der Organisationen nutzen ihn. | Anbieter-Blog, Original nicht geöffnet | Zweistufige Anfrage ist unbelegt; selbst testen. |
| NextAfter-Audit über Anedot (siehe oben) | 66 % mit hervorgehobenem Betrag, 62 % mit Sicherheitshinweis, nur 14 % fragen auf der Dankesseite nach Dauerspende. | 138 Organisationen, Dritthand (Meinung) | Beschreibt Brauch, keine Wirkung. |
| Wirkungsangabe je Betrag, Betragsformat ohne «.00», Zahlungslogos, «above the fold», Teilen auf der Dankesseite | Kein kontrollierter Test gefunden. | Suche | **Nicht belegt.** «50 CHF» statt «50.00» ist Konvention und Hausregel G25; Wirkungsangaben nur, wenn wahr. |
| Dankesseite und Mail, DonorsChoose (arXiv): https://arxiv.org/pdf/1503.02729 (Suche) | Schnellere Dankesnoten gingen mit höherer Rückkehrrate einher, am stärksten binnen 24 h. «48 Stunden» und «4×» stammen aus Blogs ohne Beleg. | Korrelation | Dank sofort und automatisch; die Blog-Zahlen nicht zitieren. |
| Small, Loewenstein, Slovic 2007, über https://www.gsb.stanford.edu/insights/increase-charitable-donations-appeal-heart-not-head | Identifizierbares Opfer; vorregistrierte Replikation bestätigte es nicht. | Laborstudien, umstritten | Nicht als Gestaltungsgrund verwenden. |

## 3. Schweiz und Deutschland

| Quelle | Aussage | Methode | Folgerung |
|---|---|---|---|
| RaiseNow-Studie 2025 (Daten 2024): https://www.raisenow.com/en/about/press/fundraising-study-2025 | TWINT = 68,1 % des CHF-Spendenvolumens; 53,8 % der Online-Spenden mobil; Ø Spende CHF 33,5. | 7 194 Organisationen, Plattformdaten (Hersteller) | TWINT zuerst, mobil zuerst. |
| RaiseNow-Studie 2026 über https://www.verbandsbuero.de/zahlungsmethoden-im-fundraising/ | 2025: TWINT 77,6 %, Einzahlungsschein 11,2 %, Karte 6,5 %; Apple Pay 4,9 % wo angeboten. | Sekundär; Sprung 68 → 78 % ungeklärt | Karte nachrangig, Wallets als Zusatz. |
| TWINT-Zahlen: https://www.finews.ch/news/finanzplatz/71218-twint-2025-transaktionen-kunden | Über 6 Mio. Nutzende, rund zwei von drei Einwohnenden; Akzeptanz 86 % der Online-Shops. | Herstellerangabe | Ein Formular ohne TWINT lässt den Heimmarkt aus. |
| Blick 2023: https://www.blick.ch/wirtschaft/viele-spender-merken-es-nicht-einmal-schweizer-banken-kassieren-bei-spenden-ueber-twint-mit-id18977489.html | Rotes Kreuz: ein Drittel der Online-Spenden via TWINT; Glückskette: etwas mehr als die Hälfte. | Angaben der Organisationen | Anteil je nach Haus ein Drittel bis die Hälfte. |
| Fundraise Up, TWINT: https://fundraiseup.com/docs/twint/ | TWINT für einmalig und jede Wiederholung; mobil «Open TWINT», am Rechner QR-Code, 10 Minuten gültig. | Doku | Beide Wege und den Rückweg erklären. |
| Stripe, TWINT: https://docs.stripe.com/payments/twint | Minimum 0.50 CHF, Maximum 5 000 CHF; Wiederholung per Mandat; kein Express-Checkout. | Doku | Für Grossspenden Überweisung oder QR-Rechnung nennen. |
| Stripe, Zahlarten ordnen: https://docs.stripe.com/payments/customize-payment-methods | Standard: dynamische Reihenfolge; mit `paymentMethodOrder` festlegbar; höchstens fünf sichtbar im Akkordeon. | Doku, kein Konversionsbeleg | Reihenfolge TWINT, Karte/Wallets, PayPal setzen; Wirkung Erfahrungswert. |
| Pro Juventute: https://www.projuventute.ch/de/spenden · SRF 2022: https://www.srf.ch/news/transaktionsgebuehren-verdient-sich-jemand-eine-goldene-nase-an-den-ukraine-spenden | Gebühren je Zahlart ausgewiesen: TWINT 1.3 %, Karte 1.25 %, QR-Rechnung 0.2 %; RaiseNow im Schnitt 1,8 %. | geöffnet | Gebühren offen nennen, Übernahme anbieten. |
| QR-Rechnung: https://www.postfinance.ch/de/ueber-uns/medien/newsroom/einzahlungsscheine-werden-2022-vom-markt-genommen.html (Suche) | Einzahlungsscheine seit 30. 9. 2022 nicht mehr verarbeitet. Leeres Betragsfeld für Spenden: nur bei einem kommerziellen Generator belegt. | Suche | QR-Rechnung zum Herunterladen neben dem Formular. |
| Kanton Zürich: https://www.zh.ch/de/steuern-finanzen/steuern/steuern-natuerliche-personen/spenden-an-gemeinnuetzige-organisationen.html | Abzug ab CHF 100 im Jahr, höchstens 20 % des Nettoeinkommens, Bescheinigung auf Nachfrage. Andere Kantone weichen ab (nur Suche, nicht verifiziert). | Behördenseite | Keine feste Zusage «ab 100 Franken»; sagen, wann die Bescheinigung kommt. |
| Deutschland: https://www.finanzverwaltung.nrw.de/spenden | Bis 300 € genügt der Kontoauszug (vereinfachter Nachweis). Ob je Spende oder je Jahr: Quellen widersprüchlich. | Behördenseite | Gilt nur für in Deutschland anerkannte Empfänger; Klärung nötig. |
| EDÖB-Merkblatt Cookies, 27. 3. 2026: https://www.edoeb.admin.ch/dam/de/sd-web/ByXs53ExpIEy/20260327%20Merkblatt%20Cookies_DE.pdf | Schweizer Recht (Art. 45c FMG): informieren und Ablehnen ermöglichen; Zustimmung vorab nur bei unerwarteter oder risikoreicher Bearbeitung; notwendige Cookies als eigene Kategorie. Anwaltsquellen lesen den Leitfaden strenger. | Behördenmerkblatt gelesen | Zwangs-Wand vor dem Formular ist nach dem Merkblatt nicht verlangt; Anwalt klären lassen. |
| Farronato, Fradkin, Lin 2025, «Designing Consent»: https://www.nber.org/papers/w34025 (Suche) | Ohne Eingriff akzeptieren über die Hälfte alle Cookies; Optionen hinter Zusatzklicks verschieben die Wahl. | Feldexperiment, Abstract | Gleich grosse Knöpfe «Alle akzeptieren» und «Ablehnen». |
| Banner und Konversion (Herstellerblogs): https://pandectes.io/blog/cookie-consent-rate/ | Spannen 8–15 % weniger Konversion nach Banner; nicht blockierendes Banner +32 % in einem Shop-Test. | Anbieter, Online-Handel | **Kein Beleg für Spenden.** «Vertrauen durch Banner» ist Erfahrungswert. |

## 4. Beispiele

Unicef Schweiz und Pro Natura waren nicht abrufbar (HTTP 403).

| Beispiel | Drei Beobachtungen | Lehre |
|---|---|---|
| charity: water, https://www.charitywater.org/donate | Alternativwege (Überweisung ab 6 000 $, Aktien); Vertrauensbündel (Candid Platin, Charity Navigator, 501(c)(3), «100 %»); Monatsspende getrennt. Das Formular selbst war nicht lesbar. | Vertrauensbelege bündeln; Aufbau nicht beurteilbar. |
| Wikimedia, https://wikimediafoundation.org/give/ | Einmalig, monatlich, jährlich; Apple Pay, Google Pay, PayPal; ehrlicher Steuerhinweis («wahrscheinlich nicht» absetzbar ausserhalb der USA) und ein Satz Datenschutzzusage. Banner-Tests 2010: kein Unterschied zwischen Betragsreihen ($15–$500 gegen $20–$250), Suche. | Ehrlich sagen, wo der Abzug nicht gilt; Betragsstufen haben weniger Hebel als erwartet. |
| GiveWell, https://secure.givewell.org/ | Einmalig oder monatlich, Freibetrag ab 5 $, keine Stufen; Bankkonto bei grossen Beträgen billiger; viele Felder samt Herkunftsfrage und zwei Einwilligungen. | Gebührentransparenz ja; die Zahl der Felder ist hoch. |
| WWF Schweiz, https://www.wwf.ch/de/spenden | Sieben CHF-Stufen plus Freibetrag, Themenwahl; Zahlarten im Text, TWINT dort nicht erwähnt; Zewo, Telefonnummer, Bescheinigung «im darauffolgenden Januar». | Telefonnummer und Termin der Bescheinigung nennen. |
| Pro Juventute, https://www.projuventute.ch/de/spenden | Zahlarten mit Gebühren sichtbar; Zewo und Rechtsform; Steuerhinweis, Jahresbestätigung bis Mitte Februar. | Gebühren und Termin offenlegen. |
| Caritas Schweiz, https://www.caritas.ch/ | Häufigkeit einmalig/monatlich/jährlich, Stufen 75, 125, 250 CHF plus Freibetrag; «Mit TWINT spenden» als eigener Knopf; «Ihre Daten sind bei uns sicher», Zewo. | Häufigkeit und TWINT-Direktweg schon am Einstieg. |
| Glückskette, https://www.glueckskette.ch/ | Startseite nennt QR-Rechnung und E-Banking, TWINT erst im Formular; Vertrauen über Unabhängigkeit und SRG; Steuerhinweis in einem Satz. | Einstiegsblock und Formular trennen. |

## 5. Barrierefreiheit (WCAG 2.2)

| Kriterium | Inhalt | Folgerung |
|---|---|---|
| 3.3.7 Redundant Entry (A): https://www.w3.org/WAI/WCAG22/Understanding/redundant-entry.html | Bereits im Vorgang Eingegebenes nicht erneut abfragen; bei Fehler Werte nicht löschen. | Quittungsadresse = Spenderadresse; kein E-Mail-Wiederholungsfeld; Betrag bleibt bei Rücksprung. |
| 3.3.8 Accessible Authentication (AA): https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html | Bei Anmeldung keine kognitive Prüfung; Einfügen in Codefelder erlauben. | Für Spende ohne Login wenig betroffen; Captcha ohne Rätsel wählen. |
| 1.3.5 Input Purpose (AA): https://www.w3.org/WAI/WCAG22/Understanding/identify-input-purpose.html | `autocomplete`-Tokens für Personenangaben. | `given-name`, `family-name`, `email`, `street-address`, `postal-code`, `address-level2`, `country` setzen (die letzten fünf in der Seitenzusammenfassung nicht ausdrücklich genannt). |
| 2.5.8 Target Size (AA): https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | Mindestens 24 × 24 CSS-Pixel. | Haus gibt 44 px; Kästchen heute 22 px, also unter dem WCAG-Minimum. |
| 3.3.1 und 3.3.3: https://www.w3.org/WAI/WCAG22/Understanding/error-identification.html · https://www.w3.org/WAI/WCAG22/Understanding/error-suggestion.html | Fehler in Text, nicht nur Farbe; Korrekturvorschlag. | Eigene Texte mit `aria-invalid` und `aria-describedby`. |
| 1.4.12 Text Spacing: https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | Zeilenhöhe 1,5, Buchstabenabstand 0,12 em ohne Verlust. | Knöpfe und Labels mit `min-height` und `em`. |
| 4.1.3 Status Messages: https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html | `role="status"` und `role="alert"` für Meldungen ohne Fokuswechsel. | «Zahlung wird verarbeitet» und Betragsänderung als Status. |

## Zwanzig belegte Regeln für das Goetheanum-Spendenformular

Erfahrungswerte sind als solche gekennzeichnet.

1. Zuerst der Betrag, dann Angaben, dann Zahlung (Aufbau plausibel; NextAfter, Fund for American Studies, schwacher Test).
2. Nur nötige Felder; jede Zusatzfrage streichen oder nach der Zahlung (Baymard, Feldzahl; NextAfter Care Net; Gegenbeispiel Buckner, daher testen).
3. Kein Konto, keine Telefonnummer (Baymard, Checkout 2025).
4. Pflicht und freiwillig sichtbar trennen (NN/g Pflichtfelder; Baymard: 61 % tun es nicht).
5. Label sichtbar über dem Feld, einspaltig, Platzhalter nie als Label (GOV.UK Text input; NN/g Platzhalter; Wroblewski).
6. Eingabefelder ≥16 px, nie Zoom sperren (iOS-Zoom, squirrelscan; Haus B03).
7. Alle Ziele ≥44 px, Kästchen eingeschlossen; WCAG-Minimum 24 px (NN/g Touch Target; WCAG 2.5.8).
8. Fehler: Zusammenfassung oben mit Sprunglinks, gleicher Text am Feld, konkreter Satz, Eingaben bleiben (GOV.UK Error summary; WCAG 3.3.1, 3.3.3, 3.3.7).
9. Prüfung beim Verlassen des Felds, nicht beim Tippen (NN/g Fehler in Formularen).
10. `autocomplete`-Tokens an allen Personenfeldern, `inputmode="decimal"` am Betrag (WCAG 1.3.5; GOV.UK Text input).
11. Betrag ohne «.00», Währung im Label nennen (GOV.UK Text input; Hausregel G25; Wirkung auf Spenden nicht belegt).
12. Mehr Betragsstufen mit tieferem Einstieg ausprobieren, eigene Stufen für monatlich (NextAfter CaringBridge, Jerusalem Prayer Team, Leadership Institute).
13. Standardbetrag verschiebt die Verteilung, nicht sicher die Summe; als Test führen (Altmann u. a. 2019; charity: water).
14. Einmalig/monatlich ist ein sichtbarer Wahlschalter; «monatlich» als Standard erst nach Test, weil Einmalspenden sinken können (NextAfter 2025: −34,2 %; Focus on the Family: Umsatz je Besucher −50 %; M+R: 27 % des Umsatzes monatlich).
15. TWINT als erste Zahlart, danach Karte/Wallets, PayPal; Zahlarten vor dem Absenden sichtbar (RaiseNow 2025: TWINT 68,1 % bzw. 77,6 % des CHF-Volumens; Stripe-Doku zur Reihenfolge; Sichtbarkeit selbst: Erfahrungswert).
16. Beide TWINT-Wege erklären (App-Wechsel mobil, QR am Rechner) und Rückweg klar machen (Fundraise Up; Stripe: Maximum 5 000 CHF, daneben QR-Rechnung/Überweisung nennen).
17. Gebühren je Zahlart offen nennen und Übernahme anbieten (Pro Juventute; Glückskette über Blick/SRF).
18. Bescheinigung: sagen, wann sie kommt, und keine feste Kantonszusage geben (WWF, Pro Juventute; Kanton Zürich; Kantone weichen ab).
19. Cookie-Hinweis darf den Zahlschritt nicht blockieren; «Alle akzeptieren» und «Ablehnen» gleich gross (EDÖB-Merkblatt 2026; Farronato u. a. 2025; Wirkung auf Spenden: nicht belegt).
20. Dank sofort und automatisch, Dankesseite nennt, was geschieht (Mail, Bescheinigung); Zweitanfrage «monatlich» dort ist selten und ungetestet (DonorsChoose, Korrelation; NextAfter-Audit, 14 %).

## Offene Fragen an den Auftraggeber

1. Soll «monatlich» als Wahl angeboten werden, und wenn ja: ohne Vorauswahl (GOV.UK) oder als Test mit Vorauswahl? Mass wäre der Lebenswert, nicht die Zahl der Spenden.
2. Welche Zahlarten sind heute tatsächlich freigeschaltet (TWINT, Karte, PayPal, Apple Pay, QR-Rechnung), und wer trägt die Gebühren?
3. Welche Adresse braucht die Spendenbescheinigung, und wird sie für Spenden unter einem Betrag überhaupt verschickt? Gilt sie für Spendende aus Deutschland?
4. Ist die Cookie-Wand (iubenda) zwingend, oder darf der Hinweis den Zahlschritt freigeben? Das klärt eine Rechtsprüfung, nicht diese Recherche.
5. Dürfen Wirkungsangaben je Betrag («50 CHF = …») stehen, und welche Beträge und Wirkungen sind wahr? Ohne diese Angaben bleibt die Wirkungszeile weg.

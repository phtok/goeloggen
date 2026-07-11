# Rücklauf-Agent — Vertrag

Der Rücklauf-Agent schliesst die Gegenlese-Schleife: **offener Kommentar → Fassung
in `heroes.json` → gebaut → PR → nach Merge erledigt.** Er *bereitet vor und schlägt
vor*; den Versand löst weiterhin ein Mensch aus. Kleiner Blast-Radius, weil er nur
an einer Stelle schreibt (`heroes.json`) und die Prüfmaschinen (typo-check, ds-lint)
jede Regelverletzung abfangen.

## Herz (deterministisch)
`python3 ruecklauf.py` — holt die **offenen** Kommentare aus Supabase und macht daraus
eine Arbeitsliste: je Kommentar der **exakte heroes.json-Pfad**, der **aktuelle Text**
und die **Kommentar-ID**. `--json` maschinenlesbar, `--alle` inkl. erledigter (Rückschau).
Nur Lesen. Das ist der Teil, den der Agent nicht neu erraten muss.

## Die Schleife (der Agent)
1. **Briefing holen:** `python3 ruecklauf.py`. Keine offenen → fertig, nichts tun.
2. **Je Kommentar einordnen:**
   - **Klar und umsetzbar** (konkrete Fassung, eindeutige Korrektur): umsetzen.
   - **Mehrdeutig** (z. B. „macht vielleicht mehr Sinn" ohne Fassung, Geschmacksfrage,
     Struktur-/Architekturfrage): **nicht raten.** Rückfrage als Kommentar zurück-
     schreiben (siehe unten) oder Philipp direkt fragen. Kommentar bleibt offen.
3. **Umsetzen — nur in `heroes.json`** am genannten Pfad. Betroffene Regel-IDs nennen
   (G/B/DS). Die Fabrik (`build_editor.py`) bleibt unangetastet.
4. **Bauen:** `python3 build_editor.py --publish`. Bricht der Build oder eine Prüfmaschine
   (Hook) → Fehler zuerst lösen, nicht drumherum bauen.
5. **PR** auf `main`, Titel wie üblich. Prüfmaschinen (CI-Job „pruefen") grün → **Squash-
   Merge** (Haus-Regel: Claude-PRs werden gemergt, nicht als Draft geparkt). Danach den
   Arbeits-Branch frisch von `main` ziehen.
6. **Nach dem Merge** `python3 build_editor.py --verify` (alle URLs live).
7. **Erledigt setzen** — für jeden umgesetzten Kommentar:
   - Antwort einfügen (Insert in `sommer2026_mail_comments`): `autor='claude'`, gleicher
     `mail_key`, kurze Notiz was geändert wurde (+ PR-Nummer).
   - Original per RPC schliessen: `sommer2026_comment_erledigt(kommentar_id, true)`.

## Grenzen (bewusst)
- **Nie senden, nie Fristen im Fremdsystem setzen, nie Zahlungs-/Offer-Konfiguration.**
  Das sind die Haus-Ausnahmen (fragen, nicht tun). Der Agent ändert nur Quelltext.
- **Nach dem Versand einer Welle** ist ihr Text beim Empfänger — Korrekturen daran sind
  wirkungslos; der Agent prüft `config.json → wellen.*.versand` und lässt bereits
  versendete Wellen in Ruhe (nur noch Landingpages/Bilder wären änderbar).
- **Mehrdeutiges eskaliert**, es wird nicht interpretiert. Lieber eine Rückfrage zu viel.

## Rückfrage zurückschreiben (statt raten)
Insert in `sommer2026_mail_comments` mit `autor='claude'`, gleichem `mail_key`, der
konkreten Rückfrage — erscheint im Editor unter demselben Element, Philipp antwortet dort.
Den auslösenden Kommentar **offen lassen**, bis die Fassung klar ist.

## Auslöser
Manuell (jederzeit `python3 ruecklauf.py`) oder als geplante Routine, die eine frische
Session weckt, das Briefing liest und bei offenen Kommentaren die Schleife fährt. Bei
0 offenen endet sie sofort — ein HTTP-Aufruf, kein Aufwand.

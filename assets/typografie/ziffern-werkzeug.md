# Ziffern-Sets schnell umschalten (Regel G25)

Grundton der Goetheanum Schrift v2.7 ist **proportional** (ruhig im Fließtext).
Wo Zahlen **fluchten** müssen (Tabellen, Listen, Beträge), gilt **zwingend
tabellarisch** (`tnum`). Dieses Werkzeug macht das Umschalten schnell und – wo
möglich – automatisch.

| Einsatz | Set | OpenType |
|---|---|---|
| Fließtext (Standard) | proportional, Versalhöhe | `pnum` `lnum` |
| Tabelle, Liste, Betrag | **dicktengleich** | `tnum` `lnum` |
| Mengentext mit vielen Zahlen | Kurzziffern (x-Höhe) | `onum` |
| Codes, Kennungen | schlummernde 0 | `zero` |

## Web — automatisch
`assets/typografie/ziffern.css` einbinden. Dann:
- **`<table>` schaltet automatisch auf `tnum`** – kein Zutun nötig.
- Klassen: `.tabellenziffern`, `.zahl` (rechtsbündig), `.kurzziffern`,
  `.schlummernde-null`, `.proportional`. Komponierbar.

```html
<link rel="stylesheet" href="assets/typografie/ziffern.css">
<td class="zahl">1 487</td>            <!-- fluchtet automatisch -->
<span class="kurzziffern">im Jahr 1923</span>
<span class="schlummernde-null">Kennung 0761</span>
```

## InDesign — Zeichenstile + GREP (einmal anlegen, immer schnell)
Drei **Zeichenformate** anlegen (Fenster → Stile → Zeichenformate → OpenType):
- **Tabellenziffern** → OpenType → Zahlenformat: *Tabellarisch, Versalziffern*
- **Kurzziffern** → OpenType → Zahlenformat: *Proportional, Mediäval*
- **Durchgestrichene Null** → OpenType → *Durchgestrichene Null* aktivieren

**Automatisch in Tabellen:** Im Absatzformat der Tabellenzellen einen
**GREP-Stil** ergänzen: *Zeichenformat* „Tabellenziffern" auf den Ausdruck
`\d` anwenden → jede Ziffer in der Tabelle wird ohne Nachdenken dicktengleich.
(Absatzformat → GREP-Stil → Neuer GREP-Stil.)

Schnelltaste: den drei Zeichenformaten je einen Shortcut zuweisen
(Zeichenformat-Optionen → Tastaturbefehl).

## Office (Word/Pages, wo OpenType verfügbar)
Über die Schrift-/Zeichendialoge die OpenType-Zahlenformate wählen
(*Tabellarisch* für Tabellen, *Mediäval* für Kurzziffern, *Durchgestrichene
Null*). Wo der Dialog fehlt, bleibt der proportionale Grundton.

## Regelbezug
**G25** — Grundton proportional; in Tabellen/Listen/Beträgen **zwingend** `tnum`,
rechtsbündig, exakt untereinander, nie mit Leerzeichen ausgerichtet.

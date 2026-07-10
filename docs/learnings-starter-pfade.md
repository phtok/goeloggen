# Übergabe: Starter auf relative Fundament-Pfade umstellen

**Zielsession:** Design-System / `design-system/starter.html`
**Nicht** vom Signatur-Generator-Branch mitmergen — eigener, kleiner Commit.

---

## Der Vorfall

Der **Signatur-Generator** (`apps/signatur-generator/`) wurde aufs gemeinsame
Fundament gehoben. Dabei wurden Tokens/Base/Nav **1:1 aus `starter.html`**
übernommen — also per **absoluter** URL:

```html
<link rel="stylesheet" href="https://phtok.github.io/goeloggen/design-system/tokens.css" />
<script src="https://phtok.github.io/goeloggen/design-system/nav.js"
        data-root="https://phtok.github.io/goeloggen/" …></script>
```

**Folge:** Auf der produktiven **Custom-Domain** `werkzeuge.goetheanum.ch`
lud die Seite **kein** CSS/JS und erschien komplett **ungestylt** (Serifen-
Rohtext, kein Kopf, kein Layout).

### Ursache
`CNAME = werkzeuge.goetheanum.ch` → GitHub Pages liefert die Site im **Root**
aus (`werkzeuge.goetheanum.ch/design-system/…`), **ohne** das `/goeloggen/`-
Präfix. Die Absolut-URLs `phtok.github.io/goeloggen/design-system/…` laufen
dort ins Leere (404). Alle **funktionierenden** Apps (`apps/*/index.html`)
binden das Fundament dagegen **relativ** ein:

```html
<link rel="stylesheet" href="../../design-system/tokens.css" />
<script src="../../design-system/nav.js" data-root="../../" …></script>
```

Relative Pfade tragen auf **beiden** Auslieferungen (Custom-Domain-Root **und**
`phtok.github.io/goeloggen/`).

### Behoben (im Signatur-Generator)
PR #291 — auf relative Pfade umgestellt.

### Das eigentliche Problem
`starter.html` **empfiehlt** die absoluten URLs und behauptet im Kommentar,
sie „funktionieren von JEDEM Ort". Das ist auf der Custom-Domain **falsch** —
und war die Quelle des Fehlers. Darum: den Starter korrigieren.

---

## Der Patch

Stellt `starter.html` auf **relative** Pfade um (Root-Beispiel), korrigiert den
irreführenden Kommentar und dokumentiert die Pfadtiefe (Root vs. `apps/x/`).
Datei `starter-relative-pfade.patch` liegt bei; anwenden mit:

```
git apply starter-relative-pfade.patch
```

<details><summary>Diff inline</summary>

```diff
--- a/design-system/starter.html	2026-07-08 19:38:42.854375480 +0000
+++ b/design-system/starter.html	2026-07-08 19:38:42.891073745 +0000
@@ -16,9 +16,11 @@
          tabellarische Ziffern, Betonung = Laut, Leise statt Kursive (G02/G05/G16/G25 …).
        · Fürs Falsche (Unterstreichen/Versal-Hervorhebung/Sperren) gibt es kein Utility.
 
-     Pfad-Hinweis: Die zwei <link> unten laden das System per absoluter URL und
-     funktionieren von JEDEM Ort. Für lokale Arbeit ohne Netz die relative Variante
-     daneben (auskommentiert) nutzen und den Pfad an die Tiefe deiner Datei anpassen.
+     Pfad-Hinweis: Das Fundament wird RELATIV eingebunden – das trägt auf der
+     Custom-Domain (werkzeuge.goetheanum.ch, Auslieferung im Root) UND unter
+     phtok.github.io/goeloggen/. KEINE absoluten https://phtok.github.io/goeloggen/-URLs:
+     die greifen auf der Custom-Domain nicht (kein /goeloggen/-Präfix → 404 → ungestylt).
+     Pfadtiefe an den ORT deiner Datei anpassen (siehe unten).
      ============================================================================= -->
 <html lang="de-CH">
 <head>
@@ -26,15 +28,16 @@
 <meta name="viewport" content="width=device-width, initial-scale=1" />
 <title>Neues Werkzeug · Goetheanum</title>
 <meta name="description" content="Kurzbeschreibung des Werkzeugs – ein Satz, was es tut." />
-<link rel="icon" type="image/svg+xml" href="https://phtok.github.io/goeloggen/assets/logos/goetheanum-mark-blue.svg" />
+<!-- Pfadtiefe an den Ort DEINER Datei anpassen:
+       · Root (./mein-werkzeug.html):   design-system/… · assets/… · data-root="./"
+       · App  (apps/x/index.html):      ../../design-system/… · ../../assets/… · data-root="../../"
+     Diese Vorlage steht als Root-Beispiel. -->
+<link rel="icon" type="image/svg+xml" href="assets/logos/goetheanum-mark-blue.svg" />
 
-<!-- Das Fundament – eine Quelle der Wahrheit. NICHT kopieren, EINBINDEN. -->
-<link rel="stylesheet" href="https://phtok.github.io/goeloggen/design-system/tokens.css" />
-<link rel="stylesheet" href="https://phtok.github.io/goeloggen/design-system/base.css" />
-<link rel="stylesheet" href="https://phtok.github.io/goeloggen/design-system/nav.css" />
-<!-- Lokal/offline stattdessen (Pfadtiefe anpassen):
+<!-- Das Fundament – eine Quelle der Wahrheit. NICHT kopieren, EINBINDEN. RELATIV, nie absolut. -->
 <link rel="stylesheet" href="design-system/tokens.css" />
-<link rel="stylesheet" href="design-system/base.css" /> -->
+<link rel="stylesheet" href="design-system/base.css" />
+<link rel="stylesheet" href="design-system/nav.css" />
 
 <style>
   /* NUR werkzeug-eigene Gestaltung hierher. Alles Gemeinsame steht schon in base.css.
@@ -48,9 +51,7 @@
 
 <!-- Globale Navigation: erzeugt Kopfzeile + klappbares Menü aus tools.json.
      data-variant="werkzeug" zeigt zusätzlich ein sichtbares „← Übersicht". -->
-<script src="https://phtok.github.io/goeloggen/design-system/nav.js"
-        data-root="https://phtok.github.io/goeloggen/"
-        data-variant="werkzeug"></script>
+<script src="design-system/nav.js" data-root="./" data-variant="werkzeug"></script>
 
 <main class="wrap">
 
```
</details>

---

## Optional: Wächter, damit es nicht wiederkehrt

Ergänze in `tools/ds-lint.py` (bzw. `design-system/contract.json`) eine Regel,
die **absolute Fundament-URLs** in ausgelieferten Seiten als Fehler meldet:

- Muster: `href|src = "https://phtok.github.io/goeloggen/(design-system|assets)/…"`
- Meldung: „Fundament/Assets absolut eingebunden — relativ (`../…`) verwenden;
  bricht auf der Custom-Domain (Root ohne /goeloggen/)."
- Läuft im Commit-Hook (`tools/hooks`) und/oder CI → jeder neue Nachzügler
  fällt sofort auf.

So wird aus dem einmaligen Fehlgriff eine dauerhaft erzwungene Regel.

# Recherche: Chialabs zweite Serif (Titillium Pro)

Stand: 26. 11. 2026. Frage des Inhabers: «Wie steht es um Chialabs zweite
Serif?» Vorgänger: `docs/recherche_titillium-pro.md` (Sichtung 31. 10. 2026).

## Befund

- **Nichts Neues, die zweite Serif existiert öffentlich nicht.** Kein Name,
  kein Entwerfer, kein Zeitplan, keine Datei, kein Branch, kein Repo. Es
  gibt nur die Absichtserklärung («parallel eine zweite Version … näher an
  den historischen Serif-Kanones»).
- **Der letzte Commit (4. 2. 2026) ist eine Textkorrektur** im README des
  Branchs `serif` (Titel ohne Unterstrich), keine Schriftarbeit. Die
  Schriftdateien der Serif-Beta stammen vom 1. 8. 2024; `main` ruht seit
  14. 6. 2024.
- **Die bestehende Serif ist unverändert:** Regular und Italic, kein Fett,
  keine Umlaute, keine Kerning-Feature, nur `mark`/`mkmk` und `ccmp`.
- **Lizenz unverändert OFL 1.1**, kein Reserved Font Name erklärt.
- **Für uns:** Beobachtungsstatus bleibt, keine Abhängigkeit aufbauen. Die
  eigene Serif-Linie (E4/S1) darf nicht auf Chialabs zweite Serif warten.

## Belege

| Was | Quelle | Datum |
|---|---|---|
| Remote-Stand: nur `main` (`dc0addd`), `serif` (`65ca153`) und `refs/pull/2/head`; keine weiteren Branches, keine Tags | `git ls-remote https://github.com/chialab/titillium_pro` | abgefragt 26. 11. 2026 |
| `main`: letzter Commit «Change UFO file» | https://github.com/chialab/titillium_pro/tree/main | 14. 6. 2024 |
| `serif`: jüngster Commit «Fix font name formatting in README» (Edoardo Cavazza), ändert nur README-Titel und einen Satz | https://github.com/chialab/titillium_pro/commit/65ca1530fcc8ab4a864e4f3bc87672e5b8da821f | 4. 2. 2026 |
| `serif`: «Adding first serif beta», einziger Commit am Verzeichnis `Serif_BETA` | https://github.com/chialab/titillium_pro/commit/ee519167 | 1. 8. 2024 |
| Serif-Beta-Dateien: `TitilliumProSerif-Regular.otf` (117 Glyphen/Zeichen), `…-RegularItalic.otf` (102), beide Version 1.000, Glyphs 3.2.3, Gewicht 400; Features nur `mark`, `mkmk`, `ccmp`; kein `adieresis` | https://github.com/chialab/titillium_pro/tree/serif/Serif_BETA/OTF (selbst geladen, mit fontTools gelesen) | 26. 11. 2026 |
| Issues: 9 offen (#4–#12), alle von m-casanova, keines zur Serif; #4 «Font variabile?» | https://github.com/chialab/titillium_pro/issues | Juni 2024 |
| PR #2: Rechtschreibkorrekte am README, am selben Tag ohne Merge geschlossen; kein weiterer PR | https://github.com/chialab/titillium_pro/pull/2 | 23. 1. 2024 |
| Keine Releases, keine Tags | `git tag` im Klon; `git ls-remote` (siehe oben) | 26. 11. 2026 |
| Organisation chialab: kein Repo mit «serif» im Namen oder in der Beschreibung | https://github.com/orgs/chialab/repositories?q=serif | 26. 11. 2026 |
| Absicht «zweite Version in Diskontinuität mit der Sans, näher an den historischen Serif-Kanones; doppelter Weg; Vertikalmetriken der Familie bleiben»; «Al momento accontentatevi della versione in continuità con il sans» | https://www.chialab.it/lang/en/tatzebao/titillium-pro-serif-prime-forme (Seite ohne Datum und Autor) | undatiert |
| Wortlaut zur Serif-Forschung («wird in Chialab in den kommenden Monaten aufgenommen und entwickelt»); keine Gewichte, kein Termin | https://www.chialab.it/lang/en/works/lunga-vita-al-titillium | undatiert |
| Entwurf der ersten Serif: Lorenzo Volpe, Thesis «Titillium Serif. Ricerca e pratica tipografica», ISIA Faenza, Betreuung Antonio D'Elisiis | dieselben zwei Chialab-Seiten | undatiert |
| README `serif` nennt nur «primo prototipo di Titillium Pro Serif», keine zweite Serif, keinen Plan | https://github.com/chialab/titillium_pro/blob/serif/README.md | Stand 4. 2. 2026 |
| Lizenz: SIL OFL 1.1, «Copyright (c) 2024 The Titillium Pro Project Authors»; kein Reserved Font Name nach dem Copyright-Vermerk erklärt | https://github.com/chialab/titillium_pro/blob/serif/LICENSE.txt | 2024 |
| Tatzebao-Übersicht: bis 2026 keine neuere Titillium-Meldung | https://www.chialab.it/lang/en/tatzebao | 26. 11. 2026 |

## Nicht auffindbar

Ausdrücklich gesucht, nichts gefunden: Name oder Arbeitstitel der zweiten
Serif, ein Entwerfer dafür, Gewichte, Zeitplan, Ankündigung 2025/2026 auf
chialab.it, Webseite oder Social-Beiträge von D'Elisiis (nur Hierax
Antiqua, 2021, https://ecal.ch/en/feed/projects/4871/hierax-antiqua/, und
sein Profil https://fontsinuse.com/type_designers/9629/antonio-d-elisiis),
Treffer zu Volpe ausser den Chialab-Seiten, ISIA Faenza, Urbino, Forum
Italia, Designers Italia. Der Suchlauf deckt nur, was Suchmaschine und
Seitenabruf liefern; Instagram, LinkedIn und Mastodon waren nicht prüfbar,
ebenso nicht der private Posteingang unter titillium@chialab.it.

## Korrekturen an der Notiz vom 31. 10. 2026

- «Letzter Commit 4. 2. 2026» stimmt, betrifft aber nur das README.
  Inhaltlich zuletzt bewegt: `serif` am 1. 8. 2024, `main` am 14. 6. 2024.
- Die Italic hat 102 Zeichen, die Regular 117 (Notiz: «117 Zeichen» für
  beide).
- Die Notiz nennt «geplant: eine zweite Serif» als Stand; das ist belegt,
  aber undatiert und seit mindestens 2024 unverändert.

## Offen/Beobachten

- Vermutung, nicht belegt: Das Projekt ruht. Anhaltspunkte sind der Stillstand
  seit Sommer 2024, offene Issues ohne Antwort und der einzige Commit 2026 als
  Textpflege. Es kann intern weitergehen, ohne dass es sichtbar wird.
- Halbjährlich dieselbe Probe wiederholen (nächste: Mai 2027):
  `git ls-remote https://github.com/chialab/titillium_pro` auf neue
  Branches, Tags und Hashes, dazu die Tatzebao-Seite.
- Wer Gewissheit will: Anfrage an titillium@chialab.it (Adresse laut
  Websuche-Zusammenfassung zur Chialab-Seite, nicht selbst geprüft); dem
  Inhaber überlassen.
- Entscheid E4/S1 (eigener Serif-Ausbau) braucht diese Antwort nicht
  abzuwarten.

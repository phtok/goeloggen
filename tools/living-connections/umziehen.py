#!/usr/bin/env python3
"""Living Connections: Umzug des Archivs nach werkzeuge.goetheanum.ch/living-connections/.

Quelle ist das statische Archiv der früheren Website living-connections.info
(Repo phtok/designs, Branch claude/living-connections-archiv, Ordner
living-connections/, gebaut von dessen werkzeug/bauen.py). Dieses Skript
nimmt daraus, was bleibt, und setzt es auf das Fundament des Hauses
(tokens.css, base.css, nav.js) – Beschluss des Inhabers vom 25. 10. 2026:
‹Interviews + Tagungen›.

  Bleibt   die 14 Interviews und Essays aus ‹Texte› (alte Adressen
           /texte/JJJJ/M/T/…/), das Gespräch mit Nathaniel Williams
           (/conversations/2018/1/9/…/), die Video-Interviews von 2022 und
           je eine Seite für die Tagungen 2017, 2021 und 2022.
  Entfällt Faces-Porträts, Workshops, FAQ, Preise, Formulare, Seitenkopien,
           der Zähl-Beacon (keine Drittdienste auf werkzeuge.goetheanum.ch)
           und die Squarespace-Datenschutzerklärung.

Aufruf:  python3 -I tools/living-connections/umziehen.py <quelle> <ziel>
         z. B. <quelle> = …/designs/living-connections, <ziel> = living-connections

Idempotent: <ziel> wird jedes Mal neu geschrieben.
"""
import html as H
import os
import re
import shutil
import sys

QUELLE, ZIEL = sys.argv[1], sys.argv[2]

MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Was unter /living-connections/ als Seite bestehen bleibt (Pfad ohne Schrägstriche).
TAGUNGEN = {"2017", "2021", "2022"}


def lesen(pfad):
    """<main>-Inhalt und Sprache einer Archivseite."""
    s = open(os.path.join(QUELLE, pfad, "index.html"), encoding="utf-8").read()
    lang = re.search(r'<html lang="([^"]+)"', s).group(1)
    main = re.search(r'<main id="inhalt">(.*?)</main>', s, re.S).group(1)
    return main, lang


def artikelpfade():
    aus = []
    for basis in ("texte", "conversations"):
        for wurzel, _, dateien in os.walk(os.path.join(QUELLE, basis)):
            rel = os.path.relpath(wurzel, QUELLE)
            if "index.html" in dateien and re.match(r"[a-z]+/\d{4}/", rel):
                aus.append(rel)
    return sorted(aus)


ARTIKEL = artikelpfade()
BLEIBT = set(ARTIKEL) | TAGUNGEN | {""}


def tiefe(p):
    return len([x for x in p.split("/") if x])


def zum_archiv(p):
    """Relativer Weg von Seite p zur Wurzel /living-connections/."""
    return "../" * tiefe(p) or "./"


def zum_haus(p):
    """Relativer Weg von Seite p zur Wurzel von werkzeuge.goetheanum.ch."""
    return "../" * (tiefe(p) + 1)


def datum_de(text):
    """‹27 April 2018› oder ‹9. Januar 2018› → ‹27. April 2018›."""
    m = re.search(r"(\d{1,2})\.? (\w+) (\d{4})", text)
    if not m:
        return ""
    t, mon, j = m.groups()
    if mon in MONTHS:
        mon = MONATE[MONTHS.index(mon)]
    return f"{int(t)}. {mon} {j}"


def saeubern(h, p):
    """Gemeinsame Reinigung jedes übernommenen Bruchstücks."""
    # Logo-Bild, das auf ein Anmeldeformular verlinkte; Anmelde-Knöpfe.
    h = re.sub(r'<figure><a href="https://forms\.gle/[^"]*">.*?</figure>', "", h, flags=re.S)
    h = re.sub(r'<p class="knopf"><a href="https://docs\.google\.com/forms/[^"]*">.*?</a></p>', "", h)
    # Verweise auf Seiten, die nicht mitkommen: Text bleibt, Link fällt.
    def link(m):
        ziel = m.group(1)
        if ziel.startswith(("http", "mailto:", "#")) or "/dateien/" in "/" + ziel or "/bilder/" in "/" + ziel:
            return m.group(0)
        rest = re.sub(r"^(\.\./)+|^\./", "", ziel).strip("/")
        if rest in BLEIBT:
            return m.group(0)
        return m.group(2)
    h = re.sub(r'<a href="([^"]*)">(.*?)</a>', link, h, flags=re.S)
    # Ein Merkmal, nicht zwei (G01): Laut+Leise → Laut.
    h = re.sub(r"<strong><em>(.*?)</em></strong>", r"<strong>\1</strong>", h, flags=re.S)
    h = re.sub(r"<em>(\s*)</em>", r"\1", h)
    # Ganzer Absatz leise = Lesetext in Leise; im Haus nicht (Betonung = Laut).
    h = re.sub(r"<p><em>((?:(?!</?p>).)*?)</em></p>",
               lambda m: m.group(0) if "<em>" in m.group(1) else f"<p>{m.group(1)}</p>", h, flags=re.S)
    # Striche (G18): Bereich ohne Leerschritte, Gedankenstrich als Halbgeviert.
    def striche(t):
        t = re.sub(r"(\d) ?- ?(\d)", "\\1–\\2", t)
        return re.sub(r"(?:(?<=\S)|^) - (?=\S|$)", " – ", t)
    h = re.sub(r">([^<]+)<", lambda m: ">" + striche(m.group(1)) + "<", h)
    # Volle Stunden ohne Nullen (G22).
    h = h.replace("roughly 20:00–21:00", "roughly 20–21 h")
    # Leerzeilen-Ersatz aus dem Squarespace-Editor.
    h = re.sub(r"(<h\d>)(\s*<br>)+", r"\1", h)
    h = re.sub(r"(<br>\s*)+(</h\d>)", r"\2", h)
    h = re.sub(r"<p>(\s|&nbsp;|<br>)*</p>", "", h)
    h = h.replace("Andrea <br>de la Cruze", "Andrea de la Cruze")  # Umbruch mitten im Namen
    h = re.sub(r"\n{3,}", "\n\n", h)
    return h.strip()


def tiefer(h, um=1):
    """Überschriften eines Bruchstücks um eine Ebene absenken (h1 entfällt vorher)."""
    for n in range(5, 0, -1):
        h = re.sub(rf"<(/?)h{n}>", rf"<\1h{min(n + um, 6)}>", h)
    return h


def ohne_h1(h):
    return re.sub(r"<h1>.*?</h1>", "", h, count=1, flags=re.S)


def seite(p, titel, kopf, inhalt, beschreibung, lang="de-CH"):
    haus, lc = zum_haus(p), zum_archiv(p)
    return f"""<!doctype html>
<!-- Living Connections – Archiv der früheren Website living-connections.info.
     Erzeugt von tools/living-connections/umziehen.py; dort ändern, nicht hier. -->
<html lang="{lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>{H.escape(titel)}</title>
<meta name="description" content="{H.escape(beschreibung)}" />
<link rel="icon" type="image/svg+xml" href="{haus}assets/logos/goetheanum-mark-blue.svg" />
<link rel="stylesheet" href="{haus}design-system/tokens.css" />
<link rel="stylesheet" href="{haus}design-system/base.css" />
<link rel="stylesheet" href="{haus}design-system/nav.css" />
<link rel="stylesheet" href="{lc}archiv.css" />
</head>
<body>
<script src="{haus}design-system/nav.js" data-root="{haus}" data-invite="aus"></script>

<main class="wrap">
{kopf}
{inhalt}
</main>

<footer class="ds-footer">
  <div class="wrap frow">
    <span>Archiv der Website living-connections.info, 2016–2022</span>
    <span><a href="{lc}">Living Connections</a></span>
  </div>
</footer>
</body>
</html>
"""


def artkopf(p, kicker, titel, lede="", pfad=None, lang=None):
    lc = zum_archiv(p)
    krumen = f'<a href="{lc}">Living Connections</a>'
    if pfad:
        krumen += f' <span aria-hidden="true">›</span> <a href="{lc}{pfad[0]}">{H.escape(pfad[1])}</a>'
    la = f' lang="{lang}"' if lang else ""
    return f"""<header class="artkopf">
  <nav class="crumbs" aria-label="Pfad">{krumen}</nav>
  <span class="kicker">{kicker}</span>
  <h1{la}>{titel}</h1>
  {f'<p class="lede">{lede}</p>' if lede else ""}
</header>"""


# --------------------------------------------------------------------------- Artikel
VERZEICHNIS = []   # (datum-schlüssel, pfad, titel, datum, ton, sprache)


def artikel(p):
    main, lang = lesen(p)
    main = re.sub(r'<p class="zurueck">.*?</p>', "", main, flags=re.S)
    m = re.search(r"<article><h1>(.*?)</h1>(?:<p class=meta>(.*?)</p>)?(.*)</article>", main, re.S)
    titel, meta, rumpf = m.group(1).strip(), m.group(2) or "", m.group(3)
    datum = datum_de(meta)
    gespraech = p.startswith("conversations/")
    if gespraech:
        titel = f"Gespräch mit {titel}"
    art = "Gespräch" if gespraech else ("Essay" if "Essay" in meta else "Interview")
    rumpf = saeubern(rumpf, p)
    rumpf = re.sub(r"<figcaption>\s*<p>(.*?)</p>\s*</figcaption>", r"<figcaption>\1</figcaption>", rumpf, flags=re.S)
    rumpf = re.sub(r'(<figure class="hoeren">.*?<figcaption>)[^<]*· ', r"\1", rumpf, flags=re.S)
    ton = "<audio" in rumpf
    j, mo, t = re.match(r"[a-z]+/(\d{4})/(\d+)/(\d+)/", p).groups()
    VERZEICHNIS.append((f"{j}{int(mo):02d}{int(t):02d}", p, titel, datum, ton, lang))
    kicker = f"{art} · {datum}" if datum else art
    kopf = artkopf(p, kicker, H.escape(titel) if not gespraech else titel, pfad=("#interviews", "Interviews"),
                   lang=None if lang.startswith("de") else lang)
    inhalt = f'<article class="prose" lang="{lang}">\n{rumpf}\n</article>'
    return seite(p, f"{titel} · Living Connections", kopf, inhalt,
                 f"{art} aus dem Archiv Living Connections, {datum}.")


# --------------------------------------------------------------------------- Tagungen
def bruch(p, ziel, absenken=1):
    h, _ = lesen(p)
    return tiefer(saeubern(ohne_h1(h), ziel), absenken)


def dokumente(ziel, eintraege):
    lc = zum_archiv(ziel)
    li = "".join(f'<li><a href="{lc}dateien/{d}">{H.escape(t)}</a> <span class="meta">PDF</span></li>' for d, t in eintraege)
    return f'<section class="block"><h2>Dokumente</h2><ul class="dokumente">{li}</ul></section>'


def tag_versal(h):
    """‹APRIL 22› + ‹Thursday› aus dem Zeitplan → ein Zwischentitel (keine Versalien, G05)."""
    return re.sub(r"<p>APRIL (\d+)</p>\s*<h(\d)>(\w+)</h\d>",
                  lambda m: f"<h{m.group(2)}>{m.group(3)}, {m.group(1)} April</h{m.group(2)}>", h)


def tagung_2017():
    z = "2017"
    intro = bruch("introduction", z)
    intro = re.sub(r"<figure><a [^>]*><img [^>]*englishdeutsch[^>]*></a></figure>", "", intro)
    intro = re.sub(r"<h3>July 7–9 2017.*?</h3>", "", intro, flags=re.S)
    intro = re.sub(r"<h4>Download the Flyer</h4>.*?(?=<h4>)", "", intro, flags=re.S)
    intro = intro.replace('alt="Introduction"', 'alt="Plakat der Tagung 2017"')
    teile = intro.split("<h4><em>Deutsch:", 1)
    en = teile[0]
    de = "<h4><em>Deutsch:" + teile[1] if len(teile) > 1 else ""
    en = re.sub(r"<h4><em>English: (.*?)</h4>", r"<h3>\1</h3>", en, flags=re.S)
    de = re.sub(r"<h4><em>Deutsch: (.*?)</h4>", r"<h3>\1</h3>", de, flags=re.S)
    # Zwischentitel ganz leise gesetzt: im Haus trägt der Titel selbst (G03).
    en, de = (re.sub(r"<h3>(.*?)</h3>", lambda m: "<h3>" + re.sub(r"</?em>", "", m.group(1)) + "</h3>", x, flags=re.S)
              for x in (en, de))
    oeff = bruch("publicconference", z, 2)
    oeff = re.sub(r"<h4>July 7-9 2017.*?</h4>", "", oeff, flags=re.S)
    oeff = re.sub(r"<h4><strong>(.*?)</strong></h4>", r"<h4>\1</h4>", oeff)
    vor = bruch("preconference", z, 2)
    vor = re.sub(r"<h4>July 5–7 2017.*?</h4>", "", vor, flags=re.S)
    inhalt = f"""<section class="block prose" lang="en">
{en}
</section>
<section class="block prose" lang="de">
{de}
</section>
{dokumente(z, [("LivingC_English_monitor.pdf", "Flyer English"), ("LivingC_Deutsch_monitor.pdf", "Flyer Deutsch"),
               ("lc_fr.pdf", "Flyer français"), ("lc_es.pdf", "Flyer español")])}
<section class="block prose" lang="en">
<h2>Public Conference, 7–9 July 2017</h2>
{oeff}
</section>
<section class="block prose" lang="en">
<h2>Pre-Conference, 5–7 July 2017</h2>
{vor}
</section>"""
    kopf = artkopf(z, "Tagung · 7.–9. Juli 2017 · Goetheanum", "Worldwide Perspectives on Anthroposophical Meditation",
                   "Die erste öffentliche Tagung am Goetheanum, die ganz der Meditation gewidmet war.",
                   pfad=("#tagungen", "Tagungen"), lang="en")
    return seite(z, "Tagung 2017 · Living Connections", kopf, inhalt,
                 "Living Connections 2017: Worldwide Perspectives on Anthroposophical Meditation, Goetheanum.")


WEG_2021 = ("Register below", "Workshop information will be updated", "Registrieren Sie sich",
            "Die Workshop-Informationen werden", "Einladungsschreiben April 2021", "Invitation Letter April 2021")


def ohne_absaetze(h, merkmale):
    return re.sub(r"<p>(?:(?!</p>).)*?</p>",
                  lambda m: "" if any(x in m.group(0) for x in merkmale) else m.group(0), h, flags=re.S)


def tagung_2021():
    z = "2021"
    en = ohne_absaetze(bruch("2021", z), WEG_2021)
    de = ohne_absaetze(bruch("willkommen-21", z), WEG_2021)
    for name in ("en", "de"):
        h = en if name == "en" else de
        h = re.sub(r"<figure><img [^>]*bildschirmfoto-2020-12-16[^>]*></figure>", "", h)
        h = re.sub(r"<h4>(?:Online Conference|Online-Konferenz).*?</h4>", "", h, flags=re.S)
        # Steiner-Zitat am Schluss: Zitat mit Quelle, nicht zwei Plakat-Titel.
        h = re.sub(r"<h3>(.*?)</h3><h4>- (Rudolf Steiner, 1922)</h4>",
                   r"<blockquote><p>\1</p><p>\2</p></blockquote>", h, flags=re.S)
        if name == "en":
            en = h
        else:
            de = h
    zeit = tag_versal(bruch("timetable-21", z, 1))
    zeit = re.sub(r"<p>Download a PDF version.*?</p>", "", zeit, flags=re.S)
    zeit = re.sub(r"<figure><img [^>]*timetable[^>]*></figure>", "", zeit)
    zeit = re.sub(r"<h3>Colour \(Participation\) Key:</h3><h4>(.*?)</h4>",
                  r"<h3>Colour key</h3><p>\1</p>", zeit, flags=re.S)
    inhalt = f"""<section class="block prose" lang="en">
{en}
</section>
<section class="block prose" lang="de">
<h2>Anthroposophische Meditation erkunden</h2>
{de}
</section>
{dokumente(z, [("LivingConnections2021-SaveTheDate_english.pdf", "Save the Date (English)"),
               ("LC2021-Open-Conference-Letter.pdf", "Invitation Letter, December 2020 (English)"),
               ("LC2021-DE-Offene-Konferenz-Brief.pdf", "Einladungsbrief, Dezember 2020 (Deutsch)"),
               ("April-2021-Invitation-Letter-EN-1.pdf", "Invitation Letter, April 2021 (English)"),
               ("LIVING-CONNECTIONS-Timetable.pdf", "Timetable (English)"),
               ("LIVING-CONNECTIONS-Zeitplan.pdf", "Zeitplan (Deutsch)")])}
<section class="block prose" lang="en">
<h2>Timetable</h2>
{zeit}
</section>"""
    kopf = artkopf(z, "Online-Tagung · 22.–25. April 2021 · Goetheanum", "Exploring Anthroposophical Meditation",
                   "Wegen der Pandemie online, auf Englisch und Deutsch.",
                   pfad=("#tagungen", "Tagungen"), lang="en")
    return seite(z, "Tagung 2021 · Living Connections", kopf, inhalt,
                 "Living Connections 2021: Exploring Anthroposophical Meditation, online vom Goetheanum.")


def celan(h):
    """Das Celan-Motto steht als Zitat, nicht als Zwischentitel."""
    return re.sub(r"<h4>((?:So|Also)<br>.*?)</h4><p>(?:Aus )?Paul Celan: (.*?)</p>",
                  r'<blockquote><p>\1</p><p>Paul Celan, \2</p></blockquote>', h, flags=re.S)


def tagung_2022():
    z = "2022"
    en = celan(bruch("welcome-1", z))
    de = celan(bruch("", z))
    # Das Motto steht im englischen Teil zweisprachig – im deutschen nicht noch einmal.
    de = re.sub(r"<blockquote>.*?</blockquote>", "", de, count=1, flags=re.S)
    for alt, neu in (("<h3>Living Connections:<br>Bridging the Abyss</h3>", ""),
                     ("<h3>Living Connections:<br>Den Abgrund überbrücken</h3>", ""),
                     ("<p>(English: see ENGLISH-Nav Menu in top-line)</p>", "")):
        en, de = en.replace(alt, neu), de.replace(alt, neu)
    en = re.sub(r"<h4>Attention:.*?</h4>", "", en, flags=re.S)
    de = re.sub(r"<h4>Achtung:.*?</h4>", "", de, flags=re.S)
    en = re.sub(r"<p>More information and suggestions:.*", "", en, flags=re.S)
    de = re.sub(r"<p>Mehr Informationen und Vorschläge:.*", "", de, flags=re.S)
    en = re.sub(r"\s*See reduced program", "", en)
    de = re.sub(r"\s*Siehe Reduziertes Programm", "", de)
    neu_en = re.search(r"<h3>Changed Program</h3>(.*)", bruch("reduced-program", z), re.S).group(1)
    neu_de = bruch("reduziertes-programm", z)
    neu_de = re.sub(r"<blockquote>.*?</blockquote>|<h4>Also<br>.*?</p>", "", celan(neu_de), flags=re.S)
    neu_de = re.sub(r"^.*?<p>Da wir", "<p>Da wir", neu_de, flags=re.S)
    inhalt = f"""<section class="block prose" lang="en">
{en}
<h3>Changed program</h3>
{neu_en}
</section>
<section class="block prose" lang="de">
<h2>Den Abgrund überbrücken</h2>
{de}
<h3>Geändertes Programm</h3>
{neu_de}
</section>"""
    kopf = artkopf(z, "Tagung · 8.–10. September 2022 · Goetheanum", "Bridging the Abyss",
                   "Geplant für über 250 Teilnehmende, mangels Anmeldungen abgesagt; vorgesehen war stattdessen ein Treffen mit den Kursleitern und den Angemeldeten.",
                   pfad=("#tagungen", "Tagungen"), lang="en")
    return seite(z, "Tagung 2022 · Living Connections", kopf, inhalt,
                 "Living Connections 2022: Bridging the Abyss – abgesagt, mit geändertem Programm.")


# --------------------------------------------------------------------------- Einstieg
def einstieg():
    z = ""
    eintraege = []
    for _, p, titel, datum, ton, lang in sorted(VERZEICHNIS, reverse=True):
        zusatz = " · ".join(x for x in [datum, "mit Ton" if ton else "", "deutsch" if lang.startswith("de") else ""] if x)
        la = "" if lang.startswith("de") else f' lang="{lang}"'
        eintraege.append(f'<li><a href="{p}/"{la}>{H.escape(titel) if not p.startswith("conversations/") else titel}</a> '
                         f'<span class="meta">{zusatz}</span></li>')
    videos, _ = lesen("de22-1")
    yt = re.findall(r'href="(https://www\.youtube\.com/watch\?v=[^"]+)"', videos)
    vid = "".join(f'<li><a href="{u}">Andreas Heertsch, Teil {i}</a> <span class="meta">YouTube</span></li>'
                  for i, u in enumerate(yt, 1))
    kanal = re.search(r'href="(https://www\.youtube\.com/channel/[^"]+)"', lesen("de22-interviews")[0]).group(1)
    inhalt = f"""<section class="block" id="interviews">
  <h2>Interviews</h2>
  <p class="lese">Zur Tagung 2017 führte Inessa Guseva Gespräche über die eigene Meditationspraxis und setzte sie danach fort; auf Deutsch erschienen sie in der Wochenschrift <q>Das Goetheanum</q>. Die Texte sind englisch, ausser wo vermerkt.</p>
  <ul class="verzeichnis">{"".join(eintraege)}</ul>
</section>
<section class="block" id="video">
  <h2>Video-Interviews 2022</h2>
  <p class="lese">Fragen zur anthroposophischen Meditation, englisch, teils mit deutschen Untertiteln. Alle Folgen auf dem <a href="{kanal}">YouTube-Kanal</a>.</p>
  <ul class="verzeichnis">{vid}</ul>
</section>
<section class="block" id="tagungen">
  <h2>Tagungen</h2>
  <ul class="verzeichnis">
    <li><a href="2017/" lang="en">Worldwide Perspectives on Anthroposophical Meditation</a> <span class="meta">7.–9. Juli 2017 · Goetheanum</span></li>
    <li><a href="2021/" lang="en">Exploring Anthroposophical Meditation</a> <span class="meta">22.–25. April 2021 · online</span></li>
    <li><a href="2022/" lang="en">Bridging the Abyss</a> <span class="meta">8.–10. September 2022 · abgesagt</span></li>
  </ul>
</section>"""
    kopf = """<header class="artkopf">
  <span class="kicker">Archiv · 2016–2022</span>
  <h1>Living Connections</h1>
  <p class="lede">Gespräche über anthroposophische Meditation und die drei Tagungen am Goetheanum, aus denen sie hervorgingen.</p>
</header>"""
    return seite(z, "Living Connections · Goetheanum", kopf, inhalt,
                 "Interviews über anthroposophische Meditation und die Tagungen Living Connections 2017, 2021 und 2022.")


# --------------------------------------------------------------------------- Schreiben
def schreiben(p, inhalt):
    ordner = os.path.join(ZIEL, p) if p else ZIEL
    os.makedirs(ordner, exist_ok=True)
    with open(os.path.join(ordner, "index.html"), "w", encoding="utf-8") as f:
        f.write(inhalt)


if os.path.isdir(ZIEL):
    for name in os.listdir(ZIEL):
        if name != "archiv.css":
            weg = os.path.join(ZIEL, name)
            shutil.rmtree(weg) if os.path.isdir(weg) else os.remove(weg)

for p in ARTIKEL:
    schreiben(p, artikel(p))
schreiben("2017", tagung_2017())
schreiben("2021", tagung_2021())
schreiben("2022", tagung_2022())
schreiben("", einstieg())

# Nur Bilder und Dateien, die eine bleibende Seite wirklich nennt.
genannt = set()
for wurzel, _, dateien in os.walk(ZIEL):
    for d in dateien:
        if d.endswith(".html"):
            s = open(os.path.join(wurzel, d), encoding="utf-8").read()
            genannt |= set(re.findall(r'(?:\.\./)*((?:bilder|dateien)/[^"#?]+)', s))
for rel in sorted(genannt):
    os.makedirs(os.path.join(ZIEL, os.path.dirname(rel)), exist_ok=True)
    shutil.copy2(os.path.join(QUELLE, rel), os.path.join(ZIEL, rel))
print(f"{len(ARTIKEL)} Artikel, 3 Tagungen, 1 Einstieg; {len(genannt)} Bilder/Dateien.")

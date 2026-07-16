#!/usr/bin/env python3
"""build_editor.py — rendert die Wellen-Matrix (Segment × Welle × Sprache) und den
Gegenlese-Editor (dist/editor.html; Kommentare -> Supabase, key = element-id).

Zwei Bild-Modi (config.json / asset_base_url):
  leer    -> Data-URIs überall (nur Vorschau; Gmail clippt >102 KB und blockt Data-URIs)
  gesetzt -> gehostete URLs in Mails UND Editor-Vorschauen (versandfähig, < 100 KB je Mail;
             der Editor zeigt exakt die Versand-Mails — kein Doppel-Rendering, kleine Seite)

`--publish` kopiert Editor + gehostete Assets nach ../../apps/mail-editor/
(GitHub Pages deployt apps/ -> https://werkzeuge.goetheanum.ch/apps/mail-editor/).
`--verify` prüft nach dem Merge, ob alle gehosteten Assets live erreichbar sind.
"""
import json, base64, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageOps

# Quelle der Instanz: eigener Ordner (Standard) oder per --quelle eine andere
# Kampagnen-Instanz (heroes.json + config.json + links.py) auf derselben Fabrik —
# so bleibt build_editor.py die EINE Fabrik für alle dreistufigen Kampagnen.
ROOT = (Path(sys.argv[sys.argv.index("--quelle") + 1]).resolve()
        if "--quelle" in sys.argv else Path(__file__).parent)
G = ROOT / "assets/generated"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
H = json.loads((ROOT / "heroes.json").read_text(encoding="utf-8"))
# Ausgabeort im Hub: config `editor_app` (relativ zur Repo-Wurzel); Standard bleibt
# der Sommer-Editor — bestehende Builds ändern sich nicht.
APP = Path(__file__).resolve().parent.parent.parent / CFG.get("editor_app", "apps/mail-editor")
# links.py der Quelle laden — jede Instanz bringt ihre eigene UTM-Regel mit.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("links", ROOT / "links.py")
links = _ilu.module_from_spec(_spec); _spec.loader.exec_module(links)

# Editor-Beschriftung je Instanz (Kopf, Titel, Fusszeile, Bereichs-Nav).
KICKER = CFG.get("editor_kicker", "Sommer-Aktion 2026")
ONPAGE = CFG.get("editor_onpage",
                 "Cockpit:../sommer-zaehler/|Aktivitäten:../sommer-zaehler/aktivitaeten.html"
                 "|Kosten:../sommer-zaehler/kosten.html|Multiplikatoren:../sommer-zaehler/multiplikatoren.html"
                 "|Links:../utm-generator/|Mail:../mail-editor/|Ablauf:../kampagnen-drehbuch/")

S = 2; WMX = 600
BASE = (CFG.get("asset_base_url") or "").rstrip("/")
T = CFG["theme"]
AKZENT, AKZENT_TIEF, WASH = T["akzent"], T["akzent_tief"], T["wash"]
INK, MIST, MUTED, FUSS = T["tinte"], T["nebel"], T["gedaempft"], T["fuss"]
FONT_STACK, HL_STACK = T["font_stack"], T["headline_stack"]
SEG_OF = {m: H["motive"][m]["segment"] for m in H["motive"]}
MOTIV_OF = {v: k for k, v in SEG_OF.items()}


def xml(s):
    """XML-Escaping für alles Redaktionelle, das in MJML läuft (ein & im Betreff bricht sonst den Build)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def kleinzeile(s):
    """Definierter Umbruch statt Zufallsfluss. Enthält die Quelle Zeilenumbrüche (\\n),
    wird GENAU dort gebrochen (manueller Umbruch); der Mittepunkt bleibt dann in der Zeile,
    mit geschütztem Spatium davor. Sonst: je Aussage eine Zeile (Umbruch am ·)."""
    if "\n" in s:
        return "<br />".join(xml(z.strip()).replace(" ·", "&#160;·") for z in s.split("\n") if z.strip())
    return "&#160;·<br />".join(xml(t.strip()) for t in s.split("·"))


def titel(s, key=None):
    """Titelzeile ohne einzelnes Schlusswort: letztes Wortpaar unzertrennlich (trägt in
    jedem Client); text-wrap:balance gleicht die Zeilen aus, wo Clients es können.
    Optionaler `key` markiert die balance-Div als inline-editierbar (WYSIWYG-Overlay)."""
    t = xml(s.strip())
    i = t.rfind(" ")
    if i > 0:
        t = t[:i] + "&#160;" + t[i + 1:]
    de = f' data-edit="{key}"' if key else ""
    return f'<div style="text-wrap:balance"{de}>{t}</div>'


def wrap_edit(inner, key):
    """Inhalt als inline-editierbares Element markieren (WYSIWYG-Overlay findet es per
    `[data-edit]`). MJML reicht nur die INNERE HTML von mj-text/mj-button durch — darum
    den Inhalt umschliessen, nicht das Tag. `data-edit` ist in Mail-Clients inert."""
    return f'<span data-edit="{key}">{inner}</span>'


def cta_editable(ctas, labels):
    """CTA nur inline editierbar, wenn eindeutig: eine Welle mit EINEM Button UND das
    Motiv hat genau ein cta_label (sonst wüsste die Fassung #cta nicht, welches Label)."""
    return len(ctas) == 1 and len(labels) == 1


def logo(out="logo_goetheanum.png", height=20):
    """Offizielle Wortmarke (assets/logos/goetheanum-logo.svg) als PNG, Original-Blau —
    das Logo bleibt das Logo, kein Schriftersatz (Kommentar shared#wortmarke, 9.7.)."""
    import cairosvg
    svg = ROOT.parent.parent / "assets/logos/goetheanum-logo.svg"
    cairosvg.svg2png(url=str(svg), write_to=str(G / out), output_height=height * S)
    return out, Image.open(G / out).width // S


def data_uri(rel):
    mime = "image/png" if rel.endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode((G / rel).read_bytes()).decode()


def src_for(rel):
    """Bildquelle je Modus: gehostete URL (versandfähig) oder Data-URI (nur Vorschau)."""
    return f"{BASE}/{rel}" if BASE else data_uri(rel)


def compose(var, key):
    """Hero-Zuschnitt. Wird immer neu gerendert (8 Bilder, billig) — Crop-Änderungen greifen sofort."""
    W = WMX * S; out = G / f"hero_{key}.jpg"
    src = Image.open(ROOT/var["bild"]).convert("RGB"); ctr = tuple(var.get("center", [0.5, 0.45]))
    ar = {"still": 1.6, "voll": 1/0.60}.get(var["stil"], 1/0.56)
    ImageOps.fit(src, (W, int(W/ar)), Image.LANCZOS, centering=ctr).save(out, quality=82)
    return out.name


def variation(motiv, vid):
    for v in H["motive"][motiv]["variationen"]:
        if v["id"] == vid: return v
    raise KeyError(vid)


def preheader(c):
    """Eigenes Feld, sonst Text an der Wortgrenze gekürzt (Vorschauzeile im Posteingang)."""
    if c.get("preheader"): return c["preheader"]
    t = c["text"]
    return t if len(t) <= 95 else t[:95].rsplit(" ", 1)[0] + " …"


def ctas_for(seg, welle, lang):
    """CTA-Ziele je Welle aus config (Attribution!), Labels aus heroes. Deckungsgleich mit dem
    eingespielten Register: noabo w1/w3 = zwei Buttons (ws/tv), sonst einer."""
    scfg = CFG["segmente"][seg]
    ziele = (scfg.get("wellen_ctas") or {}).get(welle) or [scfg["ziele"][0]]
    labels = H["motive"][MOTIV_OF[seg]][lang]["cta_labels"]
    return [(z, labels[z]) for z in ziele]


def ps_block(seg, welle, lang):
    """Leises Teilen-PS: das link_wort wird zum Teilen-Link auf das Angebot der Gruppe
    (links.share_link_for — nie ein schon bezahltes Produkt, eigenes utm_content)."""
    ps = H.get("ps", {})
    p = ps.get(lang)
    if not p or welle not in ps.get("wellen", []):
        return ""
    url = links.share_link_for(welle, seg, lang)["url"]
    wort = p["link_wort"]
    txt = xml(p["text"]).replace(
        xml(wort), f'<a href="{xml(url)}" style="color:{AKZENT};text-decoration:underline">{xml(wort)}</a>', 1)
    txt = txt.replace("\n", "<br />")  # manueller Umbruch aus der Quelle (\n) übernehmen
    return (f'<mj-text font-size="13px" line-height="20px" color="{MUTED}" '
            f'padding="0 0 26px 0">{txt}</mj-text>')


def render_mail(motiv, welle, lang, wm):
    seg = SEG_OF[motiv]
    vid = H["wellenplan"][seg][welle].split("/")[1]
    var = variation(motiv, vid)
    c = H["wellen"][motiv][welle][lang]
    ctas = ctas_for(seg, welle, lang)
    mehrere = len(ctas) > 1
    cta_links = [(label, links.link_for(welle, seg, ziel, lang, mehrere)) for ziel, label in ctas]
    hero = src_for(compose(var, f"{motiv}_{vid}"))
    haupt = cta_links[0][1]["url"]  # Logo und Hero verlinken zur Landing (Kommentar ph 11.7.) — utm bleibt dran
    faces = "".join(f"@font-face{{font-family:'{w['family']}';src:url('{w['url']}') format('woff2');"
                    f"font-weight:{w['weight']};font-style:normal;}}" for w in T.get("webfonts", []))
    fontface = f"<mj-style>{faces}</mj-style>" if (BASE and faces) else ""
    base = f"{motiv}_{welle}_{lang}"
    ed_cta = cta_editable(ctas, H["motive"][motiv][lang].get("cta_labels", {}))
    btns = []
    for i, (label, l) in enumerate(cta_links):
        primaer = i == 0
        border = "" if primaer else f'border="2px solid {AKZENT}" '
        pad = 14 if i == len(cta_links) - 1 else 10
        lab_html = wrap_edit(xml(label), f"{base}#cta") if (ed_cta and primaer) else xml(label)
        btns.append(
            f'<mj-button href="{xml(l["url"])}" background-color="{AKZENT if primaer else "#FFFFFF"}" '
            f'color="{"#FFFFFF" if primaer else AKZENT}" {border}border-radius="999px" font-size="16px" '
            f'font-weight="600" inner-padding="15px 30px" align="left" padding="0 0 {pad}px 0">{lab_html}</mj-button>')
    btns = "".join(btns)
    # ‹Im Browser lesen›: zeigt auf die ohnehin gehostete Versand-URL (dieselbe Datei,
    # die AC bestückt) — keine Merge-Tags, immer erreichbar, gut zum Gegenlesen mit Kolleg:innen.
    # Nur wenn gehostet (BASE gesetzt); im reinen Vorschau-Modus gibt es keine URL.
    mail_url = f"{BASE.rsplit('/assets', 1)[0]}/mails/mail_{motiv}_{welle}_{lang}.html" if BASE else ""
    browser_txt = "Im Browser lesen" if lang == "de" else "Read in browser"
    browser_bar = (f'<mj-section background-color="{MIST}" padding="6px 28px 0 28px"><mj-column>'
                   f'<mj-text align="right" font-size="13px" line-height="18px" color="{MUTED}" padding="0">'
                   f'<a href="{mail_url}" style="color:{MUTED};text-decoration:underline;">{browser_txt}</a>'
                   f'</mj-text></mj-column></mj-section>') if mail_url else ""
    mjml = f"""<mjml><mj-head><mj-title>{xml(c['betreff'])}</mj-title><mj-preview>{xml(preheader(c))}</mj-preview>{fontface}
<mj-attributes><mj-all font-family="{FONT_STACK}"/><mj-text font-size="16px" line-height="25px" color="{INK}"/></mj-attributes></mj-head>
<mj-body background-color="{MIST}">
{browser_bar}
<mj-section background-color="#FFFFFF" padding="18px 28px 14px 28px"><mj-column><mj-image src="{src_for(wm[0])}" href="{xml(haupt)}" alt="Goetheanum" width="{wm[1]}px" align="left" padding="0"/></mj-column></mj-section>
<mj-section background-color="#FFFFFF" padding="0"><mj-column><mj-image src="{hero}" href="{xml(haupt)}" alt="{xml(var.get('alt',''))}" padding="0" fluid-on-mobile="true"/></mj-column></mj-section>
<mj-section background-color="#FFFFFF" padding="24px 28px 0 28px"><mj-column>
  <mj-text font-size="14px" line-height="20px" color="{AKZENT}" padding="0 0 10px 0">{wrap_edit(xml(H['badge'][lang]), f"shared#badge#{lang}")}</mj-text>
  <mj-text font-family="{HL_STACK}" font-size="30px" line-height="35px" font-weight="700" color="{INK}" padding="0 0 14px 0">{titel(c['botschaft'], f"{base}#botschaft")}</mj-text>
  <mj-text padding="0 0 22px 0">{wrap_edit(xml(c['text']), f"{base}#text")}</mj-text>
  {btns}
  <mj-text font-size="13px" line-height="20px" color="{MUTED}" padding="0 0 14px 0">{wrap_edit(kleinzeile(H['kleinzeile'][motiv][lang]), f"shared#kleinzeile#{motiv}#{lang}")}</mj-text>
  {ps_block(seg, welle, lang)}
</mj-column></mj-section>
<mj-section background-color="{WASH}" padding="16px 28px"><mj-column><mj-text font-size="14px" line-height="22px" color="{AKZENT_TIEF}" align="left" padding="0">{wrap_edit(xml(H['proof'][lang]), f"shared#beweisband#{lang}")}</mj-text></mj-column></mj-section>
</mj-body></mjml>"""
    p = subprocess.run(["mjml", "-i", "-s"], input=mjml, capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr)
    return p.stdout, c


def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def commentable(key, label, value_html):
    # Die ganze Kopfzeile klappt den Kommentarbereich auf/zu (grosses Ziel, B04).
    return f"""<div class="fld" data-key="{esc(key)}"><div class="fh" onclick="toggle(this)"><span class="lbl">{label}</span>
<button class="cbtn" type="button">💬 <span class="cc" data-cc="{esc(key)}">0</span></button></div>
<div class="val">{value_html}</div>
<div class="cpanel" hidden><ul class="clist" data-cl="{esc(key)}"></ul>
<div class="cin"><button class="uebn" type="button" onclick="uebernehmen(this)" title="Feldtext übernehmen — direkt die gewünschte Fassung schreiben" aria-label="Feldtext übernehmen">✎</button><input placeholder="Kommentar oder gewünschte Fassung …"><button onclick="send(this,'{esc(key)}')">senden</button></div></div></div>"""


def vorschlag_panel(base, welle, c):
    """‹Fassung vorschlagen›: je Feld ein vorbefülltes Eingabefeld; ‹vorschlagen›
    schickt die neue Fassung unter {base}#{feld} als Vorschlag ins Backend
    (Präfix ‹Fassung → ›), der Rücklauf-Agent nimmt sie in heroes.json auf."""
    felder = [("betreff", "Betreff", c.get("betreff", "")),
              ("preheader", "Betreff+ (Anriss)", preheader(c)),
              ("botschaft", "Botschaft", c.get("botschaft", "")),
              ("text", "Fliesstext", c.get("text", ""))]
    if welle == "w3" and c.get("alt"):
        felder.append(("alt", "Alt-Betreff (Nicht-Öffner)", c["alt"]))
    rows = "".join(
        f'<label class="pf"><span>{lab}</span>'
        f'<textarea rows="2">{esc(val)}</textarea>'
        f'<button type="button" onclick="vorschlag(this,\'{base}#{feld}\')">vorschlagen</button></label>'
        for feld, lab, val in felder)
    return (f'<details class="propose"><summary>✎ Fassung vorschlagen</summary>'
            f'<p class="phint">Feldtext ändern und ‹vorschlagen› — geht als Vorschlag ins '
            f'Backend, der Rücklauf-Agent nimmt ihn in <code>heroes.json</code> auf.</p>{rows}</details>')


def maildata_for(seg, motiv, welle, lang, c, ctas):
    """Redaktionelle Felder einer Mail als JS-Datensatz für den Overlay-Editor
    (openEditor liest MAILDATA[base]). Nur vorhandene Felder; Reihenfolge/Labels
    macht der Client. CTA nur editierbar, wenn die Mail genau EINEN Button hat —
    der Fassungs-Key (…#cta) kann kein Ziel kodieren (Multi-Button = beides)."""
    fields = {"betreff": c.get("betreff", ""), "preheader": preheader(c),
              "botschaft": c.get("botschaft", ""), "text": c.get("text", "")}
    if welle == "w3" and c.get("alt"):
        fields["alt"] = c["alt"]
    cta = {"editable": False}
    labels = H["motive"][motiv][lang].get("cta_labels", {})
    if cta_editable(ctas, labels):
        ziel, label = ctas[0]
        cta = {"editable": True, "ziel": ziel, "label": label}
    return {"label": f"{seg} · {motiv} · {welle} · {lang.upper()}", "fields": fields, "cta": cta}


# WYSIWYG-Overlay (einmal in der Seite): Vollfenster, dünner Balken, Mail zentriert und
# direkt in der Vorschau editierbar, Pfeile links/rechts zum Blättern. openEditor(base) füllt.
# `editor_hinweis` (config.json): Warnstreifen unter dem Balken — die Mails liegen in AC,
# Änderungen hier erreichen den Versand nicht von selbst.
WYZ_NOTE = (f'<div class="wyz-note" role="note">{esc(CFG["editor_hinweis"])}</div>'
            if CFG.get("editor_hinweis") else "")
WYZ_DIALOG = (
    '<dialog id="wyz" class="wyz">'
    '<div class="wyz-bar">'
    '<span class="wyz-label" id="wyz-label"></span>'
    '<span class="wyz-msg" id="wyz-msg"></span>'
    '<input class="wyz-autor" id="wyz-autor" placeholder="Kürzel" aria-label="Ihr Kürzel">'
    '<button class="wyz-save" type="button" onclick="saveAll()">Speichern</button>'
    '<button class="wyz-x" type="button" onclick="closeEditor()" aria-label="Schliessen">✕</button>'
    '</div>'
    f'{WYZ_NOTE}'
    '<button class="wyz-nav prev" type="button" onclick="navTo(-1)" aria-label="Vorherige Mail">‹</button>'
    '<button class="wyz-nav next" type="button" onclick="navTo(1)" aria-label="Nächste Mail">›</button>'
    '<div class="wyz-stage"><div class="wyz-col">'
    '<div class="wyz-inbox" id="wyz-chrome"></div>'
    '<iframe id="wyz-frame" class="wyz-frame" scrolling="no" title="Live-Editor"></iframe>'
    '</div></div>'
    '</dialog>')


def verify():
    """Nach Merge/Deploy: sind Editor und alle gehosteten Assets live erreichbar?
    Make-or-break vor dem Versand — vor dem Deploy sind die Bild-URLs tot."""
    if not BASE:
        sys.exit("asset_base_url ist leer — nichts zu verifizieren (reiner Vorschau-Modus).")
    import urllib.request
    files = sorted(f.name for f in G.iterdir()) if G.exists() else []
    if not files:
        sys.exit("assets/generated/ ist leer — zuerst bauen: python3 build_editor.py --publish")
    root_url = BASE.rsplit("/assets", 1)[0]
    mails = sorted(p.name for p in (ROOT/"dist").glob("mail_*.html"))
    urls = ([root_url + "/"] + [f"{BASE}/{n}" for n in files]
            + [f"{root_url}/mails/{n}" for n in mails])
    fails = 0
    for u in urls:
        try:
            with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=20) as r:
                ok = r.status == 200
        except Exception:
            ok = False
        fails += not ok
        print(f"  {'ok      ' if ok else '!! FEHLT'}  {u}")
    if fails:
        sys.exit(f"{fails} URL(s) nicht erreichbar — erst mergen/deployen, dann versenden.")
    print(f"Alle {len(urls)} URLs live — versandbereit.")


def main():
    publish = "--publish" in sys.argv
    G.mkdir(parents=True, exist_ok=True); (ROOT/"dist").mkdir(exist_ok=True)
    for alt in G.iterdir():
        alt.unlink()  # alles in G wird je Build erzeugt — keine Leichen (z. B. alte Font-TTFs)
    wm = logo()
    # Kein Font-Hosting mehr in den Mail-Assets: die Headline lädt die Hausschrift
    # (theme.headline_webfont) direkt aus dem Schriften-Bestand des Repos (OFL).
    rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                         text=True, cwd=ROOT).stdout.strip() or "?"
    jetzt = datetime.now()
    stand = f"{jetzt:%d.%m.%Y}, {jetzt.hour}.{jetzt.minute:02d} Uhr"  # Uhrzeit mit Punkt, ohne führende Null (G22)
    seg_blocks, sizes, maildata = [], [], {}
    for motiv in H["motive"]:
        seg = SEG_OF[motiv]
        wave_cards = []
        for welle in H["wellenplan"][seg]:
            lang_cards = []
            for lang in ("de", "en"):
                versand, c = render_mail(motiv, welle, lang, wm)
                out = ROOT/"dist"/f"mail_{motiv}_{welle}_{lang}.html"
                out.write_text(versand, encoding="utf-8")
                sizes.append((out.name, len(versand.encode("utf-8"))))
                # Editor-Vorschau = exakt die Versand-Mail (gehostete Bilder, kleine Seite).
                html = versand
                base = f"{motiv}_{welle}_{lang}"
                maildata[base] = maildata_for(seg, motiv, welle, lang, c, ctas_for(seg, welle, lang))
                # Posteingang-Zeile: was Empfangende zuerst sehen (Betreff + Anriss);
                # bei w3 zusätzlich die Zweitrahmung des AC-Splits für Nicht-Öffner.
                alt_zeile = (f'<div class="ib-alt"><span>Nicht-Öffner erhalten:</span> {esc(c["alt"])}</div>'
                             if welle == "w3" else "")
                inbox = (f'<div class="inbox"><div class="ib-b">{esc(c["betreff"])}</div>'
                         f'<div class="ib-a">{esc(preheader(c))}</div>{alt_zeile}</div>')
                lang_cards.append(f"""<div class="mail" data-lang="{lang}">
  <div class="mhd">{welle.upper()} · {lang.upper()}<button class="mhd-edit" type="button" onclick="openEditor('{base}')">✎ Bearbeiten</button><a href="mails/mail_{base}.html" title="Versand-HTML öffnen (AC-Bestückung)">HTML</a></div>
  {inbox}
  <iframe srcdoc="{html.replace('"','&quot;')}" loading="lazy" title="Vorschau {base}"></iframe>
  <div class="flds">{commentable(f"{base}#gesamt","Anmerkung zur Mail","<i>Was auffällt — das Element einfach benennen (Betreff, Bild, Text …)</i>")}
  {vorschlag_panel(base, welle, c)}</div></div>""")
            wave_cards.append(f'<div class="wave">{"".join(lang_cards)}</div>')
        seg_blocks.append(f'<section class="segment"><h2>{H["motive"][motiv]["label"]} — {seg}</h2><div class="waves">{"".join(wave_cards)}</div></section>')

    # Gemeinsame Elemente. Der Button-Stil zeigt die Mail-DNA — Artefakt, kein Theme.
    shared = [
        ("shared#wortmarke", "Wortmarke", f'<img src="{data_uri(wm[0])}" style="height:20px" alt="Goetheanum"> — offizielles Logo'),
        ("shared#badge", "Badge", f'<span style="color:{AKZENT}">{esc(H["badge"]["de"])}</span> / <span style="color:{AKZENT}">{esc(H["badge"]["en"])}</span> — HTML-Text, normal statt fett (G05) <!-- # ds-ok Mail-DNA, kein Theme -->'),
        ("shared#beweisband", "Beweis-Band", f'{esc(H["proof"]["de"])}<br>{esc(H["proof"]["en"])}'),
        ("shared#button", "Button-Stil", f'<span style="background:{AKZENT};color:#fff;border-radius:999px;padding:8px 18px;font:600 14px {FONT_STACK}">Gratis testen →</span> <!-- # ds-ok Mail-DNA, kein Theme -->'),
        ("shared#kleinzeile", "Kleinzeile (je Motiv)", "<br>".join(esc(H["kleinzeile"][m]["de"]) for m in H["motive"])),
        ("shared#footer", "Footer", "kommt aus ActiveCampaign (Absender-Adresse + Abmelden) — bewusst NICHT im HTML, sonst doppelt"),
    ]
    shared_html = "".join(commentable(k, l, v) for k, l, v in shared)

    sb_url = CFG["supabase"]["url"]; tab = CFG["supabase"]["kommentar_tabelle"]
    sb_key = CFG["supabase"].get("publishable_key", "")
    maildata_json = json.dumps(maildata, ensure_ascii=False)
    navbases_json = json.dumps(list(maildata.keys()))
    page = f"""<!doctype html>
<!-- =============================================================================
     Mail-Editor · {KICKER} (Gegenlesen)
     Generiert von services/mailing-sommer2026/build_editor.py — NICHT von Hand
     editieren; Änderungen an heroes.json/config.json, dann neu bauen (--publish).
     Chrome aus tokens.css/base.css (DS01/DS02, B01-B04, Labels normal statt
     versal G05/G23). Die Mail-Vorschauen (iframes) und Feld-Werte tragen die
     Kampagnen-DNA der Landingpages — Artefakt, kein Theme (ds-ok je Zeile).
     ============================================================================= -->
<html lang="de-CH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mail-Editor · {KICKER} · Goetheanum</title>
<meta name="robots" content="noindex">
<link rel="icon" type="image/svg+xml" href="../../assets/logos/goetheanum-mark-blue.svg">
<link rel="stylesheet" href="../../design-system/tokens.css">
<link rel="stylesheet" href="../../design-system/base.css">
<link rel="stylesheet" href="../../design-system/nav.css">
<style>
/* Nur editor-eigene Gestalt; alles Gemeinsame aus base.css, nur Tokens (DS02). */
/* Arbeitsfläche statt Lesespalte: die Galerie darf das Fenster nutzen (Lede
   behält ihr Lesemass); Karten wachsen mit dem Schirm mit. */
main.wrap{{max-width:min(1960px,96vw)}}
main{{--mailw:clamp(340px,30vw,600px)}} /* 600 = native Mail-Breite: Vorschau in Originalgrösse */
.lead{{padding:clamp(24px,5vw,44px) 0 var(--s4)}}
.controls{{display:flex;gap:var(--s2);align-items:center;flex-wrap:wrap;margin-top:var(--s4)}}
.controls .lab{{font-family:var(--font-text);font-size:var(--t-small);color:var(--muted)}}
.pill{{min-height:var(--tap);padding:8px 18px;border-radius:999px;border:1px solid var(--line);
  background:var(--paper);color:var(--ink);font:inherit;font-size:var(--t-small);cursor:pointer}}
.pill.on{{background:var(--gold-deep);border-color:var(--gold-deep);color:var(--on-accent);font-weight:600}}
.controls input{{min-height:var(--tap);font:inherit;font-size:var(--t-small);padding:6px 12px;
  border:1px solid var(--line);border-radius:var(--r-control);background:var(--field-bg);color:var(--ink);width:110px}}
#status{{font-family:var(--font-text);font-size:var(--t-small);color:var(--muted)}}
.segment h2{{margin:var(--s8) 0 var(--s2)}}
.shared{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--s3);margin-bottom:var(--s4)}}
.waves{{display:flex;gap:var(--s6);overflow-x:auto;padding:var(--s2) 0 var(--s5)}}
.wave{{display:flex;gap:var(--s3)}}
.mail{{width:var(--mailw);flex:0 0 auto;background:var(--paper);border:1px solid var(--line-soft);border-radius:10px;overflow:hidden}}
.mhd{{display:flex;align-items:center;background:var(--ink);color:var(--paper);font-family:var(--font-text);font-size:var(--t-micro);font-weight:600;padding:6px 12px}}
.mhd a{{margin-left:auto;color:inherit;text-decoration:none;border:1px solid var(--paper);border-radius:999px;padding:1px 9px;font-weight:400}}
.mhd a:hover{{background:var(--paper);color:var(--ink)}}
/* Posteingang-Zeile: was Empfangende zuerst sehen — Betreff fett, Anriss gedämpft. */
.inbox{{padding:var(--s2) var(--s3);border-bottom:1px solid var(--line-soft);font-family:var(--font-text)}}
.ib-b{{font-size:var(--t-small);font-weight:600;color:var(--ink)}}
.ib-a{{font-size:var(--t-small);color:var(--muted);line-height:1.45;margin-top:2px}}
.ib-alt{{font-size:var(--t-micro);color:var(--muted);line-height:1.45;margin-top:4px}}
.ib-alt span{{color:var(--gold-ink);font-weight:600}}
.mail iframe{{width:100%;height:calc(var(--mailw)*1.55);border:0;display:block;background:#F6F4F2}} /* # ds-ok Mail-Grund (Artefakt) */
.flds{{padding:var(--s2) var(--s3)}}
.fld{{border-top:1px solid var(--line-soft);padding:8px 4px}} .fld:first-child{{border-top:0}}
.fh{{display:flex;align-items:center;gap:var(--s2)}}
.lbl{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--muted);flex:1}}
.cbtn{{min-height:var(--tap);background:var(--field-bg);border:1px solid var(--line-soft);border-radius:999px;padding:2px 12px;font:inherit;font-size:var(--t-micro);cursor:pointer;color:var(--ink)}}
.cc.has{{background:var(--gold-deep);color:var(--on-accent);border-radius:10px;padding:0 7px}}
.val{{font-family:var(--font-text);font-size:var(--t-small);line-height:1.5;margin-top:4px;color:var(--ink)}}
.val code{{font-family:var(--font-mono);font-size:var(--t-micro);color:var(--muted);word-break:break-all}}
.fh{{cursor:pointer}}
.cpanel{{margin-top:var(--s2);background:var(--field-bg);border-radius:8px;padding:6px}}
.clist{{list-style:none;margin:0;padding:0;font-family:var(--font-text);font-size:var(--t-small)}}
.clist:not(:empty){{margin-bottom:6px}}
/* Untereinander, nicht nebeneinander: Kopfzeile klein, Text volle Breite. */
.clist li{{display:block;padding:4px 7px;background:var(--paper);border-radius:6px;margin-bottom:3px}}
.khead{{display:flex;gap:8px;align-items:baseline}}
.khead b{{color:var(--gold-ink);font-size:var(--t-micro)}}
.kzeit{{font-size:var(--t-micro);color:var(--muted);white-space:nowrap;margin-left:auto}}
.ktxt{{display:block;line-height:1.45}}
.clist li.done .ktxt{{text-decoration:line-through;color:var(--muted)}}
/* Kleines Zeichen, grosses Fingerziel: unsichtbare Trefferfläche ≥44px (B04). */
.kdone{{position:relative;background:none;border:0;padding:0 2px;font:inherit;font-size:var(--t-micro);color:var(--muted);cursor:pointer;line-height:1}}
.kdone::after{{content:"";position:absolute;inset:-13px}}
.kdone:hover{{color:var(--gold-ink)}}
.cin{{display:flex;gap:6px}}
.cin input{{flex:1;min-height:var(--tap);font:inherit;font-size:var(--t-small);padding:4px 10px;border:1px solid var(--line);border-radius:var(--r-control);background:var(--paper);color:var(--ink);min-width:0}}
.cin button{{min-height:var(--tap);background:var(--blue-solid);color:var(--on-accent);border:0;border-radius:var(--r-control);padding:4px 12px;font:inherit;font-size:var(--t-small);cursor:pointer}}
.uebn{{min-height:var(--tap);background:var(--paper);border:1px solid var(--line-soft);border-radius:var(--r-control);padding:4px 10px;font:inherit;font-size:var(--t-small);cursor:pointer;color:var(--muted)}}
.uebn:hover{{color:var(--gold-ink);border-color:var(--gold-ink)}}
/* ‹Fassung vorschlagen›: je Feld vorbefüllt, ‹vorschlagen› → Backend → Rücklauf-Agent. */
.propose{{margin-top:var(--s2);font-family:var(--font-text);font-size:var(--t-small)}}
.propose summary{{cursor:pointer;color:var(--gold-ink);font-weight:600;padding:4px 0;min-height:var(--tap);display:flex;align-items:center}}
.propose .phint{{color:var(--muted);font-size:var(--t-micro);line-height:1.4;margin:2px 0 8px}}
.pf{{display:grid;gap:3px;margin-bottom:8px}}
.pf>span{{font-size:var(--t-micro);color:var(--muted)}}
.pf textarea{{width:100%;font:inherit;font-size:var(--t-small);line-height:1.4;padding:5px 8px;border:1px solid var(--line-soft);border-radius:var(--r-control);background:var(--paper);color:var(--ink);resize:vertical;box-sizing:border-box}}
.pf textarea:focus{{outline:2px solid var(--gold-ink);outline-offset:-1px}}
.pf button{{justify-self:start;min-height:var(--tap);background:var(--paper);border:1px solid var(--gold-ink);border-radius:var(--r-control);padding:3px 12px;font:inherit;font-size:var(--t-small);color:var(--gold-ink);cursor:pointer}}
.pf button:hover{{background:var(--field-bg)}}
/* Sammelansicht: alle offenen Kommentare, anklicken springt zum Feld. */
.offen{{list-style:none;margin:0;padding:0;display:grid;gap:var(--s2)}}
.offen button{{display:block;width:100%;text-align:left;min-height:var(--tap);background:var(--paper);border:1px solid var(--line-soft);border-radius:8px;padding:var(--s2) var(--s3);font:inherit;cursor:pointer;color:var(--ink)}}
.offen button:hover{{border-color:var(--gold-ink)}}
.offen .okey{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--gold-ink);font-weight:600}}
.offen .otxt{{display:block;font-family:var(--font-text);font-size:var(--t-small);line-height:1.5;margin-top:2px}}
.offen .ometa{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--muted);margin-left:8px}}
.offen li.done button{{opacity:.72}}
.offen li.done .otxt{{text-decoration:line-through;color:var(--muted)}}
.offen li.done .okey{{color:var(--muted)}}
.fld.blitz{{outline:2px solid var(--gold-deep);outline-offset:4px;border-radius:8px}}
/* Global ausblenden: Schalter «Kommentare» in der Kopfleiste. */
body.nocmt .cbtn,body.nocmt .cpanel,body.nocmt .offen-sec{{display:none}}
/* «Nur Mails»: alle Einzelelemente weg — reine Galerie der Vorschauen. */
body.nurmails .flds,body.nurmails .shared-sec{{display:none}}
.shared .fld{{background:var(--paper);border:1px solid var(--line-soft);border-radius:8px;padding:var(--s2) var(--s3)}}
.subline{{font-family:var(--font-text);font-size:var(--t-small);color:var(--muted);margin:0 0 var(--s3)}}
/* Overlay-Editor: Mail gross bearbeiten, Speichern schreibt eine ‹Fassung → ›-Anmerkung. */
.mhd-edit{{min-height:var(--tap);margin-left:8px;background:transparent;border:1px solid var(--paper);border-radius:999px;color:var(--paper);padding:2px 10px;font:inherit;font-size:var(--t-micro);cursor:pointer}}
.mhd-edit:hover{{background:var(--paper);color:var(--ink)}}
/* WYSIWYG-Overlay: Vollfenster, dünner Balken, Mail zentriert und direkt editierbar. */
.wyz{{border:0;padding:0;margin:0;width:100vw;max-width:100vw;height:100vh;height:100dvh;max-height:100vh;max-height:100dvh;inset:0;background:var(--paper);color:var(--ink);overflow:hidden}}
.wyz:not([open]){{display:none}}  /* geschlossen = unsichtbar (nicht vom eigenen display überschreiben) */
.wyz[open]{{display:flex;flex-direction:column}}
.wyz::backdrop{{background:rgba(20,24,28,.55)}} /* # ds-ok Scrim, kein Theme */
.wyz-bar{{flex:0 0 auto;display:flex;align-items:center;gap:var(--s2);min-height:var(--tap);padding:2px var(--s3);background:var(--ink);color:var(--paper)}}
.wyz-label{{flex:1;min-width:0;font-family:var(--font-text);font-size:var(--t-micro);color:var(--paper);opacity:.85;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.wyz-msg{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--paper);opacity:.7;text-align:right;white-space:nowrap}}
.wyz-autor{{min-height:32px;width:84px;background:var(--paper);color:var(--ink);border:1px solid var(--line);border-radius:var(--r-control);padding:2px 8px;font:inherit;font-size:16px}} /* 16px: kein iOS-Zoom beim Fokus */
.wyz-save{{min-height:32px;background:var(--blue-solid);color:var(--on-accent);border:0;border-radius:var(--r-control);padding:4px 16px;font:inherit;font-size:var(--t-small);font-weight:600;cursor:pointer}}
.wyz-x{{min-height:32px;min-width:32px;background:transparent;border:1px solid var(--paper);border-radius:999px;color:var(--paper);font:inherit;cursor:pointer}}
.wyz-x:hover{{background:var(--paper);color:var(--ink)}}
.wyz-note{{flex:0 0 auto;background:var(--gold-deep);color:var(--on-accent);font-family:var(--font-text);font-size:var(--t-small);line-height:1.5;padding:var(--s1) var(--s3)}} /* B01: Weiss auf dunklem Gold (4.55:1) */
.wyz-stage{{flex:1 1 auto;overflow:auto;display:flex;justify-content:center;align-items:flex-start;padding:var(--s5) var(--s3) var(--s8);background:var(--field-bg)}}
.wyz-col{{width:600px;max-width:100%;box-shadow:0 6px 30px rgba(20,24,28,.16)}} /* # ds-ok Blatt-Schatten */
/* Posteingang-Streifen: echte Formularfelder (in jedem Browser editierbar, auch im Modal-Dialog). */
.wyz-inbox{{background:var(--paper);border:1px solid var(--line-soft);border-radius:8px 8px 0 0;border-bottom:0;padding:var(--s2) var(--s3);font-family:var(--font-text);display:grid;gap:3px}}
.wyz-ib-lab{{font-size:var(--t-micro);color:var(--muted);margin-top:4px}}
.wyz-ib-lab:first-child{{margin-top:0}}
.wyz-ib-b,.wyz-ib-a,.wyz-ib-alt-in{{width:100%;box-sizing:border-box;font-family:var(--font-text);font-size:16px;color:var(--ink);background:var(--field-bg);border:1px solid var(--line-soft);border-radius:var(--r-control);padding:6px 8px}} /* 16px: Eingabefeld-Minimum (B03), kein iOS-Zoom */
.wyz-ib-b{{font-weight:600}}
.wyz-ib-a{{line-height:1.4;resize:vertical}}
.wyz-inbox input:focus,.wyz-inbox textarea:focus{{outline:2px solid var(--gold-ink);outline-offset:1px}}
.wyz-frame{{width:100%;border:0;display:block;background:#F6F4F2}} /* # ds-ok Mail-Grund (Artefakt); Breite folgt der Spalte (mobil fluid) */
.wyz-nav{{position:fixed;top:50%;transform:translateY(-50%);z-index:2;width:56px;height:56px;background:var(--paper);border:1px solid var(--line);border-radius:999px;color:var(--ink);font-size:28px;line-height:1;cursor:pointer;box-shadow:0 2px 10px rgba(20,24,28,.18)}} /* # ds-ok Schatten */
.wyz-nav:hover{{border-color:var(--gold-ink);color:var(--gold-ink)}}
.wyz-nav:disabled{{opacity:.3;cursor:default;box-shadow:none}}
.wyz-nav.prev{{left:max(8px,calc(50vw - 300px - 68px))}}
.wyz-nav.next{{right:max(8px,calc(50vw - 300px - 68px))}}
@media(max-width:720px){{
  .wyz-stage{{padding:var(--s3) 6px 84px}}  /* schmalere Ränder, Platz unten für die Pfeile */
  .wyz-nav{{top:auto;bottom:calc(12px + env(safe-area-inset-bottom, 0px));transform:none;width:48px;height:48px}}
  .wyz-nav.prev{{left:12px}}
  .wyz-nav.next{{right:12px}}
  .wyz-msg{{display:none}}  /* im schmalen Balken den Statustext weglassen */
}}
</style></head><body>

<script src="../../design-system/nav.js" data-root="../../" data-variant="werkzeug"
        data-onpage="{ONPAGE}"></script>

<main class="wrap">
<section class="lead">
  <span class="kicker">{KICKER}</span>
  <h1>Mail-Editor</h1>
  <p class="lede" style="max-width:var(--measure)">Alle Wellen-Mails der drei Segmente zum Gegenlesen — je Feld kommentierbar, Kommentare landen im Werkzeug-Backend. Korrigiert wird in <code>heroes.json</code>, dann wird neu gebaut.</p>
  <p class="subline">Stand dieses Builds: {stand} · <code>{rev}</code></p>
  <div class="controls">
    <span class="lab">Sprache</span>
    <button id="b-de" class="pill on" onclick="setLang('de')">Deutsch</button>
    <button id="b-en" class="pill" onclick="setLang('en')">English</button>
    <span class="lab" style="margin-left:var(--s3)">Ihr Kürzel</span>
    <input id="autor" placeholder="z. B. ph">
    <button id="b-done" class="pill" onclick="toggleDone()">Erledigte zeigen</button>
    <button id="b-cmt" class="pill on" onclick="toggleComments()" aria-pressed="true">Kommentare</button>
    <button id="b-nur" class="pill" onclick="toggleNur()" aria-pressed="false">Nur Mails</button>
    <span id="status" style="margin-left:auto">verbinde …</span>
  </div>
</section>

<section class="segment offen-sec" id="offen-sec" hidden><h2 id="offen-titel">Offene Kommentare</h2>
<p class="subline" id="offen-sub">Die To-do-Liste des Gegenlesens — anklicken springt zum Feld.</p>
<ul class="offen" id="offenliste"></ul></section>

<section class="segment shared-sec"><h2>Gemeinsame Elemente</h2>
<p class="subline">Einmal kommentieren — gilt für alle Mails.</p>
<div class="shared">{shared_html}</div></section>
{''.join(seg_blocks)}
{WYZ_DIALOG}
</main>

<footer class="ds-footer"><div class="wrap"><div class="frow">
  <span><strong>Mail-Editor</strong> · {KICKER} · Kommentare ins Werkzeug-Backend, nur Kürzel, keine Personendaten</span>
  <span><a href="../../design-system/">Design-System</a></span>
</div></div></footer>

<script>
const SB_URL="{sb_url}", SB_KEY="{sb_key}", TAB="{tab}";
const REST=SB_URL+"/rest/v1/"+TAB, RPC=SB_URL+"/rest/v1/rpc/sommer2026_comment_erledigt";
const HDR={{"apikey":SB_KEY,"Authorization":"Bearer "+SB_KEY,"Content-Type":"application/json"}};
let COMMENTS={{}}, SHOW_DONE=false;
const MAILDATA={maildata_json};
const NAVBASES={navbases_json};
let PENDING={{}}, SUBMITTED={{}}, CUR=null, UILANG='de';
const st=t=>document.getElementById('status').textContent=t;
function setLang(l){{UILANG=l;document.getElementById('b-de').classList.toggle('on',l=='de');document.getElementById('b-en').classList.toggle('on',l=='en');
 document.querySelectorAll('.mail').forEach(m=>m.style.display=(m.dataset.lang==l?'':'none'));}}
function toggleDone(){{SHOW_DONE=!SHOW_DONE;document.getElementById('b-done').classList.toggle('on',SHOW_DONE);render();}}
function toggleComments(){{const b=document.getElementById('b-cmt'),an=document.body.classList.toggle('nocmt');
 b.classList.toggle('on',!an);b.setAttribute('aria-pressed',String(!an));}}
function toggleNur(){{const b=document.getElementById('b-nur'),an=document.body.classList.toggle('nurmails');
 b.classList.toggle('on',an);b.setAttribute('aria-pressed',String(an));}}
function toggle(el){{const p=el.closest('.fld').querySelector('.cpanel');p.hidden=!p.hidden;}}
function esc(s){{const d=document.createElement('div');d.textContent=s;return d.innerHTML;}}
function zeit(iso){{try{{return new Date(iso).toLocaleString('de-CH',{{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}}).replace(', ',' ');}}catch(e){{return '';}}}}
function sammel(key){{
 // Mail-Panels (…#gesamt) bündeln ALLE Kommentare ihrer Mail — auch den
 // Altbestand aus der früheren Feld-Ansicht (…#Betreff usw.).
 if(!key.endsWith('#gesamt')) return COMMENTS[key]||[];
 const basis=key.slice(0,key.length-'gesamt'.length);
 let alle=[];
 Object.keys(COMMENTS).forEach(k=>{{if(k.startsWith(basis))alle=alle.concat(COMMENTS[k]);}});
 return alle.sort((a,b)=>a.created_at<b.created_at?-1:1);
}}
function render(){{
 document.querySelectorAll('.clist').forEach(ul=>{{
   const items=sammel(ul.dataset.cl).filter(c=>SHOW_DONE||!c.erledigt);
   ul.innerHTML=items.map(c=>'<li class="'+(c.erledigt?'done':'')+'">'
     +'<div class="khead"><b>'+esc(c.autor||'?')+'</b><span class="kzeit">'+zeit(c.created_at)+'</span>'
     +'<button class="kdone" onclick="erledigt('+c.id+','+(!c.erledigt)+')" title="'+(c.erledigt?'wieder öffnen':'erledigt')+'" aria-label="'+(c.erledigt?'wieder öffnen':'erledigt')+'">'+(c.erledigt?'↩':'✓')+'</button></div>'
     +'<span class="ktxt">'+esc(c.kommentar)+'</span></li>').join('');}});
 document.querySelectorAll('.cc').forEach(s=>{{const n=sammel(s.dataset.cc).filter(c=>SHOW_DONE||!c.erledigt).length;
   s.textContent=n;s.classList.toggle('has',n>0);}});
 // Sammelliste oben: normal die offene To-do-Liste; mit «Erledigte zeigen» auch die erledigten.
 const off=[];Object.values(COMMENTS).forEach(l=>l.forEach(c=>{{if(SHOW_DONE||!c.erledigt)off.push(c);}}));
 off.sort((a,b)=>a.created_at<b.created_at?-1:1);
 const titel=document.getElementById('offen-titel'), sub=document.getElementById('offen-sub');
 if(SHOW_DONE){{titel.textContent='Alle Kommentare';sub.textContent='Offene und erledigte — anklicken springt zum Feld.';}}
 else{{titel.textContent='Offene Kommentare';sub.textContent='Die To-do-Liste des Gegenlesens — anklicken springt zum Feld.';}}
 document.getElementById('offen-sec').hidden=off.length===0;
 document.getElementById('offenliste').innerHTML=off.map(c=>{{const[wo,feld]=c.mail_key.split('#');
   return '<li'+(c.erledigt?' class="done"':'')+'><button type="button" data-go="'+esc(c.mail_key)+'"><span class="okey">'
     +esc(wo==='shared'?'Gemeinsam':wo)+' · '+esc(feld||'')+(c.erledigt?' · erledigt':'')+'</span><span class="ometa">'+esc(c.autor||'?')+' · '+zeit(c.created_at)+'</span>'
     +'<span class="otxt">'+esc(c.kommentar)+'</span></button></li>';}}).join('');
}}
function springe(key){{
 let fld=document.querySelector('.fld[data-key="'+CSS.escape(key)+'"]');
 if(!fld){{const basis=key.split('#')[0];
   fld=document.querySelector('.fld[data-key="'+CSS.escape(basis+'#gesamt')+'"]');}}
 if(!fld) return;
 const m=key.match(/_(de|en)#/); if(m) setLang(m[1]);
 fld.querySelector('.cpanel').hidden=false;
 fld.scrollIntoView({{behavior:'smooth',block:'center'}});
 fld.classList.add('blitz'); setTimeout(()=>fld.classList.remove('blitz'),1800);
}}
function uebernehmen(b){{
 const fld=b.closest('.fld'), i=fld.querySelector('.cin input');
 i.value=fld.querySelector('.val').textContent.trim(); i.focus();
}}
async function load(){{
 try{{const r=await fetch(REST+"?select=id,created_at,mail_key,autor,kommentar,erledigt&order=created_at",{{headers:HDR}});
  if(!r.ok) throw new Error("HTTP "+r.status);
  const data=await r.json(); COMMENTS={{}};
  data.forEach(c=>{{(COMMENTS[c.mail_key]=COMMENTS[c.mail_key]||[]).push(c);}});
  render(); st("verbunden · "+data.filter(c=>!c.erledigt).length+" offene Kommentare");
 }}catch(e){{st("offline — Kommentare nicht ladbar ("+e.message+")");}}
}}
async function erledigt(id,wert){{
 st("speichere …");
 try{{const r=await fetch(RPC,{{method:"POST",headers:HDR,body:JSON.stringify({{kommentar_id:id,wert:wert}})}});
  if(!r.ok) throw new Error("HTTP "+r.status);
  await load();
 }}catch(e){{st("Fehler: "+e.message);}}
}}
function spracheAus(key){{const m=key.match(/(?:_|#)(de|en)(?:#|$)/);return m?m[1]:null;}}
async function send(btn,key){{
 const inp=btn.previousElementSibling, txt=inp.value.trim(); if(!txt) return;
 const eingabe=(document.getElementById('autor').value||'').trim();
 try{{if(eingabe)localStorage.setItem('autor',eingabe);}}catch(e){{}}
 const autor=eingabe||'anon';
 btn.disabled=true; st("sende …");
 try{{
  const r=await fetch(REST,{{method:"POST",headers:{{...HDR,"Prefer":"return=minimal"}},body:JSON.stringify({{mail_key:key,autor,kommentar:txt,sprache:spracheAus(key)}})}});
  if(!r.ok) throw new Error("HTTP "+r.status+" "+(await r.text()).slice(0,120));
  inp.value=""; await load();
 }}catch(e){{st("Fehler: "+e.message); alert("Konnte nicht senden:\\n"+e.message+"\\n\\nTipp: Diese Seite über werkzeuge.goetheanum.ch öffnen — in eingebetteten Vorschauen sind Netzwerkzugriffe oft blockiert.");}}
 btn.disabled=false;
}}
async function postFassung(key,txt,autor){{
 // Eine Feld-Fassung schreiben (Präfix ‹Fassung → ›, unter dem Feld-Key). Genau die
 // Zeile, die der Rücklauf-Agent konsumiert — von ‹vorschlagen› wie vom Overlay-Speichern.
 const r=await fetch(REST,{{method:"POST",headers:{{...HDR,"Prefer":"return=minimal"}},body:JSON.stringify({{mail_key:key,autor,kommentar:"Fassung → "+txt,sprache:spracheAus(key)}})}});
 if(!r.ok) throw new Error("HTTP "+r.status+" "+(await r.text()).slice(0,120));
}}
async function vorschlag(btn,key){{
 const ta=btn.previousElementSibling, txt=ta.value.trim(); if(!txt) return;
 const eingabe=(document.getElementById('autor').value||'').trim();
 try{{if(eingabe)localStorage.setItem('autor',eingabe);}}catch(e){{}}
 const autor=eingabe||'anon';
 btn.disabled=true; st("sende Vorschlag …");
 try{{ await postFassung(key,txt,autor); st("Vorschlag gespeichert ✓"); await load(); }}
 catch(e){{st("Fehler: "+e.message); alert("Konnte nicht senden:\\n"+e.message+"\\n\\nTipp: Diese Seite über werkzeuge.goetheanum.ch öffnen — in eingebetteten Vorschauen sind Netzwerkzugriffe oft blockiert.");}}
 btn.disabled=false;
}}
/* ── WYSIWYG-Overlay ──────────────────────────────────────────────────────────
   Direkt IN der Mailvorschau texten. Die editierbaren Stellen tragen data-edit
   (aus dem Build); im Overlay-iframe werden sie contentEditable. Speichern schreibt
   je geändertem Feld eine ‹Fassung → ›-Anmerkung (postFassung) — die veröffentlichte
   HTML arbeitet die Rücklauf-Schleife ein. Geteilte Elemente (badge/proof/kleinzeile)
   werden sofort in ALLEN geladenen iframes gespiegelt. */
const CE_SINGLE={{betreff:1,alt:1,cta:1,badge:1,botschaft:1,kleinzeile:1}};
const wmsg=t=>{{const m=document.getElementById('wyz-msg');if(m)m.textContent=t;}};
function feldOf(key){{return key.split('#')[1];}}  // mail: 'text'; shared#badge#de → 'badge'
function normNbsp(s){{return (s||'').replace(/\\u00a0/g,' ');}}
function kleinzeileMirror(s){{return s.split('·').map(t=>esc(t.trim())).join('&#160;·<br>');}}
function readCE(node,feld){{
 if(feld==='kleinzeile') return normNbsp(node.textContent).split('·').map(t=>t.trim()).filter(Boolean).join(' · ');
 if(feld==='text'||feld==='preheader'){{
   const t=node.innerText!=null?node.innerText:node.textContent;
   return normNbsp(t).replace(/[ \\t]+/g,' ').replace(/\\n{{3,}}/g,'\\n\\n').trim();
 }}
 return normNbsp(node.textContent).replace(/\\s+/g,' ').trim();
}}
function readField(node,feld){{  // Formularfeld (Posteingang) vs. contentEditable (Mail-Body)
 if(node.tagName==='INPUT'||node.tagName==='TEXTAREA'){{
   const v=node.value||'';
   if(feld==='preheader') return v.replace(/[ \\t]+/g,' ').replace(/\\n{{3,}}/g,'\\n\\n').trim();
   return v.replace(/\\s+/g,' ').trim();
 }}
 return readCE(node,feld);
}}
function writeCE(node,feld,val){{
 if(node.tagName==='INPUT'||node.tagName==='TEXTAREA'){{ node.value=val; return; }}
 if(feld==='kleinzeile'){{ node.innerHTML=kleinzeileMirror(val); return; }}
 if(feld==='botschaft'){{ const t=(val||'').trim(),i=t.lastIndexOf(' ');
   node.textContent=(i>0?t.slice(0,i)+'\\u00a0'+t.slice(i+1):t); return; }}
 node.textContent=val;
}}
function allDocs(){{
 const docs=[]; const f=document.getElementById('wyz-frame');
 try{{if(f&&f.contentDocument&&f.contentDocument.body)docs.push(f.contentDocument);}}catch(e){{}}
 document.querySelectorAll('.mail iframe').forEach(fr=>{{try{{if(fr.contentDocument&&fr.contentDocument.body)docs.push(fr.contentDocument);}}catch(e){{}}}});
 return docs;
}}
function applyEdit(key,val,exceptNode){{
 const feld=feldOf(key), sel='[data-edit="'+key+'"]';
 allDocs().forEach(d=>d.querySelectorAll(sel).forEach(n=>{{ if(n!==exceptNode) writeCE(n,feld,val); }}));
}}
function applyPending(doc){{
 const merged=Object.assign({{}},SUBMITTED,PENDING);
 Object.keys(merged).forEach(key=>{{const feld=feldOf(key);
   doc.querySelectorAll('[data-edit="'+key+'"]').forEach(n=>writeCE(n,feld,merged[key]));}});
}}
function autosizeIframe(f){{ try{{const d=f.contentDocument; if(d&&d.body){{
  const h=Math.max(d.body.scrollHeight,d.body.offsetHeight,d.documentElement.scrollHeight,d.documentElement.offsetHeight);
  if(h>0) f.style.height=h+'px';
}}}}catch(e){{}} }}
function onCE(e){{
 const node=e.target.closest&&e.target.closest('[data-edit]'); if(!node) return;
 const key=node.getAttribute('data-edit'), feld=feldOf(key);
 clearTimeout(node._wt); node._wt=setTimeout(()=>{{  // Timer je Node: schnelle Feldwechsel löschen sich nicht
   const val=readField(node,feld); PENDING[key]=val; applyEdit(key,val,node);
   autosizeIframe(document.getElementById('wyz-frame'));
   const n=Object.keys(PENDING).length; wmsg(n?('· '+n+' Änderung'+(n>1?'en':'')+' offen'):'');
 }},150);
}}
function ceKeydown(e){{
 if((e.metaKey||e.ctrlKey)&&(e.key==='s'||e.key==='S')){{e.preventDefault();saveAll();return;}}
 if(e.key!=='Enter'||e.shiftKey) return;
 const node=e.target.closest&&e.target.closest('[data-edit]'); if(!node) return;
 if(CE_SINGLE[feldOf(node.getAttribute('data-edit'))]) e.preventDefault();
}}
function navList(){{return NAVBASES.filter(b=>b.slice(-3)==='_'+UILANG);}}
function updateNav(){{const l=navList(),i=l.indexOf(CUR);
 document.querySelector('.wyz-nav.prev').disabled=(i<=0);
 document.querySelector('.wyz-nav.next').disabled=(i<0||i>=l.length-1);}}
function navTo(delta){{const l=navList(),i=l.indexOf(CUR); if(i<0) return;
 const j=i+delta; if(j<0||j>=l.length) return; openEditor(l[j]);}}
function openEditor(base){{
 const d=MAILDATA[base]; if(!d) return;
 CUR=base; UILANG=base.slice(-2);
 document.getElementById('wyz-label').textContent=d.label; wmsg('');
 try{{const a=document.getElementById('wyz-autor');if(!a.value)a.value=(localStorage.getItem('autor')||document.getElementById('autor').value||'');}}catch(e){{}}
 const f=d.fields||{{}};
 let chrome='<span class="wyz-ib-lab">Betreff</span>'
   +'<input class="wyz-ib-b" data-edit="'+base+'#betreff" value="'+esc(f.betreff||'')+'">'
   +'<span class="wyz-ib-lab">Anriss (Vorschauzeile)</span>'
   +'<textarea class="wyz-ib-a" rows="2" data-edit="'+base+'#preheader">'+esc(f.preheader||'')+'</textarea>';
 if('alt' in f) chrome+='<span class="wyz-ib-lab">Alt-Betreff (Nicht-Öffner)</span>'
   +'<input class="wyz-ib-alt-in" data-edit="'+base+'#alt" value="'+esc(f.alt)+'">';
 const chromeEl=document.getElementById('wyz-chrome'); chromeEl.innerHTML=chrome;
 chromeEl.oninput=onCE; chromeEl.onkeydown=ceKeydown; applyPending(document);
 const src=document.querySelector('.mail iframe[title="Vorschau '+base+'"]');
 const frame=document.getElementById('wyz-frame'); let done=false;
 const setup=()=>{{ const doc=frame.contentDocument; if(done||!doc||!doc.body) return; done=true;
   doc.querySelectorAll('[data-edit]').forEach(n=>n.setAttribute('contenteditable','true'));
   const stl=doc.createElement('style');
   stl.textContent='[data-edit]{{outline:1px dashed transparent;cursor:text}}[data-edit]:hover{{outline-color:rgba(0,0,0,.18)}}[data-edit]:focus{{outline:2px solid #3b82f6;outline-offset:2px}}'; /* # ds-ok Artefakt-Affordance */
   doc.head.appendChild(stl);
   doc.addEventListener('input',onCE); doc.addEventListener('keydown',ceKeydown);
   doc.addEventListener('click',ev=>{{if(ev.target.closest('a')&&ev.target.closest('[data-edit]'))ev.preventDefault();}});
   applyPending(doc); autosizeIframe(frame);
   // Höhe robust nachziehen: Bilder laden auf Mobil verzögert (4G), iOS meldet
   // ResizeObserver/‹load› unzuverlässig — darum zusätzlich mehrfach nachmessen.
   try{{new frame.contentWindow.ResizeObserver(()=>autosizeIframe(frame)).observe(doc.body);}}catch(e){{}}
   doc.querySelectorAll('img').forEach(im=>{{ if(im.complete) return; im.addEventListener('load',()=>autosizeIframe(frame)); im.addEventListener('error',()=>autosizeIframe(frame)); }});
   [120,400,900,1800,3000,5000,8000].forEach(ms=>setTimeout(()=>autosizeIframe(frame),ms));
 }};
 frame.onload=setup; frame.srcdoc=src?src.srcdoc:'';
 // Nicht auf das load-Event warten (Bilder können es verzögern): aufsetzen, sobald der Body da ist.
 let t=0; const iv=setInterval(()=>{{ setup(); if(done||++t>60) clearInterval(iv); }},50);
 updateNav(); if(!document.getElementById('wyz').open) document.getElementById('wyz').showModal();
}}
async function saveAll(){{
 const keys=Object.keys(PENDING); if(!keys.length){{ wmsg('nichts geändert'); return; }}
 const eingabe=(document.getElementById('wyz-autor').value||document.getElementById('autor').value||'').trim();
 try{{if(eingabe){{localStorage.setItem('autor',eingabe);document.getElementById('autor').value=eingabe;}}}}catch(e){{}}
 const autor=eingabe||'anon';
 wmsg('speichere '+keys.length+' …');
 try{{ await Promise.all(keys.map(k=>postFassung(k,PENDING[k],autor)));
   Object.assign(SUBMITTED,PENDING); PENDING={{}}; wmsg('gespeichert ✓'); await load();
   st('gespeichert ✓ — der Rücklauf-Agent arbeitet die Fassung in die HTML ein'); }}
 catch(e){{ wmsg('Fehler: '+e.message); alert("Konnte nicht speichern:\\n"+e.message+"\\n\\nTipp: Diese Seite über werkzeuge.goetheanum.ch öffnen — in eingebetteten Vorschauen sind Netzwerkzugriffe oft blockiert."); }}
}}
function closeEditor(){{ document.getElementById('wyz').close(); }}
document.getElementById('wyz').addEventListener('close',()=>{{document.getElementById('wyz-frame').removeAttribute('srcdoc');}});
window.addEventListener('resize',()=>{{ if(document.getElementById('wyz').open) autosizeIframe(document.getElementById('wyz-frame')); }});
document.getElementById('wyz').addEventListener('keydown',e=>{{
 if((e.metaKey||e.ctrlKey)&&(e.key==='s'||e.key==='S')){{e.preventDefault();saveAll();return;}}
 if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight') return;
 const a=document.activeElement; if(a&&(a.isContentEditable||a.id==='wyz-frame')) return;
 e.preventDefault(); navTo(e.key==='ArrowRight'?1:-1);
}});
document.getElementById('offenliste').addEventListener('click',e=>{{const b=e.target.closest('[data-go]');if(b)springe(b.dataset.go);}});
try{{const a=localStorage.getItem('autor');if(a&&a!=='anon')document.getElementById('autor').value=a;}}catch(e){{}}
setLang('de');load();
</script></body></html>"""
    (ROOT/"dist/editor.html").write_text(page, encoding="utf-8")

    print(f"Editor: dist/editor.html ({len(page.encode('utf-8'))//1024} KB) · Modus: "
          + (f"gehostet ({BASE})" if BASE else "eingebettet (nur Vorschau — NICHT versandfähig)"))
    limit = 100 * 1024; schwer = 0
    for name, n in sorted(sizes):
        mark = "  ok" if n <= limit else "  !! ÜBER 100 KB — Gmail clippt"
        print(f"  {name:<26}{n/1024:7.1f} KB{mark}")
        schwer += n > limit
    if BASE and schwer:
        sys.exit(f"{schwer} Mail(s) über 100 KB — nicht versandfähig.")

    if publish:
        APP.mkdir(parents=True, exist_ok=True)
        (APP/"index.html").write_text(page, encoding="utf-8")
        adir = APP/"assets"; adir.mkdir(exist_ok=True)
        for old in adir.iterdir():
            old.unlink()  # keine Leichen aus früheren Builds im Deploy
        for f in sorted(G.iterdir()):
            shutil.copy(f, adir/f.name)
        # Versand-HTML mit ausliefern: Quelle für die AC-Bestückung (Mail per URL abholen).
        # noindex nur in der Web-Kopie (Hausregel: jede Seite trägt noindex) — dist/ bleibt rein.
        mdir = APP/"mails"; mdir.mkdir(exist_ok=True)
        for old in mdir.iterdir():
            old.unlink()
        for f in sorted((ROOT/"dist").glob("mail_*.html")):
            html = f.read_text(encoding="utf-8").replace(
                "<head>", '<head><meta name="robots" content="noindex">', 1)
            (mdir/f.name).write_text(html, encoding="utf-8")
        print(f"Publiziert: {APP}/index.html + {len(list(adir.iterdir()))} Assets -> {BASE or '(asset_base_url leer!)'}")


if __name__ == "__main__":
    verify() if "--verify" in sys.argv else main()

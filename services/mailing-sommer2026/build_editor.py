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

ROOT = Path(__file__).parent
G = ROOT / "assets/generated"
APP = ROOT.parent.parent / "apps/mail-editor"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
H = json.loads((ROOT / "heroes.json").read_text(encoding="utf-8"))
import links

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
    """Definierter Umbruch statt Zufallsfluss: jede Aussage eine Zeile, der Mittepunkt
    schliesst die Zeile (geschütztes Spatium davor, damit er nie allein rutscht)."""
    return "&#160;·<br />".join(xml(t.strip()) for t in s.split("·"))


def titel(s):
    """Titelzeile ohne einzelnes Schlusswort: letztes Wortpaar unzertrennlich (trägt in
    jedem Client); text-wrap:balance gleicht die Zeilen aus, wo Clients es können."""
    t = xml(s.strip())
    i = t.rfind(" ")
    if i > 0:
        t = t[:i] + "&#160;" + t[i + 1:]
    return f'<div style="text-wrap:balance">{t}</div>'


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
    btns = []
    for i, (label, l) in enumerate(cta_links):
        primaer = i == 0
        border = "" if primaer else f'border="2px solid {AKZENT}" '
        pad = 14 if i == len(cta_links) - 1 else 10
        btns.append(
            f'<mj-button href="{xml(l["url"])}" background-color="{AKZENT if primaer else "#FFFFFF"}" '
            f'color="{"#FFFFFF" if primaer else AKZENT}" {border}border-radius="999px" font-size="16px" '
            f'font-weight="600" inner-padding="15px 30px" align="left" padding="0 0 {pad}px 0">{xml(label)}</mj-button>')
    btns = "".join(btns)
    mjml = f"""<mjml><mj-head><mj-title>{xml(c['betreff'])}</mj-title><mj-preview>{xml(preheader(c))}</mj-preview>{fontface}
<mj-attributes><mj-all font-family="{FONT_STACK}"/><mj-text font-size="16px" line-height="25px" color="{INK}"/></mj-attributes></mj-head>
<mj-body background-color="{MIST}">
<mj-section background-color="#FFFFFF" padding="18px 28px 14px 28px"><mj-column><mj-image src="{src_for(wm[0])}" href="{xml(haupt)}" alt="Goetheanum" width="{wm[1]}px" align="left" padding="0"/></mj-column></mj-section>
<mj-section background-color="#FFFFFF" padding="0"><mj-column><mj-image src="{hero}" href="{xml(haupt)}" alt="{xml(var.get('alt',''))}" padding="0" fluid-on-mobile="true"/></mj-column></mj-section>
<mj-section background-color="#FFFFFF" padding="24px 28px 0 28px"><mj-column>
  <mj-text font-size="14px" line-height="20px" color="{AKZENT}" padding="0 0 10px 0">{xml(H['badge'][lang])}</mj-text>
  <mj-text font-family="{HL_STACK}" font-size="30px" line-height="35px" font-weight="700" color="{INK}" padding="0 0 14px 0">{titel(c['botschaft'])}</mj-text>
  <mj-text padding="0 0 22px 0">{xml(c['text'])}</mj-text>
  {btns}
  <mj-text font-size="13px" line-height="20px" color="{MUTED}" padding="0 0 26px 0">{kleinzeile(H['kleinzeile'][motiv][lang])}</mj-text>
</mj-column></mj-section>
<mj-section background-color="{WASH}" padding="16px 28px"><mj-column><mj-text font-size="14px" line-height="22px" color="{AKZENT_TIEF}" align="center" padding="0">{xml(H['proof'][lang])}</mj-text></mj-column></mj-section>
<mj-section background-color="{MIST}" padding="20px 28px"><mj-column><mj-text font-size="12px" line-height="19px" color="{FUSS}" padding="0">Allgemeine Anthroposophische Gesellschaft · Goetheanum · Dornach<br/><a href="https://goetheanum.ch" style="color:{FUSS};">goetheanum.ch</a> · <a href="%UNSUBSCRIBELINK%" style="color:{FUSS};">Abmelden</a></mj-text></mj-column></mj-section>
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
    seg_blocks, sizes = [], []
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
                # Posteingang-Zeile: was Empfangende zuerst sehen (Betreff + Anriss);
                # bei w3 zusätzlich die Zweitrahmung des AC-Splits für Nicht-Öffner.
                alt_zeile = (f'<div class="ib-alt"><span>Nicht-Öffner erhalten:</span> {esc(c["alt"])}</div>'
                             if welle == "w3" else "")
                inbox = (f'<div class="inbox"><div class="ib-b">{esc(c["betreff"])}</div>'
                         f'<div class="ib-a">{esc(preheader(c))}</div>{alt_zeile}</div>')
                lang_cards.append(f"""<div class="mail" data-lang="{lang}">
  <div class="mhd">{welle.upper()} · {lang.upper()}<a href="mails/mail_{base}.html" title="Versand-HTML öffnen (AC-Bestückung)">HTML</a></div>
  {inbox}
  <iframe srcdoc="{html.replace('"','&quot;')}" loading="lazy" title="Vorschau {base}"></iframe>
  <div class="flds">{commentable(f"{base}#gesamt","Anmerkung zur Mail","<i>Was auffällt — das Element einfach benennen (Betreff, Bild, Text …)</i>")}</div></div>""")
            wave_cards.append(f'<div class="wave">{"".join(lang_cards)}</div>')
        seg_blocks.append(f'<section class="segment"><h2>{H["motive"][motiv]["label"]} — {seg}</h2><div class="waves">{"".join(wave_cards)}</div></section>')

    # Gemeinsame Elemente. Der Button-Stil zeigt die Mail-DNA — Artefakt, kein Theme.
    shared = [
        ("shared#wortmarke", "Wortmarke", f'<img src="{data_uri(wm[0])}" style="height:20px" alt="Goetheanum"> — offizielles Logo'),
        ("shared#badge", "Badge", f'<span style="color:{AKZENT}">{esc(H["badge"]["de"])}</span> / <span style="color:{AKZENT}">{esc(H["badge"]["en"])}</span> — HTML-Text, normal statt fett (G05) <!-- # ds-ok Mail-DNA, kein Theme -->'),
        ("shared#beweisband", "Beweis-Band", f'{esc(H["proof"]["de"])}<br>{esc(H["proof"]["en"])}'),
        ("shared#button", "Button-Stil", f'<span style="background:{AKZENT};color:#fff;border-radius:999px;padding:8px 18px;font:600 14px {FONT_STACK}">Gratis testen →</span> <!-- # ds-ok Mail-DNA, kein Theme -->'),
        ("shared#kleinzeile", "Kleinzeile (je Motiv)", "<br>".join(esc(H["kleinzeile"][m]["de"]) for m in H["motive"])),
        ("shared#footer", "Footer", "Allgemeine Anthroposophische Gesellschaft · Goetheanum · Dornach · Abmelden"),
    ]
    shared_html = "".join(commentable(k, l, v) for k, l, v in shared)

    sb_url = CFG["supabase"]["url"]; tab = CFG["supabase"]["kommentar_tabelle"]
    sb_key = CFG["supabase"].get("publishable_key", "")
    page = f"""<!doctype html>
<!-- =============================================================================
     Mail-Editor · Sommer-Aktion 2026 (Gegenlesen)
     Generiert von services/mailing-sommer2026/build_editor.py — NICHT von Hand
     editieren; Änderungen an heroes.json/config.json, dann neu bauen (--publish).
     Chrome aus tokens.css/base.css (DS01/DS02, B01-B04, Labels normal statt
     versal G05/G23). Die Mail-Vorschauen (iframes) und Feld-Werte tragen die
     Kampagnen-DNA der Landingpages — Artefakt, kein Theme (ds-ok je Zeile).
     ============================================================================= -->
<html lang="de-CH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mail-Editor · Sommer-Aktion 2026 · Goetheanum</title>
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
/* Sammelansicht: alle offenen Kommentare, anklicken springt zum Feld. */
.offen{{list-style:none;margin:0;padding:0;display:grid;gap:var(--s2)}}
.offen button{{display:block;width:100%;text-align:left;min-height:var(--tap);background:var(--paper);border:1px solid var(--line-soft);border-radius:8px;padding:var(--s2) var(--s3);font:inherit;cursor:pointer;color:var(--ink)}}
.offen button:hover{{border-color:var(--gold-ink)}}
.offen .okey{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--gold-ink);font-weight:600}}
.offen .otxt{{display:block;font-family:var(--font-text);font-size:var(--t-small);line-height:1.5;margin-top:2px}}
.offen .ometa{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--muted);margin-left:8px}}
.fld.blitz{{outline:2px solid var(--gold-deep);outline-offset:4px;border-radius:8px}}
/* Global ausblenden: Schalter «Kommentare» in der Kopfleiste. */
body.nocmt .cbtn,body.nocmt .cpanel,body.nocmt .offen-sec{{display:none}}
/* «Nur Mails»: alle Einzelelemente weg — reine Galerie der Vorschauen. */
body.nurmails .flds,body.nurmails .shared-sec{{display:none}}
.shared .fld{{background:var(--paper);border:1px solid var(--line-soft);border-radius:8px;padding:var(--s2) var(--s3)}}
.subline{{font-family:var(--font-text);font-size:var(--t-small);color:var(--muted);margin:0 0 var(--s3)}}
</style></head><body>

<script src="../../design-system/nav.js" data-root="../../" data-variant="werkzeug"
        data-onpage="Cockpit:../sommer-zaehler/|Aktivitäten:../sommer-zaehler/aktivitaeten.html|Kosten:../sommer-zaehler/kosten.html|Multiplikatoren:../sommer-zaehler/multiplikatoren.html|Links:../utm-generator/|Mail:../mail-editor/|Ablauf:../kampagnen-drehbuch/"></script>

<main class="wrap">
<section class="lead">
  <span class="kicker">Sommer-Aktion 2026</span>
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

<section class="segment offen-sec" id="offen-sec" hidden><h2>Offene Kommentare</h2>
<p class="subline">Die To-do-Liste des Gegenlesens — anklicken springt zum Feld.</p>
<ul class="offen" id="offenliste"></ul></section>

<section class="segment shared-sec"><h2>Gemeinsame Elemente</h2>
<p class="subline">Einmal kommentieren — gilt für alle Mails.</p>
<div class="shared">{shared_html}</div></section>
{''.join(seg_blocks)}
</main>

<footer class="ds-footer"><div class="wrap"><div class="frow">
  <span><strong>Mail-Editor</strong> · Sommer-Aktion 2026 · Kommentare ins Werkzeug-Backend, nur Kürzel, keine Personendaten</span>
  <span><a href="../../design-system/">Design-System</a></span>
</div></div></footer>

<script>
const SB_URL="{sb_url}", SB_KEY="{sb_key}", TAB="{tab}";
const REST=SB_URL+"/rest/v1/"+TAB, RPC=SB_URL+"/rest/v1/rpc/sommer2026_comment_erledigt";
const HDR={{"apikey":SB_KEY,"Authorization":"Bearer "+SB_KEY,"Content-Type":"application/json"}};
let COMMENTS={{}}, SHOW_DONE=false;
const st=t=>document.getElementById('status').textContent=t;
function setLang(l){{document.getElementById('b-de').classList.toggle('on',l=='de');document.getElementById('b-en').classList.toggle('on',l=='en');
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
 document.querySelectorAll('.cc').forEach(s=>{{const n=sammel(s.dataset.cc).filter(c=>!c.erledigt).length;
   s.textContent=n;s.classList.toggle('has',n>0);}});
 const off=[];Object.values(COMMENTS).forEach(l=>l.forEach(c=>{{if(!c.erledigt)off.push(c);}}));
 off.sort((a,b)=>a.created_at<b.created_at?-1:1);
 document.getElementById('offen-sec').hidden=off.length===0;
 document.getElementById('offenliste').innerHTML=off.map(c=>{{const[wo,feld]=c.mail_key.split('#');
   return '<li><button type="button" data-go="'+esc(c.mail_key)+'"><span class="okey">'
     +esc(wo==='shared'?'Gemeinsam':wo)+' · '+esc(feld||'')+'</span><span class="ometa">'+esc(c.autor||'?')+' · '+zeit(c.created_at)+'</span>'
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
function spracheAus(key){{const m=key.match(/_(de|en)#/);return m?m[1]:null;}}
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

#!/usr/bin/env python3
"""build_editor.py — rendert die Wellen-Matrix (Segment × Welle × Sprache) und den
Gegenlese-Editor (dist/editor.html; Kommentare -> Supabase, key = element-id).

Zwei Bild-Modi (config.json / asset_base_url):
  leer    -> Data-URIs in den Mails (nur Vorschau; Gmail clippt >102 KB und blockt Data-URIs)
  gesetzt -> gehostete URLs in dist/mail_*.html (versandfähig, Ziel < 100 KB je Mail)
Der Editor bettet die Vorschauen immer ein (eine Datei, offline teilbar).

`--publish` kopiert Editor + gehostete Assets nach ../../apps/mail-editor/
(GitHub Pages deployt apps/ -> https://werkzeuge.goetheanum.ch/apps/mail-editor/).
"""
import json, base64, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw, ImageOps

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


def typo(text, out, px, color, wrap=None, weight="Bold"):
    """FazetaSans-Zeile als PNG (Wortmarke, Badge). Wird immer neu gerendert — kein Stale-Cache."""
    f = ImageFont.truetype(str(ROOT / f"assets/fonts/FazetaSans-{weight}.ttf"), px * S)
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8))); lines = [text]
    if wrap:
        words, cur, lines = text.split(), "", []
        for w in words:
            t = (cur + " " + w).strip()
            if d0.textlength(t, font=f) <= wrap * S or not cur: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
    asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.02)
    Wd = int(max(d0.textlength(l, font=f) for l in lines)) + 8 * S; Ht = lh * len(lines) + 8 * S
    img = Image.new("RGBA", (Wd, Ht), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)); y = 4 * S
    for l in lines: d.text((4*S, y), l, font=f, fill=rgb+(255,)); y += lh
    img.save(G / out); return out, Wd // S


def src_for(rel, embed):
    """Bildquelle je Modus: Data-URI (Editor/Vorschau) oder gehostete URL (Versand)."""
    if embed or not BASE:
        mime = "image/png" if rel.endswith(".png") else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode((G / rel).read_bytes()).decode()
    return f"{BASE}/{rel}"


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


def render_mail(motiv, welle, lang, wm, badges, embed):
    seg = SEG_OF[motiv]
    vid = H["wellenplan"][seg][welle].split("/")[1]
    var = variation(motiv, vid)
    c = H["wellen"][motiv][welle][lang]
    ctas = ctas_for(seg, welle, lang)
    mehrere = len(ctas) > 1
    cta_links = [(label, links.link_for(welle, seg, ziel, lang, mehrere)) for ziel, label in ctas]
    hero = src_for(compose(var, f"{motiv}_{vid}"), embed)
    badge = badges[lang]
    fontface = (f"<mj-style>@font-face{{font-family:'Fazeta Sans';src:url('{BASE}/FazetaSans-Bold.ttf') "
                "format('truetype');font-weight:700;font-style:normal;}</mj-style>") if BASE else ""
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
<mj-section background-color="#FFFFFF" padding="18px 28px 14px 28px"><mj-column><mj-image src="{src_for(wm[0], embed)}" alt="Das Goetheanum" width="{wm[1]}px" align="left" padding="0"/></mj-column></mj-section>
<mj-section background-color="#FFFFFF" padding="0"><mj-column><mj-image src="{hero}" alt="{xml(var.get('alt',''))}" padding="0" fluid-on-mobile="true"/></mj-column></mj-section>
<mj-section background-color="#FFFFFF" padding="24px 28px 0 28px"><mj-column>
  <mj-image src="{src_for(badge[0], embed)}" alt="{xml(H['badge'][lang])}" width="{badge[1]}px" align="left" padding="0 0 10px 0"/>
  <mj-text font-family="{HL_STACK}" font-size="30px" line-height="35px" font-weight="700" color="{INK}" padding="0 0 14px 0">{xml(c['botschaft'])}</mj-text>
  <mj-text padding="0 0 22px 0">{xml(c['text'])}</mj-text>
  {btns}
  <mj-text font-size="13px" line-height="20px" color="{MUTED}" padding="0 0 26px 0">{xml(H['kleinzeile'][motiv][lang])}</mj-text>
</mj-column></mj-section>
<mj-section background-color="{WASH}" padding="16px 28px"><mj-column><mj-text font-size="14px" line-height="22px" color="{AKZENT_TIEF}" align="center" padding="0">{xml(H['proof'][lang])}</mj-text></mj-column></mj-section>
<mj-section background-color="{MIST}" padding="20px 28px"><mj-column><mj-text font-size="12px" line-height="19px" color="{FUSS}" padding="0">Allgemeine Anthroposophische Gesellschaft · Goetheanum · Dornach<br/><a href="%UNSUBSCRIBELINK%" style="color:{FUSS};">Abmelden</a></mj-text></mj-column></mj-section>
</mj-body></mjml>"""
    p = subprocess.run(["mjml", "-i", "-s"], input=mjml, capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr)
    fields = {"Motiv": f"{motiv}/{vid} — {var.get('alt','')}", "Betreff": c["betreff"],
              "Botschaft": c["botschaft"], "Text": c["text"],
              "CTA": " · ".join(label for label, _ in cta_links),
              "Alt-Betreff (AC-Split)": c["alt"],
              "Link": " · ".join(l["url"] for _, l in cta_links)}
    return p.stdout, fields


def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def commentable(key, label, value_html):
    return f"""<div class="fld" data-key="{esc(key)}"><div class="fh"><span class="lbl">{label}</span>
<button class="cbtn" onclick="toggle(this)">💬 <span class="cc" data-cc="{esc(key)}">0</span></button></div>
<div class="val">{value_html}</div>
<div class="cpanel" hidden><ul class="clist" data-cl="{esc(key)}"></ul>
<div class="cin"><input placeholder="Kommentar …"><button onclick="send(this,'{esc(key)}')">senden</button></div></div></div>"""


def main():
    publish = "--publish" in sys.argv
    G.mkdir(parents=True, exist_ok=True); (ROOT/"dist").mkdir(exist_ok=True)
    wm = typo("DAS GOETHEANUM", "wm_slate.png", 15, T["wortmarke"])
    badges = {"de": typo(H["badge"]["de"], "badge_de.png", 17, AKZENT),
              "en": typo(H["badge"]["en"], "badge_en.png", 17, AKZENT)}
    if BASE:
        shutil.copy(ROOT/"assets/fonts/FazetaSans-Bold.ttf", G/"FazetaSans-Bold.ttf")
    seg_blocks, sizes = [], []
    for motiv in H["motive"]:
        seg = SEG_OF[motiv]
        wave_cards = []
        for welle in H["wellenplan"][seg]:
            lang_cards = []
            for lang in ("de", "en"):
                versand, fields = render_mail(motiv, welle, lang, wm, badges, embed=False)
                out = ROOT/"dist"/f"mail_{motiv}_{welle}_{lang}.html"
                out.write_text(versand, encoding="utf-8")
                sizes.append((out.name, len(versand.encode("utf-8"))))
                # Editor-Vorschau immer eingebettet (eine Datei, offline teilbar)
                html = versand if not BASE else render_mail(motiv, welle, lang, wm, badges, embed=True)[0]
                base = f"{motiv}_{welle}_{lang}"
                frows = "".join(commentable(f"{base}#{k}", k, esc(v) if k != "Link" else f'<code>{esc(v)}</code>')
                                for k, v in fields.items())
                lang_cards.append(f"""<div class="mail" data-lang="{lang}">
  <div class="mhd">{welle.upper()} · {lang.upper()}</div>
  <iframe srcdoc="{html.replace('"','&quot;')}" loading="lazy" title="Vorschau {base}"></iframe>
  <div class="flds">{frows}
    {commentable(f"{base}#gesamt","Ganze Mail","<i>Anmerkung zur ganzen Mail</i>")}
  </div></div>""")
            wave_cards.append(f'<div class="wave">{"".join(lang_cards)}</div>')
        seg_blocks.append(f'<section class="segment"><h2>{H["motive"][motiv]["label"]} — {seg}</h2><div class="waves">{"".join(wave_cards)}</div></section>')

    # Gemeinsame Elemente. Der Button-Stil zeigt die Mail-DNA — Artefakt, kein Theme.
    shared = [
        ("shared#wortmarke", "Wortmarke", f'<img src="{src_for(wm[0], True)}" style="height:22px" alt="Das Goetheanum">'),
        ("shared#badge", "Badge", f'<img src="{src_for(badges["de"][0], True)}" style="height:22px" alt="{esc(H["badge"]["de"])}"> / <img src="{src_for(badges["en"][0], True)}" style="height:22px" alt="{esc(H["badge"]["en"])}">'),
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
.mail{{width:340px;flex:0 0 auto;background:var(--paper);border:1px solid var(--line-soft);border-radius:10px;overflow:hidden}}
.mhd{{background:var(--bar-bg);color:var(--on-accent);font-family:var(--font-text);font-size:var(--t-micro);font-weight:600;padding:6px 12px}}
.mail iframe{{width:100%;height:520px;border:0;display:block;background:#F6F4F2}} /* # ds-ok Mail-Grund (Artefakt) */
.flds{{padding:var(--s2) var(--s3)}}
.fld{{border-top:1px solid var(--line-soft);padding:8px 4px}} .fld:first-child{{border-top:0}}
.fh{{display:flex;align-items:center;gap:var(--s2)}}
.lbl{{font-family:var(--font-text);font-size:var(--t-micro);color:var(--muted);flex:1}}
.cbtn{{min-height:var(--tap);background:var(--field-bg);border:1px solid var(--line-soft);border-radius:999px;padding:2px 12px;font:inherit;font-size:var(--t-micro);cursor:pointer;color:var(--ink)}}
.cc.has{{background:var(--gold-deep);color:var(--on-accent);border-radius:10px;padding:0 7px}}
.val{{font-family:var(--font-text);font-size:var(--t-small);line-height:1.5;margin-top:4px;color:var(--ink)}}
.val code{{font-family:var(--font-mono);font-size:var(--t-micro);color:var(--muted);word-break:break-all}}
.cpanel{{margin-top:var(--s2);background:var(--field-bg);border-radius:8px;padding:var(--s2)}}
.clist{{list-style:none;margin:0 0 var(--s2);padding:0;font-family:var(--font-text);font-size:var(--t-small)}}
.clist li{{display:flex;gap:8px;align-items:baseline;padding:5px 8px;background:var(--paper);border-radius:6px;margin-bottom:4px}}
.clist li.done .ktxt{{text-decoration:line-through;color:var(--muted)}}
.clist b{{color:var(--gold-ink)}} .clist .kzeit{{font-size:var(--t-micro);color:var(--muted);white-space:nowrap}}
.clist .ktxt{{flex:1}}
.kdone{{min-height:var(--tap);background:none;border:1px solid var(--line-soft);border-radius:999px;padding:0 10px;font:inherit;font-size:var(--t-micro);color:var(--muted);cursor:pointer}}
.kdone:hover{{border-color:var(--gold-deep);color:var(--gold-ink)}}
.cin{{display:flex;gap:var(--s2)}}
.cin input{{flex:1;min-height:var(--tap);font:inherit;font-size:var(--t-small);padding:6px 10px;border:1px solid var(--line);border-radius:var(--r-control);background:var(--paper);color:var(--ink)}}
.cin button{{min-height:var(--tap);background:var(--blue-solid);color:var(--on-accent);border:0;border-radius:var(--r-control);padding:6px 14px;font:inherit;font-size:var(--t-small);cursor:pointer}}
.shared .fld{{background:var(--paper);border:1px solid var(--line-soft);border-radius:8px;padding:var(--s2) var(--s3)}}
.subline{{font-family:var(--font-text);font-size:var(--t-small);color:var(--muted);margin:0 0 var(--s3)}}
</style></head><body>

<script src="../../design-system/nav.js" data-root="../../" data-variant="werkzeug"></script>

<main class="wrap">
<section class="lead">
  <span class="kicker">Sommer-Aktion 2026</span>
  <h1>Mail-Editor</h1>
  <p class="lede" style="max-width:var(--measure)">Alle Wellen-Mails der drei Segmente zum Gegenlesen — je Feld kommentierbar, Kommentare landen im Werkzeug-Backend. Korrigiert wird in <code>heroes.json</code>, dann wird neu gebaut.</p>
  <div class="controls">
    <span class="lab">Sprache</span>
    <button id="b-de" class="pill on" onclick="setLang('de')">Deutsch</button>
    <button id="b-en" class="pill" onclick="setLang('en')">English</button>
    <span class="lab" style="margin-left:var(--s3)">Ihr Kürzel</span>
    <input id="autor" placeholder="z. B. ph">
    <button id="b-done" class="pill" onclick="toggleDone()">Erledigte zeigen</button>
    <span id="status" style="margin-left:auto">verbinde …</span>
  </div>
</section>

<section class="segment"><h2>Gemeinsame Elemente</h2>
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
function toggle(b){{const p=b.closest('.fld').querySelector('.cpanel');p.hidden=!p.hidden;}}
function esc(s){{const d=document.createElement('div');d.textContent=s;return d.innerHTML;}}
function zeit(iso){{try{{return new Date(iso).toLocaleString('de-CH',{{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}});}}catch(e){{return '';}}}}
function render(){{
 document.querySelectorAll('.clist').forEach(ul=>{{
   const items=(COMMENTS[ul.dataset.cl]||[]).filter(c=>SHOW_DONE||!c.erledigt);
   ul.innerHTML=items.map(c=>'<li class="'+(c.erledigt?'done':'')+'"><b>'+esc(c.autor||'?')+'</b>'
     +'<span class="ktxt">'+esc(c.kommentar)+'</span><span class="kzeit">'+zeit(c.created_at)+'</span>'
     +'<button class="kdone" onclick="erledigt('+c.id+','+(!c.erledigt)+')">'+(c.erledigt?'wieder öffnen':'erledigt ✓')+'</button></li>').join('');}});
 document.querySelectorAll('.cc').forEach(s=>{{const n=(COMMENTS[s.dataset.cc]||[]).filter(c=>!c.erledigt).length;
   s.textContent=n;s.classList.toggle('has',n>0);}});
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
 const autor=(document.getElementById('autor').value||'').trim()||'anon';
 try{{localStorage.setItem('autor',autor);}}catch(e){{}}
 btn.disabled=true; st("sende …");
 try{{
  const r=await fetch(REST,{{method:"POST",headers:{{...HDR,"Prefer":"return=minimal"}},body:JSON.stringify({{mail_key:key,autor,kommentar:txt,sprache:spracheAus(key)}})}});
  if(!r.ok) throw new Error("HTTP "+r.status+" "+(await r.text()).slice(0,120));
  inp.value=""; await load();
 }}catch(e){{st("Fehler: "+e.message); alert("Konnte nicht senden:\\n"+e.message+"\\n\\nTipp: Diese Seite über werkzeuge.goetheanum.ch öffnen — in eingebetteten Vorschauen sind Netzwerkzugriffe oft blockiert.");}}
 btn.disabled=false;
}}
try{{document.getElementById('autor').value=localStorage.getItem('autor')||'';}}catch(e){{}}
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
        for f in sorted(G.iterdir()):
            shutil.copy(f, adir/f.name)
        print(f"Publiziert: {APP}/index.html + {len(list(adir.iterdir()))} Assets -> {BASE or '(asset_base_url leer!)'}")


if __name__ == "__main__":
    main()

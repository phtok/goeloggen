#!/usr/bin/env python3
# ligvorschau.html: ligatures composed at Leise/Klar/Laut, shown in running text
# (variable webfont body) with a weight switch — to see esp. Leise in flow.
import os, sys, json, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

CUTS = {"Leise": (265, glob.glob(os.path.join(HERE, "input", "*-Leise.otf"))[0]),
        "Klar":  (440, glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0]),
        "Laut":  (680, glob.glob(os.path.join(HERE, "input", "*-Laut.otf"))[0])}
FONTS = {n: TTFont(p) for n, (w, p) in CUTS.items()}
SRC = os.path.join(HERE, "..", "..", "assets", "entwuerfe", "ligaturen-v2")
LIGS = [("ff", "ff-standard.svg", [0x66, 0x66]), ("ffe", "ff-alternate-Wortende.svg", [0x66, 0x66]),
        ("fi", "fi-weit.svg", [0x66, 0x131]), ("fl", "fl.svg", [0x66, 0x6C]), ("ft", "ft.svg", [0x66, 0x74])]
fK_bowtip = (lambda r: max(x for c, p in r for x, y in p) - min(x for c, p in r for x, y in p))(grec(FONTS["Klar"], 0x66)[0])

def user_layout(fname):
    root = ET.parse(os.path.join(SRC, fname)).getroot(); rps = []
    for e in root.iter():
        if e.tag.split('}')[-1] == 'path' and e.get('d'):
            rp = RecordingPen(); parse_path(e.get('d'), rp); rps.append(rp)
    order = sorted(range(len(rps)), key=lambda i: min(x for c, q in rps[i].value for x, y in q))
    comps = [[(c, tuple((x, 726-y) for x, y in q)) for c, q in rps[i].value] for i in order]  # font y-up
    m0 = min(x for c, p in comps[0] for x, y in p)
    info = []
    for comp in comps:
        cmn = min(x for c, p in comp for x, y in p); cmx = max(x for c, p in comp for x, y in p)
        info.append({"relx": cmn - m0, "delta": round((cmx - cmn) - fK_bowtip)})
    return info

LAYOUT = {key: user_layout(fn) for key, fn, _ in LIGS}

def recshift(rec, dx): return [(c, tuple((x+dx, y) for x, y in p)) for c, p in rec]
def ext_bow(rec, delta):
    return [(c, tuple((x+delta if (x > 230 and y > 590) else x, y) for x, y in p)) for c, p in rec]
def cmin(rec): return min(x for c, p in rec for x, y in p)
def cmax(rec): return max(x for c, p in rec for x, y in p)

def compose(weightfont, key, unis):
    info = LAYOUT[key]; parts = []
    for j, (u, meta) in enumerate(zip(unis, info)):
        is_f = (u == 0x66)
        rec, adv = grec(weightfont, u)
        if is_f:
            rec = ext_bow(rec, meta["delta"])
        parts.append(recshift(rec, meta["relx"]))
    gmin = min(cmin(r) for r in parts)
    parts = [recshift(r, -gmin) for r in parts]
    width = max(cmax(r) for r in parts)
    # trailing letter RSB at this weight
    tu = unis[-1]; tr, ta = grec(weightfont, tu)
    rsb = ta - max(x for c, p in tr for x, y in p)
    return parts, width, round(rsb, 1)

LSB, BASE = 29, 750
def inline_path(parts):
    d = []
    for rec in parts:
        for c, p in rec:
            Q = [(LSB + x, BASE - y) for x, y in p]
            if c == "moveTo": d.append("M%.1f %.1f" % Q[0])
            elif c == "lineTo": d.append("L%.1f %.1f" % Q[0])
            elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (Q[0]+Q[1]+Q[2]))
            elif c == "qCurveTo":
                for i in range(len(Q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (Q[i]+Q[i+1]))
            elif c == "closePath": d.append("Z")
    return "".join(d)

def user_inline(fname, tu):
    """Philipp's EXACT Klar drawing -> inline path (all components, no recomposition)."""
    root = ET.parse(os.path.join(SRC, fname)).getroot(); rps = []
    for e in root.iter():
        if e.tag.split('}')[-1] == 'path' and e.get('d'):
            rp = RecordingPen(); parse_path(e.get('d'), rp); rps.append(rp)
    recs = [[(c, tuple((x, 726-y) for x, y in q)) for c, q in rp.value] for rp in rps]  # font y-up
    gmin = min(cmin(r) for r in recs); recs = [recshift(r, -gmin) for r in recs]
    width = max(cmax(r) for r in recs)
    tr, ta = grec(FONTS["Klar"], tu); rsb = ta - max(x for c, p in tr for x, y in p)
    return {"d": inline_path(recs), "w": round(width + LSB + rsb, 1)}

DATA = {}
for wname in CUTS:
    DATA[wname] = {}
    for key, fn, unis in LIGS:
        if wname == "Klar":
            DATA[wname][key] = user_inline(fn, unis[-1])          # exact drawing
        else:
            parts, width, rsb = compose(FONTS[wname], key, unis)  # approximation (placeholder)
            DATA[wname][key] = {"d": inline_path(parts), "w": round(width + LSB + rsb, 1)}

BOUND = set(" ,.;:!?—-–)„‑")
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def markup(text):
    out = ""; i = 0; n = len(text)
    while i < n:
        if text[i:i+2] == "ff":
            nxt = text[i+2] if i+2 < n else " "
            out += '<span class="lig" data-l="%s"></span>' % ("ffe" if nxt in BOUND else "ff"); i += 2; continue
        if text[i:i+2] in ("fi", "fl", "ft"):
            out += '<span class="lig" data-l="%s"></span>' % text[i:i+2]; i += 2; continue
        out += esc(text[i]); i += 1
    return out

SAMPLE = ("Auffällige, fließende Schriftzüge: der Stoff, das Schiff, ein Pfiff, "
          "Koffer, schaffen, öffnen, die Auflage, das Pflaster, Grafik, "
          "sanfte Kraft, oft geprüft, fünf Briefe — das schafft Vertrauen.")
BODY = markup(SAMPLE)
WMAP = {"Leise": 265, "Klar": 440, "Laut": 680}

HTML = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ligaturen über die Gewichte</title>
<style>
@font-face{font-family:"G Var";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Variabel-v2.4.1.woff2") format("woff2");font-weight:190 725;font-display:swap}
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 22px 70px}
h1{font-size:22px;margin:0 0 6px}.hint{color:#737a80;font-size:14px;margin:6px 0 14px}
.sw{display:flex;gap:8px;margin:0 0 14px}
.sw button{font:inherit;font-size:14px;border:1px solid rgba(20,24,28,.2);background:#fff;border-radius:9px;padding:8px 16px;cursor:pointer}
.sw button.on{background:#23272b;color:#fff;border-color:#23272b}
.stage{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:14px;padding:30px 30px;margin:0 0 12px}
.sample{font-family:"G Var";font-size:44px;line-height:1.6;color:#23272b}
.lig{display:inline-block;vertical-align:-0.25em}
.lig svg{height:1em;fill:currentColor}
.tool{max-width:360px;margin-top:6px}.tool label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
input[type=range]{width:100%}
</style></head><body><div class="wrap">
<h1>Ligaturen über die Gewichte</h1>
<div class="hint"><b>Klar = deine echte Zeichnung.</b> Laut/Leise sind vorerst nur eine <b>mechanische Näherung</b> (Font-f + parametrischer Bogen) — sie entsprechen <i>nicht</i> deiner Hand und werden durch deine gezeichneten Laut/Leise ersetzt. Brottext = Variable Font.</div>
<div class="sw" id="sw"><button data-w="Leise">Leise (Näherung)</button><button data-w="Klar" class="on">Klar — deine Zeichnung</button><button data-w="Laut">Laut (Näherung)</button></div>
<div class="stage"><div class="sample" id="sample">__BODY__</div></div>
<div class="tool"><label>Schriftgrösse <b><span id="v_size">44</span> px</b></label><input type="range" id="s_size" min="16" max="100" value="44"></div>
</div>
<script>
var DATA=__DATA__, WMAP=__WMAP__, cur="Klar";
function render(){
 var W=WMAP[cur];
 document.getElementById("sample").style.fontVariationSettings="'wght' "+W;
 [].forEach.call(document.querySelectorAll(".lig"),function(s){
  var g=DATA[cur][s.dataset.l];
  s.innerHTML='<svg viewBox="0 0 '+g.w+' 1000" style="width:'+(g.w/1000).toFixed(3)+'em"><path d="'+g.d+'"/></svg>';
 });
}
[].forEach.call(document.querySelectorAll("#sw button"),function(b){b.addEventListener("click",function(){
 cur=b.dataset.w;[].forEach.call(document.querySelectorAll("#sw button"),function(x){x.classList.remove("on");});
 b.classList.add("on");render();});});
var sz=document.getElementById("s_size");
sz.addEventListener("input",function(){document.getElementById("sample").style.fontSize=sz.value+"px";document.getElementById("v_size").textContent=sz.value;});
document.fonts&&document.fonts.ready.then(render);render();
</script></body></html>"""
HTML = HTML.replace("__BODY__", BODY).replace("__DATA__", json.dumps(DATA)).replace("__WMAP__", json.dumps(WMAP))
open("/home/user/goeloggen/ligvorschau.html", "w").write(HTML)
print("wrote ligvorschau.html; weights:", list(DATA.keys()), "widths Klar:", {k: DATA["Klar"][k]["w"] for k in DATA["Klar"]})

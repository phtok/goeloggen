#!/usr/bin/env python3
# Generate ineinander.html: each ligature decomposed into letter components;
# live slider per ligature shifts the trailing letter(s) under the f-bow, shown in Klar text.
import os, sys, json
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

SVG = "/tmp/ph_lig/f-ligaturen_ph.svg"
root = ET.parse(SVG).getroot()
parent = {c: p for p in root.iter() for c in p}
def find(g):
    for e in root.iter():
        if e.get('id') == g: return e
def paths_of(el): return [e.get('d') for e in el.iter() if e.tag.split('}')[-1] == 'path' and e.get('d')]
def baseline_for(y): return 1020 if y < 1400 else (2340 if y < 2900 else 3660)
BASE = 760

def path_pts(d):
    rp = RecordingPen(); parse_path(d, rp); return rp

def comp_emit(rp, minx, By):
    out = []
    for c, q in rp.value:
        Q = [(x - minx, BASE - (By - y)) for x, y in q]
        if c == "moveTo": out.append("M%.1f %.1f" % Q[0])
        elif c == "lineTo": out.append("L%.1f %.1f" % Q[0])
        elif c == "curveTo": out.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (Q[0]+Q[1]+Q[2]))
        elif c == "qCurveTo":
            for i in range(len(Q)-1): out.append("Q%.1f %.1f %.1f %.1f" % (Q[i]+Q[i+1]))
        elif c == "closePath": out.append("Z")
    return "".join(out)

def decompose(gid):
    el = find(gid); ps = paths_of(el)
    if len(ps) < 2 and el in parent: ps = paths_of(parent[el])
    rps = [path_pts(d) for d in ps]
    allpts = [p for rp in rps for c, q in rp.value for p in q]
    By = baseline_for(min(y for x, y in allpts)); minx = min(x for x, y in allpts)
    # lead = leftmost path; trail = the rest (moved together)
    def pmin(rp): return min(x for c, q in rp.value for x, y in q)
    order = sorted(range(len(rps)), key=lambda i: pmin(rps[i]))
    lead_i = order[0]
    lead = comp_emit(rps[lead_i], minx, By)
    trail = "".join(comp_emit(rps[i], minx, By) for i in order[1:])
    xs_lead = [x - minx for c, q in rps[lead_i].value for x, y in q]
    xs_trail = [x - minx for i in order[1:] for c, q in rps[i].value for x, y in q]
    return {"lead": lead, "trail": trail,
            "lx": round(max(xs_lead), 1),
            "tlo": round(min(xs_trail), 1) if xs_trail else 0,
            "thi": round(max(xs_trail), 1) if xs_trail else 0}

# key -> drawn group id   (ffe = word-end ff, fil = fi with long bow, fff = triple f)
MAP = {"ff": "ff", "ffe": "ff5", "fi": "fi", "fil": "fi1", "fl": "fl", "ft": "ft", "fff": "ff1"}
DATA = {k: decompose(v) for k, v in MAP.items()}

# natural right side-bearing of the trailing letter (from the font) -> default Nachabstand
from fontfix import grec
from fontTools.ttLib import TTFont
import glob as _glob
_fK = TTFont(_glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
TRAIL = {"ff": 0x66, "ffe": 0x66, "fi": 0x131, "fil": 0x131, "fl": 0x6C, "ft": 0x74, "fff": 0x66}
for _k, _u in TRAIL.items():
    _r, _a = grec(_fK, _u)
    DATA[_k]["rsb"] = round(_a - max(x for c, p in _r for x, y in p), 1)
KEYS = ["ff", "ffe", "fi", "fil", "fl", "ft", "fff"]
LABELS = {"ff": "ff (wortintern)", "ffe": "ff (Wortende, gestreckt)", "fi": "fi",
          "fil": "fi (langer Bogen)", "fl": "fl", "ft": "ft", "fff": "fff"}

BOUND = set(" ,.;:!?—-–)„‑")
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def markup(text, fi_key="fi"):
    out = ""; i = 0; n = len(text)
    while i < n:
        if text[i:i+3] == "fff":
            out += '<span class="lig" data-l="fff"></span>'; i += 3; continue
        if text[i:i+2] == "ff":
            nxt = text[i+2] if i+2 < n else " "
            out += '<span class="lig" data-l="%s"></span>' % ("ffe" if nxt in BOUND else "ff"); i += 2; continue
        if text[i:i+2] == "fi":
            out += '<span class="lig" data-l="%s"></span>' % fi_key; i += 2; continue
        if text[i:i+2] == "fl":
            out += '<span class="lig" data-l="fl"></span>'; i += 2; continue
        if text[i:i+2] == "ft":
            out += '<span class="lig" data-l="ft"></span>'; i += 2; continue
        out += esc(text[i]); i += 1
    return out

SAMPLE = ("Auffällige, fließende Schriftzüge: der Stoff, das Schiff, ein Pfiff, "
          "Koffer, schaffen, öffnen, die Auflage, das Pflaster, Grafik, sanfte Kraft, "
          "oft geprüft. Schifffahrt, Sauerstoffflasche, stofflich.")
DEMO = "Alternatives fi mit langem Bogen: fix, fies, Grafik, definitiv, Profil."
BODY = ('<p style="margin:0 0 .35em">' + markup(SAMPLE) + '</p>'
        '<p style="margin:0;color:#6a7075;font-size:.8em">' + markup(DEMO, fi_key="fil") + '</p>')

def _cell(k):
    rsb = int(round(DATA[k]["rsb"]))
    return ('<div class="cell"><div class="ck">%s</div>'
            '<label>Überlappung <b><span id="v_%s">0</span></b></label>'
            '<input type="range" id="s_%s" min="-220" max="120" value="0">'
            '<label style="margin-top:9px">Nachabstand <b><span id="n_%s">%d</span></b></label>'
            '<input type="range" id="d_%s" min="-40" max="180" value="%d"></div>') % (LABELS[k], k, k, k, rsb, k, rsb)
ctrls = "".join(_cell(k) for k in KEYS)

HTML = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ligaturen ineinander</title>
<style>
@font-face{font-family:"G Klar";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.4.1-Klar.woff2") format("woff2");font-weight:400;font-display:swap}
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 22px 80px}
h1{font-size:22px;margin:0 0 6px}.hint{color:#737a80;font-size:14px;margin:6px 0 16px}
.stage{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:14px;padding:26px 28px;margin:14px 0}
.sample{font-family:"G Klar";font-size:46px;line-height:1.55;color:#23272b}
.lig{display:inline-block;vertical-align:-0.24em}
.lig svg{height:1em;fill:currentColor}
.ctrls{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:16px}
.ctrl label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
.cell{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:10px;padding:12px 14px}
.cell .ck{font-weight:600;margin-bottom:7px;font-size:15px}
.cell label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:4px}
.cell b,.ctrl b{font-variant-numeric:tabular-nums}
input[type=range]{width:100%}
.readout{margin-top:16px;font-size:13px;color:#3a3f44;background:#f3efe7;border-radius:10px;padding:11px 13px}
.code{font-family:ui-monospace,Menlo,monospace;white-space:pre-wrap}
.btn{font:inherit;font-size:13px;border:1px solid rgba(20,24,28,.18);background:#fff;border-radius:8px;padding:6px 11px;cursor:pointer;margin-right:8px}
small{color:#9aa0a6}
</style></head><body><div class="wrap">
<h1>Ligaturen ineinanderschieben</h1>
<div class="hint">Deine Ligaturen liegen <b>zerlegt</b> (f + Folgebuchstabe) inline im echten Klar‑Satz. Jeder Regler schiebt den Folgebuchstaben <b>unter den f‑Bogen</b>: negativ = enger, positiv = lockerer. Du justierst, während du die Ligatur <b>im Gebrauch</b> siehst. Werte in Fonteinheiten.</div>
<div class="stage"><div class="sample" id="sample">__BODY__</div></div>
<div class="ctrl" style="max-width:360px"><label>Schriftgrösse <b><span id="v_size">46</span> px</b></label><input type="range" id="s_size" min="16" max="110" value="46"></div>
<div class="ctrls">__CTRLS__</div>
<div class="readout"><span class="code" id="code"></span>
<div style="margin-top:9px"><button class="btn" id="copy">Werte kopieren</button><button class="btn" id="reset">zurücksetzen</button>
<small>Diese Überlappung wird die Komponenten‑Position in der Ligatur.</small></div></div>
</div>
<script>
var DATA=__DATA__;
var LSB=29, KEYS=["ff","ffe","fi","fil","fl","ft","fff"];
var OV={}, NA={};
KEYS.forEach(function(k){OV[k]=0;NA[k]=DATA[k].rsb;});
function svgFor(key){
 var d=DATA[key], ov=OV[key], na=NA[key];
 var inkMin=Math.min(0,d.tlo+ov), inkMax=Math.max(d.lx,d.thi+ov);
 var sh=LSB-inkMin, W=(inkMax-inkMin)+LSB+na;
 return '<svg viewBox="0 0 '+W.toFixed(1)+' 1000" style="width:'+(W/1000).toFixed(3)+'em">'
  +'<g transform="translate('+sh.toFixed(1)+',0)"><path d="'+d.lead+'"/>'
  +'<g transform="translate('+ov+',0)"><path d="'+d.trail+'"/></g></g></svg>';
}
function renderAll(){
 [].forEach.call(document.querySelectorAll(".lig"),function(s){s.innerHTML=svgFor(s.dataset.l);});
 document.getElementById("code").textContent=
  KEYS.map(function(k){return k+":  Überlappung "+(OV[k]>0?"+":"")+OV[k]+"   ·   Nachabstand "+NA[k];}).join("\\n");
}
KEYS.forEach(function(k){
 var s=document.getElementById("s_"+k);
 s.addEventListener("input",function(){OV[k]=+s.value;document.getElementById("v_"+k).textContent=(OV[k]>0?"+":"")+OV[k];renderAll();});
 var dd=document.getElementById("d_"+k);
 dd.addEventListener("input",function(){NA[k]=+dd.value;document.getElementById("n_"+k).textContent=NA[k];renderAll();});
});
document.getElementById("reset").onclick=function(){KEYS.forEach(function(k){
 OV[k]=0;NA[k]=DATA[k].rsb;
 document.getElementById("s_"+k).value=0;document.getElementById("v_"+k).textContent="0";
 document.getElementById("d_"+k).value=DATA[k].rsb;document.getElementById("n_"+k).textContent=Math.round(DATA[k].rsb);});renderAll();};
document.getElementById("copy").onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(document.getElementById("code").textContent);
 var b=this;b.textContent="kopiert ✓";setTimeout(function(){b.textContent="Werte kopieren";},1200);};
var sz=document.getElementById("s_size");
sz.addEventListener("input",function(){document.getElementById("sample").style.fontSize=sz.value+"px";document.getElementById("v_size").textContent=sz.value;});
document.fonts&&document.fonts.ready.then(renderAll);
renderAll();
</script></body></html>"""
HTML = (HTML.replace("__BODY__", BODY).replace("__CTRLS__", ctrls)
            .replace("__DATA__", json.dumps(DATA)))
open("/home/user/goeloggen/ineinander.html", "w").write(HTML)
print("wrote ineinander.html; components:", {k: (round(v["lx"]), round(v["thi"])) for k, v in DATA.items()})

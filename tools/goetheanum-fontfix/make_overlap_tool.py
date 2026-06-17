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

MAP = {"ff": "ff", "fi": "fi", "fl": "fl", "ft": "ft", "fj": "fj", "fk": "fk"}
DATA = {k: decompose(v) for k, v in MAP.items()}

LIGSEQ = ["ff", "fi", "fl", "fj", "fk", "ft"]
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def markup(text):
    out = ""; i = 0
    while i < len(text):
        seq = next((s for s in LIGSEQ if text[i:i+len(s)] == s and s in DATA), None)
        if seq:
            out += '<span class="lig" data-l="%s"></span>' % seq; i += len(seq); continue
        out += esc(text[i]); i += 1
    return out

SAMPLE = ("Auffällige, fließende Schriftzüge: der Stoff, das Schiff, ein Pfiff, "
          "Koffer, schaffen, treffen, öffnen, die Auflage, das Pflaster, "
          "Grafik, sanfte Kraft, oft geprüft, fünf.")
BODY = markup(SAMPLE)

ctrls = "".join(
    '<div class="ctrl"><label>%s · Überlappung <b><span id="v_%s">0</span></b></label>'
    '<input type="range" id="s_%s" min="-220" max="120" value="0"></div>' % (k, k, k)
    for k in ["ff", "fi", "fl", "ft", "fj", "fk"])

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
.ctrls{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px 26px;margin-top:16px}
.ctrl label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
.ctrl b{font-variant-numeric:tabular-nums}
input[type=range]{width:100%}
.readout{margin-top:16px;font-size:13px;color:#3a3f44;background:#f3efe7;border-radius:10px;padding:11px 13px}
.code{font-family:ui-monospace,Menlo,monospace}
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
var OV={ff:0,fi:0,fl:0,ft:0,fj:0,fk:0};
function svgFor(key){
 var d=DATA[key], ov=OV[key];
 var minx=Math.min(0, d.tlo+ov), maxx=Math.max(d.lx, d.thi+ov);
 var w=maxx-minx;
 return '<svg viewBox="'+minx.toFixed(1)+' 0 '+w.toFixed(1)+' 1000" style="width:'+(w/1000).toFixed(3)+'em">'
  +'<path d="'+d.lead+'"/><g transform="translate('+ov+',0)"><path d="'+d.trail+'"/></g></svg>';
}
function renderAll(){
 [].forEach.call(document.querySelectorAll(".lig"),function(s){s.innerHTML=svgFor(s.dataset.l);});
 document.getElementById("code").textContent=
  Object.keys(OV).map(function(k){return k+": "+(OV[k]>0?"+":"")+OV[k];}).join("   ·   ");
}
["ff","fi","fl","ft","fj","fk"].forEach(function(k){
 var s=document.getElementById("s_"+k);
 s.addEventListener("input",function(){OV[k]=+s.value;document.getElementById("v_"+k).textContent=(OV[k]>0?"+":"")+OV[k];renderAll();});
});
document.getElementById("reset").onclick=function(){["ff","fi","fl","ft","fj","fk"].forEach(function(k){
 OV[k]=0;document.getElementById("s_"+k).value=0;document.getElementById("v_"+k).textContent="0";});renderAll();};
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

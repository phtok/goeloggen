#!/usr/bin/env python3
# Generate ineinander.html from Philipp's redrawn ligature files (filename = role).
# Decompose each into f + trailing letter; live sliders for Überlappung, Nachabstand,
# vertikale Lage, Schriftgrösse; A/B comparison for ff and fi alternates.
import os, sys, json
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen
from fontfix import grec
from fontTools.ttLib import TTFont
import glob

SRC = "/tmp/ph_lig2"
FILES = {"ff": "ff-standard.svg", "ffe": "ff-alternate-Wortende.svg",
         "fie": "fi-eng.svg", "fiw": "fi-weit.svg", "fl": "fl.svg", "ft": "ft.svg"}
SHIFT = 750 - 726     # source baseline (svg-y 726) -> inline baseline (ascent 750)

def rp_of(d):
    rp = RecordingPen(); parse_path(d, rp); return rp
def emit(rp, minx):
    out = []
    for c, q in rp.value:
        Q = [(x - minx, y + SHIFT) for x, y in q]
        if c == "moveTo": out.append("M%.1f %.1f" % Q[0])
        elif c == "lineTo": out.append("L%.1f %.1f" % Q[0])
        elif c == "curveTo": out.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (Q[0]+Q[1]+Q[2]))
        elif c == "qCurveTo":
            for i in range(len(Q)-1): out.append("Q%.1f %.1f %.1f %.1f" % (Q[i]+Q[i+1]))
        elif c == "closePath": out.append("Z")
    return "".join(out)
def decompose(fname):
    root = ET.parse(os.path.join(SRC, fname)).getroot()
    rps = [rp_of(e.get('d')) for e in root.iter() if e.tag.split('}')[-1] == 'path' and e.get('d')]
    allx = [x for rp in rps for c, q in rp.value for x, y in q]; minx = min(allx)
    order = sorted(range(len(rps)), key=lambda i: min(x for c, q in rps[i].value for x, y in q))
    li = order[0]
    lead = emit(rps[li], minx); trail = "".join(emit(rps[i], minx) for i in order[1:])
    xl = [x - minx for c, q in rps[li].value for x, y in q]
    xt = [x - minx for i in order[1:] for c, q in rps[i].value for x, y in q]
    return {"lead": lead, "trail": trail, "lx": round(max(xl), 1),
            "tlo": round(min(xt), 1) if xt else 0, "thi": round(max(xt), 1) if xt else 0}

DATA = {k: decompose(v) for k, v in FILES.items()}
_fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
TRAIL = {"ff": 0x66, "ffe": 0x66, "fie": 0x131, "fiw": 0x131, "fl": 0x6C, "ft": 0x74}
for _k, _u in TRAIL.items():
    _r, _a = grec(_fK, _u); DATA[_k]["rsb"] = round(_a - max(x for c, p in _r for x, y in p), 1)
KEYS = ["ff", "ffe", "fie", "fiw", "fl", "ft"]
LABELS = {"ff": "ff (Standard, wortintern)", "ffe": "ff (Wortende)", "fie": "fi (eng)",
          "fiw": "fi (weit)", "fl": "fl", "ft": "ft"}

BOUND = set(" ,.;:!?—-–)„‑")
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def markup(text, ff_force=None, fi_key="fie"):
    out = ""; i = 0; n = len(text)
    while i < n:
        if text[i:i+2] == "ff":
            if ff_force: key = ff_force
            else:
                nxt = text[i+2] if i+2 < n else " "
                key = "ffe" if nxt in BOUND else "ff"
            out += '<span class="lig" data-l="%s"></span>' % key; i += 2; continue
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
          "oft geprüft. Schifffahrt, Sauerstoffflasche.")
FFW = "Stoff Schiff Pfiff schroff straff schlaff Riff"
FIW = "fix fies Grafik Profil definitiv fit Fiktion"
BODY = ('<p style="margin:0 0 .4em">' + markup(SAMPLE) + '</p>'
        '<div class="cmp"><div class="cl">ff am Wortende — Standard</div>'
        '<div class="row">' + markup(FFW, ff_force="ff") + '</div>'
        '<div class="cl">ff am Wortende — Alternate (gestreckt)</div>'
        '<div class="row">' + markup(FFW, ff_force="ffe") + '</div>'
        '<div class="cl">fi — eng</div><div class="row">' + markup(FIW, fi_key="fie") + '</div>'
        '<div class="cl">fi — weit</div><div class="row">' + markup(FIW, fi_key="fiw") + '</div></div>')

def cell(k):
    rsb = int(round(DATA[k]["rsb"]))
    return ('<div class="cell"><div class="ck">%s</div>'
            '<label>Überlappung <b><span id="v_%s">0</span></b></label>'
            '<input type="range" id="s_%s" min="-220" max="120" value="0">'
            '<label style="margin-top:9px">Nachabstand <b><span id="n_%s">%d</span></b></label>'
            '<input type="range" id="d_%s" min="-40" max="180" value="%d"></div>') % (LABELS[k], k, k, k, rsb, k, rsb)
ctrls = "".join(cell(k) for k in KEYS)

HTML = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ligaturen ineinander</title>
<style>
@font-face{font-family:"G Klar";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.4.1-Klar.woff2") format("woff2");font-weight:400;font-display:swap}
:root{--va:-220}
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 22px 80px}
h1{font-size:22px;margin:0 0 6px}.hint{color:#737a80;font-size:14px;margin:6px 0 16px}
.stage{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:14px;padding:26px 28px;margin:14px 0}
.sample{font-family:"G Klar";font-size:46px;line-height:1.6;color:#23272b}
.cmp{border-top:1px solid rgba(20,24,28,.1);margin-top:16px;padding-top:4px}
.cmp .cl{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;font-size:13px;color:#9aa0a6;margin:12px 0 0}
.cmp .row{margin:0}
.lig{display:inline-block;vertical-align:calc(var(--va)/1000*1em)}
.lig svg{height:1em;fill:currentColor}
.tools{display:flex;gap:24px;flex-wrap:wrap;margin-top:4px}
.tool{min-width:230px}.tool label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
.ctrls{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:16px}
.cell{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:10px;padding:12px 14px}
.cell .ck{font-weight:600;margin-bottom:7px;font-size:15px}
.cell label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:4px}
.cell b,.tool b{font-variant-numeric:tabular-nums}
input[type=range]{width:100%}
.readout{margin-top:16px;font-size:13px;color:#3a3f44;background:#f3efe7;border-radius:10px;padding:11px 13px}
.code{font-family:ui-monospace,Menlo,monospace;white-space:pre-wrap}
.btn{font:inherit;font-size:13px;border:1px solid rgba(20,24,28,.18);background:#fff;border-radius:8px;padding:6px 11px;cursor:pointer;margin-right:8px}
small{color:#9aa0a6}
</style></head><body><div class="wrap">
<h1>Ligaturen ineinanderschieben</h1>
<div class="hint">Deine neu gezeichneten Ligaturen, zerlegt in f + Folgebuchstabe, inline im echten Klar-Satz. Pro Ligatur <b>Überlappung</b> (negativ enger) und <b>Nachabstand</b>. Unten der A/B-Vergleich (ff Standard/Wortende, fi eng/weit). Globale Regler: vertikale Lage &amp; Schriftgrösse.</div>
<div class="stage"><div class="sample" id="sample">__BODY__</div></div>
<div class="tools">
 <div class="tool"><label>vertikale Lage <b><span id="v_va">-220</span></b></label><input type="range" id="s_va" min="-360" max="-60" value="-220"></div>
 <div class="tool"><label>Schriftgrösse <b><span id="v_size">46</span> px</b></label><input type="range" id="s_size" min="16" max="110" value="46"></div>
</div>
<div class="ctrls">__CTRLS__</div>
<div class="readout"><span class="code" id="code"></span>
<div style="margin-top:9px"><button class="btn" id="copy">Werte kopieren</button><button class="btn" id="reset">zurücksetzen</button></div></div>
</div>
<script>
var DATA=__DATA__, LSB=29, KEYS=["ff","ffe","fie","fiw","fl","ft"];
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
  KEYS.map(function(k){return k+":  Überlappung "+(OV[k]>0?"+":"")+OV[k]+"  ·  Nachabstand "+NA[k];}).join("\\n")
  +"\\nvertikale Lage "+document.getElementById("s_va").value;
}
KEYS.forEach(function(k){
 var s=document.getElementById("s_"+k);
 s.addEventListener("input",function(){OV[k]=+s.value;document.getElementById("v_"+k).textContent=(OV[k]>0?"+":"")+OV[k];renderAll();});
 var dd=document.getElementById("d_"+k);
 dd.addEventListener("input",function(){NA[k]=+dd.value;document.getElementById("n_"+k).textContent=NA[k];renderAll();});
});
var va=document.getElementById("s_va");
va.addEventListener("input",function(){document.documentElement.style.setProperty("--va",va.value);document.getElementById("v_va").textContent=va.value;renderAll();});
var sz=document.getElementById("s_size");
sz.addEventListener("input",function(){document.getElementById("sample").style.fontSize=sz.value+"px";document.getElementById("v_size").textContent=sz.value;});
document.getElementById("reset").onclick=function(){KEYS.forEach(function(k){
 OV[k]=0;NA[k]=DATA[k].rsb;document.getElementById("s_"+k).value=0;document.getElementById("v_"+k).textContent="0";
 document.getElementById("d_"+k).value=DATA[k].rsb;document.getElementById("n_"+k).textContent=Math.round(DATA[k].rsb);});
 va.value=-220;document.documentElement.style.setProperty("--va",-220);document.getElementById("v_va").textContent="-220";renderAll();};
document.getElementById("copy").onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(document.getElementById("code").textContent);
 var b=this;b.textContent="kopiert ✓";setTimeout(function(){b.textContent="Werte kopieren";},1200);};
document.fonts&&document.fonts.ready.then(renderAll);
renderAll();
</script></body></html>"""
HTML = (HTML.replace("__BODY__", BODY).replace("__CTRLS__", ctrls).replace("__DATA__", json.dumps(DATA)))
open("/home/user/goeloggen/ineinander.html", "w").write(HTML)
print("wrote ineinander.html from redrawn files; rsb:", {k: DATA[k]["rsb"] for k in KEYS})

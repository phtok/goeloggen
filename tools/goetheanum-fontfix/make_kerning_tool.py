#!/usr/bin/env python3
# Generate kerning.html: Philipp's ligatures inline in real Klar webfont text,
# with live sliders for left/right side-bearing + vertical nudge.
import os, sys, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

SVG = "/tmp/ph_lig/f-ligaturen_ph.svg"
root = ET.parse(SVG).getroot()
parent = {c: p for p in root.iter() for c in p}
def find(gid):
    for e in root.iter():
        if e.get('id') == gid: return e
def paths_of(el): return [e.get('d') for e in el.iter() if e.tag.split('}')[-1] == 'path' and e.get('d')]
def baseline_for(y): return 1020 if y < 1400 else (2340 if y < 2900 else 3660)
BASE = 760  # baseline in the 0..1000 inline viewBox
def lig_svg(gid):
    el = find(gid); ps = paths_of(el)
    if len(ps) < 2 and el in parent: ps = paths_of(parent[el])
    rp = RecordingPen()
    for d in ps: parse_path(d, rp)
    pts = [p for c, q in rp.value for p in q]
    xs = [x for x, y in pts]; By = baseline_for(min(y for x, y in pts)); minx = min(xs)
    out = []
    for c, q in rp.value:
        qq = [(x-minx, BASE-(By-y)) for x, y in q]    # font y-up -> inline (baseline at BASE)
        if c == "moveTo": out.append("M%.1f %.1f" % qq[0])
        elif c == "lineTo": out.append("L%.1f %.1f" % qq[0])
        elif c == "curveTo": out.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (qq[0]+qq[1]+qq[2]))
        elif c == "qCurveTo":
            for i in range(len(qq)-1): out.append("Q%.1f %.1f %.1f %.1f" % (qq[i]+qq[i+1]))
        elif c == "closePath": out.append("Z")
    w = max(xs)-minx
    return '<svg class="lig L_%s" viewBox="0 0 %.0f 1000" style="width:%.3fem"><path d="%s"/></svg>' % (
        "ff" if gid in ("ff", "ff5") else gid, w, w/1000.0, "".join(out)), w

LIGMAP = {"ff": "ff", "ffend": "ff5", "fi": "fi", "fl": "fl", "ft": "ft", "fj": "fj", "fk": "fk"}
SV = {k: lig_svg(v)[0] for k, v in LIGMAP.items()}

LIGSEQ = ["ff", "fi", "fl", "fj", "fk", "ft"]
BOUND = set(" ,.;:!?—-–)„")
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def markup(text):
    out = ""; i = 0
    while i < len(text):
        seq = next((s for s in LIGSEQ if text[i:i+len(s)] == s), None)
        if seq:
            key = seq
            if seq == "ff":
                nxt = text[i+2] if i+2 < len(text) else " "
                if nxt in BOUND: key = "ffend"
            out += SV[key]; i += len(seq); continue
        out += esc(text[i]); i += 1
    return out

SAMPLE = ("Auffällige, fließende Schriftzüge — der Stoff, das Schiff, ein Pfiff; "
          "Koffer, schaffen, treffen, öffnen, die Auflage, das Pflaster, "
          "Grafik, sanfte Kraft, oft geprüft, fünf.")
BODY = markup(SAMPLE)

HTML = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ligatur-Spacing</title>
<style>
@font-face{font-family:"G Klar";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.4.1-Klar.woff2") format("woff2");font-weight:400;font-display:swap}
:root{--ll:34;--lr:34;--ffl:34;--ffr:34;--va:-240}
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 22px 70px}
h1{font-size:22px;margin:0 0 6px}.hint{color:#737a80;font-size:14px;margin:6px 0 18px}
.stage{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:14px;padding:26px 28px;margin:14px 0}
.sample{font-family:"G Klar";font-size:46px;line-height:1.5;color:#23272b}
.lig{display:inline-block;height:1em;vertical-align:calc(var(--va)/1000*1em);fill:currentColor;
     margin-left:calc(var(--ll)/1000*1em);margin-right:calc(var(--lr)/1000*1em)}
.lig.L_ff{margin-left:calc(var(--ffl)/1000*1em);margin-right:calc(var(--ffr)/1000*1em)}
.ctrls{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px 26px;margin-top:18px}
.ctrl label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
.ctrl b{font-variant-numeric:tabular-nums}
input[type=range]{width:100%}
.readout{margin-top:18px;font-size:13px;color:#3a3f44;background:#f3efe7;border-radius:10px;padding:11px 13px}
.code{font-family:ui-monospace,Menlo,monospace}
.btn{font:inherit;font-size:13px;border:1px solid rgba(20,24,28,.18);background:#fff;border-radius:8px;padding:6px 11px;cursor:pointer;margin-right:8px}
small{color:#9aa0a6}
</style></head>
<body><div class="wrap">
<h1>Ligatur-Spacing justieren</h1>
<div class="hint">Deine gezeichneten Ligaturen liegen <b>inline in echtem Klar-Satz</b>. Schiebe den linken/rechten Abstand (und die vertikale Lage), bis sie den Rhythmus der Schrift halten. Werte in Tausendstel-Geviert. <b>ff</b> hat eigene Regler. Wortend-<b>ff</b> (Stoff/Schiff/Pfiff) nutzt deine Ausschwing-Form.</div>
<div class="stage"><div class="sample" id="sample">__BODY__</div></div>
<div class="ctrls">
 <div class="ctrl"><label>ff · Abstand links <b><span id="ffl-v">34</span></b></label><input type="range" id="ffl" min="-40" max="180" value="34"></div>
 <div class="ctrl"><label>ff · Abstand rechts <b><span id="ffr-v">34</span></b></label><input type="range" id="ffr" min="-40" max="180" value="34"></div>
 <div class="ctrl"><label>übrige Ligaturen · links <b><span id="ll-v">34</span></b></label><input type="range" id="ll" min="-40" max="180" value="34"></div>
 <div class="ctrl"><label>übrige Ligaturen · rechts <b><span id="lr-v">34</span></b></label><input type="range" id="lr" min="-40" max="180" value="34"></div>
 <div class="ctrl"><label>vertikale Lage <b><span id="va-v">-240</span></b></label><input type="range" id="va" min="-320" max="-160" value="-240"></div>
</div>
<div class="readout"><span class="code" id="code"></span>
 <div style="margin-top:9px"><button class="btn" id="copy">Werte kopieren</button><button class="btn" id="reset">zurücksetzen</button>
 <small>Diese Werte werden zu den Seitenrändern (sidebearings) der Ligatur-Glyphen.</small></div></div>
</div>
<script>
var V={ffl:34,ffr:34,ll:34,lr:34,va:-240};
function set(k,val){V[k]=val;document.documentElement.style.setProperty("--"+k,val);
 var e=document.getElementById(k+"-v");if(e)e.textContent=val;}
function refresh(){document.getElementById("code").textContent=
 "ff: links "+V.ffl+" · rechts "+V.ffr+"   |   übrige: links "+V.ll+" · rechts "+V.lr+"   |   vertikal "+V.va;}
["ffl","ffr","ll","lr","va"].forEach(function(k){var s=document.getElementById(k);
 set(k,+s.value);s.addEventListener("input",function(){set(k,+s.value);refresh();});});
refresh();
document.getElementById("reset").onclick=function(){var d={ffl:34,ffr:34,ll:34,lr:34,va:-240};
 Object.keys(d).forEach(function(k){var s=document.getElementById(k);s.value=d[k];set(k,d[k]);});refresh();};
document.getElementById("copy").onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(
 document.getElementById("code").textContent);this.textContent="kopiert ✓";var b=this;setTimeout(function(){b.textContent="Werte kopieren";},1200);};
</script>
</body></html>"""
HTML = HTML.replace("__BODY__", BODY)
open("/home/user/goeloggen/kerning.html", "w").write(HTML)
print("wrote kerning.html  (%d ligature SVGs inline)" % len(SV))

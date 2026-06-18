#!/usr/bin/env python3
# ligvorschau.html — VARIABLE ligatures from Philipp's real 3-master drawings.
# The baukasten gives ff/ffe/fi/fl/ft drawn at Leise/Klar/Laut. The lead-f and
# trailing letter are each point-compatible across the three weights, so the
# whole ligature interpolates per-point. A continuous weight slider drives both
# the running body text (variable webfont) and the inline ligatures together —
# Laut/Leise are now the actual hand-drawn forms, no longer a Näherung.
import os, sys, json, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

SVG = os.path.join(HERE, "..", "..", "assets", "entwuerfe", "ligatur-baukasten-ph.svg")
BASE_Y = {"Leise": 5359.5, "Klar": 859.5, "Laut": 3859.5}   # svg-y baseline per weight band
# Leise + Laut are drawn from individual letters and are point-compatible -> the
# two interpolation masters. Klar's merged drawing has one extra node, so the
# variable passes through Klar at the midpoint (the static Klar cut keeps the
# exact approved drawing). Anchors at the cut weights.
WEIGHT = {"Leise": 265, "Laut": 680}
KEYS = ["ff", "ffe", "fi", "fl", "ft"]
# component ids per (weight, ligature): [lead_f, trailing]
IDS = {
 "Klar":  {"ff":"r0-ff-standard","ffe":"r0-ff-wortende","fi":"r0-fi-weit","fl":"r0-fl","ft":"r0-ft"},
 "Laut":  {"ff":["r2-f","r2-f1"],"ffe":["r2-f2","r2-f3"],"fi":["r2-f6","__rect"],
           "fl":["r2-f4","r2-l"],"ft":["r2-f5","r2-t"]},
 "Leise": {"ff":["r3-f","r3-f1"],"ffe":["r3-f2","r3-f3"],"fi":["r3-f4","r3-dotlessi"],
           "fl":["r3-f5","r3-l"],"ft":["r3-f6","r3-t"]},
}
TRAIL_UNI = {"ff": 0x66, "ffe": 0x66, "fi": 0x131, "fl": 0x6C, "ft": 0x74}

# ---- parse baukasten ----
root = ET.parse(SVG).getroot(); elems = {}
def walk(e, gid=None):
    for c in e:
        i = c.get("id") or gid; tag = c.tag.split('}')[-1]
        if tag == "path" and c.get("d"):
            rp = RecordingPen(); parse_path(c.get("d"), rp); elems[i or "_a%d"%len(elems)] = rp.value
        elif tag == "rect":
            x=float(c.get("x")); y=float(c.get("y")); w=float(c.get("width")); h=float(c.get("height"))
            yb=y+h  # match the dotless-i path point order: bottom-left, bottom-right, top-right, top-left, close
            elems["__rect"] = [("moveTo",((x,yb),)),("lineTo",((x+w,yb),)),("lineTo",((x+w,y),)),
                               ("lineTo",((x,y),)),("lineTo",((x,yb),)),("closePath",())]
        walk(c, c.get("id") or gid)
walk(root)

def fy(value, base): return [(c, tuple((x, base-y) for x,y in p)) for c,p in value]
def minx(r): return min(x for c,p in r for x,y in p)
def maxx(r): return max(x for c,p in r for x,y in p)
def shift(r,dx): return [(c, tuple((x+dx,y) for x,y in p)) for c,p in r]
def subpaths(r):
    subs=[]; cur=[]
    for c,p in r:
        if c=="moveTo" and cur: subs.append(cur); cur=[]
        cur.append((c,p))
    if cur: subs.append(cur)
    return subs

# Klar reference: the trailing letter's overlap UNDER the lead-f bow. Keep that
# overlap (bow-tip minus trailing-left) constant across weights, so wider Laut
# forms don't drift apart — the trailing letter always tucks the same depth.
klar_off={}; klar_ov={}
for k in KEYS:
    r = fy(elems[IDS["Klar"][k]], BASE_Y["Klar"]); r = shift(r, -minx(r))
    subs = sorted(subpaths(r), key=minx); lead = subs[0]
    if len(subs)>1:
        tl = min(minx(s) for s in subs[1:])
        klar_off[k] = tl - minx(lead)
        klar_ov[k]  = maxx(lead) - tl          # bow-tip overlap (depth of tuck)
    else:
        klar_off[k] = 0; klar_ov[k] = 0

def parts_for(weight, k):
    base = BASE_Y[weight]
    if weight == "Klar":
        r = fy(elems[IDS["Klar"][k]], base); r = shift(r, -minx(r))
        subs = sorted(subpaths(r), key=minx)
        lead = subs[0]; trail = sum(subs[1:], [])
        return lead + trail                    # already composed by hand
    lid, tid = IDS[weight][k]
    lead = fy(elems[lid], base); lead = shift(lead, -minx(lead))
    trail = fy(elems[tid], base); trail = shift(trail, -minx(trail))
    trail = shift(trail, maxx(lead) - klar_ov[k])   # tuck under this weight's bow tip
    return lead + trail

# trailing RSB (nachabstand) from the Klar cut, constant across weights for preview
fK = TTFont(glob.glob(os.path.join(HERE, "input", "*-Klar.otf"))[0])
RSB = {}
for k in KEYS:
    r,a = grec(fK, TRAIL_UNI[k]); RSB[k] = round(a - max(x for c,p in r for x,y in p), 1)

# emit point-compatible masters: shared command list + per-weight coord arrays
LSB = 29
def encode(k):
    masters = {w: parts_for(w, k) for w in WEIGHT}
    # command signature (assert identical across weights)
    ref = parts_for("Leise", k)
    cmds = [(c, len(p)) for c,p in ref]
    out = {"cmds": [c for c,_ in ref]}
    for w in WEIGHT:
        rec = masters[w]
        assert [(c,len(p)) for c,p in rec] == cmds, (k, w)
        coords = []
        for c,p in rec:
            for (x,y) in p: coords += [round(x,1), round(y,1)]
        width = max(maxx(rec) for rec in [masters[w]])
        out[str(WEIGHT[w])] = {"c": coords, "adv": round(width + LSB + RSB[k], 1)}
    return out

DATA = {k: encode(k) for k in KEYS}

# ---- running-text markup ----
BOUND = set(" ,.;:!?—-–)„‑")
def esc(s): return s.replace("&","&amp;").replace("<","&lt;")
def markup(text):
    out=""; i=0; n=len(text)
    while i<n:
        if text[i:i+2]=="ff":
            nxt = text[i+2] if i+2<n else " "
            out += '<span class="lig" data-l="%s"></span>'%("ffe" if nxt in BOUND else "ff"); i+=2; continue
        if text[i:i+2] in ("fi","fl","ft"):
            out += '<span class="lig" data-l="%s"></span>'%text[i:i+2]; i+=2; continue
        out += esc(text[i]); i+=1
    return out
SAMPLE = ("Auffällige, fließende Schriftzüge: der Stoff, das Schiff, ein Pfiff, "
          "Koffer, schaffen, öffnen, die Auflage, das Pflaster, Grafik, "
          "sanfte Kraft, oft geprüft, fünf Briefe — das schafft Vertrauen.")
BODY = markup(SAMPLE)

HTML = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ligaturen variabel</title>
<style>
@font-face{font-family:"G Var";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Variabel-v2.4.1.woff2") format("woff2");font-weight:190 725;font-display:swap}
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 22px 70px}
h1{font-size:22px;margin:0 0 6px}.hint{color:#737a80;font-size:14px;margin:6px 0 14px}
.sw{display:flex;gap:8px;margin:0 0 8px;flex-wrap:wrap}
.sw button{font:inherit;font-size:14px;border:1px solid rgba(20,24,28,.2);background:#fff;border-radius:9px;padding:7px 15px;cursor:pointer}
.sw button.on{background:#23272b;color:#fff;border-color:#23272b}
.stage{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:14px;padding:30px 30px;margin:8px 0 12px}
.sample{font-family:"G Var";font-size:44px;line-height:1.6;color:#23272b}
.lig{display:inline-block;vertical-align:-0.25em}
.lig svg{height:1em;fill:currentColor}
.tool{max-width:520px;margin-top:8px}.tool label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
.tool b{font-variant-numeric:tabular-nums}
input[type=range]{width:100%}
.ticks{display:flex;justify-content:space-between;font-size:11px;color:#9aa0a6;margin-top:2px}
</style></head><body><div class="wrap">
<h1>Ligaturen variabel — deine drei Zeichnungen</h1>
<div class="hint">Leise, Klar und Laut sind jetzt <b>deine echten Zeichnungen</b> (aus dem Baukasten). Die Ligaturen werden <b>Punkt für Punkt interpoliert</b> und folgen dem Gewichtsregler — genau wie sie später variabel im Font sitzen. Brottext = Variable Font.</div>
<div class="sw" id="sw">
 <button data-w="265">Leise</button><button data-w="440" class="on">Klar</button><button data-w="680">Laut</button></div>
<div class="stage"><div class="sample" id="sample">__BODY__</div></div>
<div class="tool"><label>Gewicht <b><span id="v_w">440</span></b></label>
 <input type="range" id="s_w" min="190" max="725" value="440">
 <div class="ticks"><span>190 Flüstern</span><span>265 Leise</span><span>440 Klar</span><span>680 Laut</span><span>725 Schreien</span></div></div>
<div class="tool" style="margin-top:14px"><label>Schriftgrösse <b><span id="v_size">44</span> px</b></label><input type="range" id="s_size" min="16" max="100" value="44"></div>
</div>
<script>
var DATA=__DATA__, ANCH=[265,680], cur=440;
function lerp(a,b,t){return a+(b-a)*t;}
function coordsAt(g,w){
 var A=ANCH, lo=A[0], hi=A[A.length-1];
 if(w<=A[0]){lo=A[0];hi=A[1];}
 else if(w>=A[A.length-1]){lo=A[A.length-2];hi=A[A.length-1];}
 else{for(var i=0;i<A.length-1;i++){if(w>=A[i]&&w<=A[i+1]){lo=A[i];hi=A[i+1];break;}}}
 var t=(w-lo)/(hi-lo);
 var ca=g[lo].c, cb=g[hi].c, out=new Array(ca.length);
 for(var j=0;j<ca.length;j++) out[j]=lerp(ca[j],cb[j],t);
 var adv=lerp(g[lo].adv,g[hi].adv,t);
 return {c:out, adv:adv};
}
var BASE=750, LSB=29;
function pathD(cmds,coords){
 var d=[],k=0;
 function P(){var x=LSB+coords[k++], y=BASE-coords[k++]; return x.toFixed(1)+" "+y.toFixed(1);}
 for(var i=0;i<cmds.length;i++){var c=cmds[i];
  if(c=="moveTo")d.push("M"+P());
  else if(c=="lineTo")d.push("L"+P());
  else if(c=="curveTo")d.push("C"+P()+" "+P()+" "+P());
  else if(c=="qCurveTo"){d.push("Q"+P()+" "+P());}
  else if(c=="closePath")d.push("Z");}
 return d.join("");
}
function render(){
 var W=cur;
 document.getElementById("sample").style.fontVariationSettings="'wght' "+W;
 [].forEach.call(document.querySelectorAll(".lig"),function(s){
  var g=DATA[s.dataset.l], r=coordsAt(g,W), d=pathD(g.cmds,r.c);
  s.innerHTML='<svg viewBox="0 0 '+r.adv.toFixed(1)+' 1000" style="width:'+(r.adv/1000).toFixed(3)+'em"><path d="'+d+'"/></svg>';
 });
}
var sw=document.getElementById("s_w"), vw=document.getElementById("v_w");
function setW(w){cur=w;sw.value=w;vw.textContent=Math.round(w);
 [].forEach.call(document.querySelectorAll("#sw button"),function(b){b.classList.toggle("on",+b.dataset.w===w);});render();}
sw.addEventListener("input",function(){cur=+sw.value;vw.textContent=cur;
 [].forEach.call(document.querySelectorAll("#sw button"),function(b){b.classList.toggle("on",+b.dataset.w===cur);});render();});
[].forEach.call(document.querySelectorAll("#sw button"),function(b){b.addEventListener("click",function(){setW(+b.dataset.w);});});
var sz=document.getElementById("s_size");
sz.addEventListener("input",function(){document.getElementById("sample").style.fontSize=sz.value+"px";document.getElementById("v_size").textContent=sz.value;});
document.fonts&&document.fonts.ready.then(render);render();
</script></body></html>"""
HTML = HTML.replace("__BODY__", BODY).replace("__DATA__", json.dumps(DATA))
open("/home/user/goeloggen/ligvorschau.html","w").write(HTML)
print("wrote ligvorschau.html — variable from real masters (Leise+Laut)")
print("klar_off:", {k:round(v,1) for k,v in klar_off.items()})
print("advances Leise:", {k: DATA[k]["265"]["adv"] for k in KEYS})

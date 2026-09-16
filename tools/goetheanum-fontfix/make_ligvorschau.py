#!/usr/bin/env python3
# ligvorschau.html — full specimen of the finished f-ligatures:
#   (1) jede Ligatur einzeln, je Schnitt
#   (2) Varianten (ff wortintern vs ff Wortende) + Gewichtsvergleich
#   (3) im Fließtext, Brottext im passenden statischen Schnitt (gewichtsgleich)
# Sources: Laut = neu gezeichneter Baukasten (korrektes v2.5-Gewicht + Tuck),
#          Klar = zusammengeführte r0-Zeichnung, Leise = Einzelbuchstaben r3.
import os, sys, json, glob
import xml.etree.ElementTree as ET
HERE = "/home/user/goeloggen/tools/goetheanum-fontfix"; sys.path.insert(0, HERE)
from fontfix import grec
from fontTools.ttLib import TTFont
from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

REPO = "/home/user/goeloggen"
OLD = os.path.join(REPO, "assets", "entwuerfe", "ligatur-baukasten-ph.svg")
NEW = os.path.join(REPO, "assets", "entwuerfe", "laut-neu-baukasten-ph.svg")
KEYS = ["ff", "ffe", "fi", "fl", "ft"]
TRAIL_UNI = {"ff": 0x66, "ffe": 0x66, "fi": 0x131, "fl": 0x6C, "ft": 0x74}

def parse(path):
    root = ET.parse(path).getroot(); elems = {}; anon = []
    def walk(e, gid=None):
        for c in e:
            i = c.get("id") or gid; tag = c.tag.split('}')[-1]
            if tag == "path" and c.get("d"):
                rp = RecordingPen(); parse_path(c.get("d"), rp)
                rec = rp.value
                if i: elems[i] = (c.get("class"), rec)
                anon.append((c.get("class"), rec))
            walk(c, c.get("id") or gid)
    walk(root)
    return elems, anon

oldE, _ = parse(OLD)
_, newA = parse(NEW)

def fy(v, base): return [(c, tuple((x, base-y) for x,y in p)) for c,p in v]
def minx(r): return min(x for c,p in r for x,y in p)
def maxx(r): return max(x for c,p in r for x,y in p)
def shift(r,dx): return [(c, tuple((x+dx,y) for x,y in p)) for c,p in r]
def subpaths(r):
    out=[]; cur=[]
    for c,p in r:
        if c=="moveTo" and cur: out.append(cur); cur=[]
        cur.append((c,p))
    if cur: out.append(cur)
    return out

# ---------- Klar (r0 merged, with user tuck) ----------
KLAR_ID = {"ff":"r0-ff-standard","ffe":"r0-ff-wortende","fi":"r0-fi-weit","fl":"r0-fl","ft":"r0-ft"}
KLAR_BASE = 859.5
# Klar (r0 merged) carries Philipp's own composition (anlegen/verlängern/Distanz);
# Leise (r3) and the new Laut are likewise drawn at the intended distance. We keep
# the drawn relative positions at EVERY weight instead of imposing one tuck.
def klar_parts(k):
    rec = fy(oldE[KLAR_ID[k]][1], KLAR_BASE)
    subs = sorted(subpaths(rec), key=minx)
    return [subs[0]] + [sum(subs[1:], [])]      # lead, trailing (as drawn)

# ---------- Leise (r3 individual letters, keep Philipp's drawn distance) ----------
LEISE_ID = {"ff":["r3-f","r3-f1"],"ffe":["r3-f2","r3-f3"],"fi":["r3-f4","r3-dotlessi"],
            "fl":["r3-f5","r3-l"],"ft":["r3-f6","r3-t"]}
LEISE_BASE = 5359.5
def leise_parts(k):
    lid, tid = LEISE_ID[k]
    lead = fy(oldE[lid][1], LEISE_BASE); trail = fy(oldE[tid][1], LEISE_BASE)
    off = minx(lead)                                   # keep the drawn lead→trail distance
    return [shift(lead, -off), shift(trail, -off)]

# ---------- Laut (new baukasten, user weight + tuck) ----------
LAUT_BASE = 772.9
# black (st5) paths -> group into 5 columns by lead-f minx
blk = [fy(rec, LAUT_BASE) for cls, rec in newA if cls == "st5"]
blk.sort(key=minx)
# column boundaries (x of the lead): col0<1100, col1<2110, col2<3000, col3<3975, else col4
def colof(x):
    return 0 if x<1100 else 1 if x<2110 else 2 if x<3000 else 3 if x<3975 else 4
cols = {0:[],1:[],2:[],3:[],4:[]}
for v in blk: cols[colof(minx(v))].append(v)
laut_raw = {}
for idx,k in enumerate(KEYS):
    parts = sorted(cols[idx], key=minx)
    laut_raw[k] = [parts[0], sum(parts[1:], [])]   # lead, trailing (as drawn, keeps tuck)

def laut_parts(k): return laut_raw[k]

# ---------- assemble, normalize, advance ----------
CUTS = {"Leise": leise_parts, "Klar": klar_parts, "Laut": laut_parts}
CUTOTF = {n: TTFont(glob.glob(os.path.join(REPO, "assets","fonts","goetheanum","**","*v2.5-%s.otf"%n), recursive=True)[0]) for n in CUTS}
LSB = 29
def rsb(cut, k):
    r,a = grec(CUTOTF[cut], TRAIL_UNI[k]); return a - max(x for c,p in r for x,y in p)

def emit_inline(parts):
    gmin = min(minx(r) for r in parts)
    parts = [shift(r, -gmin) for r in parts]
    width = max(maxx(r) for r in parts)
    return parts, width

def pathd(parts):
    BASE=750; d=[]
    for rec in parts:
        for c,p in rec:
            Q=[(LSB+x, BASE-y) for x,y in p]
            if c=="moveTo": d.append("M%.1f %.1f"%Q[0])
            elif c=="lineTo": d.append("L%.1f %.1f"%Q[0])
            elif c=="curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f"%(Q[0]+Q[1]+Q[2]))
            elif c=="qCurveTo":
                for i in range(len(Q)-1): d.append("Q%.1f %.1f %.1f %.1f"%(Q[i]+Q[i+1]))
            elif c=="closePath": d.append("Z")
    return "".join(d)

DATA={}
for cut, fn in CUTS.items():
    DATA[cut]={}
    for k in KEYS:
        parts, width = emit_inline([list(x) for x in fn(k)])
        adv = width + LSB + rsb(cut, k)
        DATA[cut][k] = {"d": pathd(parts), "w": round(adv,1)}

# ---------- running text markup ----------
BOUND=set(" ,.;:!?—-–)„‑")
def esc(s): return s.replace("&","&amp;").replace("<","&lt;")
def markup(text):
    out="";i=0;n=len(text)
    while i<n:
        if text[i:i+2]=="ff":
            nxt=text[i+2] if i+2<n else " "
            out+='<span class="lig" data-l="%s"></span>'%("ffe" if nxt in BOUND else "ff");i+=2;continue
        if text[i:i+2] in ("fi","fl","ft"):
            out+='<span class="lig" data-l="%s"></span>'%text[i:i+2];i+=2;continue
        out+=esc(text[i]);i+=1
    return out
SAMPLE=("Auffällige, fließende Schriftzüge: der Stoff, das Schiff, ein Pfiff, "
        "Koffer, schaffen, öffnen, die Auflage, das Pflaster, Grafik, "
        "sanfte Kraft, oft geprüft, fünf Briefe — das schafft Vertrauen.")
BODY=markup(SAMPLE)
LABELS={"ff":"ff","ffe":"ff (Wortende)","fi":"fi","fl":"fl","ft":"ft"}

HTML="""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ligaturen — Werkschau</title>
<style>
@font-face{font-family:"G Leise";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.5-Leise.woff2") format("woff2");font-display:swap}
@font-face{font-family:"G Klar";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.5-Klar.woff2") format("woff2");font-display:swap}
@font-face{font-family:"G Laut";src:url("assets/fonts/goetheanum/Webfonts/woff2/Goetheanum-Schrift-v2.5-Laut.woff2") format("woff2");font-display:swap}
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.55 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:26px 22px 80px}
h1{font-size:23px;margin:0 0 4px}h2{font-size:17px;margin:34px 0 12px;border-top:1px solid rgba(20,24,28,.12);padding-top:20px}
.hint{color:#737a80;font-size:14px;margin:4px 0 12px}
.card{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:14px;padding:20px 22px;margin:0 0 14px}
.lig svg{fill:#23272b}
.solo{display:grid;grid-template-columns:repeat(5,1fr);gap:6px 10px;align-items:end;text-align:center}
.solo .h{font-size:12px;color:#9aa0a6}.solo .wn{font-size:12px;color:#737a80;text-align:left;align-self:center}
.solo .cell{height:110px;display:flex;align-items:flex-end;justify-content:center}
.solo .cell svg{height:92px}
.cmp{display:flex;gap:30px;align-items:flex-end;flex-wrap:wrap}
.cmp .g{display:flex;flex-direction:column;align-items:center;gap:6px}
.cmp .g svg{height:96px}.cmp .g .t{font-size:12px;color:#737a80}
.flow .sw{display:flex;gap:8px;margin:0 0 12px;flex-wrap:wrap}
.flow .sw button{font:inherit;font-size:14px;border:1px solid rgba(20,24,28,.2);background:#fff;border-radius:9px;padding:7px 15px;cursor:pointer}
.flow .sw button.on{background:#23272b;color:#fff;border-color:#23272b}
.sample{font-size:42px;line-height:1.6}
.sample .lig{display:inline-block;vertical-align:-0.25em}.sample .lig svg{height:1em}
.tool{max-width:420px;margin-top:14px}.tool label{display:flex;justify-content:space-between;font-size:13px;color:#3a3f44;margin-bottom:5px}
input[type=range]{width:100%}
</style></head><body><div class="wrap">
<h1>f-Ligaturen — Werkschau</h1>
<div class="hint">Alle fünf Ligaturen, wie sie geschnitten werden: <b>ff</b> (wortintern), <b>ff am Wortende</b> (gestreckt), <b>fi</b>, <b>fl</b>, <b>ft</b>. Leise/Klar/Laut sind deine Zeichnungen; Laut neu am korrekten v2.5-Gewicht. Brottext im passenden statischen Schnitt.</div>

<h2>1 · Jede Ligatur einzeln, je Schnitt</h2>
<div class="card"><div class="solo" id="solo"></div></div>

<h2>2 · Varianten &amp; Gewichtsvergleich</h2>
<div class="card"><div class="hint" style="margin-top:0">ff wortintern vs. ff am Wortende — je Schnitt direkt nebeneinander.</div>
<div class="cmp" id="cmpvar"></div></div>
<div class="card"><div class="hint" style="margin-top:0">Ein Schnitt, alle fünf — Rhythmus im Vergleich.</div>
<div class="cmp" id="cmprow"></div>
<div class="tool"><label>Schnitt</label>
<div class="flow"><div class="sw" id="rowsw"><button data-w="Leise">Leise</button><button data-w="Klar" class="on">Klar</button><button data-w="Laut">Laut</button></div></div></div></div>

<h2>3 · Im Fließtext</h2>
<div class="card flow">
<div class="sw" id="flowsw"><button data-w="Leise">Leise</button><button data-w="Klar" class="on">Klar</button><button data-w="Laut">Laut</button></div>
<div class="sample" id="sample">__BODY__</div>
<div class="tool"><label>Schriftgrösse <b><span id="vs">42</span> px</b></label><input type="range" id="sz" min="16" max="92" value="42"></div>
</div>
</div>
<script>
var DATA=__DATA__, KEYS=__KEYS__, LAB=__LAB__, CUTS=["Leise","Klar","Laut"], FAM={Leise:'"G Leise"',Klar:'"G Klar"',Laut:'"G Laut"'};
function svg(cut,k,h){var g=DATA[cut][k];return '<svg viewBox="0 0 '+g.w+' 1000" style="height:'+h+'"><path d="'+g.d+'"/></svg>';}
// section 1: solo grid
(function(){var el=document.getElementById("solo");var html='<div></div>';
 KEYS.forEach(function(k){html+='<div class="h">'+LAB[k]+'</div>';});
 CUTS.forEach(function(cut){html+='<div class="wn">'+cut+'</div>';
   KEYS.forEach(function(k){html+='<div class="cell">'+svg(cut,k,"92px")+'</div>';});});
 el.innerHTML=html;})();
// section 2a: ff vs ffe per cut
(function(){var el=document.getElementById("cmpvar");var html='';
 CUTS.forEach(function(cut){html+='<div class="g"><div style="display:flex;gap:10px;align-items:flex-end">'
  +svg(cut,"ff","84px")+svg(cut,"ffe","84px")+'</div><div class="t">'+cut+'</div></div>';});
 el.innerHTML=html;})();
// section 2b: all five in one cut
function renderRow(cut){var el=document.getElementById("cmprow");var html='';
 KEYS.forEach(function(k){html+='<div class="g">'+svg(cut,k,"96px")+'<div class="t">'+LAB[k]+'</div></div>';});
 el.innerHTML=html;}
renderRow("Klar");
document.querySelectorAll("#rowsw button").forEach(function(b){b.onclick=function(){
 document.querySelectorAll("#rowsw button").forEach(function(x){x.classList.remove("on");});b.classList.add("on");renderRow(b.dataset.w);};});
// section 3: flow
var cur="Klar";
function renderFlow(){document.getElementById("sample").style.fontFamily=FAM[cur];
 document.querySelectorAll("#sample .lig").forEach(function(s){s.innerHTML=svg(cur,s.dataset.l,"1em");});}
document.querySelectorAll("#flowsw button").forEach(function(b){b.onclick=function(){
 document.querySelectorAll("#flowsw button").forEach(function(x){x.classList.remove("on");});b.classList.add("on");cur=b.dataset.w;renderFlow();};});
var sz=document.getElementById("sz");sz.oninput=function(){document.getElementById("sample").style.fontSize=sz.value+"px";document.getElementById("vs").textContent=sz.value;};
document.fonts&&document.fonts.ready.then(renderFlow);renderFlow();
</script></body></html>"""
HTML=HTML.replace("__BODY__",BODY).replace("__DATA__",json.dumps(DATA)).replace("__KEYS__",json.dumps(KEYS)).replace("__LAB__",json.dumps(LABELS))
open(os.path.join(REPO,"ligvorschau.html"),"w").write(HTML)
print("wrote ligvorschau.html — Werkschau")
print("Laut advances:", {k:DATA["Laut"][k]["w"] for k in KEYS})

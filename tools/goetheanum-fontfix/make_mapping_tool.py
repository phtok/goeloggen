#!/usr/bin/env python3
# Generate zuordnen.html: every drawn variant as a clickable tile; assign a role
# (Default-ff / Wortend-ff / fi / fl / ft / fj / fk / ffi / ffl / fft / fff) per tile.
import os, sys
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

IDS = ["ff", "ff1", "ff2", "ff3", "ff4", "ff5", "ff6", "ff7", "ff8",
       "fi", "fi1", "fi2", "fl", "ft", "ft1", "fj", "fk"]
ROLES = ["—", "ff (wortintern)", "ff (Wortende)", "fi", "fl", "ft", "fj", "fk",
         "ffi", "ffl", "fft", "fff", "fb", "fh"]

def tile_svg(gid):
    el = find(gid)
    if el is None: return None
    ps = paths_of(el)
    if len(ps) < 2 and el in parent: ps = paths_of(parent[el])
    rp = RecordingPen()
    for d in ps: parse_path(d, rp)
    pts = [p for c, q in rp.value for p in q]
    if not pts: return None
    xs = [x for x, y in pts]; By = baseline_for(min(y for x, y in pts)); minx = min(xs)
    rel = [(c, tuple((x-minx, By-y) for x, y in q)) for c, q in rp.value]   # y-up, baseline 0
    ys = [y for c, q in rel for x, y in q]; ymax = max(ys); ymin = min(ys); w = max(xs)-minx
    pad = 90; H = (ymax-ymin) + 2*pad; top = ymax + pad
    d = []
    for c, q in rel:
        Q = [(x, top - y) for x, y in q]                    # flip to svg y-down
        if c == "moveTo": d.append("M%.1f %.1f" % Q[0])
        elif c == "lineTo": d.append("L%.1f %.1f" % Q[0])
        elif c == "curveTo": d.append("C%.1f %.1f %.1f %.1f %.1f %.1f" % (Q[0]+Q[1]+Q[2]))
        elif c == "qCurveTo":
            for i in range(len(Q)-1): d.append("Q%.1f %.1f %.1f %.1f" % (Q[i]+Q[i+1]))
        elif c == "closePath": d.append("Z")
    bl = top  # baseline svg-y
    return ('<svg viewBox="-30 0 %.0f %.0f" preserveAspectRatio="xMidYMid meet">'
            '<line x1="-30" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#e2ddd0" stroke-width="3"/>'
            '<path d="%s" fill="#23272b"/></svg>') % (w+60, H, bl, w+30, bl, "".join(d))

tiles = ""
for gid in IDS:
    sv = tile_svg(gid)
    if not sv: continue
    opts = "".join('<option value="%s">%s</option>' % (r, r) for r in ROLES)
    tiles += ('<div class="tile" data-id="%s"><div class="gl">%s</div>'
              '<div class="id">%s</div><select>%s</select></div>') % (gid, sv, gid, opts)

HTML = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ligaturen zuordnen</title>
<style>
body{margin:0;background:#faf8f4;color:#23272b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:26px 22px 80px}
h1{font-size:22px;margin:0 0 6px}.hint{color:#737a80;font-size:14px;margin:6px 0 18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px}
.tile{background:#fff;border:1px solid rgba(20,24,28,.12);border-radius:12px;padding:12px;text-align:center}
.tile.set{border-color:#a07a33;box-shadow:0 0 0 2px rgba(160,122,51,.2)}
.gl{height:130px;display:flex;align-items:center;justify-content:center}
.gl svg{height:130px;max-width:100%}
.id{font-size:12px;color:#9aa0a6;margin:6px 0 8px}
select{font:inherit;font-size:13px;width:100%;padding:6px;border-radius:8px;border:1px solid rgba(20,24,28,.18);background:#fff}
.sum{position:sticky;bottom:0;margin-top:22px;background:#fff;border:1px solid rgba(20,24,28,.14);border-radius:12px;padding:14px 16px}
.sum .code{font-family:ui-monospace,Menlo,monospace;font-size:13px;white-space:pre-wrap}
.btn{font:inherit;font-size:13px;border:1px solid rgba(20,24,28,.18);background:#fff;border-radius:8px;padding:7px 12px;cursor:pointer;margin-right:8px}
</style></head><body><div class="wrap">
<h1>Ligaturen zuordnen</h1>
<div class="hint">Jede deiner Zeichnungen als Kachel. Wähle pro Kachel die <b>Rolle</b> (z. B. ‹ff (Wortende)›). Unten entsteht die Zuordnung zum Kopieren — die schickst du mir, dann baue ich genau diese.</div>
<div class="grid">__TILES__</div>
<div class="sum"><div class="code" id="code">Noch nichts zugeordnet.</div>
<div style="margin-top:10px"><button class="btn" id="copy">Zuordnung kopieren</button><button class="btn" id="reset">zurücksetzen</button></div></div>
</div>
<script>
var tiles=[].slice.call(document.querySelectorAll(".tile"));
function refresh(){
 var lines=[];
 tiles.forEach(function(t){var sel=t.querySelector("select");var v=sel.value;
  t.classList.toggle("set", v!=="—");
  if(v!=="—") lines.push(v+"  =  "+t.dataset.id);});
 document.getElementById("code").textContent = lines.length? lines.join("\\n") : "Noch nichts zugeordnet.";
}
tiles.forEach(function(t){t.querySelector("select").addEventListener("change",refresh);});
document.getElementById("reset").onclick=function(){tiles.forEach(function(t){t.querySelector("select").value="—";});refresh();};
document.getElementById("copy").onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(document.getElementById("code").textContent);
 var b=this;b.textContent="kopiert ✓";setTimeout(function(){b.textContent="Zuordnung kopieren";},1200);};
refresh();
</script></body></html>"""
open("/home/user/goeloggen/zuordnen.html", "w").write(HTML.replace("__TILES__", tiles))
print("wrote zuordnen.html with %d tiles" % len(IDS))

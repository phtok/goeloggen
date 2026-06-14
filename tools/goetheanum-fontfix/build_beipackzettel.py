import cairosvg, os, re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib.instancer import instantiateVariableFont
FD="assets/fonts/goetheanum/Fonts/"; VF="assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.4.1.otf"
def L(p): ft=TTFont(p);return (ft,ft.getGlyphSet(),ft.getBestCmap(),ft["head"].unitsPerEm)
K=L(FD+"Goetheanum-Schrift-v2.4.1-Klar.otf"); LA=L(FD+"Goetheanum-Schrift-v2.4.1-Laut.otf"); LE=L(FD+"Goetheanum-Schrift-v2.4.1-Leise.otf")
def varL(w):
    ft=TTFont(VF); instantiateVariableFont(ft,{"wght":w},inplace=True); return (ft,ft.getGlyphSet(),ft.getBestCmap(),ft["head"].unitsPerEm)
IC=L(FD+"Goetheanum-Icons-v2.4.1.otf")
S=[]
def txt(F,s,size,x,y,fill="#23272b"):
    ft,gs,cmap,upm=F; sc=size/upm; cx=x
    for ch in s:
        gn=cmap.get(ord(ch))
        if not gn: cx+=size*0.3; continue
        p=SVGPathPen(gs); gs[gn].draw(p)
        d=p.getCommands()
        if d: S.append(f'<g transform="translate({cx:.2f},{y:.2f}) scale({sc:.5f},{-sc:.5f})"><path d="{d}" fill="{fill}"/></g>')
        cx+=gs[gn].width*sc
    return cx
def tw(F,string,size):
    ft,gs,cmap,upm=F; sc=size/upm; w=0
    for ch in string:
        gn=cmap.get(ord(ch)); w+= (gs[gn].width*sc) if gn else size*0.3
    return w
def rtxt(F,string,size,xr,y,fill):
    txt(F,string,size,xr-tw(F,string,size),y,fill)
def icon(slug,size,x,y):
    f=f"assets/fonts/goetheanum/Icons-Einzeldateien/svg/{slug}.svg"
    if not os.path.exists(f): return
    inner=open(f).read(); vb=re.search(r'viewBox="([^"]+)"',inner).group(1); path=re.search(r'(<path[^>]+/>)',inner).group(1)
    S.append(f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}">{path}</svg>')

W,H=842,595; M=48
S.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>')
# Title
txt(LA,"Goetheanum Schriften",30,M,76,"#23272b")
txt(K,"Hausschrift · Version 2.3 · reparierte & optimierte Fassung",10.5,M,95,"#a07a33")
S.append(f'<line x1="{M}" y1="110" x2="{W-M}" y2="110" stroke="rgba(20,24,28,.12)"/>')

# left column cards (3 statics)
LX=M; LW=360
def card(x,y,w,h):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" stroke="rgba(20,24,28,.14)"/>')
cards=[("Klar",K,"‹Goetheanum Kommunikation im Alltag›","Standard: Korrespondenz, Formulare, Lauftext.","Regular"),
       ("Laut",LA,"‹Goetheanum Programm Heute›","Titel, Wegleitung, Signaletik, Hervorhebung.","Fett · Cmd+B"),
       ("Leise",LE,"‹Goetheanum Kultur und Dialog›","Leise Auszeichnung – nicht für Fließtext-Mengen.","Kursiv · Cmd+I")]
y=128
for nm,F,sample,role,off in cards:
    card(LX,y,LW,118)
    txt(K,nm,12,LX+16,y+26,"#23272b"); rtxt(K,"Office · "+off,9.5,LX+LW-16,y+26,"#a07a33")
    txt(F,sample,21,LX+16,y+66,"#23272b")
    txt(K,role,10,LX+16,y+92,"#737a80")
    y+=130

# right column: Variable + Icons
RX=M+LW+22; RW=360
# Variable card
vy=128; vh=200
card(RX,vy,RW,vh)
txt(K,"Variable Font",12,RX+16,vy+26,"#23272b"); rtxt(K,"Achse 190–725",9.5,RX+RW-16,vy+26,"#a07a33")
for i,(w,lab) in enumerate([(190,"Flüstern"),(280,"Leise"),(450,"Klar"),(600,"Laut"),(725,"Schreien")]):
    yy=vy+58+i*27
    txt(varL(w),"Goetheanum flexibel",16,RX+16,yy,"#23272b")
    rtxt(K,lab,8.5,RX+RW-16,yy,"#9aa1a7")
txt(K,"Stufenlos. Die Extreme Flüstern & Schreien nur hier –",9.5,RX+16,vy+vh-22,"#737a80")
txt(K,"der Grafik vorbehalten. Nur für Profis.",9.5,RX+16,vy+vh-9,"#737a80")
# Icons card
iy=vy+vh+12; ih=118
card(RX,iy,RW,ih)
txt(K,"Icons",12,RX+16,iy+26,"#23272b"); rtxt(K,"81 Piktogramme",9.5,RX+RW-16,iy+26,"#a07a33")
demo=["goetheanum-badge","garderobe","wlan","treppe","wc-rollstuhl","keine-hunde","pfeil-hoch","kompass-1"]
for i,sl in enumerate(demo):
    icon(sl,30,RX+16+i*42,iy+42)
txt(K,"Tastatur-Belegung siehe Seite 2–4. Einzeln als SVG/PNG/PDF",9.5,RX+16,iy+ih-14,"#737a80")

# footer
S.append(f'<line x1="{M}" y1="540" x2="{W-M}" y2="540" stroke="rgba(20,24,28,.10)"/>')
txt(K,"Goetheanum Schriften Version 2.4.1 · Goetheanum Kommunikation, basierend auf Titillium (Urbino, SIL OFL).",9,M,557,"#737a80")
txt(K,"Reparatur & Optimierung 2026. Piktogramme und Icons u. a. von Severin Geißler und Philipp Tok.",9,M,570,"#737a80")
S.append("</svg>")
open("/tmp/beipack_p1.svg","w").write("".join(S))
cairosvg.svg2pdf(url="/tmp/beipack_p1.svg",write_to="/tmp/beipack_p1.pdf")
cairosvg.svg2png(url="/tmp/beipack_p1.svg",write_to="/tmp/beipack_p1.png",output_width=1100)
print("page1 rendered")

# splice: new page1 + original pages 2-4
from pypdf import PdfReader, PdfWriter
new=PdfReader("/tmp/beipack_p1.pdf"); orig=PdfReader("assets/fonts/goetheanum/Beipackzettel-Goetheanum-Schriften.pdf")
w=PdfWriter(); w.add_page(new.pages[0])
for i in (1,2,3): w.add_page(orig.pages[i])
with open("/tmp/Beipackzettel-neu.pdf","wb") as f: w.write(f)
print("merged ->",len(PdfReader('/tmp/Beipackzettel-neu.pdf').pages),"Seiten")

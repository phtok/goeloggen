import cairosvg, os, re
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib.instancer import instantiateVariableFont
FD="assets/fonts/goetheanum/Fonts/"; VF="assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.7.otf"
def L(p): ft=TTFont(p);return (ft,ft.getGlyphSet(),ft.getBestCmap(),ft["head"].unitsPerEm)
KP=FD+"Goetheanum-Schrift-v2.7-Klar.otf"; LAP=FD+"Goetheanum-Schrift-v2.7-Laut.otf"; LEP=FD+"Goetheanum-Schrift-v2.7-Leise.otf"; DEP=FD+"Goetheanum-Schrift-v2.7-Deutlich.otf"; RUP=FD+"Goetheanum-Schrift-v2.7-Ruhig.otf"
K=L(KP); LA=L(LAP); LE=L(LEP); D=L(DEP); RU=L(RUP)
def varL(w):
    ft=TTFont(VF); instantiateVariableFont(ft,{"wght":w},inplace=True); return (ft,ft.getGlyphSet(),ft.getBestCmap(),ft["head"].unitsPerEm)
IC=L(FD+"Goetheanum-Icons-v2.7.otf")
# HarfBuzz fonts for real shaping (ligatures + OT features)
def hbfont(path):
    blob=hb.Blob.from_file_path(path); face=hb.Face(blob); return hb.Font(face)
HB={"Klar":hbfont(KP),"Laut":hbfont(LAP),"Leise":hbfont(LEP)}
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
def shape(F,hbf,s,size,feats):
    # returns (glyph-draw list relative to x=0, total advance) at given size
    ft,gs,cmap,upm=F; sc=size/upm
    buf=hb.Buffer(); buf.add_str(s); buf.guess_segment_properties()
    hb.shape(hbf,buf,feats); cx=0.0; out=[]
    for inf,pos in zip(buf.glyph_infos,buf.glyph_positions):
        gn=ft.getGlyphName(inf.codepoint); p=SVGPathPen(gs); gs[gn].draw(p); d=p.getCommands()
        if d: out.append((cx+pos.x_offset*sc, pos.y_offset*sc, d))
        cx+=pos.x_advance*sc
    return out,cx
def stxt(F,hbf,s,size,x,y,feats=None,fill="#23272b"):
    parts,adv=shape(F,hbf,s,size,feats or {}); sc=size/(F[3])
    for gx,gy,d in parts:
        S.append(f'<g transform="translate({x+gx:.2f},{y-gy:.2f}) scale({sc:.5f},{-sc:.5f})"><path d="{d}" fill="{fill}"/></g>')
    return x+adv
def icon(slug,size,x,y):
    f=f"assets/fonts/goetheanum/Icons-Einzeldateien/svg/{slug}.svg"
    if not os.path.exists(f): return
    inner=open(f).read(); vb=re.search(r'viewBox="([^"]+)"',inner).group(1); path=re.search(r'(<path[^>]+/>)',inner).group(1)
    S.append(f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}">{path}</svg>')

W,H=842,595; M=48
S.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>')
# Title
txt(LA,"Goetheanum Schriften",30,M,76,"#23272b")
txt(K,"Die Hausschrift der Goetheanum Kommunikation",10.5,M,95,"#a07a33")
S.append(f'<line x1="{M}" y1="110" x2="{W-M}" y2="110" stroke="rgba(20,24,28,.12)"/>')

# left column cards (4 statics)
LX=M; LW=360
def card(x,y,w,h):
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="none" stroke="rgba(20,24,28,.14)"/>')
# fünf Schnitte in der Leiter-Ordnung: Leise · Ruhig · Klar · Deutlich · Laut
cards=[("Leise",LE,"‹Goetheanum Kultur und Dialog›","Leise Auszeichnung – nicht für Fließtext-Mengen.","Office · Cmd+I"),
       ("Ruhig",RU,"‹Goetheanum Lesestimme im Text›","Ruhiger Lese- und Lauftext – die Buch-Zwischenstimme.","Lesetext · 350"),
       ("Klar",K,"‹Goetheanum Kommunikation im Alltag›","Standard: Korrespondenz, Formulare, Lauftext.","Office · Regular"),
       ("Deutlich",D,"‹Goetheanum Programm Heute›","Titel und Header – die ruhige Auszeichnung.","Titel · 580"),
       ("Laut",LA,"‹Goetheanum Achtung Hinweis›","Inline-Fett, Hervorhebung, Signaletik.","Office · Cmd+B")]
y=128
for nm,F,sample,role,off in cards:
    card(LX,y,LW,70)
    txt(K,nm,11.5,LX+16,y+20,"#23272b"); rtxt(K,off,9,LX+LW-16,y+20,"#a07a33")
    txt(F,sample,17,LX+16,y+48,"#23272b")
    txt(K,role,9,LX+16,y+63,"#737a80")
    y+=80

# right column: Variable + Icons
RX=M+LW+22; RW=360
# Variable card — größer, mehr Luft zwischen den Schnitten
vy=128; vh=250
card(RX,vy,RW,vh)
txt(K,"Variable Font",12,RX+16,vy+26,"#23272b"); rtxt(K,"Achse 190–725",9.5,RX+RW-16,vy+26,"#a07a33")
for i,(w,lab) in enumerate([(190,"Flüstern"),(280,"Leise"),(365,"Ruhig"),(450,"Klar"),(525,"Deutlich"),(600,"Laut"),(725,"Schreien")]):
    yy=vy+58+i*26
    txt(varL(w),"Goetheanum flexibel",15,RX+16,yy,"#23272b")
    rtxt(K,lab,8.5,RX+RW-16,yy,"#9aa1a7")
txt(K,"Sieben benannte Schnitte, stufenlos von Flüstern bis Schreien.",9.5,RX+16,vy+vh-14,"#737a80")
# Icons card — unten bündig mit der Leise-Box (y=506)
iy=vy+vh+12; ih=116
card(RX,iy,RW,ih)
txt(K,"Icons",12,RX+16,iy+26,"#23272b"); rtxt(K,"81 Piktogramme",9.5,RX+RW-16,iy+26,"#a07a33")
demo=["goetheanum-badge","garderobe","wlan","treppe","wc-rollstuhl","keine-hunde","pfeil-hoch","kompass-1"]
for i,sl in enumerate(demo):
    icon(sl,30,RX+16+i*42,iy+44)
txt(K,"Tastatur-Belegung siehe Seite 3–5. Einzeln als SVG/PNG/PDF",9.5,RX+16,iy+ih-14,"#737a80")

# footer
S.append(f'<line x1="{M}" y1="540" x2="{W-M}" y2="540" stroke="rgba(20,24,28,.10)"/>')
txt(K,"Goetheanum Schriften Version 2.7 · Goetheanum Kommunikation, basierend auf Titillium (Urbino, SIL OFL).",9,M,557,"#737a80")
txt(K,"Ausbau & Optimierung 2026 durch Philipp Tok. Piktogramme und Icons u. a. von Severin Geißler und Philipp Tok.",9,M,570,"#737a80")
S.append("</svg>")
open("/tmp/beipack_p1.svg","w").write("".join(S))
cairosvg.svg2pdf(url="/tmp/beipack_p1.svg",write_to="/tmp/beipack_p1.pdf")
cairosvg.svg2png(url="/tmp/beipack_p1.svg",write_to="/tmp/beipack_p1.png",output_width=1100)
print("page1 rendered")

# ============================ PAGE 2 — Neu in 2.6 ============================
S=[]
S.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#ffffff"/>')
txt(LA,"Ligaturen & Sonderzeichen",30,M,76,"#23272b")
txt(K,"In den Schnitten Leise, Ruhig, Klar, Deutlich und Laut",10.5,M,95,"#a07a33")
S.append(f'<line x1="{M}" y1="110" x2="{W-M}" y2="110" stroke="rgba(20,24,28,.12)"/>')

# --- left: f-Ligaturen ---
LX=M; LW=360; ly=128; lh=300
card(LX,ly,LW,lh)
txt(K,"f-Ligaturen",12,LX+16,ly+26,"#23272b"); rtxt(K,"liga · calt",9.5,LX+LW-16,ly+26,"#a07a33")
# the four ligatures, large, shaped individually (liga on)
cx=LX+18
for lg in ["ff","fi","fl","ft"]:
    cx=stxt(K,HB["Klar"],lg,40,cx,ly+82,{"liga":True}); cx+=22
txt(K,"ff   fi   fl   ft — automatisch beim Tippen",9,LX+18,ly+104,"#9aa1a7")
txt(K,"im Wort",9,LX+18,ly+140,"#737a80")
stxt(K,HB["Klar"],"schaffen · Auflage · Grafik",21,LX+18,ly+166,{"liga":True,"calt":True})
txt(K,"am Wortende (calt schwingt über)",9,LX+18,ly+200,"#737a80")
stxt(K,HB["Klar"],"der Stoff, das Schiff, ein Pfiff.",21,LX+18,ly+226,{"liga":True,"calt":True})
txt(K,"Standard-Ligaturen, automatisch aktiv. In InDesign:",9,LX+18,ly+264,"#737a80")
txt(K,"OpenType › Ligaturen. Office setzt sie selbst.",9,LX+18,ly+278,"#737a80")

# --- right: Sonderzeichen (4 Reihen, luftig; Label weit über der Zeile) ---
RX=M+LW+22; RW=360; ry=128; rh=300
card(RX,ry,RW,rh)
txt(K,"Sonderzeichen",12,RX+16,ry+26,"#23272b"); rtxt(K,"Maße · Ziffern",9.5,RX+RW-16,ry+26,"#a07a33")
def row(yy,label,draw):
    txt(K,label,9,RX+18,yy-22,"#9aa1a7"); draw(yy)
def eszline(y):
    cx=txt(K,"STRASSE",18,RX+18,y,"#23272b")
    cx=txt(K,"  →  ",13,cx,y,"#a07a33")
    txt(K,"STRAẞE",18,cx,y,"#23272b")
row(ry+68,"Versaleszett ẞ (U+1E9E) — für den Versalsatz",eszline)
row(ry+124,"Prime & Doppelprime — Fuß/Zoll, Bogenminute (kein Apostroph)",
    lambda y: txt(K,"47° 32′ 18″  ·  5′ 11″  ·  f′(x)",19,RX+18,y,"#23272b"))
def zline(y):
    cx=txt(K,"0,75 kg · 0761",18,RX+18,y,"#23272b")
    cx=txt(K,"  →  ",13,cx,y,"#a07a33")
    stxt(K,HB["Klar"],"0,75 kg · 0761",18,cx,y,{"zero":True},"#23272b")
row(ry+180,"Schlummernde 0 (zero) — gegen Verwechslung mit O",zline)
row(ry+236,"Kurzziffern (onum) — Mediävalziffern im Fließtext",
    lambda y: stxt(K,HB["Klar"],"0123456789 · im Jahr 1923",18,RX+18,y,{"onum":True},"#23272b"))
row(ry+292,"Kapitälchen (smcp / c2sc)",
    lambda y: stxt(K,HB["Klar"],"Goetheanum Dornach",18,RX+18,y,{"smcp":True},"#23272b"))

# --- bottom: Strichvergleich (volle Breite) ---
sy=440; sh=90
card(M,sy,W-2*M,sh)
txt(K,"Striche",12,M+16,sy+24,"#23272b"); rtxt(K,"vom Bindestrich bis zum Geviert",9.5,W-M-16,sy+24,"#a07a33")
strokes=[("Bindestrich  -","blau-grün, Schiff-fahrt",lambda y,x: txt(K,"blau-grün, Schiff-fahrt",16,x,y,"#23272b")),
         ("Halbgeviert  –","Seiten 12–18",lambda y,x: txt(K,"Seiten 12–18",16,x,y,"#23272b")),
         ("Geviert  —","das Wort — der Gedanke",lambda y,x: txt(K,"das Wort — der Gedanke",16,x,y,"#23272b")),
         ("Ziffernstrich  ‒","1914‒1918",lambda y,x: stxt(K,HB["Klar"],"1914‒1918",16,x,y,{},"#23272b"))]
cw=(W-2*M)/4
for i,(lab,_,dr) in enumerate(strokes):
    x=M+16+i*cw
    txt(K,lab,9,x,sy+48,"#9aa1a7"); dr(sy+74,x)

# footer
S.append(f'<line x1="{M}" y1="548" x2="{W-M}" y2="548" stroke="rgba(20,24,28,.10)"/>')
txt(K,"Ziffern proportional im Satz, tabellarisch (gleiche Breiten) über tnum. Sonderzeichen über die Glyphentabelle. Ligaturen & Kapitälchen über OpenType, Ligaturen überall Standard.",9,M,563,"#737a80")
txt(K,"Numero-Zeichen bewusst weggelassen — im deutschen Satz gilt „Nr.“.",9,M,576,"#737a80")
S.append("</svg>")
open("/tmp/beipack_p2.svg","w").write("".join(S))
cairosvg.svg2pdf(url="/tmp/beipack_p2.svg",write_to="/tmp/beipack_p2.pdf")
cairosvg.svg2png(url="/tmp/beipack_p2.svg",write_to="/tmp/beipack_p2.png",output_width=1100)
print("page2 rendered")

# splice: new page1 + new page2 + pristine icon pages (3 Seiten, idempotente Quelle)
from pypdf import PdfReader, PdfWriter
p1=PdfReader("/tmp/beipack_p1.pdf"); p2=PdfReader("/tmp/beipack_p2.pdf")
icons=PdfReader("tools/goetheanum-fontfix/beipack_icon_pages.pdf")
w=PdfWriter(); w.add_page(p1.pages[0]); w.add_page(p2.pages[0])
for pg in icons.pages: w.add_page(pg)
out="assets/fonts/goetheanum/Beipackzettel-Goetheanum-Schriften.pdf"
with open(out,"wb") as f: w.write(f)
print("merged ->",len(PdfReader(out).pages),"Seiten ->",out)

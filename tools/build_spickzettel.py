#!/usr/bin/env python3
"""Druckbarer A4-Spickzettel (Kurzreferenz) aus den Goetheanum-Schriften."""
import cairosvg, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
FD="assets/fonts/goetheanum/Fonts/"
def L(p): ft=TTFont(p);return (ft,ft.getGlyphSet(),ft.getBestCmap(),ft["head"].unitsPerEm)
K=L(FD+"Goetheanum-Schrift-v2.4.1-Klar.otf"); LA=L(FD+"Goetheanum-Schrift-v2.4.1-Laut.otf"); LE=L(FD+"Goetheanum-Schrift-v2.4.1-Leise.otf")
S=[]
def txt(F,s,size,x,y,fill="#23272b"):
    ft,gs,cmap,upm=F; sc=size/upm; cx=x
    for ch in s:
        gn=cmap.get(ord(ch))
        if not gn: cx+=size*0.32; continue
        p=SVGPathPen(gs); gs[gn].draw(p); d=p.getCommands()
        if d: S.append(f'<g transform="translate({cx:.2f},{y:.2f}) scale({sc:.5f},{-sc:.5f})"><path d="{d}" fill="{fill}"/></g>')
        cx+=gs[gn].width*sc
    return cx
W,H=595,842; M=54  # A4 hoch (pt)
S.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>')
txt(LA,"Spickzettel",30,M,84,"#23272b")
txt(K,"Goetheanum Typografie · Kurzreferenz · zum Danebenlegen",11,M,104,"#a07a33")
S.append(f'<line x1="{M}" y1="120" x2="{W-M}" y2="120" stroke="rgba(20,24,28,.14)"/>')
# Spalten
cF, cN, cY = M, M+150, M+330
txt(K,"Fall",11,cF,150,"#737a80"); txt(K,"so nicht",11,cN,150,"#b3433c"); txt(K,"so",11,cY,150,"#3f8f5f")
rows=[("Zitat",'"so"',"‹so›"),("Apostroph","Mike's","Mike’s"),("Gedankenstrich","Ja - sofort","Ja – sofort"),
      ("Spanne","10 - 12 Uhr","10–12 Uhr"),("Abkürzung","z.B.","z. B."),("Einheit","10kg · 10%","10 kg · 10 %"),
      ("Tausender","1.000.000","1 000 000"),("(aber vierstellig)","1'318","1318"),
      ("Auslassung","...","…"),("mal","4x5","4 × 5"),("Uhrzeit","09:30 Uhr","9.30 Uhr"),
      ("Datum","11.06.2026","11. Juni 2026"),("Betonung","u n t e r","fett (Laut)"),("Minus","-5 Grad","−5 Grad")]
y=180
for fall,no,yes in rows:
    S.append(f'<line x1="{M}" y1="{y+9}" x2="{W-M}" y2="{y+9}" stroke="rgba(20,24,28,.06)"/>')
    txt(K,fall,12.5,cF,y,"#737a80")
    txt(K,no,13.5,cN,y,"#b3433c")
    (txt(LA,"fett",13.5,cY,y,"#23272b") if yes.startswith("fett") else txt(K,yes,13.5,cY,y,"#23272b"))
    y+=34
S.append(f'<line x1="{M}" y1="{y+6}" x2="{W-M}" y2="{y+6}" stroke="rgba(20,24,28,.14)"/>')
txt(K,"Hervorhebung = Laut (Cmd+B) · Nebenstimme = Leise (Cmd+I) · ein Merkmal je Auszeichnung.",10.5,M,y+30,"#737a80")
txt(K,"Mass: 45–75 Zeichen je Zeile (≈ 9 Wörter). Anführung ‹…› nach aussen. Zahlen nach Bundeskanzlei/SNB.",10.5,M,y+46,"#737a80")
txt(K,"Goetheanum Typografie · typografie.html · maschinenlesbar: typo-regeln.yaml",9.5,M,H-44,"#9aa1a7")
S.append("</svg>")
open("/tmp/spick.svg","w").write("".join(S))
out="assets/typografie/Spickzettel-Goetheanum-Typografie.pdf"
cairosvg.svg2pdf(url="/tmp/spick.svg",write_to=out)
cairosvg.svg2png(url="/tmp/spick.svg",write_to="/tmp/spick.png",output_width=620)
print("PDF:",out)

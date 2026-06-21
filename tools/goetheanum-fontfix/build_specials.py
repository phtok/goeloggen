#!/usr/bin/env python3
# v2.5 special characters, constructed weight-matched from each cut's own glyphs:
#   prime U+2032, doublePrime U+2033 (slanted wedges, cut stem),
#   figureDash U+2012 (cut endash bar at figure width),
#   numero U+2116 (cut N + geometric superior ring + bar),
#   zero.slash + 'zero' feature (cut 0 + diagonal slash).
import os, sys, glob, re, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontfix import grec, _charstring
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
K = 0.5522847498  # circle bezier

def mnx(r): return min(x for c,p in r for x,y in p)
def mxx(r): return max(x for c,p in r for x,y in p)
def mny(r): return min(y for c,p in r for x,y in p)
def mxy(r): return max(y for c,p in r for x,y in p)
def sh(r,dx,dy=0): return [(c, tuple((x+dx,y+dy) for x,y in p)) for c,p in r]

def rect(x0,y0,x1,y1):
    return [("moveTo",((x0,y0),)),("lineTo",((x1,y0),)),("lineTo",((x1,y1),)),("lineTo",((x0,y1),)),("closePath",())]
def para(x0,y0,x1,y1,slant):
    # slanted bar: bottom edge y0, top edge y1, shifted right by slant at top
    return [("moveTo",((x0,y0),)),("lineTo",((x1,y0),)),("lineTo",((x1+slant,y1),)),("lineTo",((x0+slant,y1),)),("closePath",())]

# ring quarter-cubics (cw=outer, ccw=inner counter)
def circ(cx,cy,r,cw=True):
    a=K*r
    if cw:
        return [("moveTo",((cx, cy+r),)),
                ("curveTo",((cx+a,cy+r),(cx+r,cy+a),(cx+r,cy))),
                ("curveTo",((cx+r,cy-a),(cx+a,cy-r),(cx,cy-r))),
                ("curveTo",((cx-a,cy-r),(cx-r,cy-a),(cx-r,cy))),
                ("curveTo",((cx-r,cy+a),(cx-a,cy+r),(cx,cy+r))),
                ("closePath",())]
    else:
        return [("moveTo",((cx, cy+r),)),
                ("curveTo",((cx-a,cy+r),(cx-r,cy+a),(cx-r,cy))),
                ("curveTo",((cx-r,cy-a),(cx-a,cy-r),(cx,cy-r))),
                ("curveTo",((cx+a,cy-r),(cx+r,cy-a),(cx+r,cy))),
                ("curveTo",((cx+r,cy+a),(cx+a,cy+r),(cx,cy+r))),
                ("closePath",())]

def build_specials(ft):
    cmap=ft.getBestCmap()
    rI,_=grec(ft,0x49); stem=mxx(rI)-mnx(rI); cap=mxy(rI)
    r0,a0=grec(ft,0x30); digitW=a0
    rd,_=grec(ft,0x2013); d0=mny(rd); d1=mxy(rd); dth=d1-d0   # endash bar thickness & y
    xh=500
    out={}
    # prime / doppelprime: the schrifteigene quoteright (raised comma) — gewichts-
    # richtig, an der Versalhöhe, geneigt. Kurz, kein langer Strich.
    rq, aq = grec(ft, 0x2019)
    qx0 = mnx(rq); qx1 = mxx(rq); qw = qx1 - qx0
    sb = stem * 0.42
    p1 = sh(rq, sb - qx0)
    padv = qw + 2*sb
    out["prime"] = (0x2032, p1, int(round(padv)), int(round(sb)))
    gap = stem * 0.55
    dp = p1 + sh(p1, qw + gap)
    out["doubleprime"] = (0x2033, dp, int(round(qw + gap + padv)), int(round(sb)))
    # figure dash: bar thickness=endash, width=digitW; Seitenrand ~ En-Dash (62),
    # nicht doppelt so weit wie eine Ziffer (sonst wirkt die Lücke zu groß).
    barw=digitW*0.78; x0=(digitW-barw)/2
    out["figuredash"]=(0x2012, rect(x0,d0,x0+barw,d1), digitW, int(x0))
    # zero.slash: cut 0 + diagonal slash, ENDING INSIDE the zero (kein Überstand)
    z0,za=grec(ft,0x30); zx0=mnx(z0); zx1=mxx(z0); zy0=mny(z0); zy1=mxy(z0)
    zh=zy1-zy0; cxz=(zx0+zx1)/2
    yA=zy0+zh*0.13; yB=zy1-zh*0.13               # inset within the zero
    bw=stem*0.92; sl=(yB-yA)*0.42
    bx=cxz - sl/2 - bw/2
    slashc=[("moveTo",((bx,yA),)),("lineTo",((bx+bw,yA),)),
            ("lineTo",((bx+bw+sl,yB),)),("lineTo",((bx+sl,yB),)),("closePath",())]
    out["zeroslash"]=(None, list(z0)+slashc, za, ft["hmtx"][cmap[0x30]][1])
    # numero: cut N (cap) + superior geometric ring + underline bar
    rN,aN=grec(ft,0x4E); Nx0=mnx(rN); Nx1=mxx(rN)
    N=list(rN)
    rr=(cap)*0.235                       # superior ring outer radius
    ring_th=stem*0.92
    cxr=Nx1+ rr + stem*0.7
    cyr=cap-rr
    ring=circ(cxr,cyr,rr,True)+circ(cxr,cyr,rr-ring_th,False)
    bar_y0=cyr-rr-stem*1.15; bar_y1=bar_y0+dth
    bar=rect(cxr-rr, bar_y0, cxr+rr, bar_y1)
    num=N+ring+bar
    nadv=cxr+rr+stem*0.7
    out["numero"]=(0x2116, num, int(round(nadv)), int(mnx(N)))
    return out

def add_glyph(ft, recv, adv, lsb, uni=None):
    cff=ft["CFF "].cff; td=cff[cff.fontNames[0]]
    cs=_charstring(ft, recv, adv)
    cids=[int(n[3:]) for n in td.charset if re.fullmatch(r"cid\d+",n)]
    name="cid%05d"%(max(cids)+1)
    td.CharStrings.charStringsIndex.append(cs); td.CharStrings.charStrings[name]=len(td.CharStrings.charStringsIndex)-1
    td.charset.append(name)
    if hasattr(td,"FDSelect"): td.FDSelect.append(0)
    ft["hmtx"].metrics[name]=(int(round(adv)), int(round(lsb)))
    ft.setGlyphOrder(list(td.charset))
    if uni is not None:
        for t in ft["cmap"].tables: t.cmap[uni]=name
    return name

if __name__=="__main__":
    import cairosvg
    rows=[]
    for cut in ["Leise","Klar","Laut"]:
        p=glob.glob(os.path.join(REPO,"assets/fonts/goetheanum/**/*v2.4.1-%s.otf"%cut),recursive=True)[0]
        ft=TTFont(p); sp=build_specials(ft)
        rows.append((cut, sp))
    # proof render
    def d_of(recv,ox,oy,sc):
        d=[]
        for c,p in recv:
            Q=[(ox+x*sc, oy-y*sc) for x,y in p]
            if c=="moveTo":d.append("M%.1f %.1f"%Q[0])
            elif c=="lineTo":d.append("L%.1f %.1f"%Q[0])
            elif c=="curveTo":d.append("C%.1f %.1f %.1f %.1f %.1f %.1f"%(Q[0]+Q[1]+Q[2]))
            elif c=="closePath":d.append("Z")
        return "".join(d)
    order=["prime","doubleprime","figuredash","zeroslash","numero"]
    lab={"prime":"′","doubleprime":"″","figuredash":"‒","zeroslash":"0̸","numero":"№"}
    CW=300;CH=300;sc=0.20
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">'%(CW*5,CH*3+30),'<rect width="100%" height="100%" fill="#faf8f4"/>']
    for ri,(cut,sp) in enumerate(rows):
        oy0=ri*CH+30
        svg.append('<text x="8" y="%d" font-size="15" font-family="Helvetica" fill="#23272b">%s</text>'%(oy0+16,cut))
        for ci,key in enumerate(order):
            uni,recv,adv,lsb=sp[key]; ox=ci*CW+40; by=oy0+200
            svg.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#cdd2d6"/>'%(ox-10,by,ox+250,by))
            if ri==0: svg.append('<text x="%d" y="20" font-size="13" font-family="Helvetica" fill="#9aa0a6">%s</text>'%(ox,lab[key]))
            svg.append('<path d="%s" fill="#111"/>'%d_of(recv,ox,by,sc))
    svg.append("</svg>")
    open("/tmp/specials.svg","w").write("\n".join(svg))
    cairosvg.svg2png(url="/tmp/specials.svg",write_to="/tmp/specials.png",scale=2)
    print("wrote /tmp/specials.png")

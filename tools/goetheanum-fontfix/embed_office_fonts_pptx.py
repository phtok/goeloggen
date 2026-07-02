#!/usr/bin/env python3
# Bettet die Office-TTF (Goetheanum Schrift Klar/Laut/Leise + Goetheanum Icons)
# in eine PowerPoint-Vorlage ein, damit sie auch ohne installierte Schriften
# korrekt öffnet (kein ‹überspationiert› beim Empfänger). PowerPoint bettet nur
# TrueType zuverlässig ein – darum die TTF, nicht die OTF.
#
#   python3 embed_office_fonts_pptx.py  EINGABE.pptx  AUSGABE.pptx
#
# Eingebettet werden nur die Schriften, die die Datei auch nutzt. Voll (nicht
# subsettet). fsType der TTF ist ‹installierbar›, Einbettung also erlaubt.
import os, sys, re, shutil, tempfile, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OFFICE = os.path.join(REPO, "assets/fonts/goetheanum/Office")
# sichtbarer Schriftname (wie in der Vorlage)  ->  TTF-Datei (jeweils als Regular)
FONTS = [
    ("Goetheanum Schrift Klar",     "GoetheanumSchriftKlar.ttf"),
    ("Goetheanum Schrift Laut",     "GoetheanumSchriftLaut.ttf"),
    ("Goetheanum Schrift Leise",    "GoetheanumSchriftLeise.ttf"),
    ("Goetheanum Schrift Deutlich", "GoetheanumSchriftDeutlich.ttf"),
    ("Goetheanum Icons",            "GoetheanumIcons.ttf"),
]
FONT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"

def main(src, dst):
    work = tempfile.mkdtemp()
    with zipfile.ZipFile(src) as z: z.extractall(work)
    pres = open(os.path.join(work, "ppt/presentation.xml"), encoding="utf-8").read()
    used = [(tf, ttf) for tf, ttf in FONTS if ('typeface="%s"' % tf) in
            "".join(open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read()
                    for dp, _, fs in os.walk(os.path.join(work, "ppt"))
                    for f in fs if f.endswith(".xml"))]
    if not used:
        print("keine Goetheanum-Schriften in der Vorlage gefunden"); return
    os.makedirs(os.path.join(work, "ppt/fonts"), exist_ok=True)
    # max. rId in presentation.xml.rels
    relp = os.path.join(work, "ppt/_rels/presentation.xml.rels"); rels = open(relp, encoding="utf-8").read()
    rid0 = max(int(x) for x in re.findall(r'Id="rId(\d+)"', rels)) + 1
    embed = []
    for i, (tf, ttf) in enumerate(used):
        fn = "font%d.fntdata" % (i + 1)
        shutil.copy(os.path.join(OFFICE, ttf), os.path.join(work, "ppt/fonts", fn))
        embed.append((tf, fn, "rId%d" % (rid0 + i)))
    rels = rels.replace("</Relationships>", "".join(
        '<Relationship Id="%s" Type="%s" Target="fonts/%s"/>' % (rid, FONT_REL, fn)
        for tf, fn, rid in embed) + "</Relationships>")
    open(relp, "w", encoding="utf-8").write(rels)
    pres = pres.replace('saveSubsetFonts="1"', 'saveSubsetFonts="0" embedTrueTypeFonts="1"')
    if "embedTrueTypeFonts" not in pres:
        pres = pres.replace("<p:presentation ", '<p:presentation embedTrueTypeFonts="1" saveSubsetFonts="0" ', 1)
    lst = "<p:embeddedFontLst>" + "".join(
        '<p:embeddedFont><p:font typeface="%s"/><p:regular r:id="%s"/></p:embeddedFont>' % (tf, rid)
        for tf, fn, rid in embed) + "</p:embeddedFontLst>"
    pres = (pres.replace("<p:defaultTextStyle", lst + "<p:defaultTextStyle", 1)
            if "<p:defaultTextStyle" in pres else pres.replace("</p:presentation>", lst + "</p:presentation>", 1))
    open(os.path.join(work, "ppt/presentation.xml"), "w", encoding="utf-8").write(pres)
    ctp = os.path.join(work, "[Content_Types].xml"); ct = open(ctp, encoding="utf-8").read()
    if "fntdata" not in ct:
        ct = ct.replace("</Types>", '<Default Extension="fntdata" ContentType="application/x-fontdata"/></Types>')
    open(ctp, "w", encoding="utf-8").write(ct)
    files = sorted((os.path.relpath(os.path.join(dp, f), work) for dp, _, fs in os.walk(work) for f in fs),
                   key=lambda x: (x != "[Content_Types].xml", x))
    if os.path.exists(dst): os.remove(dst)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(os.path.join(work, f), f)
    shutil.rmtree(work)
    print("eingebettet:", [tf for tf, _, _ in embed], "->", dst)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Aufruf: embed_office_fonts_pptx.py EINGABE.pptx AUSGABE.pptx"); sys.exit(2)
    main(sys.argv[1], sys.argv[2])

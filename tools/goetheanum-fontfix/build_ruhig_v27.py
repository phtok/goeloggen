#!/usr/bin/env python3
# Fügt den siebten Schnitt ‹Ruhig› (wght 350) zwischen Leise (265) und Klar (440)
# ein – die ruhige Buch-Zwischenstimme, die den grössten Sprung der Leiter
# (Leise→Klar, +32 Stammeinheiten) in zwei gleichmässige Schritte halbiert
# (Leise 50 → Ruhig 67 → Klar 82). Zwei Lieferungen, exakt wie bei Deutlich:
#   1. ein statischer Schnitt, aus der Variable bei 350 instanziert und
#      CFF2->CFF gewandelt (wie die übrigen statischen Schnitte), mit eigener
#      sauberer Benennung: typografische Familie "Goetheanum Schrift" /
#      Unterfamilie "Ruhig" (moderne Programme gruppieren ihn unter der
#      Familie), Alt-Familie "Goetheanum Schrift Ruhig" / Regular (kein
#      Bold-Italic-RIBBI-Hack). Erbt ALLE Features.
#   2. eine Named Instance + STAT-Eintrag "Ruhig" in der Variable.
# Idempotent: baut den Schnitt neu und überspringt die Instanz, wenn vorhanden.
# Danach läuft der Version-Bump 2.6 -> 2.7 (bump_version) über die ganze Familie.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.cffLib.CFF2ToCFF import convertCFF2ToCFF
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
import fontTools.ttLib.tables.otTables as ot
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
VAR = os.path.join(REPO, "assets/fonts/goetheanum/Variable/Goetheanum-Variabel-v2.6.otf")
FONTS = os.path.join(REPO, "assets/fonts/goetheanum/Fonts")
WF = os.path.join(REPO, "assets/fonts/goetheanum/Webfonts")
WGHT = 350; NAME = "Ruhig"

def webfonts(src):
    b = os.path.splitext(os.path.basename(src))[0]
    for flv, sub in (("woff", "woff"), ("woff2", "woff2")):
        f = TTFont(src); f.flavor = flv; f.save(os.path.join(WF, sub, "%s.%s" % (b, flv)))

def build_static():
    ft = TTFont(VAR)
    instantiateVariableFont(ft, {"wght": WGHT}, inplace=True)
    convertCFF2ToCFF(ft)
    nm = ft["name"]
    nm.removeNames(nameID=25)
    for rec in list(nm.names):
        if rec.nameID >= 256: nm.removeNames(nameID=rec.nameID)
    def setn(nid, s):
        nm.setName(s, nid, 3, 1, 0x409); nm.setName(s, nid, 1, 0, 0)
    setn(1, "Goetheanum Schrift Ruhig"); setn(2, "Regular")
    setn(3, "2.6;GOEA;GoetheanumSchrift-Ruhig"); setn(4, "Goetheanum Schrift Ruhig")
    setn(5, "Version 2.6"); setn(6, "GoetheanumSchrift-Ruhig")
    setn(16, "Goetheanum Schrift"); setn(17, "Ruhig")
    ft["OS/2"].usWeightClass = WGHT
    ft["OS/2"].fsSelection = (ft["OS/2"].fsSelection & ~0b101) | 0b11000000  # REGULAR + USE_TYPO, clear bold/italic
    ft["head"].macStyle = 0
    cff = ft["CFF "].cff
    cff.fontNames[0] = "GoetheanumSchrift-Ruhig"
    td = cff[cff.fontNames[0]]
    for attr in ("FullName", "FamilyName"):
        if hasattr(td, attr): setattr(td, attr, "Goetheanum Schrift Ruhig")
    if hasattr(td, "Weight"): td.Weight = "Regular"
    out = os.path.join(FONTS, "Goetheanum-Schrift-v2.6-Ruhig.otf")
    ft.save(out); webfonts(out); print("static Ruhig gebaut:", os.path.basename(out))

def add_instance():
    ft = TTFont(VAR); nm = ft["name"]; fvar = ft["fvar"]
    if any(nm.getDebugName(i.subfamilyNameID) == NAME for i in fvar.instances):
        print("Variable: Ruhig-Instanz schon vorhanden"); return
    sub_id = nm.addName(NAME)
    ps_id = nm.addName("GoetheanumVariabel-Ruhig")
    inst = NamedInstance(); inst.subfamilyNameID = sub_id; inst.postscriptNameID = ps_id
    inst.coordinates = {"wght": float(WGHT)}
    fvar.instances.append(inst)
    fvar.instances.sort(key=lambda i: i.coordinates["wght"])
    # STAT axis value (format 1) for wght 350
    st = ft["STAT"].table
    av = ot.AxisValue(); av.Format = 1; av.AxisIndex = 0; av.Flags = 0
    av.ValueNameID = sub_id; av.Value = float(WGHT)
    st.AxisValueArray.AxisValue.append(av)
    st.AxisValueArray.AxisValue.sort(key=lambda a: getattr(a, "Value", 0))
    st.AxisValueCount = len(st.AxisValueArray.AxisValue)
    ft.save(VAR); webfonts(VAR); print("Variable: Ruhig-Instanz + STAT ergänzt")

if __name__ == "__main__":
    build_static()
    add_instance()

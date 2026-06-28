#!/usr/bin/env python3
# Adds the title-weight cut ‹Deutlich› (wght 580) between Klar (440) and Laut
# (680). Two deliverables:
#   1. a static cut, instanced from the variable at 580 and converted CFF2->CFF
#      (so it matches the other static cuts), with its own clean naming:
#      typographic family "Goetheanum Schrift" / subfamily "Deutlich" (modern
#      apps group it under the family), legacy family "Goetheanum Schrift
#      Deutlich" / Regular (no Bold-Italic RIBBI hack). Inherits ALL features.
#   2. a named instance + STAT entry "Deutlich" in the variable font.
# Idempotent: re-running rebuilds the cut and skips the instance if present.
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
WGHT = 580; NAME = "Deutlich"

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
    setn(1, "Goetheanum Schrift Deutlich"); setn(2, "Regular")
    setn(3, "2.6;GOEA;GoetheanumSchrift-Deutlich"); setn(4, "Goetheanum Schrift Deutlich")
    setn(5, "Version 2.6"); setn(6, "GoetheanumSchrift-Deutlich")
    setn(16, "Goetheanum Schrift"); setn(17, "Deutlich")
    ft["OS/2"].usWeightClass = WGHT
    ft["OS/2"].fsSelection = (ft["OS/2"].fsSelection & ~0b101) | 0b11000000  # REGULAR + USE_TYPO, clear bold/italic
    ft["head"].macStyle = 0
    cff = ft["CFF "].cff
    cff.fontNames[0] = "GoetheanumSchrift-Deutlich"
    td = cff[cff.fontNames[0]]
    for attr in ("FullName", "FamilyName"):
        if hasattr(td, attr): setattr(td, attr, "Goetheanum Schrift Deutlich")
    if hasattr(td, "Weight"): td.Weight = "Regular"
    out = os.path.join(FONTS, "Goetheanum-Schrift-v2.6-Deutlich.otf")
    ft.save(out); webfonts(out); print("static Deutlich gebaut:", os.path.basename(out))

def add_instance():
    ft = TTFont(VAR); nm = ft["name"]; fvar = ft["fvar"]
    if any(nm.getDebugName(i.subfamilyNameID) == NAME for i in fvar.instances):
        print("Variable: Deutlich-Instanz schon vorhanden"); return
    sub_id = nm.addName(NAME)
    ps_id = nm.addName("GoetheanumVariabel-Deutlich")
    inst = NamedInstance(); inst.subfamilyNameID = sub_id; inst.postscriptNameID = ps_id
    inst.coordinates = {"wght": float(WGHT)}
    fvar.instances.append(inst)
    fvar.instances.sort(key=lambda i: i.coordinates["wght"])
    # STAT axis value (format 1) for wght 580
    st = ft["STAT"].table
    av = ot.AxisValue(); av.Format = 1; av.AxisIndex = 0; av.Flags = 0
    av.ValueNameID = sub_id; av.Value = float(WGHT)
    st.AxisValueArray.AxisValue.append(av)
    st.AxisValueArray.AxisValue.sort(key=lambda a: getattr(a, "Value", 0))
    st.AxisValueCount = len(st.AxisValueArray.AxisValue)
    ft.save(VAR); webfonts(VAR); print("Variable: Deutlich-Instanz + STAT ergänzt")

if __name__ == "__main__":
    build_static()
    add_instance()

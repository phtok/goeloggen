#!/usr/bin/env python3
"""Repariert die fehlende Glyphe «Goetheanum Badge invers» in ALLEN ausgelieferten
Icon-Schriftdateien und Bündeln und packt die betroffenen ZIPs neu.

Der Quell-Master trug nie ein eigenes Invers-Zeichen; U+0031 ('1', die im
Beipackzettel S.2 dokumentierte Taste) fiel auf den generischen Füll-Glyph
zurück. Die Kontur kommt aus der Einzeldatei
assets/fonts/goetheanum/Icons-Einzeldateien/svg/goetheanum-badge-invers.svg.

Betrifft:
  • Fonts/…-Icons-v2.7.otf              (CFF)
  • Webfonts/woff/…-Icons-v2.7.woff     (CFF)
  • Webfonts/woff2/…-Icons-v2.7.woff2   (CFF)
  • Goetheanum-Office-TTF.zip           → GoetheanumIcons.ttf (glyf, cu2qu)
  • Goetheanum-Schriften-v2.7.zip       → OTF · woff · woff2 · Office-TTF neu

Idempotent: erneutes Laufen ändert nichts. Aufruf aus dem Repo-Wurzelverzeichnis:
  python3 tools/goetheanum-fontfix/apply_badge_invers.py
"""
import os, sys, io, zipfile
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from fontfix import add_badge_invers, add_badge_invers_ttf, BADGE_INVERS_UNI  # noqa: E402

FONTS = os.path.join(ROOT, "assets/fonts/goetheanum")
SVG = os.path.join(FONTS, "Icons-Einzeldateien/svg/goetheanum-badge-invers.svg")
OTF = os.path.join(FONTS, "Fonts/Goetheanum-Icons-v2.7.otf")
WOFF = os.path.join(FONTS, "Webfonts/woff/Goetheanum-Icons-v2.7.woff")
WOFF2 = os.path.join(FONTS, "Webfonts/woff2/Goetheanum-Icons-v2.7.woff2")
OFFICE_ZIP = os.path.join(FONTS, "Goetheanum-Office-TTF.zip")
BUNDLE_ZIP = os.path.join(FONTS, "Goetheanum-Schriften-v2.7.zip")


def _fix_cff():
    ft = TTFont(OTF)
    if add_badge_invers(ft, SVG) is None:
        return False
    ft.flavor = None; ft.save(OTF)
    ft.flavor = "woff"; ft.save(WOFF)
    ft.flavor = "woff2"; ft.save(WOFF2)
    return True


def _fix_ttf_bytes(data):
    """Return fixed TTF bytes, or None if it already carries the glyph."""
    ft = TTFont(io.BytesIO(data))
    if add_badge_invers_ttf(ft, SVG) is None:
        return None
    buf = io.BytesIO(); ft.save(buf); return buf.getvalue()


def _repack(path, transform):
    """transform: name -> (new_bytes | None). Rewrites the zip only if something changed."""
    z = zipfile.ZipFile(path); items = {n: z.read(n) for n in z.namelist()}
    infos = {i.filename: i for i in z.infolist()}; z.close()
    changed = False
    for name in list(items):
        nb = transform(name, items[name])
        if nb is not None:
            items[name] = nb; changed = True
    if not changed:
        return False
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, data in items.items():
            zo.writestr(infos[name], data)
    return True


def main():
    cff = _fix_cff()
    print(("✓ CFF (otf/woff/woff2) ergänzt" if cff else "• CFF schon belegt") + " – U+%04X" % BADGE_INVERS_UNI)

    def office_tf(name, data):
        return _fix_ttf_bytes(data) if name.endswith("GoetheanumIcons.ttf") else None
    print("✓ Office-TTF.zip neu gepackt" if _repack(OFFICE_ZIP, office_tf) else "• Office-TTF.zip schon aktuell")

    fixed = {OTF: open(OTF, "rb").read(), WOFF: open(WOFF, "rb").read(), WOFF2: open(WOFF2, "rb").read()}
    def bundle_tf(name, data):
        want = None
        if name.endswith("Goetheanum-Icons-v2.7.otf"): want = fixed[OTF]
        elif name.endswith("Goetheanum-Icons-v2.7.woff"): want = fixed[WOFF]
        elif name.endswith("Goetheanum-Icons-v2.7.woff2"): want = fixed[WOFF2]
        elif name.endswith("GoetheanumIcons.ttf"): return _fix_ttf_bytes(data)
        return want if (want is not None and want != data) else None
    print("✓ Schriften-v2.7.zip neu gepackt" if _repack(BUNDLE_ZIP, bundle_tf) else "• Schriften-v2.7.zip schon aktuell")


if __name__ == "__main__":
    main()

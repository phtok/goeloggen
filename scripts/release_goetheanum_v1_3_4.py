#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from PIL import Image


NAME_IDS = (1, 2, 3, 4, 5, 6, 16, 17, 21, 22)
STYLE_WEIGHTS = {
    "Leise": 280,
    "Klar": 450,
    "Laut": 600,
    "Variabel": 400,
    "Icons": 400,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create cleaned Goetheanum v1.3.4 release package.")
    p.add_argument("--version", default="1.3.4")
    p.add_argument("--family", default="Goetheanum")
    p.add_argument(
        "--src-fonts",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.3.3"),
    )
    p.add_argument(
        "--src-icons",
        type=Path,
        default=Path("output/goetheanum-icons/v0.2.9"),
    )
    p.add_argument(
        "--digit-reference-fonts",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.2.1"),
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output/goetheanum-fonts/v1.3.4"),
    )
    p.add_argument("--var-instance-weight", type=float, default=400.0)
    p.add_argument("--icon-min-advance", type=int, default=1120)
    p.add_argument("--icon-extra-rsb", type=int, default=80)
    p.add_argument("--space-width", type=int, default=300)
    return p.parse_args()


def font_path(src_dir: Path, version: str, style: str) -> Path:
    p = src_dir / f"Goetheanum-v{version}-{style}.otf"
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def set_name_fields(font: TTFont, family: str, style: str, version: str) -> None:
    postscript = f"{family.replace(' ', '')}-{style}"
    full = f"{family} {style}"
    version_string = f"Version {version}"
    unique_id = f"{version};GOEA;{postscript}"

    name = font["name"]
    platforms = {
        (rec.platformID, rec.platEncID, rec.langID)
        for rec in name.names
    }
    platforms |= {(3, 1, 0x409), (1, 0, 0)}

    values = {
        1: family,
        2: style,
        3: unique_id,
        4: full,
        5: version_string,
        6: postscript,
        16: family,
        17: style,
        21: family,
        22: style,
    }
    for pid, eid, lid in sorted(platforms):
        for nid in NAME_IDS:
            name.setName(values[nid], nid, pid, eid, lid)

    if "CFF " in font:
        top = font["CFF "].cff.topDictIndex[0]
        top.FamilyName = family
        top.FullName = full
        top.FontName = postscript
        top.Weight = style


def clear_variable_tables(font: TTFont) -> None:
    for tag in ("fvar", "STAT", "avar", "MVAR", "HVAR"):
        if tag in font:
            del font[tag]


def set_static_metadata(font: TTFont, weight: int) -> None:
    os2 = font["OS/2"]
    os2.usWeightClass = int(weight)
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    os2.fsSelection |= 1 << 6

    font["head"].macStyle &= ~0b11
    font["post"].italicAngle = 0.0


def remove_logo_codepoints(font: TTFont) -> None:
    cps = {0xE100, 0xE101, 0xE102, 0xE103, 0xE140, 0xE141, 0xE142, 0xE143}
    for st in font["cmap"].tables:
        if st.isUnicode():
            for cp in list(st.cmap.keys()):
                if cp in cps:
                    del st.cmap[cp]


def repair_text_digits_from_reference(font: TTFont, ref_font_path: Path) -> None:
    if not ref_font_path.exists():
        return
    ref = TTFont(ref_font_path)
    ref_cmap = ref.getBestCmap() or {}
    ref.close()
    for cp in (0x31, 0x32, 0x33, 0x34):
        g = ref_cmap.get(cp)
        if not g:
            continue
        if g not in font.getGlyphOrder():
            continue
        for st in font["cmap"].tables:
            if st.isUnicode():
                st.cmap[cp] = g


def parse_cp(value: str) -> int:
    return int(value.replace("U+", "0x"), 16)


def apply_icons_ascii_mapping(font: TTFont, mapping_json: Path) -> None:
    data = json.loads(mapping_json.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    cmap = font.getBestCmap() or {}

    def glyph_for_cp(cp: int) -> str | None:
        return cmap.get(cp)

    default_lower = glyph_for_cp(0xE103)
    default_upper = glyph_for_cp(0xE143) or default_lower

    for row in rows:
        lower_key = row.get("lower_key", "")
        upper_key = row.get("upper_key", "")
        cp = parse_cp(row["codepoint"])
        ucp = parse_cp(row["upper_codepoint"])
        lower_glyph = glyph_for_cp(cp)
        upper_glyph = glyph_for_cp(ucp)
        if lower_key and len(lower_key) == 1 and lower_glyph:
            for st in font["cmap"].tables:
                if st.isUnicode():
                    st.cmap[ord(lower_key)] = lower_glyph
        if upper_key and len(upper_key) == 1 and upper_glyph:
            for st in font["cmap"].tables:
                if st.isUnicode():
                    st.cmap[ord(upper_key)] = upper_glyph

    # Fill still-empty ASCII letters with the default Goetheanum icon.
    for ch in "abcdefghijklmnopqrstuvwxyz":
        code = ord(ch)
        if default_lower:
            for st in font["cmap"].tables:
                if st.isUnicode() and code not in st.cmap:
                    st.cmap[code] = default_lower
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        code = ord(ch)
        if default_upper:
            for st in font["cmap"].tables:
                if st.isUnicode() and code not in st.cmap:
                    st.cmap[code] = default_upper


def patch_icons_spacing(font: TTFont, min_advance: int, extra_rsb: int, space_width: int) -> None:
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics

    glyphs = set(cmap.values())
    for g in sorted(glyphs):
        if g == "space":
            continue
        if g not in hmtx:
            continue
        adv, lsb = hmtx[g]
        bpen = BoundsPen(glyph_set)
        glyph_set[g].draw(bpen)
        if bpen.bounds:
            xmax = bpen.bounds[2]
            adv_target = int(math.ceil(xmax + extra_rsb))
            adv_new = max(adv, adv_target, min_advance)
        else:
            adv_new = max(adv, min_advance)
        hmtx[g] = (adv_new, lsb)

    if "space" in hmtx:
        _, lsb = hmtx["space"]
        hmtx["space"] = (space_width, lsb)
    font["hhea"].numberOfHMetrics = len(hmtx)


def save_font(font: TTFont, out_path: Path, family: str, style: str, version: str) -> None:
    clear_variable_tables(font)
    set_name_fields(font, family, style, version)
    set_static_metadata(font, STYLE_WEIGHTS[style])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(out_path)
    font.close()


def write_beipackzettel(out_file: Path, version: str) -> None:
    today = date.today().isoformat()
    text = "\n".join(
        [
            f"Goetheanum Schriften Version {version}",
            f"Erstellt am {today} durch die Goetheanum Kommunikation",
            "basierend auf der Schrift Titillium aus Urbino.",
            "Piktogramme und Icons u.a. von Severin Geissler und Philipp Tok.",
        ]
    )
    out_file.write_text(text + "\n", encoding="utf-8")


def make_pdf_from_png(png_path: Path, pdf_path: Path) -> None:
    img = Image.open(png_path).convert("RGB")
    img.save(pdf_path, "PDF", resolution=300.0)


def zip_dir(src_dir: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for f in sorted(src_dir.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(src_dir.parent))


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir
    off_install = out_dir / "install-offiziell"
    opt_install = out_dir / "install-optional"
    release_root = out_dir / f"Goetheanum-Familie-v{args.version}-Offiziell"
    release_install = release_root / "install-offiziell"

    if out_dir.exists():
        shutil.rmtree(out_dir)
    off_install.mkdir(parents=True, exist_ok=True)
    opt_install.mkdir(parents=True, exist_ok=True)

    src_leise = font_path(args.src_fonts, "1.3.3", "Leise")
    src_klar = font_path(args.src_fonts, "1.3.3", "Klar")
    src_laut = font_path(args.src_fonts, "1.3.3", "Laut")
    src_variabel = font_path(args.src_fonts, "1.3.3", "Klar")
    src_icons = font_path(args.src_fonts, "1.3.3", "Icons")
    ref_leise = font_path(args.digit_reference_fonts, "1.2.1", "Leise")
    ref_klar = font_path(args.digit_reference_fonts, "1.2.1", "Klar")
    ref_laut = font_path(args.digit_reference_fonts, "1.2.1", "Laut")
    mapping_json = args.src_icons / "keyboard-mapping-v0.2.9.json"
    keylayout = args.src_icons / "Goetheanum-Icons-DE.keylayout"
    mapping_md = args.src_icons / "keyboard-mapping-v0.2.9.md"

    out_fonts = {
        "Leise": off_install / f"Goetheanum-v{args.version}-Leise.otf",
        "Klar": off_install / f"Goetheanum-v{args.version}-Klar.otf",
        "Laut": off_install / f"Goetheanum-v{args.version}-Laut.otf",
        "Variabel": off_install / f"Goetheanum-v{args.version}-Variabel.otf",
        "Icons": off_install / f"Goetheanum-v{args.version}-Icons.otf",
    }

    for style, src, ref in (
        ("Leise", src_leise, ref_leise),
        ("Klar", src_klar, ref_klar),
        ("Laut", src_laut, ref_laut),
    ):
        font = TTFont(src)
        remove_logo_codepoints(font)
        repair_text_digits_from_reference(font, ref)
        save_font(font, out_fonts[style], args.family, style, args.version)

    variabel = TTFont(src_variabel)
    remove_logo_codepoints(variabel)
    repair_text_digits_from_reference(variabel, ref_klar)
    save_font(variabel, out_fonts["Variabel"], args.family, "Variabel", args.version)

    icons = TTFont(src_icons)
    apply_icons_ascii_mapping(icons, mapping_json)
    patch_icons_spacing(icons, args.icon_min_advance, args.icon_extra_rsb, args.space_width)
    save_font(icons, out_fonts["Icons"], args.family, "Icons", args.version)

    lower_png = out_dir / f"Goetheanum-Icons-Keyboard-A4-Kleinbuchstaben-v{args.version}.png"
    upper_png = out_dir / f"Goetheanum-Icons-Keyboard-A4-Grossbuchstaben-v{args.version}.png"
    subprocess.check_call(
        [
            sys.executable,
            "scripts/generate_goetheanum_icons_keyboard_a4_png.py",
            "--font-icons",
            str(out_fonts["Icons"]),
            "--font-title",
            str(out_fonts["Laut"]),
            "--font-subtitle",
            str(out_fonts["Leise"]),
            "--font-keys",
            str(out_fonts["Klar"]),
            "--mapping-json",
            str(mapping_json),
            "--out-lower",
            str(lower_png),
            "--out-upper",
            str(upper_png),
        ]
    )

    lower_pdf = off_install / f"Goetheanum-Icons-Keyboard-A4-Kleinbuchstaben-v{args.version}.pdf"
    upper_pdf = off_install / f"Goetheanum-Icons-Keyboard-A4-Grossbuchstaben-v{args.version}.pdf"
    make_pdf_from_png(lower_png, lower_pdf)
    make_pdf_from_png(upper_png, upper_pdf)

    beipackzettel = off_install / f"BEIPACKZETTEL-Goetheanum-v{args.version}.txt"
    write_beipackzettel(beipackzettel, args.version)

    shutil.copy2(keylayout, opt_install / keylayout.name)
    shutil.copy2(mapping_md, opt_install / f"keyboard-mapping-icons-v{args.version}.md")

    release_install.mkdir(parents=True, exist_ok=True)
    for f in sorted(off_install.iterdir()):
        if f.is_file() and f.suffix.lower() == ".otf":
            shutil.copy2(f, release_install / f.name)
    for f in sorted(off_install.iterdir()):
        if f.is_file() and f.suffix.lower() in {".pdf", ".txt"}:
            shutil.copy2(f, release_install / f.name)

    off_zip = out_dir / f"Goetheanum-Familie-v{args.version}-Offiziell.zip"
    opt_zip = out_dir / f"Goetheanum-Familie-v{args.version}-Optional-Input.zip"
    zip_dir(release_root, off_zip)
    zip_dir(opt_install, opt_zip)

    print(out_fonts["Leise"])
    print(out_fonts["Klar"])
    print(out_fonts["Laut"])
    print(out_fonts["Variabel"])
    print(out_fonts["Icons"])
    print(lower_pdf)
    print(upper_pdf)
    print(beipackzettel)
    print(off_zip)
    print(opt_zip)


if __name__ == "__main__":
    main()

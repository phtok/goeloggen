#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Create three-style Goetheanum release: Leise/Klar/Laut "
            "with Office hints (italic/regular/bold)."
        )
    )
    p.add_argument("--src-dir", type=Path, default=Path("output/goetheanum-fonts/v1.2.1"))
    p.add_argument("--out-dir", type=Path, default=Path("output/goetheanum-fonts/v1.3.0/three-styles"))
    p.add_argument("--family", default="Goetheanum")
    p.add_argument("--version", default="1.3.0")
    return p.parse_args()


def find_source_font(src_dir: Path, token: str) -> Path:
    matches = sorted(src_dir.glob(f"*{token}*.otf"))
    if not matches:
        raise FileNotFoundError(f"Missing source font with token '{token}' in {src_dir}")
    return matches[-1]


def ps_name(family: str, style: str) -> str:
    return f"{family.replace(' ', '')}-{style.replace(' ', '')}"


def set_name_fields(font: TTFont, family: str, style: str, version: str) -> None:
    name = font["name"]
    version_string = f"Version {version}"
    postscript = ps_name(family, style)
    unique_id = f"{version};GOEA;{postscript}"
    full = f"{family} {style}"
    for platform, enc, lang in ((3, 1, 0x409), (1, 0, 0)):
        name.setName(family, 1, platform, enc, lang)
        name.setName(style, 2, platform, enc, lang)
        name.setName(unique_id, 3, platform, enc, lang)
        name.setName(full, 4, platform, enc, lang)
        name.setName(version_string, 5, platform, enc, lang)
        name.setName(postscript, 6, platform, enc, lang)
        name.setName(family, 16, platform, enc, lang)
        name.setName(style, 17, platform, enc, lang)


def set_style_hints(font: TTFont, style: str) -> None:
    style_lower = style.lower()
    if style_lower == "leise":
        weight = 400
        is_italic = True
        is_bold = False
        is_regular = False
    elif style_lower == "laut":
        weight = 700
        is_italic = False
        is_bold = True
        is_regular = False
    elif style_lower == "klar":
        weight = 400
        is_italic = False
        is_bold = False
        is_regular = True
    else:
        raise ValueError(f"Unknown style '{style}'")

    os2 = font["OS/2"]
    os2.usWeightClass = int(weight)
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    if is_italic:
        os2.fsSelection |= 1 << 0
    if is_bold:
        os2.fsSelection |= 1 << 5
    if is_regular:
        os2.fsSelection |= 1 << 6

    head = font["head"]
    head.macStyle &= ~0b11
    if is_bold:
        head.macStyle |= 0b01
    if is_italic:
        head.macStyle |= 0b10

    post = font["post"]
    post.italicAngle = -10.0 if is_italic else 0.0


def build_font(src: Path, dst: Path, family: str, version: str, style: str) -> None:
    font = TTFont(src)
    set_name_fields(font, family, style, version)
    set_style_hints(font, style)
    dst.parent.mkdir(parents=True, exist_ok=True)
    font.save(dst)
    font.close()


def build_variable(src: Path, dst: Path, family: str, version: str) -> None:
    font = TTFont(src)
    set_name_fields(font, family, "Variable", version)
    os2 = font["OS/2"]
    os2.usWeightClass = 400
    os2.usWidthClass = 5
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    os2.fsSelection |= 1 << 6
    font["head"].macStyle &= ~0b11
    font["post"].italicAngle = 0.0

    if "fvar" in font:
        font["fvar"].instances = []
        for style, wght in (("Leise", 280.0), ("Klar", 450.0), ("Laut", 600.0)):
            sub_id = font["name"].addName(style)
            ps_id = font["name"].addName(ps_name(family, style))
            inst = NamedInstance()
            inst.subfamilyNameID = sub_id
            inst.postscriptNameID = ps_id
            inst.coordinates = {"wght": wght}
            font["fvar"].instances.append(inst)

    dst.parent.mkdir(parents=True, exist_ok=True)
    font.save(dst)
    font.close()


def copy_release_extras(src_dir: Path, dst_dir: Path, version: str) -> None:
    for extra in (
        "Goetheanum-Logos-Prefix-DE.keylayout",
        "Goetheanum-Logos-Prefix-DE-macOS.zip",
        "Goetheanum-Logos-Prefix-Anleitung.png",
        "INSTALL-Goetheanum-Logos-Prefix-DE.md",
        "keyboard-mapping-v1.2.1.md",
        "goetheanum-icons-keyboard-mac-de.png",
        "goetheanum-keyboard-real-mac-de.png",
    ):
        src_extra = src_dir / extra
        if not src_extra.exists():
            continue
        target_name = extra.replace("v1.2.1", f"v{version}")
        shutil.copy2(src_extra, dst_dir / target_name)


def write_release_notes(out_dir: Path, family: str, version: str) -> Path:
    md = out_dir / f"THREE-STYLES-v{version}.md"
    lines = [
        f"# {family} v{version} Three Styles",
        "",
        "- Visible styles:",
        "  - Leise",
        "  - Klar",
        "  - Laut",
        "",
        "- Office hints:",
        "  - Leise -> italic hint (OS/2 fsSelection italic + macStyle italic)",
        "  - Klar -> regular hint (OS/2 fsSelection regular)",
        "  - Laut -> bold hint (OS/2 fsSelection bold + macStyle bold)",
        "",
        "- Note:",
        "  - This package does not rely on classic style-linking names",
        "    (`Regular/Bold/Italic`).",
        "",
        "- Files:",
        f"  - `{family}-v{version}-Leise.otf`",
        f"  - `{family}-v{version}-Klar.otf`",
        f"  - `{family}-v{version}-Laut.otf`",
        f"  - `{family}-v{version}-Variable.otf`",
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md


def write_qa(out_dir: Path, version: str) -> Path:
    report = out_dir / f"qa-three-styles-v{version}.md"
    rows: list[str] = [
        "# QA Three Styles",
        "",
        "| File | Name1 | Name2 | Name4 | Name6 | Name16 | Name17 | Weight | fsSelection | macStyle | italicAngle |",
        "|---|---|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for p in sorted(out_dir.glob("*.otf")):
        f = TTFont(p)
        name = f["name"]
        get = lambda nid: str(name.getName(nid, 3, 1, 0x409) or name.getName(nid, 1, 0, 0) or "")
        os2 = f["OS/2"]
        rows.append(
            f"| `{p.name}` | `{get(1)}` | `{get(2)}` | `{get(4)}` | `{get(6)}` | "
            f"`{get(16)}` | `{get(17)}` | "
            f"{os2.usWeightClass} | {os2.fsSelection} | {f['head'].macStyle} | {f['post'].italicAngle} |"
        )
        f.close()
    report.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return report


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    src = {
        "Klar": find_source_font(args.src_dir, "Klar"),
        "Laut": find_source_font(args.src_dir, "Laut"),
        "Leise": find_source_font(args.src_dir, "Leise"),
        "Variable": find_source_font(args.src_dir, "Variable"),
    }

    out = {
        style: args.out_dir / f"{args.family}-v{args.version}-{style}.otf"
        for style in ("Leise", "Klar", "Laut", "Variable")
    }
    build_font(src["Leise"], out["Leise"], args.family, args.version, "Leise")
    build_font(src["Klar"], out["Klar"], args.family, args.version, "Klar")
    build_font(src["Laut"], out["Laut"], args.family, args.version, "Laut")
    build_variable(src["Variable"], out["Variable"], args.family, args.version)

    copy_release_extras(args.src_dir, args.out_dir, args.version)
    notes = write_release_notes(args.out_dir, args.family, args.version)
    qa = write_qa(args.out_dir, args.version)

    print("Wrote three-style release:")
    for style in ("Leise", "Klar", "Laut", "Variable"):
        print(" -", out[style])
    print(notes)
    print(qa)


if __name__ == "__main__":
    main()

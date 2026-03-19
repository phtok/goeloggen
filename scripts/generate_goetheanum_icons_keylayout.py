#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


LOWER_BASE = {
    0: "a",
    1: "s",
    2: "d",
    3: "f",
    4: "h",
    5: "g",
    6: "y",
    7: "x",
    8: "c",
    9: "v",
    10: "<",
    11: "b",
    12: "q",
    13: "w",
    14: "e",
    15: "r",
    16: "z",
    17: "t",
    18: "1",
    19: "2",
    20: "3",
    21: "4",
    22: "6",
    23: "5",
    24: "´",
    25: "9",
    26: "7",
    27: "ß",
    28: "8",
    29: "0",
    30: "+",
    31: "o",
    32: "u",
    33: "ü",
    34: "i",
    35: "p",
    37: "l",
    38: "j",
    39: "ö",
    40: "k",
    41: "ä",
    42: "#",
    43: ",",
    44: "-",
    45: "n",
    46: "m",
    47: ".",
    50: "^",
}

UPPER_BASE = {
    0: "A",
    1: "S",
    2: "D",
    3: "F",
    4: "H",
    5: "G",
    6: "Y",
    7: "X",
    8: "C",
    9: "V",
    10: ">",
    11: "B",
    12: "Q",
    13: "W",
    14: "E",
    15: "R",
    16: "Z",
    17: "T",
    18: "!",
    19: '"',
    20: "§",
    21: "$",
    22: "&",
    23: "%",
    24: "`",
    25: ")",
    26: "/",
    27: "?",
    28: "(",
    29: "=",
    30: "*",
    31: "O",
    32: "U",
    33: "Ü",
    34: "I",
    35: "P",
    37: "L",
    38: "J",
    39: "Ö",
    40: "K",
    41: "Ä",
    42: "'",
    43: ";",
    44: "_",
    45: "N",
    46: "M",
    47: ":",
    50: "°",
}

# keycode -> (base codepoint, label)
ICON_KEYS = {
    18: (0xE100, "Goetheanum Logo"),
    19: (0xE102, "Goetheanum Square"),
    # Regeln
    12: (0xE215, "Bitte anfassen"),
    13: (0xE208, "Nur mit den Augen"),
    14: (0xE209, "Eintritt"),
    15: (0xE20A, "Hunde anleinen"),
    17: (0xE20F, "Keine Hunde"),
    16: (0xE210, "Keine Fotos"),
    32: (0xE207, "Draussen essen"),
    34: (0xE20E, "Keine Taschen"),
    31: (0xE216, "Geräte aus"),
    # Orte
    0: (0xE20B, "Fahrstuhl"),
    1: (0xE214, "Treppe"),
    2: (0xE20C, "Schliessfächer"),
    3: (0xE217, "Garderobe"),
    5: (0xE21E, "WLAN"),
    # Müll
    4: (0xE212, "Bioabfall"),
    38: (0xE213, "Papier"),
    40: (0xE20D, "Restmüll"),
    # WC
    10: (0xE21A, "WC Damen"),
    6: (0xE219, "WC Herren"),
    7: (0xE21C, "WC Rollstuhl"),
    8: (0xE211, "Wickelraum"),
    9: (0xE218, "WC alle"),
    11: (0xE21B, "WC ohne Herren"),
}

DEFAULT_FREE_LETTER_ICON_CP = 0xE101
# Keep free keys filled with the point icon, but avoid repeated label noise.
DEFAULT_FREE_LETTER_ICON_LABEL = ""

# Per-layer overrides for explicit exceptions requested in the layout:
# - "!" keeps logo with text (uppercase), while lower "1" is point.
# - lower "2" is square, while upper '"' stays placeholder.
# - "§" stays placeholder on both layers.
LOWER_CODEPOINT_OVERRIDES = {
    18: 0xE101,  # 1 -> Point
    19: 0xE102,  # 2 -> Square
}
UPPER_CODEPOINT_OVERRIDES = {
    19: 0xE101,  # " -> placeholder
    20: 0xE101,  # § -> placeholder
}

# Option/Alt layer: arrow board (16 variants) + compass needles (4)
ALT_ICON_KEYS = {
    # Kreuz 1 (kurz): 2 / q e / s
    19: (0xE260, "Pfeil kurz up"),
    12: (0xE263, "Pfeil kurz left"),
    14: (0xE261, "Pfeil kurz right"),
    1: (0xE262, "Pfeil kurz down"),
    # Kreuz 2 (lang): 6 / t u / h
    22: (0xE264, "Pfeil lang up"),
    17: (0xE267, "Pfeil lang left"),
    32: (0xE265, "Pfeil lang right"),
    4: (0xE266, "Pfeil lang down"),
    # Kreuz 3 (gebogen, gespiegelt): 0 / o ü / ö
    29: (0xE26C, "Pfeil gebogen up"),
    31: (0xE26F, "Pfeil gebogen left"),
    33: (0xE26D, "Pfeil gebogen right"),
    39: (0xE26E, "Pfeil gebogen down"),
    # Kompass auf y/x/c/v (¥ … √)
    6: (0xE203, "Kompass Süd oben"),
    7: (0xE204, "Kompass N-S"),
    8: (0xE205, "Kompass S-N"),
    9: (0xE206, "Kompass Nord oben"),
}


def is_letter_output(ch: str) -> bool:
    return len(ch) == 1 and ch.isalpha()


def default_icon_codes() -> set[int]:
    # Fill every unassigned key of the base keyboard with the default icon.
    return {code for code in LOWER_BASE.keys() if code not in ICON_KEYS}


def upper_codepoint_for(code: int, cp: int, upper_mode: str, upper_codepoint_offset: int) -> int:
    if upper_mode != "labeled-glyph":
        return cp
    if code not in ICON_KEYS:
        return cp
    return cp + upper_codepoint_offset


def layer_codepoints(code: int, upper_mode: str, upper_codepoint_offset: int) -> tuple[int, int, str]:
    if code in ICON_KEYS:
        cp, label = ICON_KEYS[code]
    else:
        cp, label = DEFAULT_FREE_LETTER_ICON_CP, DEFAULT_FREE_LETTER_ICON_LABEL

    lower_cp = cp
    upper_cp = upper_codepoint_for(code, cp, upper_mode, upper_codepoint_offset)
    if code in LOWER_CODEPOINT_OVERRIDES:
        lower_cp = LOWER_CODEPOINT_OVERRIDES[code]
    if code in UPPER_CODEPOINT_OVERRIDES:
        upper_cp = UPPER_CODEPOINT_OVERRIDES[code]
    return lower_cp, upper_cp, label


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Goetheanum Icons macOS keylayout + mapping docs.")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
    )
    p.add_argument("--version", default="0.3.14")
    p.add_argument("--layout-name", default="Goetheanum Icons (DE)")
    p.add_argument("--layout-id", default="7220")
    p.add_argument(
        "--upper-mode",
        choices=["text", "labeled-glyph"],
        default="text",
        help="Shift layer output: text => icon + label text; labeled-glyph => dedicated PUA glyph.",
    )
    p.add_argument(
        "--upper-codepoint-offset",
        type=lambda s: int(s, 0),
        default=0x40,
        help="Codepoint offset for labeled glyphs when --upper-mode labeled-glyph is used.",
    )
    return p.parse_args()


def xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def emit_keymap(
    index: int,
    mapping: dict[int, str],
    icon_mode: bool,
    upper_mode: str,
    upper_codepoint_offset: int,
) -> str:
    lines = [f'    <keyMap index="{index}">']
    fallback_codes = default_icon_codes()
    for code in sorted(mapping):
        val = mapping[code]
        if icon_mode and code in ICON_KEYS:
            cp, label = ICON_KEYS[code]
            icon = chr(cp)
            if index == 0:
                out = icon
            elif index == 1 and upper_mode == "labeled-glyph":
                out = chr(cp + upper_codepoint_offset)
            else:
                out = f"{icon} {label}"
            lines.append(f'      <key code="{code}" output="{xml_escape(out)}"/>')
        elif icon_mode and code in fallback_codes:
            cp = DEFAULT_FREE_LETTER_ICON_CP
            icon = chr(cp)
            if index == 0:
                out = icon
            elif index == 1 and upper_mode == "labeled-glyph":
                # Free keys stay icon-only on Shift to avoid duplicated text labels.
                out = icon
            else:
                out = icon if not DEFAULT_FREE_LETTER_ICON_LABEL else f"{icon} {DEFAULT_FREE_LETTER_ICON_LABEL}"
            lines.append(f'      <key code="{code}" output="{xml_escape(out)}"/>')
        else:
            lines.append(f'      <key code="{code}" output="{xml_escape(val)}"/>')
    lines.append("    </keyMap>")
    return "\n".join(lines)


def emit_alt_keymap(index: int, mapping: dict[int, str]) -> str:
    lines = [f'    <keyMap index="{index}">']
    for code in sorted(mapping):
        if code in ALT_ICON_KEYS:
            cp, _label = ALT_ICON_KEYS[code]
            out = chr(cp)
        else:
            out = mapping[code]
        lines.append(f'      <key code="{code}" output="{xml_escape(out)}"/>')
    lines.append("    </keyMap>")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir or Path(f"output/goetheanum-icons/v{args.version}")
    out_dir.mkdir(parents=True, exist_ok=True)

    keylayout_path = out_dir / "Goetheanum-Icons-DE.keylayout"
    mapping_path = out_dir / f"keyboard-mapping-v{args.version}.md"
    mapping_json = out_dir / f"keyboard-mapping-v{args.version}.json"

    keylayout = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">
<keyboard group="126" id="{args.layout_id}" name="{xml_escape(args.layout_name)}" maxout="128">
  <layouts>
    <layout first="0" last="0" modifiers="modifiers" mapSet="icons"/>
  </layouts>
  <modifierMap id="modifiers" defaultIndex="0">
    <keyMapSelect mapIndex="0"><modifier keys=""/></keyMapSelect>
    <keyMapSelect mapIndex="1"><modifier keys="anyShift"/></keyMapSelect>
    <keyMapSelect mapIndex="2"><modifier keys="anyOption"/></keyMapSelect>
    <keyMapSelect mapIndex="3"><modifier keys="anyOption anyShift"/></keyMapSelect>
  </modifierMap>
  <keyMapSet id="icons">
{emit_keymap(0, LOWER_BASE, icon_mode=True, upper_mode=args.upper_mode, upper_codepoint_offset=args.upper_codepoint_offset)}
{emit_keymap(1, UPPER_BASE, icon_mode=True, upper_mode=args.upper_mode, upper_codepoint_offset=args.upper_codepoint_offset)}
{emit_alt_keymap(2, LOWER_BASE)}
{emit_alt_keymap(3, UPPER_BASE)}
  </keyMapSet>
</keyboard>
"""
    keylayout_path.write_text(keylayout, encoding="utf-8")

    md = [
        f"# Goetheanum Icons Keyboard v{args.version}",
        "",
        f"- Eingabequelle: `{args.layout_name}`",
        "- Ebene ohne Shift: `klein -> Icon pur`",
        "- Ebene mit Shift: "
        + (
            "`GROSS -> Label-Glyph (PUA)`"
            if args.upper_mode == "labeled-glyph"
            else "`GROSS -> Icon + Labeltext`"
        ),
        "",
        "| Taste | Klein | Gross | Funktion |",
        "|---|---|---|---|",
    ]
    all_codes = sorted(set(ICON_KEYS) | default_icon_codes())
    for code in all_codes:
        cp, upper_cp, label = layer_codepoints(code, args.upper_mode, args.upper_codepoint_offset)
        lower = LOWER_BASE.get(code, "")
        upper = UPPER_BASE.get(code, "")
        if args.upper_mode == "labeled-glyph":
            md.append(
                f"| `{lower}` | `U+{cp:04X}` | `U+{upper_cp:04X}` | `{label}` |"
            )
        else:
            md.append(f"| `{lower}` | `U+{cp:04X}` | `U+{cp:04X} + {label}` | `{label}` |")
    mapping_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    json_rows = []
    for code in all_codes:
        cp, upper_cp, label = layer_codepoints(code, args.upper_mode, args.upper_codepoint_offset)
        json_rows.append(
            {
                "keycode": code,
                "lower_key": LOWER_BASE.get(code, ""),
                "upper_key": UPPER_BASE.get(code, ""),
                "codepoint": f"U+{cp:04X}",
                "glyph": chr(cp),
                "upper_codepoint": f"U+{upper_cp:04X}",
                "upper_glyph": chr(upper_cp),
                "label": label,
            }
        )
    mapping_json.write_text(
        json.dumps(
            {
                "version": args.version,
                "layout_name": args.layout_name,
                "icon_count": len(json_rows),
                "rows": json_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(keylayout_path)
    print(mapping_path)
    print(mapping_json)


if __name__ == "__main__":
    main()

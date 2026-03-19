#!/usr/bin/env python3
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = "/Users/philipptok/goeloggen"
OUT = os.path.join(ROOT, "output", "tv_cover_demo_v3")
CUTOUT_SINGLE = os.path.join(ROOT, "assets", "tv_cutouts", "single_person_cutout.png")
CUTOUT_DOUBLE = os.path.join(ROOT, "assets", "tv_cutouts", "double_people_cutout.png")

FONTS = {
    "light": os.path.join(ROOT, "assets", "fonts", "Titillium-LightUpright.otf"),
    "regular": os.path.join(ROOT, "assets", "fonts", "Titillium-RegularUpright.otf"),
    "semi": os.path.join(ROOT, "assets", "fonts", "Titillium-SemiboldUpright.otf"),
}

SERIES_TITLE = {
    "de": "Lebenskraefte\nder Sprache",
    "en": "Life Forces\nof Language",
}

EPISODE_TITLE = {
    "de": "Sprechen\nund Leben",
    "en": "Speech\nand Life",
}
EPISODE_TITLE_2 = {
    "de": "Aetherarten\nim Sprechen",
    "en": "Ether in\nSpeech",
}


@dataclass
class FormatSpec:
    key: str
    family: str  # uscreen | social
    variant: str  # banner | cover_quer | cover_hoch | story | square | portrait
    width: int
    height: int


FORMATS: List[FormatSpec] = [
    # Uscreen
    FormatSpec("uscreen_banner", "uscreen", "banner", 1900, 800),
    FormatSpec("uscreen_cover_quer", "uscreen", "cover_quer", 1920, 1080),
    FormatSpec("uscreen_cover_hoch", "uscreen", "cover_hoch", 1188, 1682),
    # Social
    FormatSpec("social_story", "social", "story", 1080, 1920),
    FormatSpec("social_square", "social", "square", 1080, 1080),
    FormatSpec("social_portrait", "social", "portrait", 1080, 1350),
]


def font(name: str, size: int):
    return ImageFont.truetype(FONTS[name], size)


def new_transparent(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def make_background(w: int, h: int) -> Image.Image:
    bg = Image.new("RGBA", (w, h), (38, 52, 68, 255))
    d = ImageDraw.Draw(bg, "RGBA")

    color_blobs = [
        ((0.18, 0.22), 0.58, (186, 86, 55, 205)),
        ((0.62, 0.28), 0.52, (96, 52, 47, 190)),
        ((0.80, 0.76), 0.48, (198, 106, 45, 178)),
        ((0.35, 0.77), 0.40, (97, 110, 116, 130)),
    ]

    for (cx, cy), rel_r, col in color_blobs:
        r = int(min(w, h) * rel_r)
        x = int(w * cx)
        y = int(h * cy)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)

    bg = bg.filter(ImageFilter.GaussianBlur(radius=max(32, min(w, h) // 9)))

    grade = Image.new("RGBA", (w, h), (45, 20, 16, 70))
    bg = Image.alpha_composite(bg, grade)

    floor = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor, "RGBA")
    fd.rectangle((0, int(h * 0.865), w, h), fill=(228, 132, 18, 160))
    floor = floor.filter(ImageFilter.GaussianBlur(radius=max(14, min(w, h) // 20)))
    bg = Image.alpha_composite(bg, floor)

    return bg


def make_frame_layer(w: int, h: int) -> Image.Image:
    layer = new_transparent(w, h)
    d = ImageDraw.Draw(layer, "RGBA")
    m = int(min(w, h) * 0.032)
    stroke = max(2, int(min(w, h) * 0.0045))
    rad = int(min(w, h) * 0.022)
    d.rounded_rectangle((m, m, w - m, h - m), radius=rad, outline=(228, 235, 242, 245), width=stroke)
    return layer


def draw_head(d: ImageDraw.ImageDraw, x: int, y: int, s: float, variant: int = 1) -> None:
    skin = (232, 197, 174, 255) if variant == 1 else (227, 196, 171, 255)
    hair = (84, 84, 86, 255) if variant == 1 else (70, 58, 46, 255)
    jacket = (43, 79, 126, 255) if variant == 1 else (158, 63, 58, 255)
    shirt = (238, 241, 244, 252)

    d.rounded_rectangle((x - 220 * s, y + 115 * s, x + 220 * s, y + 570 * s), radius=50 * s, fill=jacket)
    d.polygon([(x, y + 160 * s), (x - 70 * s, y + 295 * s), (x + 70 * s, y + 295 * s)], fill=shirt)
    d.rounded_rectangle((x - 40 * s, y + 82 * s, x + 40 * s, y + 170 * s), radius=17 * s, fill=skin)
    d.ellipse((x - 112 * s, y - 132 * s, x + 112 * s, y + 102 * s), fill=skin)
    d.pieslice((x - 132 * s, y - 165 * s, x + 132 * s, y + 80 * s), start=192, end=360, fill=hair)
    d.ellipse((x - 120 * s, y - 96 * s, x + 120 * s, y + 96 * s), fill=skin)


def _compose_cutout_canvas(w: int, h: int, cutout: Image.Image, layout_variant: str, subject: str) -> Image.Image:
    canvas = new_transparent(w, h)

    # target heights and placement are tuned per output variant
    h_map_single = {
        "banner": 0.92,
        "cover_quer": 0.84,
        "cover_hoch": 0.62,
        "story": 0.46,
        "square": 0.64,
        "portrait": 0.62,
    }
    h_map_double = {
        "banner": 0.90,
        "cover_quer": 0.82,
        "cover_hoch": 0.60,
        "story": 0.45,
        "square": 0.63,
        "portrait": 0.60,
    }
    cx_map_single = {
        "banner": 0.83,
        "cover_quer": 0.82,
        "cover_hoch": 0.60,
        "story": 0.66,
        "square": 0.67,
        "portrait": 0.65,
    }
    cx_map_double = {
        "banner": 0.77,
        "cover_quer": 0.76,
        "cover_hoch": 0.57,
        "story": 0.61,
        "square": 0.60,
        "portrait": 0.58,
    }

    if subject == "double":
        target_h = int(h * h_map_double.get(layout_variant, 0.62))
        center_x = int(w * cx_map_double.get(layout_variant, 0.60))
    else:
        target_h = int(h * h_map_single.get(layout_variant, 0.62))
        center_x = int(w * cx_map_single.get(layout_variant, 0.65))

    scale = target_h / cutout.height
    target_w = max(1, int(cutout.width * scale))
    resized = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)

    if layout_variant == "story":
        margin_bottom = int(h * 0.05)
    else:
        margin_bottom = int(h * 0.02)
    y = h - target_h - margin_bottom
    x = center_x - target_w // 2

    shadow = Image.new("RGBA", resized.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    sd.bitmap((0, 0), resized.split()[-1], fill=(8, 12, 16, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(5, min(w, h) // 140)))

    canvas.alpha_composite(shadow, (x + int(w * 0.004), y + int(h * 0.004)))
    canvas.alpha_composite(resized, (x, y))
    return canvas


def make_portrait_layer(w: int, h: int, variant: str = "single", layout_variant: str = "cover_quer") -> Image.Image:
    source = CUTOUT_SINGLE if variant == "single" else CUTOUT_DOUBLE
    if os.path.exists(source):
        cutout = Image.open(source).convert("RGBA")
        return _compose_cutout_canvas(w, h, cutout, layout_variant, variant)

    # Fallback if cutouts are unavailable
    layer = new_transparent(w, h)
    d = ImageDraw.Draw(layer, "RGBA")
    s = min(w, h) / 1080

    if variant == "single":
        draw_head(d, int(w * 0.74), int(h * 0.50), s, variant=1)
    else:
        draw_head(d, int(w * 0.66), int(h * 0.53), s * 0.92, variant=2)
        draw_head(d, int(w * 0.82), int(h * 0.53), s * 0.92, variant=1)

    return layer


def draw_text_lines(d: ImageDraw.ImageDraw, title: str, x: int, y: int, fs: int) -> None:
    ff = font("semi", fs)
    shadow = (15, 20, 28, 155)
    color = (246, 249, 252, 248)
    yy = y
    for line in title.split("\n"):
        d.text((x + 2, yy + 2), line, font=ff, fill=shadow)
        d.text((x, yy), line, font=ff, fill=color)
        yy += int(fs * 0.95)


def make_series_text_layer(w: int, h: int, lang: str) -> Image.Image:
    layer = new_transparent(w, h)
    d = ImageDraw.Draw(layer, "RGBA")

    # Reihencover: deutlich groessere Typografie
    if w / h >= 1.6:
        fs = int(h * 0.17)
        x = int(w * 0.12)
        y = int(h * 0.19)
    elif h / w > 1.35:
        fs = int(w * 0.135)
        x = int(w * 0.11)
        y = int(h * 0.09)
    else:
        fs = int(min(w, h) * 0.165)
        x = int(w * 0.10)
        y = int(h * 0.14)

    fs = max(72, min(220, fs))
    draw_text_lines(d, SERIES_TITLE[lang], x, y, fs)
    return layer


def make_episode_text_layer(w: int, h: int, title: str) -> Image.Image:
    layer = new_transparent(w, h)
    d = ImageDraw.Draw(layer, "RGBA")

    if w / h >= 1.6:
        fs = int(h * 0.125)
        x = int(w * 0.09)
        y = int(h * 0.20)
    elif h / w > 1.35:
        fs = int(w * 0.105)
        x = int(w * 0.12)
        y = int(h * 0.08)
    else:
        fs = int(min(w, h) * 0.118)
        x = int(w * 0.10)
        y = int(h * 0.13)

    fs = max(52, min(162, fs))
    draw_text_lines(d, title, x, y, fs)
    return layer


def make_badge_layer(w: int, h: int) -> Image.Image:
    layer = new_transparent(w, h)
    d = ImageDraw.Draw(layer, "RGBA")
    fs = max(24, int(min(w, h) * 0.06))
    ff = font("semi", fs)
    label = "tv"
    tw = d.textbbox((0, 0), label, font=ff)[2]
    pad = int(fs * 0.45)
    x = int(w * 0.12)
    y = int(h * 0.06)
    d.ellipse((x, y, x + tw + pad * 2, y + fs + int(pad * 1.4)), fill=(239, 245, 252, 220))
    d.text((x + pad, y + int(pad * 0.2)), label, font=ff, fill=(84, 51, 46, 255))
    return layer


def merge_layers(layers: List[Image.Image]) -> Image.Image:
    base = layers[0].copy()
    for layer in layers[1:]:
        base.alpha_composite(layer)
    return base


def save_layers(base_dir: str, layers: Dict[str, Image.Image]) -> None:
    os.makedirs(base_dir, exist_ok=True)
    for k, im in layers.items():
        im.save(os.path.join(base_dir, f"{k}.png"), "PNG")


def build_set(
    kind: str,
    fmt: FormatSpec,
    lang: str = "de",
    subject: str = "single",
    episode_title_map: Optional[Dict[str, str]] = None,
) -> Dict[str, Image.Image]:
    w, h = fmt.width, fmt.height
    layers: Dict[str, Image.Image] = {
        "layer_01_background": make_background(w, h),
        "layer_02_frame": make_frame_layer(w, h),
    }

    if kind == "series":
        layers["layer_03_text"] = make_series_text_layer(w, h, lang)
    elif kind == "episode":
        title_map = episode_title_map or EPISODE_TITLE
        layers["layer_03_portrait"] = make_portrait_layer(w, h, subject, fmt.variant)
        layers["layer_04_text"] = make_episode_text_layer(w, h, title_map[lang])
    elif kind == "clean":
        layers["layer_03_portrait"] = make_portrait_layer(w, h, subject, fmt.variant)
        layers["layer_04_badge"] = make_badge_layer(w, h)

    return layers


def main() -> None:
    os.makedirs(OUT, exist_ok=True)

    manifest = {
        "formats": [],
        "note": "V3 aligned to format families: Uscreen (banner/quer/hoch), Social (story/square/portrait)",
    }

    preview_paths = []

    for fmt in FORMATS:
        # Story format: always clean (portrait + TV badge), no text layer.
        if fmt.variant == "story":
            for subject in ["single", "double"]:
                layers = build_set("clean", fmt, "de", subject=subject)
                comp = merge_layers(list(layers.values()))
                name = f"episode_clean_{subject}_{fmt.key}_{fmt.width}x{fmt.height}"
                out_png = os.path.join(OUT, f"{name}.png")
                comp.convert("RGB").save(out_png, "PNG")
                save_layers(os.path.join(OUT, "layers", name), layers)
                preview_paths.append(out_png)
                manifest["formats"].append({
                    "name": name,
                    "family": fmt.family,
                    "variant": fmt.variant,
                    "width": fmt.width,
                    "height": fmt.height,
                    "kind": "episode_clean",
                    "subject": subject,
                    "lang": "none",
                    "file": out_png,
                })
            continue

        # series DE/EN
        for lang in ["de", "en"]:
            layers = build_set("series", fmt, lang)
            comp = merge_layers(list(layers.values()))
            name = f"series_{lang}_{fmt.key}_{fmt.width}x{fmt.height}"
            out_png = os.path.join(OUT, f"{name}.png")
            comp.convert("RGB").save(out_png, "PNG")
            save_layers(os.path.join(OUT, "layers", name), layers)
            preview_paths.append(out_png)
            manifest["formats"].append({
                "name": name,
                "family": fmt.family,
                "variant": fmt.variant,
                "width": fmt.width,
                "height": fmt.height,
                "kind": "series",
                "lang": lang,
                "file": out_png,
            })

        # episode DE/EN (single + double)
        for lang in ["de", "en"]:
            # single
            layers = build_set("episode", fmt, lang, subject="single", episode_title_map=EPISODE_TITLE)
            comp = merge_layers(list(layers.values()))
            name = f"episode_{lang}_single_{fmt.key}_{fmt.width}x{fmt.height}"
            out_png = os.path.join(OUT, f"{name}.png")
            comp.convert("RGB").save(out_png, "PNG")
            save_layers(os.path.join(OUT, "layers", name), layers)
            preview_paths.append(out_png)
            manifest["formats"].append({
                "name": name,
                "family": fmt.family,
                "variant": fmt.variant,
                "width": fmt.width,
                "height": fmt.height,
                "kind": "episode",
                "subject": "single",
                "lang": lang,
                "file": out_png,
            })

            # double
            layers = build_set("episode", fmt, lang, subject="double", episode_title_map=EPISODE_TITLE_2)
            comp = merge_layers(list(layers.values()))
            name = f"episode_{lang}_double_{fmt.key}_{fmt.width}x{fmt.height}"
            out_png = os.path.join(OUT, f"{name}.png")
            comp.convert("RGB").save(out_png, "PNG")
            save_layers(os.path.join(OUT, "layers", name), layers)
            preview_paths.append(out_png)
            manifest["formats"].append({
                "name": name,
                "family": fmt.family,
                "variant": fmt.variant,
                "width": fmt.width,
                "height": fmt.height,
                "kind": "episode",
                "subject": "double",
                "lang": lang,
                "file": out_png,
            })

        # clean variants once per non-story format (single + double)
        for subject in ["single", "double"]:
            layers = build_set("clean", fmt, "de", subject=subject)
            comp = merge_layers(list(layers.values()))
            name = f"episode_clean_{subject}_{fmt.key}_{fmt.width}x{fmt.height}"
            out_png = os.path.join(OUT, f"{name}.png")
            comp.convert("RGB").save(out_png, "PNG")
            save_layers(os.path.join(OUT, "layers", name), layers)
            preview_paths.append(out_png)
            manifest["formats"].append({
                "name": name,
                "family": fmt.family,
                "variant": fmt.variant,
                "width": fmt.width,
                "height": fmt.height,
                "kind": "episode_clean",
                "subject": subject,
                "lang": "none",
                "file": out_png,
            })

    # contactsheet
    thumbs = []
    for p in sorted(preview_paths):
        im = Image.open(p).convert("RGB")
        thumbs.append((os.path.basename(p), im))

    cols = 4
    tw, th = 420, 236
    gap, label_h = 18, 44
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * (th + label_h) + (rows + 1) * gap), (24, 33, 44))
    d = ImageDraw.Draw(sheet)
    ff = font("regular", 22)
    for i, (name, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap)
        y = gap + r * (th + label_h + gap)
        scale = min(tw / im.width, th / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        rs = im.resize((nw, nh), Image.Resampling.LANCZOS)
        panel = Image.new("RGB", (tw, th), (45, 58, 74))
        panel.paste(rs, ((tw - nw) // 2, (th - nh) // 2))
        sheet.paste(panel, (x, y))
        d.rectangle((x, y, x + tw, y + th), outline=(94, 112, 135), width=2)
        d.text((x, y + th + 8), name, font=ff, fill=(220, 229, 240))

    sheet_path = os.path.join(OUT, "_contactsheet_v3.png")
    sheet.save(sheet_path)

    manifest_path = os.path.join(OUT, "manifest_v3.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"generated entries: {len(manifest['formats'])}")
    print(sheet_path)
    print(manifest_path)


if __name__ == "__main__":
    main()

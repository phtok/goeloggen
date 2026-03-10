#!/usr/bin/env python3
import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = "/Users/philipptok/goeloggen"
OUT_DIR = os.path.join(ROOT, "output", "tv_cover_demo")
LAYERS_DIR = os.path.join(OUT_DIR, "layers")

FONT_REGULAR = os.path.join(ROOT, "assets", "fonts", "Titillium-RegularUpright.otf")
FONT_LIGHT = os.path.join(ROOT, "assets", "fonts", "Titillium-LightUpright.otf")
FONT_SEMIBOLD = os.path.join(ROOT, "assets", "fonts", "Titillium-SemiboldUpright.otf")


@dataclass
class CoverSpec:
    key: str
    width: int
    height: int
    label: str


FORMATS: List[CoverSpec] = [
    CoverSpec("goetheanum_tv_cover", 740, 420, "Goetheanum TV Cover"),
    CoverSpec("goetheanum_tv_cover_2x", 1480, 840, "Goetheanum TV Cover 2x"),
    CoverSpec("youtube_thumbnail", 1280, 720, "YouTube Thumbnail"),
    CoverSpec("hero_banner", 1900, 800, "Hero Banner"),
    CoverSpec("open_graph", 1200, 630, "Open Graph"),
    CoverSpec("instagram_portrait", 1080, 1350, "Instagram Feed 4:5"),
    CoverSpec("instagram_square", 1080, 1080, "Instagram Square 1:1"),
    CoverSpec("instagram_story", 1080, 1920, "Instagram Story 9:16"),
]


CONTENT = {
    "series": "Goetheanum Gespraeche",
    "title_long": "Wie entsteht Zukunft zwischen Kunst, Biografie und Verantwortung?",
    "title_short": "Zukunft braucht Mut",
    "speaker": "Mara Engel",
    "subtitle": "Künstlerin und Sozialgestalterin",
    "keywords": ["zukunft", "kunst", "verantwortung"],
}


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(LAYERS_DIR, exist_ok=True)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def make_background(width: int, height: int) -> Image.Image:
    bg = Image.new("RGBA", (width, height), (40, 56, 76, 255))
    px = bg.load()
    top = (58, 74, 97)
    mid = (52, 70, 93)
    bottom = (44, 60, 82)

    for y in range(height):
        t = y / max(1, height - 1)
        if t < 0.55:
            u = t / 0.55
            r = int(lerp(top[0], mid[0], u))
            g = int(lerp(top[1], mid[1], u))
            b = int(lerp(top[2], mid[2], u))
        else:
            u = (t - 0.55) / 0.45
            r = int(lerp(mid[0], bottom[0], u))
            g = int(lerp(mid[1], bottom[1], u))
            b = int(lerp(mid[2], bottom[2], u))
        for x in range(width):
            px[x, y] = (r, g, b, 255)

    overlays = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlays, "RGBA")
    glow_shapes = [
        ((int(width * 0.18), int(height * 0.32)), int(min(width, height) * 0.35), (112, 165, 214, 72)),
        ((int(width * 0.78), int(height * 0.22)), int(min(width, height) * 0.30), (194, 110, 147, 62)),
        ((int(width * 0.65), int(height * 0.72)), int(min(width, height) * 0.40), (64, 125, 190, 48)),
        ((int(width * 0.30), int(height * 0.84)), int(min(width, height) * 0.28), (225, 172, 117, 40)),
    ]
    for (cx, cy), radius, color in glow_shapes:
        od.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)

    overlays = overlays.filter(ImageFilter.GaussianBlur(radius=max(16, min(width, height) // 18)))
    bg = Image.alpha_composite(bg, overlays)

    vignette = Image.new("L", (width, height), 0)
    vd = ImageDraw.Draw(vignette)
    margin = int(min(width, height) * 0.04)
    vd.rectangle((margin, margin, width - margin, height - margin), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=max(24, min(width, height) // 12)))
    vignette = ImageChops.invert(vignette)

    dark = Image.new("RGBA", (width, height), (15, 21, 30, 155))
    bg = Image.composite(dark, bg, vignette)
    return bg


def make_portrait(width: int, height: int) -> Image.Image:
    art = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(art, "RGBA")

    center_x = int(width * 0.56)
    base_y = int(height * 0.76)

    shoulder_w = int(width * 0.62)
    shoulder_h = int(height * 0.42)
    d.ellipse(
        (
            center_x - shoulder_w // 2,
            base_y - shoulder_h,
            center_x + shoulder_w // 2,
            base_y + int(height * 0.22),
        ),
        fill=(24, 42, 61, 245),
    )

    neck_w = int(width * 0.11)
    neck_h = int(height * 0.15)
    d.rounded_rectangle(
        (center_x - neck_w // 2, base_y - int(height * 0.34), center_x + neck_w // 2, base_y - int(height * 0.18)),
        radius=int(width * 0.02),
        fill=(214, 182, 162, 255),
    )

    head_r = int(min(width, height) * 0.18)
    head_cx = center_x
    head_cy = base_y - int(height * 0.46)
    d.ellipse((head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r), fill=(226, 194, 173, 255))

    hair = [
        (head_cx - int(head_r * 1.05), head_cy + int(head_r * 0.05)),
        (head_cx - int(head_r * 0.95), head_cy - int(head_r * 0.65)),
        (head_cx - int(head_r * 0.45), head_cy - int(head_r * 1.10)),
        (head_cx + int(head_r * 0.40), head_cy - int(head_r * 1.15)),
        (head_cx + int(head_r * 0.92), head_cy - int(head_r * 0.60)),
        (head_cx + int(head_r * 0.84), head_cy + int(head_r * 0.32)),
        (head_cx + int(head_r * 0.28), head_cy + int(head_r * 0.14)),
        (head_cx + int(head_r * 0.00), head_cy - int(head_r * 0.02)),
        (head_cx - int(head_r * 0.25), head_cy + int(head_r * 0.22)),
    ]
    d.polygon(hair, fill=(58, 69, 88, 255))

    d.ellipse(
        (
            head_cx - int(head_r * 0.62),
            head_cy - int(head_r * 0.15),
            head_cx + int(head_r * 0.62),
            head_cy + int(head_r * 0.63),
        ),
        fill=(226, 194, 173, 255),
    )

    d.rounded_rectangle(
        (
            center_x - int(shoulder_w * 0.54),
            base_y - int(shoulder_h * 0.72),
            center_x + int(shoulder_w * 0.54),
            base_y + int(height * 0.08),
        ),
        radius=int(width * 0.03),
        fill=(36, 58, 84, 255),
    )

    d.polygon(
        [
            (center_x, base_y - int(height * 0.20)),
            (center_x - int(width * 0.08), base_y + int(height * 0.02)),
            (center_x + int(width * 0.08), base_y + int(height * 0.02)),
        ],
        fill=(225, 230, 236, 235),
    )

    d.ellipse(
        (
            center_x - int(width * 0.10),
            base_y - int(height * 0.63),
            center_x + int(width * 0.10),
            base_y - int(height * 0.43),
        ),
        fill=(243, 212, 188, 80),
    )

    edge = art.filter(ImageFilter.GaussianBlur(radius=max(2, min(width, height) // 120)))
    return edge


def text_block(draw: ImageDraw.ImageDraw, w: int, h: int, area: Tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = area
    area_w = x1 - x0
    area_h = y1 - y0

    fs_series = max(20, int(area_h * 0.08))
    fs_title = max(36, int(area_h * 0.17))
    fs_sub = max(22, int(area_h * 0.10))
    fs_name = max(26, int(area_h * 0.11))
    fs_chip = max(16, int(area_h * 0.07))

    f_series = font(FONT_LIGHT, fs_series)
    f_title = font(FONT_SEMIBOLD, fs_title)
    f_sub = font(FONT_REGULAR, fs_sub)
    f_name = font(FONT_SEMIBOLD, fs_name)
    f_chip = font(FONT_LIGHT, fs_chip)

    y = y0
    draw.text((x0, y), CONTENT["series"].upper(), font=f_series, fill=(210, 224, 241, 230))
    y += int(fs_series * 1.5)

    title = CONTENT["title_short"].upper()
    max_w = int(area_w * 0.92)
    words = title.split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        tw = draw.textbbox((0, 0), candidate, font=f_title)[2]
        if tw <= max_w or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines[:3]:
        draw.text((x0, y), line, font=f_title, fill=(246, 248, 252, 255))
        y += int(fs_title * 1.04)

    y += int(fs_sub * 0.6)
    draw.text((x0, y), CONTENT["speaker"], font=f_name, fill=(227, 235, 246, 245))
    y += int(fs_name * 1.20)
    draw.text((x0, y), CONTENT["subtitle"], font=f_sub, fill=(196, 210, 228, 240))

    chip_y = y1 - int(fs_chip * 2.0)
    chip_x = x0
    for kw in CONTENT["keywords"]:
        label = f"#{kw}"
        bbox = draw.textbbox((0, 0), label, font=f_chip)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pad_x = int(fs_chip * 0.65)
        pad_y = int(fs_chip * 0.38)
        chip_w = tw + pad_x * 2
        chip_h = th + pad_y * 2
        draw.rounded_rectangle((chip_x, chip_y, chip_x + chip_w, chip_y + chip_h), radius=int(chip_h * 0.42), fill=(31, 50, 74, 188), outline=(125, 157, 194, 168), width=max(1, fs_chip // 10))
        draw.text((chip_x + pad_x, chip_y + pad_y - int(fs_chip * 0.06)), label, font=f_chip, fill=(216, 228, 243, 245))
        chip_x += chip_w + int(fs_chip * 0.45)


def compose_cover(width: int, height: int) -> Image.Image:
    img = make_background(width, height)

    portrait_layer = make_portrait(width, height)

    if width >= height:
        p_w = int(width * 0.44)
        p_h = int(height * 0.90)
        px = int(width * 0.54)
        py = int(height * 0.08)
        text_area = (int(width * 0.08), int(height * 0.14), int(width * 0.56), int(height * 0.90))
    else:
        if height / width >= 1.6:
            p_w = int(width * 0.90)
            p_h = int(height * 0.44)
            px = int(width * 0.05)
            py = int(height * 0.07)
            text_area = (int(width * 0.08), int(height * 0.50), int(width * 0.92), int(height * 0.92))
        else:
            p_w = int(width * 0.62)
            p_h = int(height * 0.46)
            px = int(width * 0.36)
            py = int(height * 0.08)
            text_area = (int(width * 0.08), int(height * 0.52), int(width * 0.92), int(height * 0.93))

    portrait = portrait_layer.resize((p_w, p_h), Image.Resampling.LANCZOS)

    shadow = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((0, 0, portrait.size[0], portrait.size[1]), radius=max(16, min(portrait.size) // 18), fill=(0, 0, 0, 105))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(10, min(portrait.size) // 30)))
    img.alpha_composite(shadow, (px + int(width * 0.008), py + int(height * 0.01)))
    img.alpha_composite(portrait, (px, py))

    d = ImageDraw.Draw(img, "RGBA")
    text_block(d, width, height, text_area)

    brand = "GOETHEANUM TV"
    bf = font(FONT_SEMIBOLD, max(14, int(min(width, height) * 0.028)))
    bw = d.textbbox((0, 0), brand, font=bf)[2]
    d.text((width - bw - int(width * 0.03), int(height * 0.04)), brand, font=bf, fill=(214, 226, 242, 220))

    return img


def save_layers(master_w: int = 1920, master_h: int = 1080) -> Dict[str, str]:
    bg = make_background(master_w, master_h)
    portrait = make_portrait(master_w, master_h)

    bg_path = os.path.join(LAYERS_DIR, "background.png")
    portrait_path = os.path.join(LAYERS_DIR, "portrait_cutout.png")

    bg.convert("RGB").save(bg_path, "PNG")
    portrait.save(portrait_path, "PNG")

    return {
        "background": bg_path,
        "portrait_cutout": portrait_path,
    }


def export_formats() -> List[Dict[str, str]]:
    items = []
    for spec in FORMATS:
        img = compose_cover(spec.width, spec.height)
        png_path = os.path.join(OUT_DIR, f"{spec.key}_{spec.width}x{spec.height}.png")
        jpg_path = os.path.join(OUT_DIR, f"{spec.key}_{spec.width}x{spec.height}.jpg")
        img.save(png_path, "PNG")
        img.convert("RGB").save(jpg_path, "JPEG", quality=95, optimize=True)
        items.append(
            {
                "key": spec.key,
                "label": spec.label,
                "width": spec.width,
                "height": spec.height,
                "png": png_path,
                "jpg": jpg_path,
            }
        )
    return items


def write_manifest(exports: List[Dict[str, str]], layers: Dict[str, str]) -> str:
    manifest = {
        "concept": "tv-cover-demo",
        "content": CONTENT,
        "exports": exports,
        "layers": layers,
        "notes": {
            "background": "synthetic blurry motif",
            "portrait": "synthetic generated portrait cutout",
            "style": "Goetheanum TV draft concept with safe text zones",
        },
    }
    path = os.path.join(OUT_DIR, "manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return path


def main() -> None:
    ensure_dirs()
    layers = save_layers()
    exports = export_formats()
    manifest = write_manifest(exports, layers)
    print(f"Generated {len(exports)} formats")
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()

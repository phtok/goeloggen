#!/usr/bin/env python3
import os
from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = "/Users/philipptok/goeloggen"
OUT = os.path.join(ROOT, "output", "tv_cover_demo_v2")
FONTS = {
    "light": os.path.join(ROOT, "assets", "fonts", "Titillium-LightUpright.otf"),
    "regular": os.path.join(ROOT, "assets", "fonts", "Titillium-RegularUpright.otf"),
    "semi": os.path.join(ROOT, "assets", "fonts", "Titillium-SemiboldUpright.otf"),
}

SERIES_DE = "Lebenskraefte\nder Sprache"
SERIES_EN = "Life Forces\nof Language"
EP_DE = "Sprechen\nund Leben"
EP_EN = "Speech\nand Life"
EP2_DE = "Aetherarten\nim Sprechen"
EP2_EN = "Ether in\nSpeech"


@dataclass
class Spec:
    name: str
    w: int
    h: int
    mode: str  # series | episode_single | episode_double | clean
    lang: str  # de | en | none


SPECS: List[Spec] = [
    Spec("01_series_16x9_de", 1920, 1080, "series", "de"),
    Spec("02_series_16x9_en", 1920, 1080, "series", "en"),
    Spec("03_episode1_16x9_de", 1920, 1080, "episode_single", "de"),
    Spec("04_episode1_16x9_en", 1920, 1080, "episode_single", "en"),
    Spec("05_episode1_portrait_de", 1188, 1682, "episode_single", "de"),
    Spec("06_episode1_portrait_en", 1188, 1682, "episode_single", "en"),
    Spec("07_episode1_story_clean", 1080, 1920, "clean", "none"),
    Spec("08_episode1_banner_clean", 1900, 800, "clean", "none"),
    Spec("09_episode1_square", 1080, 1080, "episode_single", "de"),
    Spec("10_episode2_16x9_de", 1920, 1080, "episode_double", "de"),
    Spec("11_episode2_16x9_en", 1920, 1080, "episode_double", "en"),
    Spec("12_episode2_story_clean", 1080, 1920, "clean2", "none"),
    Spec("13_episode2_banner_clean", 1900, 800, "clean2", "none"),
    Spec("14_episode2_square", 1080, 1080, "episode_double", "en"),
]


def f(key: str, size: int):
    return ImageFont.truetype(FONTS[key], size)


def make_bg(w: int, h: int) -> Image.Image:
    base = Image.new("RGBA", (w, h), (43, 56, 73, 255))
    d = ImageDraw.Draw(base, "RGBA")

    colors = [
        (187, 83, 54, 195),
        (106, 51, 45, 190),
        (202, 104, 40, 180),
        (90, 109, 115, 135),
    ]
    blobs = [
        (0.18, 0.18, 0.52),
        (0.62, 0.30, 0.56),
        (0.78, 0.72, 0.46),
        (0.28, 0.76, 0.44),
    ]
    for (cx, cy, s), c in zip(blobs, colors):
        r = int(min(w, h) * s)
        x = int(w * cx)
        y = int(h * cy)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)

    base = base.filter(ImageFilter.GaussianBlur(radius=max(34, min(w, h) // 9)))

    tone = Image.new("RGBA", (w, h), (50, 24, 19, 70))
    base = Image.alpha_composite(base, tone)

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.rectangle((0, int(h * 0.86), w, h), fill=(224, 129, 18, 165))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(15, min(w, h) // 20)))
    base = Image.alpha_composite(base, glow)

    vign = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vign)
    m = int(min(w, h) * 0.03)
    vd.rectangle((m, m, w - m, h - m), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(radius=max(25, min(w, h) // 10)))
    dark = Image.new("RGBA", (w, h), (19, 25, 33, 130))
    base = Image.composite(dark, base, vign)
    return base


def draw_frame(img: Image.Image):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    margin = int(min(w, h) * 0.032)
    stroke = max(2, int(min(w, h) * 0.0045))
    rad = int(min(w, h) * 0.022)
    d.rounded_rectangle((margin, margin, w - margin, h - margin), radius=rad, outline=(226, 233, 240, 240), width=stroke)


def draw_head(d: ImageDraw.ImageDraw, x: int, y: int, s: float, variant: int = 1):
    skin = (230, 195, 171, 255) if variant == 1 else (229, 199, 176, 255)
    hair = (88, 88, 87, 255) if variant == 1 else (84, 60, 44, 255)
    jacket = (38, 72, 118, 255) if variant == 1 else (165, 63, 58, 255)
    shirt = (236, 239, 242, 250)

    # torso
    d.rounded_rectangle((x - 220 * s, y + 110 * s, x + 220 * s, y + 560 * s), radius=48 * s, fill=jacket)
    d.polygon([(x, y + 160 * s), (x - 66 * s, y + 290 * s), (x + 66 * s, y + 290 * s)], fill=shirt)

    # neck
    d.rounded_rectangle((x - 38 * s, y + 78 * s, x + 38 * s, y + 165 * s), radius=16 * s, fill=skin)

    # head
    d.ellipse((x - 110 * s, y - 130 * s, x + 110 * s, y + 100 * s), fill=skin)

    # hair cap
    d.pieslice((x - 130 * s, y - 160 * s, x + 130 * s, y + 78 * s), start=195, end=360, fill=hair)
    d.ellipse((x - 118 * s, y - 96 * s, x + 118 * s, y + 94 * s), fill=skin)


def draw_single_portrait_layer(w: int, h: int) -> Image.Image:
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(p, "RGBA")
    scale = min(w, h) / 1080
    cx = int(w * 0.74)
    cy = int(h * 0.50)
    draw_head(d, cx, cy, scale, variant=1)
    return p


def draw_double_portrait_layer(w: int, h: int) -> Image.Image:
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(p, "RGBA")
    scale = min(w, h) / 1080
    draw_head(d, int(w * 0.66), int(h * 0.53), scale * 0.92, variant=2)
    draw_head(d, int(w * 0.82), int(h * 0.53), scale * 0.92, variant=1)
    return p


def text_block(img: Image.Image, title: str, compact: bool = False):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")

    if w / h >= 1.6:
        x = int(w * 0.09)
        y = int(h * 0.20)
        fs = int(h * (0.115 if compact else 0.13))
    elif h / w > 1.35:
        x = int(w * 0.12)
        y = int(h * 0.07)
        fs = int(w * 0.112)
    else:
        x = int(w * 0.10)
        y = int(h * 0.13)
        fs = int(min(w, h) * 0.12)

    fs = max(54, min(170, fs))
    font_title = f("semi", fs)

    shadow = (16, 21, 30, 150)
    col = (244, 247, 250, 245)

    yy = y
    for line in title.split("\n"):
        d.text((x + 2, yy + 2), line, font=font_title, fill=shadow)
        d.text((x, yy), line, font=font_title, fill=col)
        yy += int(fs * 0.96)


def badge_tv(img: Image.Image):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    fs = max(26, int(min(w, h) * 0.06))
    ff = f("semi", fs)
    text = "tv"
    tw = d.textbbox((0, 0), text, font=ff)[2]
    pad = int(fs * 0.45)
    x = int(w * 0.12)
    y = int(h * 0.06)
    d.ellipse((x, y, x + tw + pad * 2, y + fs + pad * 1.4), fill=(238, 244, 250, 220))
    d.text((x + pad, y + pad * 0.2), text, font=ff, fill=(84, 50, 44, 255))


def compose(spec: Spec) -> Image.Image:
    img = make_bg(spec.w, spec.h)

    if spec.mode == "series":
        title = SERIES_DE if spec.lang == "de" else SERIES_EN
        text_block(img, title)

    elif spec.mode == "episode_single":
        p = draw_single_portrait_layer(spec.w, spec.h)
        sh = p.filter(ImageFilter.GaussianBlur(radius=max(6, min(spec.w, spec.h) // 120)))
        img.alpha_composite(sh, (int(spec.w * 0.003), int(spec.h * 0.007)))
        img.alpha_composite(p)
        title = EP_DE if spec.lang == "de" else EP_EN
        text_block(img, title, compact=True)

    elif spec.mode == "episode_double":
        p = draw_double_portrait_layer(spec.w, spec.h)
        sh = p.filter(ImageFilter.GaussianBlur(radius=max(6, min(spec.w, spec.h) // 120)))
        img.alpha_composite(sh, (int(spec.w * 0.003), int(spec.h * 0.007)))
        img.alpha_composite(p)
        title = EP2_DE if spec.lang == "de" else EP2_EN
        text_block(img, title, compact=True)

    elif spec.mode == "clean":
        p = draw_single_portrait_layer(spec.w, spec.h)
        img.alpha_composite(p)
        badge_tv(img)

    elif spec.mode == "clean2":
        p = draw_double_portrait_layer(spec.w, spec.h)
        img.alpha_composite(p)
        badge_tv(img)

    draw_frame(img)
    return img


def build_contact_sheet(paths: List[str], out_path: str):
    thumbs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        thumbs.append((os.path.basename(p), im))

    cols = 4
    tw = 420
    th = 236
    gap = 18
    label_h = 42
    rows = (len(thumbs) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * (th + label_h) + (rows + 1) * gap), (25, 33, 44))
    d = ImageDraw.Draw(canvas)
    lf = f("regular", 24)

    for i, (name, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap)
        y = gap + r * (th + label_h + gap)

        scale = min(tw / im.width, th / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        rs = im.resize((nw, nh), Image.Resampling.LANCZOS)
        frame = Image.new("RGB", (tw, th), (46, 58, 74))
        frame.paste(rs, ((tw - nw) // 2, (th - nh) // 2))
        canvas.paste(frame, (x, y))
        d.rectangle((x, y, x + tw, y + th), outline=(95, 111, 133), width=2)
        d.text((x, y + th + 7), name, font=lf, fill=(220, 229, 240))

    canvas.save(out_path)


def main():
    os.makedirs(OUT, exist_ok=True)
    out_files = []
    for spec in SPECS:
        img = compose(spec)
        p = os.path.join(OUT, f"{spec.name}_{spec.w}x{spec.h}.png")
        img.convert("RGB").save(p, "PNG")
        out_files.append(p)

    sheet = os.path.join(OUT, "_contactsheet_v2.png")
    build_contact_sheet(out_files, sheet)

    # comparison with previous attempt
    comp = Image.new("RGB", (2200, 1250), (20, 27, 36))
    d = ImageDraw.Draw(comp)
    title_f = f("semi", 44)
    sub_f = f("regular", 28)
    d.text((70, 42), "Vorher (V1) vs. Neu (V2)", font=title_f, fill=(238, 244, 250))

    old = Image.open(os.path.join(ROOT, "output", "tv_cover_demo", "goetheanum_tv_cover_740x420.png")).convert("RGB").resize((980, 556), Image.Resampling.LANCZOS)
    new = Image.open(os.path.join(OUT, "03_episode1_16x9_de_1920x1080.png")).convert("RGB").resize((980, 556), Image.Resampling.LANCZOS)
    comp.paste(old, (70, 160))
    comp.paste(new, (1150, 160))
    d.text((70, 740), "V1: generisch, zu redaktionell, zu viele Meta-Infos", font=sub_f, fill=(196, 210, 226))
    d.text((1150, 740), "V2: Reihen-System, kurzes Schlagwort + Gesicht, formatstabil", font=sub_f, fill=(196, 210, 226))

    old2 = Image.open(os.path.join(ROOT, "output", "tv_cover_demo", "instagram_story_1080x1920.png")).convert("RGB").resize((420, 746), Image.Resampling.LANCZOS)
    new2 = Image.open(os.path.join(OUT, "07_episode1_story_clean_1080x1920.png")).convert("RGB").resize((420, 746), Image.Resampling.LANCZOS)
    comp.paste(old2, (350, 440))
    comp.paste(new2, (1430, 440))

    comp.save(os.path.join(OUT, "_comparison_v1_vs_v2.png"))

    print(f"generated {len(out_files)} files")
    print(sheet)


if __name__ == "__main__":
    main()

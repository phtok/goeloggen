#!/usr/bin/env python3
"""Create a natural, brand-consistent portrait without hard cutout artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def _clamp_crop(
    x0: int, y0: int, width: int, height: int, image_width: int, image_height: int
) -> tuple[int, int, int, int]:
    x0 = max(0, min(x0, image_width - width))
    y0 = max(0, min(y0, image_height - height))
    return x0, y0, x0 + width, y0 + height


def detect_largest_face(image: np.ndarray) -> tuple[int, int, int, int]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = classifier.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=6,
        minSize=(40, 40),
    )
    if len(faces) == 0:
        h, w = image.shape[:2]
        size = int(min(h, w) * 0.3)
        return (w // 2 - size // 2, h // 4 - size // 2, size, size)
    return max(faces, key=lambda face: int(face[2]) * int(face[3]))


def compute_brand_crop(image: np.ndarray, face: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    h, w = image.shape[:2]
    fx, fy, fw, fh = face

    crop_h = min(h, max(int(fh * 3.8), int(h * 0.9)))
    crop_w = int(crop_h * 0.8)  # 4:5
    if crop_w > w:
        crop_w = w
        crop_h = int(crop_w / 0.8)
    if crop_h > h:
        crop_h = h
        crop_w = int(crop_h * 0.8)

    # Shift slightly to the right to avoid leftover group edges on the left.
    cx = int(fx + fw * 0.72)
    cy = int(fy + fh * 1.42)

    x0 = cx - crop_w // 2
    y0 = cy - crop_h // 2
    x0, y0, x1, y1 = _clamp_crop(x0, y0, crop_w, crop_h, w, h)

    min_left = int(w * 0.22)
    if x0 < min_left:
        x0 = min_left
        if x0 + crop_w > w:
            crop_w = w - x0
            crop_h = int(crop_w / 0.8)
            if crop_h > h:
                crop_h = h
                crop_w = int(crop_h * 0.8)
            y0 = max(0, min(y0, h - crop_h))
        x1 = x0 + crop_w
        y1 = y0 + crop_h
    return x0, y0, x1, y1


def white_balance(image: np.ndarray) -> np.ndarray:
    f32 = image.astype(np.float32) / 255.0
    means = f32.reshape(-1, 3).mean(axis=0)
    gray = float(means.mean())
    scales = np.clip(gray / (means + 1e-6), 0.9, 1.1)
    balanced = f32 * scales.reshape(1, 1, 3)
    return np.clip(balanced * 255.0, 0.0, 255.0).astype(np.uint8)


def suppress_edge_remnants(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    out = image.copy()
    left_w = int(w * 0.085)
    if left_w > 10:
        ref = out[:, left_w : left_w * 2]
        ref = cv2.GaussianBlur(ref, (0, 0), 6.0)
        fill = cv2.resize(ref, (left_w, h), interpolation=cv2.INTER_LINEAR)
        alpha = np.linspace(1.0, 0.0, left_w, dtype=np.float32).reshape(1, left_w, 1)
        out[:, :left_w] = (
            fill.astype(np.float32) * alpha + out[:, :left_w].astype(np.float32) * (1.0 - alpha)
        ).astype(np.uint8)
    return out


def tone_and_detail(image: np.ndarray) -> np.ndarray:
    denoised = cv2.bilateralFilter(image, d=0, sigmaColor=12, sigmaSpace=6)

    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    graded = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # Mild cinematic contrast curve.
    f = graded.astype(np.float32) / 255.0
    f = np.clip((f - 0.5) * 1.08 + 0.52, 0.0, 1.0)
    f[..., 2] *= 1.01  # tiny warmth
    f[..., 0] *= 0.99
    graded = np.clip(f * 255.0, 0.0, 255.0).astype(np.uint8)

    blur = cv2.GaussianBlur(graded, (0, 0), 0.9)
    return cv2.addWeighted(graded, 1.22, blur, -0.22, 0)


def focus_blend(
    image: np.ndarray, face: tuple[int, int, int, int], crop_offset: tuple[int, int]
) -> np.ndarray:
    x_off, y_off = crop_offset
    fx, fy, fw, fh = face
    cx = int(fx - x_off + fw / 2)
    cy = int(fy - y_off + fh / 2)

    h, w = image.shape[:2]
    sharp = image
    soft = cv2.GaussianBlur(image, (0, 0), 2.2)

    mask = np.zeros((h, w), np.float32)
    cv2.ellipse(
        mask,
        center=(cx, cy + int(fh * 0.12)),
        axes=(max(35, int(fw * 1.15)), max(45, int(fh * 1.55))),
        angle=0,
        startAngle=0,
        endAngle=360,
        color=1.0,
        thickness=-1,
    )
    mask = cv2.GaussianBlur(mask, (0, 0), 28.0)[..., None]
    return np.clip(
        sharp.astype(np.float32) * mask + soft.astype(np.float32) * (1.0 - mask), 0.0, 255.0
    ).astype(np.uint8)


def finalize(image: np.ndarray) -> np.ndarray:
    out = cv2.resize(image, (1200, 1500), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
    h, w = out.shape[:2]
    x = np.linspace(-1.0, 1.0, w, dtype=np.float32)
    y = np.linspace(-1.0, 1.0, h, dtype=np.float32)
    xg, yg = np.meshgrid(x, y)
    vignette = 1.0 - 0.06 * (xg**2 + yg**2)
    out *= np.clip(vignette, 0.92, 1.0)[..., None]

    grain = np.random.default_rng(7).normal(0.0, 0.006, out.shape).astype(np.float32)
    out = np.clip(out + grain, 0.0, 1.0)
    return (out * 255.0).astype(np.uint8)


def run(input_path: Path, output_path: Path) -> None:
    source = cv2.imread(str(input_path))
    if source is None:
        raise FileNotFoundError(f"Input image not found or unreadable: {input_path}")

    face = detect_largest_face(source)
    x0, y0, x1, y1 = compute_brand_crop(source, face)
    crop = source[y0:y1, x0:x1].copy()

    balanced = white_balance(crop)
    graded = tone_and_detail(balanced)
    finished = finalize(graded)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), finished, [int(cv2.IMWRITE_JPEG_QUALITY), 95])


def main() -> None:
    parser = argparse.ArgumentParser(description="Create natural studio-like portrait variant.")
    parser.add_argument("--input", required=True, type=Path, help="Path to source image")
    parser.add_argument("--output", required=True, type=Path, help="Path to output image")
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()

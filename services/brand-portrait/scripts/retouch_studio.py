#!/usr/bin/env python3
"""Create a cleaner, studio-like brand portrait from a single source image."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def clamp_crop(
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


def compute_crop(image: np.ndarray, face: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    h, w = image.shape[:2]
    fx, fy, fw, fh = face

    crop_h = min(h, max(int(fh * 3.6), int(h * 0.84)))
    crop_w = int(crop_h * 0.8)  # 4:5
    if crop_w > w:
        crop_w = w
        crop_h = int(crop_w / 0.8)
    if crop_h > h:
        crop_h = h
        crop_w = int(crop_h * 0.8)

    cx = int(fx + fw * 0.57)
    cy = int(fy + fh * 1.35)

    x0 = cx - crop_w // 2
    y0 = cy - crop_h // 2
    x0, y0, x1, y1 = clamp_crop(x0, y0, crop_w, crop_h, w, h)

    # Keep a little safer margin from the extreme left where group-photo leftovers appear.
    min_left = int(w * 0.06)
    if x0 < min_left:
        x0 = min_left
        x1 = x0 + crop_w
        if x1 > w:
            x1 = w
            x0 = x1 - crop_w
    return x0, y0, x1, y1


def build_subject_mask(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (int(w * 0.08), int(h * 0.03), int(w * 0.84), int(h * 0.94))

    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(image, mask, rect, bg_model, fg_model, 5, cv2.GC_INIT_WITH_RECT)
        subject = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1.0, 0.0)
    except cv2.error:
        subject = np.zeros((h, w), np.float32)
        cv2.ellipse(
            subject,
            center=(w // 2, int(h * 0.56)),
            axes=(int(w * 0.35), int(h * 0.48)),
            angle=0,
            startAngle=0,
            endAngle=360,
            color=1.0,
            thickness=-1,
        )

    subject_u8 = (subject * 255).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(subject_u8, connectivity=8)
    if num_labels > 1:
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        subject = (labels == largest).astype(np.float32)

    # Force lower torso into foreground to avoid "misty" falloff in jacket area.
    h, w = image.shape[:2]
    subject_bin = (subject > 0.45).astype(np.uint8)
    cv2.rectangle(
        subject_bin,
        (int(w * 0.24), int(h * 0.48)),
        (int(w * 0.76), int(h * 0.995)),
        color=1,
        thickness=-1,
    )
    kernel = np.ones((5, 5), np.uint8)
    subject_bin = cv2.morphologyEx(subject_bin, cv2.MORPH_CLOSE, kernel, iterations=2)
    subject = cv2.GaussianBlur(subject_bin.astype(np.float32), (0, 0), 5.0)
    subject = np.clip(subject, 0.0, 1.0)
    return subject[..., None]


def white_balance(image: np.ndarray) -> np.ndarray:
    image = image.astype(np.float32) / 255.0
    channel_means = image.reshape(-1, 3).mean(axis=0)
    gray_mean = float(channel_means.mean())
    scales = np.clip(gray_mean / (channel_means + 1e-6), 0.92, 1.08)
    balanced = image * scales.reshape(1, 1, 3)
    return np.clip(balanced, 0.0, 1.0)


def enhance_subject(image: np.ndarray) -> np.ndarray:
    denoised = cv2.bilateralFilter(image, d=0, sigmaColor=22, sigmaSpace=7)
    blurred = cv2.GaussianBlur(denoised, (0, 0), 1.0)
    sharpened = cv2.addWeighted(denoised, 1.22, blurred, -0.22, 0)

    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB).astype(np.float32)
    l_channel = lab[..., 0]
    l_channel = np.clip((l_channel - 127.0) * 1.06 + 127.0, 0.0, 255.0)
    lab[..., 0] = l_channel
    graded = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    return graded


def _studio_background(height: int, width: int) -> np.ndarray:
    top = np.array([212.0, 214.0, 216.0], dtype=np.float32)  # BGR
    bottom = np.array([176.0, 184.0, 192.0], dtype=np.float32)

    y = np.linspace(0.0, 1.0, height, dtype=np.float32).reshape(height, 1, 1)
    gradient = top * (1.0 - y) + bottom * y
    bg = np.repeat(gradient, width, axis=1)

    x = np.linspace(-1.0, 1.0, width, dtype=np.float32)
    x_grid, y_grid = np.meshgrid(x, np.linspace(-1.0, 1.0, height, dtype=np.float32))
    spotlight = np.exp(-(((x_grid * 0.92) ** 2) + ((y_grid + 0.22) ** 2)) / 0.34)
    bg += (spotlight[..., None] * 18.0).astype(np.float32)

    noise = np.random.default_rng(42).normal(0.0, 1.5, (height, width, 1)).astype(np.float32)
    noise = cv2.GaussianBlur(noise, (0, 0), 2.0)
    if noise.ndim == 2:
        noise = noise[..., None]
    bg += np.repeat(noise, 3, axis=2)
    return np.clip(bg, 0.0, 255.0).astype(np.uint8)


def stylize_background(image: np.ndarray, mode: str) -> np.ndarray:
    if mode == "studio":
        h, w = image.shape[:2]
        return _studio_background(h, w)

    background = cv2.GaussianBlur(image, (0, 0), 4.2)
    hsv = cv2.cvtColor(background, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 0.78
    hsv[..., 2] *= 0.97
    toned = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Clean group-photo remnants near edges by replacing with blurred nearby texture.
    h, w = toned.shape[:2]
    left_w = int(w * 0.11)
    right_w = int(w * 0.07)
    if left_w > 8:
        ref = toned[:, left_w : left_w * 2]
        ref = cv2.GaussianBlur(ref, (0, 0), 8.0)
        toned[:, :left_w] = cv2.resize(ref, (left_w, h), interpolation=cv2.INTER_LINEAR)
    if right_w > 8:
        ref = toned[:, w - right_w * 2 : w - right_w]
        ref = cv2.GaussianBlur(ref, (0, 0), 8.0)
        toned[:, w - right_w :] = cv2.resize(ref, (right_w, h), interpolation=cv2.INTER_LINEAR)
    return toned


def apply_global_finish(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    out = image.astype(np.float32) / 255.0

    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)
    x_grid, y_grid = np.meshgrid(xx, np.linspace(-1.0, 1.0, h, dtype=np.float32))
    vignette = 1.0 - 0.05 * (x_grid**2 + y_grid**2)
    out *= np.clip(vignette, 0.95, 1.0)[..., None]

    out = np.clip(out, 0.0, 1.0)
    out = (out * 255.0).astype(np.uint8)
    final_blur = cv2.GaussianBlur(out, (0, 0), 1.0)
    return cv2.addWeighted(out, 1.15, final_blur, -0.15, 0)


def run(input_path: Path, output_path: Path, background_mode: str) -> None:
    source = cv2.imread(str(input_path))
    if source is None:
        raise FileNotFoundError(f"Input image not found or unreadable: {input_path}")

    face = detect_largest_face(source)
    x0, y0, x1, y1 = compute_crop(source, face)
    crop = source[y0:y1, x0:x1].copy()

    subject_mask = build_subject_mask(crop)
    balanced = (white_balance(crop) * 255.0).astype(np.uint8)
    subject = enhance_subject(balanced)
    background = stylize_background(balanced, mode=background_mode)

    composed = subject.astype(np.float32) * subject_mask + background.astype(np.float32) * (
        1.0 - subject_mask
    )

    # Slight lift in face area to keep eyes/skin alive after background calming.
    face_in_crop = (face[0] - x0, face[1] - y0, face[2], face[3])
    fx, fy, fw, fh = face_in_crop
    h, w = crop.shape[:2]
    skin_lift = np.zeros((h, w), np.float32)
    cv2.ellipse(
        skin_lift,
        center=(fx + fw // 2, fy + fh // 2),
        axes=(int(fw * 0.75), int(fh * 0.9)),
        angle=0,
        startAngle=0,
        endAngle=360,
        color=1.0,
        thickness=-1,
    )
    skin_lift = cv2.GaussianBlur(skin_lift, (0, 0), 9.0)[..., None]
    composed = np.clip(composed + skin_lift * 6.0, 0.0, 255.0).astype(np.uint8)

    upscaled = cv2.resize(composed, (1200, 1500), interpolation=cv2.INTER_CUBIC)
    finished = apply_global_finish(upscaled)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), finished, [int(cv2.IMWRITE_JPEG_QUALITY), 95])


def main() -> None:
    parser = argparse.ArgumentParser(description="Create studio-like portrait variant.")
    parser.add_argument("--input", required=True, type=Path, help="Path to source image")
    parser.add_argument("--output", required=True, type=Path, help="Path to output image")
    parser.add_argument(
        "--background",
        choices=["studio", "stairs"],
        default="studio",
        help="Background style",
    )
    args = parser.parse_args()
    run(args.input, args.output, args.background)


if __name__ == "__main__":
    main()

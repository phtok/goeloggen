#!/usr/bin/env python3
import os
import cv2
import numpy as np

ROOT = '/Users/philipptok/goeloggen'
SRC_DIR = '/tmp/testcx_lebenskraefte'
OUT_DIR = os.path.join(ROOT, 'assets', 'tv_cutouts')


def extract(src_path: str, rect: tuple[int, int, int, int], keep_components: int, out_name: str) -> str:
    img = cv2.imread(src_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(src_path)

    mask = np.zeros(img.shape[:2], np.uint8)
    bg = np.zeros((1, 65), np.float64)
    fg = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bg, fg, 7, cv2.GC_INIT_WITH_RECT)

    # probable/definite foreground
    m = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 255).astype(np.uint8)

    k = np.ones((5, 5), np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k, iterations=1)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=2)

    # keep largest connected components (single:1, double:2)
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats((m > 0).astype(np.uint8), connectivity=8)
    if n_labels > 1:
        areas = [(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, n_labels)]
        areas.sort(key=lambda t: t[1], reverse=True)
        keep = {i for i, _ in areas[:keep_components]}
        cleaned = np.zeros_like(m)
        for i in keep:
            cleaned[labels == i] = 255
        m = cleaned

    # soften alpha edges
    alpha = cv2.GaussianBlur(m, (0, 0), sigmaX=1.2, sigmaY=1.2)

    ys, xs = np.where(alpha > 6)
    if len(xs) == 0 or len(ys) == 0:
        raise RuntimeError(f'No foreground extracted from {src_path}')

    x0, x1 = max(0, xs.min() - 8), min(alpha.shape[1], xs.max() + 9)
    y0, y1 = max(0, ys.min() - 8), min(alpha.shape[0], ys.max() + 9)

    crop = img[y0:y1, x0:x1]
    a_crop = alpha[y0:y1, x0:x1]

    rgba = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = a_crop

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, out_name)
    cv2.imwrite(out_path, rgba)
    return out_path


def main() -> None:
    single_src = os.path.join(SRC_DIR, '8.png')
    double_src = os.path.join(SRC_DIR, '14.png')

    single_path = extract(single_src, rect=(1080, 110, 760, 680), keep_components=1, out_name='single_person_cutout.png')
    double_path = extract(double_src, rect=(900, 95, 980, 700), keep_components=2, out_name='double_people_cutout.png')

    print(single_path)
    print(double_path)


if __name__ == '__main__':
    main()

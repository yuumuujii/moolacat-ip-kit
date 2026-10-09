"""把图里藏蓝针织帽的颜色换成固定颜色，保留原有的明暗和笔触。

整顶帽子区域统一换色相（不留灰斑），饱和度和明度按「目标色 / 原中位色」等比例调整。
颜色默认读 modes.json 里 life.beanie_color；输出默认在原图旁边加 -recolored 后缀。

用法:
  python scripts/recolor_beanie.py <图片路径> [输出路径] [--color #RRGGBB]
例:
  python scripts/recolor_beanie.py ~/Downloads/生活形态01.jpg
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

import os
ROOT = Path(os.environ.get("IP_IDENTITY_DIR", Path(__file__).resolve().parent.parent / "identity")).resolve()


def hat_mask(rgb: np.ndarray) -> np.ndarray:
    """帽子区域：蓝色像素闭运算后的大连通块，再去掉其中的头发（棕色）和皮肤。"""
    import cv2
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    blue = ((h > 95) & (h < 135) & (s > 45)).astype(np.uint8)
    closed = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(closed)
    region = np.zeros(blue.shape, bool)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 8000:
            region |= lab == i
    warm = (h < 35) & (s > 60)            # 头发、皮肤这类暖色不动
    return region & ~warm


def recolor(src: Path, dst: Path, target_hex: str):
    rgb = np.asarray(Image.open(src).convert("RGB")).copy()
    region = hat_mask(rgb)
    if region.sum() < 2000:
        raise SystemExit(f"{src} 里没找到明显的蓝色帽子，未处理")
    hsv = np.asarray(Image.fromarray(rgb).convert("HSV")).astype(float)
    s, v = hsv[..., 1], hsv[..., 2]
    t = np.asarray(Image.new("RGB", (1, 1), target_hex).convert("HSV")).astype(float)[0, 0]
    core = region & (s > 64)               # 用纯色部分算比例，避免线条和高光干扰
    out = hsv.copy()
    out[..., 0][region] = t[0]             # 整个帽子区域统一色相，不留灰斑
    out[..., 1][region] = np.clip(np.maximum(s[region], 40) * t[1] / np.median(s[core]), 0, 255)
    out[..., 2][region] = np.clip(v[region] * t[2] / np.median(v[core]), 0, 255)
    Image.fromarray(out.astype("uint8"), "HSV").convert("RGB").save(dst)
    print("saved", dst)


if __name__ == "__main__":
    default_color = json.loads((ROOT / "modes.json").read_text(encoding="utf-8")).get("life", {}).get("beanie_color", "#6B82A6")
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path, nargs="?")
    ap.add_argument("--color", default=default_color)
    a = ap.parse_args()
    src = a.src.expanduser()
    if not src.exists():
        raise SystemExit(f"找不到图片：{src}（请把命令里的路径换成实际图片的位置）")
    dst = a.dst.expanduser() if a.dst else src.with_name(f"{src.stem}-recolored.png")
    recolor(src, dst, a.color)

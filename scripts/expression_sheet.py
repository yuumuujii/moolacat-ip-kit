"""角色表情概览表（Expression Sheet）：1920×1080，和 Character Mode Sheet 同一套纸底、字体与手绘圆弧。

表情图来自 identity/expressions/；生活形态戴帽的图会先把帽子统一成固定色。
用法: .venv/bin/python scripts/expression_sheet.py [输出路径]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw
from rembg import new_session, remove

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mode_sheet import H, INK, PAPER, REPO, W, WHITE, halo, text   # noqa: E402
from recolor_beanie import hat_mask   # noqa: E402

# 配色：Tangerine + Slate Blue（cover/colors.json 里的配方），生活=橘、科技=石板蓝
LIFE, LIFE_LIGHT = (228, 108, 45), (244, 200, 170)
TECH, TECH_LIGHT = (71, 115, 165), (180, 200, 222)

CARDS = [  # (文件, 形态, 表情名)
    ("life-side-eye.jpg", "life", "斜眼怀疑"),
    ("life-grin.jpg", "life", "开心大笑"),
    ("life-smirk-cheek.jpg", "life", "托腮坏笑"),
    ("life-nose-push.jpg", "life", "推鼻不服"),
    ("tech-puff-shock.jpg", "tech", "瞪眼鼓腮"),
    ("tech-pout-cheeks.jpg", "tech", "捧脸无奈"),
]
COLS, ROWS = 3, 2
TOP, BOTTOM = 190, 1080
CELL_W, CELL_H = W // COLS, (BOTTOM - TOP) // ROWS
HEAD_H = 430
SESSION = new_session("isnet-anime")


def unify_beanie(im: Image.Image) -> Image.Image:
    """帽子统一成 #6B82A6（和 identity/modes.json 一致）。"""
    rgb = np.asarray(im.convert("RGB")).copy()
    region = hat_mask(rgb)
    if region.sum() < 2000:
        return im
    hsv = np.asarray(Image.fromarray(rgb).convert("HSV")).astype(float)
    t = np.asarray(Image.new("RGB", (1, 1), "#6B82A6").convert("HSV")).astype(float)[0, 0]
    s, v = hsv[..., 1], hsv[..., 2]
    core = region & (s > 64)
    hsv[..., 0][region] = t[0]
    hsv[..., 1][region] = np.clip(np.maximum(s[region], 40) * t[1] / np.median(s[core]), 0, 255)
    hsv[..., 2][region] = np.clip(v[region] * t[2] / np.median(v[core]), 0, 255)
    return Image.fromarray(hsv.astype("uint8"), "HSV").convert("RGB")


def head(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    if path.name.startswith("life"):
        im = unify_beanie(im)
    mask = remove(im, session=SESSION, only_mask=True)
    # 抠图偶尔会把浅色纸底留下：和画面边缘连通的近白区域一律透明
    import cv2
    a = np.asarray(im)
    bgish = ((a.min(axis=2) > 222) & ((a.max(axis=2).astype(int) - a.min(axis=2)) < 18)).astype(np.uint8)
    n, lab = cv2.connectedComponents(bgish)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = np.asarray(mask).copy(); m[np.isin(lab, list(edge))] = 0
    mask = Image.fromarray(m)
    s = HEAD_H / im.height
    im, mask = im.resize((int(im.width * s), HEAD_H), Image.LANCZOS), mask.resize((int(im.width * s), HEAD_H), Image.LANCZOS)
    fade = Image.linear_gradient("L").resize(im.size).point(lambda v: 255 if v < 170 else max(0, int(255 - (v - 170) * 3)))
    out = im.convert("RGBA")
    out.putalpha(ImageChops.multiply(mask, fade))
    return out


def build(out: Path):
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    text(d, (W / 2, 28), "Expression Sheet", 84, INK, anchor="ma")
    d.line([(W / 2 - 280, 136), (W / 2 + 280, 136)], fill=LIFE_LIGHT, width=6)
    text(d, (W / 2, 148), "角色表情概览", 34, (110, 110, 110), anchor="ma")
    # 图例
    for k, (name, c) in enumerate((("生活随笔", LIFE), ("科技金融", TECH))):
        x = W - 330 + k * 160
        d.ellipse((x, 160, x + 22, 182), fill=c)
        text(d, (x + 30, 152), name, 26, c)

    for i, (fname, mode, label) in enumerate(CARDS):
        col, row = i % COLS, i // COLS
        cx, y0 = CELL_W * col + CELL_W / 2, TOP + CELL_H * row
        color, light = (LIFE, LIFE_LIGHT) if mode == "life" else (TECH, TECH_LIGHT)
        h = head(REPO / "identity" / "expressions" / fname)
        y0 = y0 - 10
        hy = y0 + HEAD_H * 0.45
        halo(canvas, cx + 40, hy, h.width * 0.44, WHITE, seed=40 + i)
        halo(canvas, cx + 45, hy + 5, h.width * 0.48, light, seed=60 + i)
        canvas.alpha_composite(h, (int(cx - h.width / 2 + 40), int(y0)))
        d = ImageDraw.Draw(canvas)
        # 表情名放在头像左上角，序号 + 名称
        text(d, (cx - CELL_W / 2 + 36, y0 + 40), f"{i + 1:02d}", 30, color, stroke=5)
        text(d, (cx - CELL_W / 2 + 36, y0 + 78), label, 40, color, stroke=6)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out)


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "docs" / "expression-sheet.jpg")

"""Q 版概览（Chibi Sheet）：1920×1080，和 Character Mode Sheet 同一套纸底与字体。

叙事：左边正常比例全身（约 7.5 头身）→ 箭头「Q 版化」→ 右边两张 Q 版（约 2.5 头身），
脚底对齐在同一条地面线上，方便看出比例变化。
用法: .venv/bin/python scripts/chibi_sheet.py [输出路径]
"""
import math
import random
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from rembg import new_session, remove

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mode_sheet import H, INK, PAPER, REPO, W, text   # noqa: E402

# 配色：Cyan + Brick Red（cover/colors.json 里的配方）
MAIN, ACCENT = (21, 157, 218), (182, 64, 50)
MAIN_LIGHT = (176, 214, 233)
GREY = (110, 110, 110)

POSES = REPO / "identity" / "chibi-poses"
GROUND = 1035                 # 地面线：所有人物脚底对齐
SESSION = new_session("isnet-anime")


def figure(path: Path, height: int) -> Image.Image:
    """抠图 → 裁到人物范围 → 缩放到指定高度。"""
    im = Image.open(path).convert("RGB")
    mask = np.asarray(remove(im, session=SESSION, only_mask=True)).copy()
    a = np.asarray(im)
    bgish = ((a.min(axis=2) > 222) & ((a.max(axis=2).astype(int) - a.min(axis=2)) < 18)).astype(np.uint8)
    n, lab = cv2.connectedComponents(bgish)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    mask[np.isin(lab, list(edge))] = 0
    m = Image.fromarray(mask)
    box = m.point(lambda v: 255 if v > 160 else 0).getbbox()   # 只按实心部分裁，忽略飘散的淡色杂点
    cut = im.convert("RGBA"); cut.putalpha(m)
    cut = cut.crop(box)
    s = height / cut.height
    return cut.resize((int(cut.width * s), height), Image.LANCZOS)


def hand_arrow(d, x0, x1, y, color, seed=3):
    """手绘横向粗箭头，略带起伏。"""
    rnd = random.Random(seed)
    pts = [(x, y + 10 * math.sin((x - x0) / (x1 - x0) * math.pi) * -1 + rnd.uniform(-1, 1))
           for x in range(x0, x1 + 1, 6)]
    d.line(pts, fill=color, width=9, joint="curve")
    bx, by = pts[-1]
    for s in (-1, 1):
        d.line([(bx, by), (bx - 34, by + s * 26)], fill=color, width=9)


def build(out: Path):
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    text(d, (W / 2, 28), "Chibi Sheet", 84, INK, anchor="ma")
    d.line([(W / 2 - 230, 136), (W / 2 + 230, 136)], fill=MAIN_LIGHT, width=6)
    text(d, (W / 2, 148), "Q 版形象概览 · 科技金融形态", 34, GREY, anchor="ma")

    # 地面线（淡色手绘感）
    rnd = random.Random(9)
    d.line([(x, GROUND + rnd.uniform(-1.5, 1.5)) for x in range(90, W - 90, 10)], fill=MAIN_LIGHT, width=4)

    # 左：正常比例全身
    normal = figure(POSES / "tech-fullbody-normal.webp", 780)
    nx = 360
    canvas.alpha_composite(normal, (int(nx - normal.width / 2), GROUND - normal.height))
    d = ImageDraw.Draw(canvas)
    text(d, (nx, GROUND - normal.height - 72), "正常比例", 44, ACCENT, anchor="ma", stroke=6)
    text(d, (nx, GROUND + 6), "约 7.5 头身", 28, GREY, anchor="ma", stroke=4)

    # 中：Q 版化箭头 + 保留特征
    hand_arrow(d, 640, 860, 560, ACCENT)
    text(d, (750, 470), "Q 版化", 46, ACCENT, anchor="ma", stroke=6)
    keep = ["栗棕微卷发", "全息护目镜", "白 T + 灰短裤"]
    for k, line in enumerate(keep):
        text(d, (750, 620 + k * 44), line, 28, MAIN, anchor="ma", stroke=5)
    text(d, (750, 620 + len(keep) * 44 + 6), "保持不变", 24, GREY, anchor="ma", stroke=4)

    # 右：两张 Q 版，脚底对齐地面线
    chibis = [("chibi-tech-standing-coffee.jpg", 1180, "捧杯发呆"),
              ("chibi-tech-sip-notebook.webp", 1610, "边喝边读")]
    for i, (fname, cx, label) in enumerate(chibis):
        c = figure(POSES / fname, 560)
        canvas.alpha_composite(c, (int(cx - c.width / 2), GROUND - c.height))
        d = ImageDraw.Draw(canvas)
        text(d, (cx, GROUND - c.height - 64), label, 40, MAIN, anchor="ma", stroke=6)
    text(d, (1395, GROUND + 6), "Q 版 · 约 2.5 头身", 28, GREY, anchor="ma", stroke=4)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out)


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "docs" / "chibi-sheet.jpg")

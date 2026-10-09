"""角色形态说明图（Character Mode Sheet）：16:9 横版，左科技金融、右生活随笔，手写标注 + 箭头。

用法: .venv/bin/python scripts/mode_sheet.py [输出路径]
"""
import math
import random
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from rembg import new_session, remove

REPO = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
FONT = REPO / "cover" / "fonts" / "ZCOOLKuaiLe-Regular.ttf"      # 站酷快乐体，描边加粗
FALLBACK = REPO / "cover" / "fonts" / "MaokenAssortedSans-TC.otf"  # 主字体缺字时补字

PAPER = (245, 241, 232)        # Pale Beige
INK = (48, 52, 58)             # Charcoal，标题
TECH = (33, 72, 184)           # Cobalt，科技标题与标注
LIFE = (198, 95, 56)           # Terracotta，生活标题与标注
TECH_LIGHT = (158, 184, 211)   # Powder Blue，淡色描边
LIFE_LIGHT = (232, 196, 176)   # 淡赤陶
WHITE = (255, 255, 255)

PANELS = [
    {   # 科技金融
        "src": "identity/refs/identity-tech.png", "cx": 530, "color": TECH, "light": TECH_LIGHT,
        "title": "1. 科技金融形态", "sub": "Tech-Finance Mode",
        # (标注文字, 标注文字左上角, 箭头指向的原图坐标)
        "notes": [("全息护目镜", (30, 420), (225, 470)),
                  ("淡蓝色反光\n数字图案", (30, 640), (300, 520))],
    },
    {   # 生活随笔
        "src": "identity/refs/identity-life-beanie.png", "cx": 1390, "color": LIFE, "light": LIFE_LIGHT,
        "title": "2. 生活随笔形态", "sub": "Everyday Casual Mode",
        "notes": [("藏蓝针织冷帽", (1700, 340), (690, 250)),
                  ("单边圆眼镜", (1715, 560), (640, 470)),
                  ("细长金属链", (1715, 800), (660, 900))],
    },
]
CHAR_TOP = 235
CHAR_H = H - CHAR_TOP + 40   # 人物一直延伸到画面底边，肩膀在底部渐隐融进纸底
BOLD = 0.022                 # 加粗：同色描边宽度占字号的比例；再大笔画会糊在一起


def font(size):
    return ImageFont.truetype(str(FONT), size)


CMAP = TTFont(str(FONT)).getBestCmap()


def text(d, xy, s, size, fill, anchor="la", stroke=0, bold=True):
    """逐行排字，同色描边加粗；stroke 是外圈纸色描边。主字体缺的字用备用字体补上。
    anchor 支持 la（左上）和 ma（居中上）。"""
    f, fb = font(size), ImageFont.truetype(str(FALLBACK), size)
    bold = max(1, round(size * BOLD)) if bold else 0
    x0, y = xy
    for line in s.split("\n"):
        w = sum((f if ord(ch) in CMAP else fb).getlength(ch) + bold for ch in line)
        x = x0 - w / 2 if anchor == "ma" else x0
        for ch in line:
            ff = f if ord(ch) in CMAP else fb
            if stroke:
                d.text((x, y), ch, font=ff, fill=PAPER, stroke_width=bold + stroke, stroke_fill=PAPER)
            d.text((x, y), ch, font=ff, fill=fill, stroke_width=bold, stroke_fill=fill)
            x += ff.getlength(ch) + bold
        y += int(size * 1.2)
    return w


def cutout(path):
    im = Image.open(REPO / path).convert("RGB")
    mask = remove(im, session=new_session("isnet-anime"), only_mask=True)
    s = CHAR_H / im.height
    im = im.resize((int(im.width * s), CHAR_H), Image.LANCZOS)
    mask = mask.resize(im.size, Image.LANCZOS)
    fade = Image.linear_gradient("L").resize(im.size)            # 上黑下白
    fade = fade.point(lambda v: 255 if v < 175 else max(0, int(255 - (v - 175) * 3.4)))   # 最下方约 30% 渐隐
    from PIL import ImageChops
    out = im.convert("RGBA"); out.putalpha(ImageChops.multiply(mask, fade))
    return out, s


def halo(canvas, cx, cy, r, color, seed):
    """人物身后的淡色手绘圆弧描边。"""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    drift = 0
    for i in range(700):
        t = i / 700
        a = math.radians(-130 + 250 * t)
        drift = drift * 0.97 + rnd.uniform(-0.6, 0.6)
        x, y = cx + (r + drift) * math.sin(a), cy - (r * 0.95 + drift) * math.cos(a)
        w = 26 * math.sin(math.pi * t) ** 0.6 + 4
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=color + (255,))
    canvas.alpha_composite(layer)


def arrow(d, start, end, color, seed):
    """手绘曲线箭头：二次贝塞尔 + 轻微抖动 + 箭头。"""
    rnd = random.Random(seed)
    (x0, y0), (x1, y1) = start, end
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), x1 - x0
    L = math.hypot(nx, ny) or 1
    bend = 0.18 * L * rnd.choice([-1, 1])
    cx, cy = mx + nx / L * bend, my + ny / L * bend
    pts = []
    for i in range(41):
        t = i / 40
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        pts.append((x + rnd.uniform(-0.8, 0.8), y + rnd.uniform(-0.8, 0.8)))
    d.line(pts, fill=color, width=5, joint="curve")
    (ax, ay), (bx, by) = pts[-4], pts[-1]
    ang = math.atan2(by - ay, bx - ax)
    for s in (-1, 1):
        a = ang + math.pi + s * 0.5
        d.line([(bx, by), (bx + 26 * math.cos(a), by + 26 * math.sin(a))], fill=color, width=5)


def build(out: Path):
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))

    d = ImageDraw.Draw(canvas)
    text(d, (W / 2, 28), "Character Mode Sheet", 84, INK, anchor="ma")
    d.line([(W / 2 - 330, 136), (W / 2 + 330, 136)], fill=TECH_LIGHT, width=6)
    text(d, (W / 2, 148), "角色形态说明", 34, (110, 110, 110), anchor="ma")

    for i, p in enumerate(PANELS):
        char, s = cutout(p["src"])
        x = int(p["cx"] - char.width / 2)
        hy = CHAR_TOP + CHAR_H * 0.44          # 圆弧圆心下移，顶部离开两栏标题
        halo(canvas, p["cx"], hy, char.width * 0.45, WHITE, seed=7 + i)
        halo(canvas, p["cx"] + 6, hy + 6, char.width * 0.49, p["light"], seed=17 + i)
        canvas.alpha_composite(char, (x, CHAR_TOP))
        d = ImageDraw.Draw(canvas)
        text(d, (p["cx"], 190), p["title"], 50, p["color"], anchor="ma", stroke=6)
        text(d, (p["cx"], 252), p["sub"], 28, p["color"], anchor="ma", stroke=5)
        for j, (label, (tx, ty), (px, py)) in enumerate(p["notes"]):
            tw = max(text(d, (tx, ty + k * 46), l, 36, p["color"], stroke=6) for k, l in enumerate(label.split("\n")))
            th = 46 * len(label.split("\n"))
            target = (x + px * s, CHAR_TOP + py * s)
            # 箭头从标注文字靠近人物的一侧出发
            sx = tx + tw + 10 if tx < target[0] else tx - 10
            arrow(d, (sx, ty + th / 2), target, p["color"], seed=31 + i * 10 + j)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out)


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "docs" / "character-mode-sheet.jpg")

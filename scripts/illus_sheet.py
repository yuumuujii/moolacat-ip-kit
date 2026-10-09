"""长文插图流程图（Illustration Workflow）：1920×1080，和 Character Mode Sheet 同一套纸底与字体。

上：四步流程；下：长文片段（标出插图位置）→ 生成的 16:9 插图。
用法: .venv/bin/python scripts/illus_sheet.py <插图> [输出路径]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from rembg import new_session, remove

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chibi_sheet import hand_arrow   # noqa: E402
from mode_sheet import H, INK, PAPER, REPO, W, text   # noqa: E402
from workflow_sheet import card   # noqa: E402

# 配色：Ultramarine + Safety Orange（cover/colors.json 里的配方）
MAIN, ACCENT = (38, 62, 153), (229, 93, 43)
MAIN_LIGHT = (184, 194, 228)
ACCENT_LIGHT = (250, 214, 196)
GREY = (90, 90, 90)

ARTICLE = [  # 示例长文片段：第 2 行是关键句
    "收藏了几百条教程，",
    "缺的是一条主线。",
    "串起来，才有复利。",
]
ANCHOR = 1   # 高亮的那一行


def step_icons(chibi: Image.Image):
    icons = []
    # 01 放大镜扫过文字
    a = Image.new("RGBA", (110, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(a)
    for k in range(4):
        d.line((6, 18 + k * 20, 70 if k != 2 else 88, 18 + k * 20), fill=(170, 170, 170), width=6)
    d.rectangle((6, 52, 88, 64), fill=ACCENT_LIGHT)
    d.ellipse((58, 28, 96, 66), outline=MAIN, width=6); d.line((90, 62, 106, 80), fill=MAIN, width=8)
    icons.append(a)
    # 02 shot list 卡片
    b = Image.new("RGBA", (96, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    d.rounded_rectangle((4, 4, 92, 106), 10, fill=(255, 255, 255), outline=(190, 190, 190), width=3)
    for k, w in enumerate((60, 48, 66, 40)):
        d.ellipse((14, 20 + k * 22, 24, 30 + k * 22), fill=ACCENT if k == 0 else MAIN_LIGHT)
        d.line((32, 25 + k * 22, 32 + w * 0.8, 25 + k * 22), fill=(150, 150, 150), width=5)
    icons.append(b)
    # 03 Q 版形象
    icons.append(chibi)
    # 04 检查勾
    c = Image.new("RGBA", (100, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    for k in range(3):
        y = 14 + k * 30
        d.rounded_rectangle((6, y, 30, y + 24), 5, outline=MAIN, width=3)
        d.line([(10, y + 12), (17, y + 19), (28, y + 4)], fill=ACCENT, width=4)
        d.line((40, y + 12, 92, y + 12), fill=(170, 170, 170), width=5)
    icons.append(c)
    return icons


def article_card(w, h):
    """一张纸：长文片段 + 高亮锚点 + [插图①] 标记。"""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
    y = 120
    for k, line in enumerate(ARTICLE):
        if k == ANCHOR:
            d.rectangle((30, y + 8, 30 + 40 * len(line) + 10, y + 54), fill=ACCENT_LIGHT)
        text(d, (36, y), line, 40, INK if k == ANCHOR else GREY, bold=False)
        y += 84
        if k == ANCHOR:
            d.rounded_rectangle((36, y, 196, y + 52), 10, fill=ACCENT)
            text(d, (64, y + 8), "插图 ①", 30, (255, 255, 255), bold=False)
            y += 84
    pad = 24
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((pad + 6, pad + 10, pad + w + 6, pad + h + 10), fill=(0, 0, 0, 60))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    out.alpha_composite(im, (pad, pad))
    return out


def build(illus: Path, out: Path):
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    text(d, (W / 2, 28), "Illustration Workflow", 84, INK, anchor="ma")
    d.line([(W / 2 - 320, 136), (W / 2 + 320, 136)], fill=MAIN_LIGHT, width=6)
    text(d, (W / 2, 148), "长文插图，三步搞定", 34, GREY, anchor="ma")

    # 上：四步
    src = Image.open(REPO / "identity" / "refs" / "chibi-tech-3.png").convert("RGB")
    m = remove(src, session=new_session("isnet-anime"), only_mask=True)
    chibi = src.convert("RGBA"); chibi.putalpha(m)
    chibi = chibi.crop(m.point(lambda v: 255 if v > 160 else 0).getbbox()); chibi.thumbnail((90, 110))
    steps = ["挑一句关键话", "想一个画面", "让她来演"]
    icons = step_icons(chibi)
    icons = [icons[0], icons[1], icons[2]]
    col_w, top = (W - 120) / 3, 215
    for k, (title, icon) in enumerate(zip(steps, icons)):
        x = 60 + k * col_w + 90
        canvas.alpha_composite(icon, (int(x), int(top + (112 - icon.height) / 2)))
        d = ImageDraw.Draw(canvas)
        text(d, (x + 130, top + 32), f"{k + 1}  {title}", 40, MAIN if k % 2 == 0 else ACCENT, bold=False)
        if k < 2:
            hand_arrow(d, int(60 + (k + 1) * col_w - 30), int(60 + (k + 1) * col_w + 30), top + 58, MAIN_LIGHT, seed=20 + k)
    d.line([(60, 372), (W - 60, 372)], fill=MAIN_LIGHT, width=3)

    # 下：长文 → 插图
    art = article_card(500, 530)
    ax, ay = 50, 405
    canvas.alpha_composite(art, (ax, ay))
    ill = card(Image.open(illus), 530)
    ix, iy = W - 50 - ill.width, ay
    canvas.alpha_composite(ill, (ix, iy))
    d = ImageDraw.Draw(canvas)
    text(d, (ax + art.width / 2, ay + art.height + 2), "文章", 34, MAIN, anchor="ma", bold=False)
    text(d, (ix + ill.width / 2, iy + ill.height + 2), "插图", 34, ACCENT, anchor="ma", bold=False)
    hand_arrow(d, ax + art.width + 10, ix + 10, ay + 290, ACCENT, seed=7)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out)


def build_vertical(illus: Path, out: Path):
    """竖版 1080×1440，适合直接发小红书笔记：标题 → 三步 → 文章 → 插图，从上往下读。"""
    VW, VH = 1080, 1440
    canvas = Image.new("RGBA", (VW, VH), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    text(d, (VW / 2, 40), "Illustration", 78, INK, anchor="ma")
    text(d, (VW / 2, 128), "Workflow", 78, INK, anchor="ma")
    d.line([(VW / 2 - 200, 226), (VW / 2 + 200, 226)], fill=MAIN_LIGHT, width=6)
    text(d, (VW / 2, 240), "长文插图，三步搞定", 32, GREY, anchor="ma")

    # 三步：一行三个，图标在上、文字在下
    src = Image.open(REPO / "identity" / "refs" / "chibi-tech-3.png").convert("RGB")
    m = remove(src, session=new_session("isnet-anime"), only_mask=True)
    chibi = src.convert("RGBA"); chibi.putalpha(m)
    chibi = chibi.crop(m.point(lambda v: 255 if v > 160 else 0).getbbox()); chibi.thumbnail((80, 100))
    icons = step_icons(chibi)[:3]
    steps = ["挑一句关键话", "想一个画面", "让她来演"]
    col_w, top = VW / 3, 310
    for k, (title, icon) in enumerate(zip(steps, icons)):
        cx = col_w * k + col_w / 2
        canvas.alpha_composite(icon, (int(cx - icon.width / 2), int(top + (110 - icon.height) / 2)))
        d = ImageDraw.Draw(canvas)
        text(d, (cx, top + 124), f"{k + 1} {title}", 32, MAIN if k % 2 == 0 else ACCENT, anchor="ma", bold=False)
        if k < 2:
            hand_arrow(d, int(col_w * (k + 1) - 26), int(col_w * (k + 1) + 26), top + 55, MAIN_LIGHT, seed=20 + k)

    # 文章：一条横向纸片，关键句高亮
    ay = 500
    strip = Image.new("RGBA", (VW - 160, 120), (255, 255, 255, 255)); sd = ImageDraw.Draw(strip)
    line = ARTICLE[ANCHOR]
    sd.rectangle((24, 34, 24 + 38 * len(line) + 12, 84), fill=ACCENT_LIGHT)
    text(sd, (30, 32), line, 38, INK, bold=False)
    sd.rounded_rectangle((strip.width - 190, 32, strip.width - 30, 86), 10, fill=ACCENT)
    text(sd, (strip.width - 164, 40), "插图 ①", 30, (255, 255, 255), bold=False)
    canvas.alpha_composite(card(strip, 120), (56, ay))
    d = ImageDraw.Draw(canvas)

    # 向下箭头
    d.line([(VW / 2, ay + 180), (VW / 2, ay + 238)], fill=ACCENT, width=8)
    d.line([(VW / 2 - 22, ay + 216), (VW / 2, ay + 240), (VW / 2 + 22, ay + 216)], fill=ACCENT, width=8)

    # 插图（竖版）
    ill = card(Image.open(illus), 640)
    canvas.alpha_composite(ill, (int(VW / 2 - ill.width / 2), ay + 250))
    d = ImageDraw.Draw(canvas)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out)


if __name__ == "__main__":
    if "--vertical" in sys.argv:
        args = [x for x in sys.argv[1:] if x != "--vertical"]
        build_vertical(Path(args[0]) if args else REPO / "illustration" / "examples" / "illus-tech-main-thread-vertical.png",
                       Path(args[1]) if len(args) > 1 else REPO / "docs" / "illustration-workflow-vertical.jpg")
        sys.exit()
    a = sys.argv[1:]
    build(Path(a[0]) if a else REPO / "illustration" / "examples" / "illus-tech-main-thread.png",
          Path(a[1]) if len(a) > 1 else REPO / "docs" / "illustration-workflow.jpg")

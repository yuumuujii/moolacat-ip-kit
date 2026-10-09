"""小红书封面排版：大头裁切 + 标题排版 + 双色配方 + 手绘白色大弧线 + 底部波浪。

配色读取 cover/colors.json，只作用于文字和装饰；角色图保持原色。
用法:
  .venv/bin/python scripts/compose_cover.py <角色图> <输出.jpg 或目录> --title "主标题 副标题"
      [--layout auto|side] [--recipe auto|<配方 id>|all] [--substrate auto|<纸底 id>]
      [--font maoken|pf-hutu] [--visible 0.62] [--shift 170] [--no-swoosh]
"""
import argparse
import numpy as np
import json
import math
import random
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from rembg import new_session, remove


REPO = Path(__file__).resolve().parent.parent
W, H = 1080, 1440
COLORS = json.loads((REPO / "cover" / "colors.json").read_text(encoding="utf-8"))

FONTS = {
    # max_size：字号上限。gap：标题与头顶轮廓的距离，负数表示压进头发。
    # front：标题放在人物前面（加纸色描边），可以压进头发，字号更大。
    # layout：arc = 整个标题排在头顶一条弧上；rings = 中文贴着头顶走内弧、英文走外弧，两行同心（字号更大）
    # gap 只允许轻微压进头发（约 20px），避免标题盖住头发
    "pf-hutu": {"file": "PFPinfanHutu.ttf", "name": "PF频凡胡涂体", "max_size": 460,
                "gap": -22, "front": True, "layout": "rings"},
    "maoken": {"file": "MaokenAssortedSans-TC.otf", "name": "猫啃什锦黑", "max_size": 460,
               "gap": -22, "front": True, "layout": "rings"},
}

TITLE = "Web3学习"
HAIR_WIDTH_MAX = 0.80 # 头发最宽处最多占画布宽度的比例
VISIBLE = 0.62        # 从头顶往下保留多少原图高度：大头为主，手势可以被画面底边裁掉（比露出悬空的手更自然）
BOTTOM_KEEP = 40      # 画布底部留白
SHIFT_X = 0           # 人物水平偏移（正数往右）；side 版式会自动设成右移
LAYOUT = "auto"       # auto = 按字体配置（标题环绕头顶）；side = 人物靠右、标题在头顶 + 左侧竖排
HEAD_TOP = 500        # 头顶在画布上的高度，上方留给两行弧形标题
MAX_HALF_ANGLE = 80   # 弧形标题最多向两侧展开的角度（度）
MARGIN = 16           # 标题墨迹离画布边缘的最小距离


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def place_big_head(src: Path):
    """抠图后按头发宽度放大，返回人物层和头部圆（cx, cy, r）。"""
    im = Image.open(src).convert("RGB")
    mask = remove(im, session=new_session("isnet-anime"), only_mask=True)
    solid = mask.point(lambda v: 255 if v > 160 else 0)
    top = solid.getbbox()[1]
    # 在头顶往下 18% 图高处量头发宽度（这一段只有头发，不含手和道具）
    row = solid.crop((0, top + int(im.height * 0.18), im.width, top + int(im.height * 0.18) + 1))
    left, _, right, _ = row.getbbox()
    # 按「头顶以下 VISIBLE 原图高度」放满画布剩余高度来缩放；同时不让头发超过画布宽度上限。
    # 按头发宽度缩放在正脸构图里会把下巴挤出画面，所以以高度为准。
    s = min((H - BOTTOM_KEEP - HEAD_TOP) / (im.height * VISIBLE), W * HAIR_WIDTH_MAX / (right - left))
    w, h = int(im.width * s), int(im.height * s)
    im, mask = im.resize((w, h), Image.LANCZOS), mask.resize((w, h), Image.LANCZOS)
    x = int(W / 2 - (left + right) / 2 * s) + SHIFT_X
    y = int(HEAD_TOP - top * s)
    cut = im.convert("RGBA")
    cut.putalpha(mask)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(cut, (x, y), cut)
    r = (right - left) * s / 2
    return layer, (W / 2 + SHIFT_X, HEAD_TOP + r, r)


def glyph(ch, f, fill, stroke=0, stroke_fill=None):
    l, t, r, b = f.getbbox(ch, stroke_width=stroke)
    pad = stroke + 8
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), ch, font=f, fill=fill,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def draw_arc(text, font_path, head, size, gap, color, stroke, stroke_fill, seed):
    """在比画布大一圈的透明层上沿圆弧排字，返回 (图层, 偏移)。字底朝向圆心。"""
    cx, cy, r = head
    rnd = random.Random(seed)
    pad = 600
    layer = Image.new("RGBA", (W + pad * 2, H + pad * 2), (0, 0, 0, 0))
    f = ImageFont.truetype(str(font_path), size)
    radius = r + gap + size * 0.5
    # 按墨迹实际宽度排，不用字体的步进宽度（PF 等字体两侧留白很大，会显得字距松散）
    widths = [(f.getbbox(ch)[2] - f.getbbox(ch)[0]) + size * 0.06 for ch in text]
    span = math.degrees(sum(widths) / radius)
    a = -span / 2
    for ch, wch in zip(text, widths):
        mid = a + math.degrees(wch / 2 / radius)
        rad = math.radians(mid)
        px, py = pad + cx + radius * math.sin(rad), pad + cy - radius * math.cos(rad)
        g = ImageFont.truetype(str(font_path), int(size * rnd.uniform(0.95, 1.05)))
        im = glyph(ch, g, color, stroke, stroke_fill).rotate(
            -mid + rnd.uniform(-3, 3), resample=Image.BICUBIC, expand=True)
        layer.alpha_composite(im, (int(px - im.width / 2), int(py - im.height / 2)))
        a += math.degrees(wch / radius)
    return layer, pad, span


def arc_title(canvas, text, font_path, head, color, cfg, paper, seed=1):
    """从字号上限往下试，取第一个「整行墨迹都在画布内、展开角不超限」的字号。"""
    stroke = 10 if cfg["front"] else 0
    for size in range(cfg["max_size"], 79, -8):
        layer, pad, span = draw_arc(text, font_path, head, size, cfg["gap"], color,
                                    stroke, paper, seed)
        l, t, r, b = layer.getbbox()
        fits = (l >= pad + MARGIN and r <= pad + W - MARGIN and t >= pad + MARGIN
                and span <= MAX_HALF_ANGLE * 2)
        if fits:
            canvas.alpha_composite(layer.crop((pad, pad, pad + W, pad + H)))
            return size
    raise SystemExit("标题太长，最小字号也放不下")


def rings_title(canvas, outer_text, inner_text, font_path, head, color, cfg, paper,
                outer_color=None, ratio=(0.85, 1.3)):
    """两行同心弧：内弧贴着头顶（只轻微压进头发），外弧紧贴内弧外侧。
    从大到小试内弧字号，取第一组「两行都放得下、外弧字号在内弧的 ratio 范围内」的字号。
    主副标题时 ratio 设成 (0.4, 0.62)：内弧放大号主标题，外弧放小号副标题。"""
    lo, hi = ratio
    for inner in range(cfg["max_size"], 79, -12):
        trial = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        try:
            got_inner = arc_title(trial, inner_text, font_path, head, color, dict(cfg, max_size=inner), paper)
            outer_cfg = dict(cfg, gap=cfg["gap"] + got_inner * 0.95, max_size=int(got_inner * hi))
            got_outer = arc_title(trial, outer_text, font_path, head, outer_color or color, outer_cfg, paper)
        except SystemExit:
            continue
        if got_outer >= got_inner * lo:
            canvas.alpha_composite(trial)
            return got_outer, got_inner
    raise SystemExit("两行标题放不下")


def crown_line(canvas, text, font_path, head, color, cfg, paper, seed=4):
    """中文横排压在头顶的头发上（类似写在帽子上），宽度不超过画布 72%，下缘不超过头顶以下 40% 头高。"""
    cx, cy, r = head
    rnd = random.Random(seed)
    stroke = 10 if cfg["front"] else 0
    for size in range(cfg["max_size"], 79, -8):
        f = ImageFont.truetype(str(font_path), size)
        ims = [glyph(ch, f, color, stroke, paper).rotate(rnd.uniform(-5, 5), resample=Image.BICUBIC, expand=True)
               for ch in text]
        total = sum(im.width for im in ims) - stroke * 2 * (len(ims) - 1)
        if total <= W * 0.72:
            x, top = int(cx - total / 2), int(cy - r + 75)
            for im in ims:
                canvas.alpha_composite(im, (x, top))
                x += im.width - stroke * 2
            return size
    raise SystemExit("头顶放不下")


def wave(color, alpha, base_y, amp, wavelength, phase, seed, outline=None):
    rnd = random.Random(seed)
    jitter = [rnd.uniform(-1, 1) for _ in range(12)]
    pts = [(x, base_y + amp * math.sin(2 * math.pi * x / wavelength + phase)
            + jitter[(x // 100) % 12] * amp * 0.18) for x in range(0, W + 9, 8)]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon(pts + [(W, H), (0, H)], fill=color + (alpha,))
    if outline:
        d.line(pts, fill=outline + (255,), width=5, joint="curve")
    return layer


def side_title(canvas, main, sub, font_path, person, c_main, c_sub, paper, seed=11):
    """side 版式：主标题横排在画面顶部（下缘可轻压帽顶），副标题竖排在左侧空白里。
    两者字号都取「放得下」的最大值；竖排副标题按人物轮廓避让，不压脸和手。"""
    rnd = random.Random(seed)
    alpha = np.asarray(person.getchannel("A")) > 40
    stroke = 10
    # 1) 主标题：横排，宽度不超过画布 90%
    for size in range(320, 79, -8):
        f = ImageFont.truetype(str(font_path), size)
        ims = [glyph(ch, f, c_main, stroke, paper).rotate(rnd.uniform(-5, 5), resample=Image.BICUBIC, expand=True)
               for ch in main]
        step = [im.width - stroke * 2 - size * 0.12 for im in ims]
        if sum(step) <= W - 2 * MARGIN - 20:
            break
    main_size = size
    x, top_y = (W - sum(step)) / 2, 60
    for im, st in zip(ims, step):
        canvas.alpha_composite(im, (int(x), top_y + int(rnd.uniform(-12, 12))))
        x += st
    main_bottom = top_y + max(im.height for im in ims)
    # 2) 副标题：左侧竖排，按人物左边缘留出的空白定字号
    y0 = main_bottom + 30
    for size in range(260, 79, -8):
        col_h = int(size * 0.98 * len(sub))
        if y0 + col_h > H - MARGIN:
            continue
        band = alpha[y0:y0 + col_h]
        cols = np.where(band.any(axis=0))[0]
        free = (cols.min() if len(cols) else W) - MARGIN - 12
        if size + stroke * 2 <= free:
            break
    f = ImageFont.truetype(str(font_path), size)
    cx, y = MARGIN + (size + stroke * 2) // 2, y0
    for ch in sub:
        im = glyph(ch, f, c_sub, stroke, paper).rotate(rnd.uniform(-6, 6), resample=Image.BICUBIC, expand=True)
        # 每个字在固定高度的格子里垂直居中（「一」这类扁字不会贴着格子顶）
        cell = int(size * 0.98)
        canvas.alpha_composite(im, (int(cx - im.width / 2 + rnd.uniform(-6, 6)), int(y + (cell - im.height) / 2)))
        y += cell
    return main_size, size


def swoosh(head, color, seed=7):
    """人物身后的手绘大弧线：从左下绕过头顶到右侧，笔锋两头细、中间粗，带轻微抖动。"""
    cx, cy, r = head
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a0, a1 = -128, 112          # 角度：0 = 正上方，顺时针为正
    rx, ry = r * 1.16, r * 1.08  # 略扁的椭圆，比头大一圈
    ox, oy = cx + r * 0.04, cy + r * 0.10
    steps = 900
    drift = 0.0
    for i in range(steps + 1):
        t = i / steps
        a = math.radians(a0 + (a1 - a0) * t)
        drift += rnd.uniform(-0.6, 0.6)
        drift *= 0.97
        x = ox + (rx + drift) * math.sin(a)
        y = oy - (ry + drift) * math.cos(a)
        width = 50 * math.sin(math.pi * min(1, t * 1.15)) ** 0.6 + 6   # 起笔细、中段粗、收笔略快
        d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=color + (255,))
    return layer


def compose(placed, out, font_key, recipe_id, substrate_id, with_swoosh=True):
    """placed = place_big_head() 的结果，批量出多套配色时只抠一次图。"""
    person, head = placed
    if recipe_id == "auto":   # 按标题在保留的配方里固定挑一组：同一标题每次结果一样，不同标题轮换
        import hashlib
        rs = COLORS["recipes"]
        recipe_id = rs[int(hashlib.md5(TITLE.encode()).hexdigest(), 16) % len(rs)]["id"]
    recipe = next(r for r in COLORS["recipes"] if r["id"] == recipe_id)
    if substrate_id == "auto":   # 纸底跟随配方自适应
        substrate_id = recipe["substrate"]
    paper = hex_rgb(next(s for s in COLORS["substrates"] if s["id"] == substrate_id)["hex"])
    dominant, accent = hex_rgb(recipe["dominant"]), hex_rgb(recipe["accent"])
    lum = lambda c: (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255
    # 标题用两色里更深的那一色，另一色给副标题；波浪仍按主色 / 强调色分工
    title_main, title_sub = (dominant, accent) if lum(dominant) <= lum(accent) + 0.15 else (accent, dominant)
    font_cfg = FONTS[font_key]
    font_path = REPO / "cover" / "fonts" / font_cfg["file"]
    cmap = TTFont(font_path).getBestCmap()
    missing = [ch for ch in TITLE if ord(ch) not in cmap]
    if missing:  # 字库小的字体（如 PF频凡胡涂体只有约 4300 字）可能缺字，缺字时直接报错
        raise SystemExit(f"{font_cfg['name']} 缺少这些字：{''.join(missing)}")

    canvas = Image.new("RGBA", (W, H), paper + (255,))
    title = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # 主标题：主色，沿头顶弧线环绕。放人物后面时发丝可以盖过字；放前面时加纸色描边
    if LAYOUT == "side":
        parts = TITLE.split()
        if len(parts) < 2:          # 没有空格：对半拆，前半做主标题
            k = (len(TITLE) + 1) // 2
            parts = [TITLE[:k], TITLE[k:]]
        size = side_title(title, parts[0], "".join(parts[1:]), font_path, person, title_main, title_sub, paper)
    elif font_cfg["layout"] == "rings":
        parts = TITLE.split()
        if len(parts) >= 2:
            # 主标题 + 副标题（用空格分开）：主标题大字贴头顶走内弧，副标题小字用强调色走外弧
            main, sub = parts[0], "".join(parts[1:])
            size = rings_title(title, sub, main, font_path, head, title_main, font_cfg, paper,
                               outer_color=title_sub, ratio=(0.4, 0.62))
        else:
            latin = "".join(ch for ch in TITLE if ch.isascii())
            cjk = "".join(ch for ch in TITLE if not ch.isascii())
            if latin:      # 中英混排：英文走外弧，中文走内弧
                outer, inner = latin, cjk
            else:          # 全中文：按字数对半拆，前半（多的一半）走外弧
                k = (len(cjk) + 1) // 2
                outer, inner = cjk[:k], cjk[k:]
            size = rings_title(title, outer, inner, font_path, head, title_main, font_cfg, paper)
    else:
        size = arc_title(title, TITLE, font_path, head, title_main, font_cfg, paper)

    # 波浪：后层用主色浅版本（只算浓淡），前层用强调色，顶边描一条主色线
    waves = [wave(dominant, 90, H - 300, 30, 430, 0.6, seed=2),
             wave(accent, 255, H - 215, 34, 360, 2.2, seed=5, outline=dominant)]

    # 分层：纸底 →（后置标题）→ 波浪 → 手绘大弧线（白色，呼应水彩高光）→ 人物 →（前置标题）
    if not font_cfg["front"]:
        canvas.alpha_composite(title)
    for wv in waves:
        canvas.alpha_composite(wv)
    if with_swoosh:
        canvas.alpha_composite(swoosh(head, (255, 255, 255)))
    canvas.alpha_composite(person)
    if font_cfg["front"]:
        canvas.alpha_composite(title)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out, "font", font_cfg["name"], "recipe", recipe_id, "substrate", substrate_id, "title_size", size)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path, help="单张时是 .jpg 路径；--recipe all 时是输出目录")
    ap.add_argument("--font", default="maoken", choices=FONTS)
    ap.add_argument("--recipe", default="auto",
                    help="配方 id；auto = 按标题自动挑一组（默认）；all = 输出全部配方")
    ap.add_argument("--no-swoosh", action="store_true", help="不画人物身后的手绘大弧线")
    ap.add_argument("--title", default=TITLE, help="封面标题；空格前是主标题，空格后是副标题")
    ap.add_argument("--layout", default="auto", choices=["auto", "side"],
                    help="auto = 标题环绕头顶；side = 人物靠右、主标题横排在顶部、副标题竖排在左侧")
    ap.add_argument("--shift", type=int, default=170, help="side 版式下人物右移的像素")
    ap.add_argument("--visible", type=float, default=VISIBLE,
                    help="从头顶往下保留多少原图高度（0-1）；大头图、手势在下方时调大")
    ap.add_argument("--substrate", default="auto", help="纸底 id；auto = 跟随配方（默认）")
    a = ap.parse_args()
    TITLE, VISIBLE, LAYOUT = a.title, a.visible, a.layout
    if LAYOUT == "side":
        SHIFT_X, HEAD_TOP = a.shift, 430
    placed = place_big_head(a.src)
    if a.recipe == "all":
        for r in COLORS["recipes"]:
            compose(placed, a.out / f"{a.font}-{r['id']}.jpg", a.font, r["id"], a.substrate, not a.no_swoosh)
    else:
        compose(placed, a.out, a.font, a.recipe, a.substrate, not a.no_swoosh)

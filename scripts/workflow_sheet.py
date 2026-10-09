"""小红书封面流程图（Cover Workflow）：1920×1080，和 Character Mode Sheet 同一套纸底与字体。

左：原图 → 中：四步流程（每步配小示意）→ 右：成品封面。
用法: .venv/bin/python scripts/workflow_sheet.py <原图> <成品封面> [输出路径]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from rembg import new_session, remove

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chibi_sheet import hand_arrow   # noqa: E402
from mode_sheet import H, INK, PAPER, REPO, W, text   # noqa: E402

# 配色：Botanical Green + Oxblood（cover/colors.json 里的配方）
MAIN, ACCENT = (0, 138, 75), (143, 52, 52)
MAIN_LIGHT = (180, 214, 196)
GREY = (110, 110, 110)


def card(img: Image.Image, height: int) -> Image.Image:
    """图片缩放 + 柔和投影，像一张放在纸上的卡片。"""
    s = height / img.height
    img = img.convert("RGB").resize((int(img.width * s), height), Image.LANCZOS)
    pad = 24
    out = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((pad + 6, pad + 10, pad + img.width + 6, pad + img.height + 10), fill=(0, 0, 0, 60))
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    out.paste(img, (pad, pad))
    return out


def build(src: Path, cover: Path, recipe_id: str, out: Path):
    canvas = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(canvas)
    text(d, (W / 2, 28), "Cover Workflow", 84, INK, anchor="ma")
    d.line([(W / 2 - 280, 136), (W / 2 + 280, 136)], fill=MAIN_LIGHT, width=6)
    text(d, (W / 2, 148), "小红书封面流程 · 原图 → 封面", 34, GREY, anchor="ma")

    # 左：原图
    CARD_H, CARD_Y = 690, 275          # 原图和封面同样大小、同一高度
    left = card(Image.open(src), CARD_H)
    lx, ly = 70, CARD_Y
    canvas.alpha_composite(left, (lx, ly))
    d = ImageDraw.Draw(canvas)
    lc = lx + left.width / 2
    text(d, (lc, ly - 64), "原图", 44, ACCENT, anchor="ma", stroke=6)
    text(d, (lc, ly + left.height + 4), "Gemini 生成 · 纯白底 · 不画字", 24, GREY, anchor="ma", stroke=4)

    # 右：成品封面
    right = card(Image.open(cover), CARD_H)
    rx, ry = W - 70 - right.width, CARD_Y
    canvas.alpha_composite(right, (rx, ry))
    d = ImageDraw.Draw(canvas)
    rc = rx + right.width / 2
    text(d, (rc, ry - 64), "封面", 44, MAIN, anchor="ma", stroke=6)
    text(d, (rc, ry + right.height + 4), "1080 × 1440 · 3:4", 24, GREY, anchor="ma", stroke=4)

    # 中：四步流程
    mx0, mx1 = lx + left.width + 40, rx - 40
    hand_arrow(d, mx0, mx0 + 90, 600, ACCENT, seed=5)
    hand_arrow(d, mx1 - 80, mx1, 600, MAIN, seed=6)
    col_x = mx0 + 120
    steps_top, step_h = 290, 175
    recipe = next(r for r in json.loads((REPO / "cover" / "colors.json").read_text(encoding="utf-8"))["recipes"]
                  if r["id"] == recipe_id)
    paper = next(s for s in json.loads((REPO / "cover" / "colors.json").read_text(encoding="utf-8"))["substrates"]
                 if s["id"] == recipe["substrate"])

    # 每步的小示意
    thumbs = []
    im = Image.open(src).convert("RGB")
    m = remove(im, session=new_session("isnet-anime"), only_mask=True)
    cut = im.convert("RGBA"); cut.putalpha(m)
    cut = cut.crop(m.point(lambda v: 255 if v > 160 else 0).getbbox())
    cut.thumbnail((120, 130))
    thumbs.append(cut)
    sw = Image.new("RGBA", (130, 110), (0, 0, 0, 0)); sd = ImageDraw.Draw(sw)
    sd.rounded_rectangle((0, 0, 128, 108), 14, fill=paper["hex"], outline=(200, 200, 200), width=2)
    sd.ellipse((14, 30, 62, 78), fill=recipe["dominant"]); sd.ellipse((66, 30, 114, 78), fill=recipe["accent"])
    thumbs.append(sw)
    tt = Image.new("RGBA", (140, 110), (0, 0, 0, 0)); td = ImageDraw.Draw(tt)
    td.arc((10, 40, 130, 160), 200, 340, fill=INK, width=4)
    text(td, (70, 6), "标题", 40, INK, anchor="ma")
    thumbs.append(tt)
    sl = Image.new("RGBA", (140, 110), (0, 0, 0, 0)); ld = ImageDraw.Draw(sl)
    ld.rounded_rectangle((0, 0, 138, 108), 14, fill=paper["hex"])
    ld.arc((20, 14, 120, 120), 200, 340, fill=(255, 255, 255), width=10)
    ld.rectangle((0, 80, 138, 108), fill=recipe["accent"])
    thumbs.append(sl)

    steps = [("抠图去底", "动漫抠图模型，保留发丝"),
             ("自动配色", "9 组双色配方 · 纸底自适应"),
             ("手写标题", "猫啃什锦黑，环绕头顶"),
             ("分层装饰", "白色弧线 + 底部波浪")]
    d = ImageDraw.Draw(canvas)
    for k, ((title, sub), th) in enumerate(zip(steps, thumbs)):
        y = steps_top + k * step_h
        canvas.alpha_composite(th, (int(col_x), int(y + (110 - th.height) / 2)))
        d = ImageDraw.Draw(canvas)
        tx = col_x + 160
        # 步骤文字不加粗、不描边，小字号下更清楚
        text(d, (tx, y + 4), f"{k + 1:02d}  {title}", 38, MAIN if k % 2 == 0 else ACCENT, bold=False)
        text(d, (tx, y + 58), sub, 26, (90, 90, 90), bold=False)
        if k < 3:
            d.line([(col_x + 65, y + 128), (col_x + 65, y + step_h - 12)], fill=MAIN_LIGHT, width=4)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    print("saved", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    build(Path(a[0]), Path(a[1]), a[2] if len(a) > 2 else "charcoal-signal-red",
          Path(a[3]) if len(a) > 3 else REPO / "docs" / "cover-workflow.jpg")

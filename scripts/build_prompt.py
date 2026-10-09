"""拼出一次生图要发的完整 prompt 和垫图顺序。

每个形态在 modes.json 里指定一个基础 prompt（正常比例用 prompt-base.txt，Q 版用 chibi/prompt-base.txt），
只替换两处：{{OUTFIT}} 按形态替换，{{SCENE}} 写这一张图具体发生什么。
其余文字一个字都不改，这是稳定性的来源。

用法:
  python scripts/build_prompt.py tech "close-up head-and-shoulders portrait, eyes wide in shock, both hands raised" [--out prompt.txt]
  python scripts/build_prompt.py life "..." [--no-beanie]
  python scripts/build_prompt.py chibi-tech "sitting cross-legged, sipping coffee; white T-shirt and grey shorts"
  python scripts/build_prompt.py chibi-life "..."
"""
import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# 角色身份目录：默认是 moolacat（identity/）；用自己的角色时设置环境变量 IP_IDENTITY_DIR=my-identity
import os
ROOT = Path(os.environ.get("IP_IDENTITY_DIR", REPO / "identity")).resolve()


FORMATS = {   # 插图画幅：长文用横版，小红书笔记内页用竖版
    "16:9": "Generate one standalone 16:9 horizontal illustration for a Chinese long-form article.",
    "3:4": ("Generate one standalone 3:4 vertical illustration for a Xiaohongshu (RedNote) note page. "
            "Arrange the idea top-to-bottom: the flow or path runs downward, objects stack vertically, "
            "and the character sits in the middle third. Keep the top 20% of the canvas mostly empty white."),
}


def build(mode: str, scene: str, beanie: bool = True, aspect: str = "16:9") -> tuple[str, list[Path]]:
    modes = json.loads((ROOT / "modes.json").read_text(encoding="utf-8"))
    m = modes[mode]
    outfit = m["outfit"]
    if "{{MONOCLE_EYE}}" in outfit:
        outfit = outfit.replace("{{MONOCLE_EYE}}", m["monocle_eye"])
    if "{{BEANIE}}" in outfit:
        outfit = outfit.replace("{{BEANIE}}", m["beanie_on"] if beanie else m["beanie_off"])
    base = (ROOT / m["base"]).read_text(encoding="utf-8")
    prompt = base.replace("{{OUTFIT}}", outfit).replace("{{SCENE}}", scene.strip())
    prompt = prompt.replace("{{FORMAT}}", FORMATS.get(aspect, FORMATS["16:9"]))
    ref_list = m["refs_no_beanie"] if (not beanie and "refs_no_beanie" in m) else m["refs"]
    items = [r if isinstance(r, dict) else {"path": r, "role": "identity"} for r in ref_list]
    refs = [ROOT / r["path"] for r in items]
    # 在 prompt 最前面说明每张垫图的用途：身份图学长相，画风图学笔触
    lines = ["REFERENCE IMAGES (attached in this order):"]
    for i, r in enumerate(items, 1):
        if r["role"] == "identity":
            lines.append(f"Image {i}: identity sheet — copy her face, hairstyle, hair color and accessories exactly.")
        elif r["role"] == "scene-style":
            lines.append(f"Image {i}: illustration style reference — match its white space, light line work, "
                         "watercolor wash and the way short handwritten labels and arrows are drawn. "
                         "Do not copy its objects, composition, labels or the character's accessories.")
        else:
            lines.append(f"Image {i}: approved style reference — match its ink line quality, watercolor texture, "
                         "color warmth and looseness exactly. Do not copy its pose, expression or outfit.")
    lines.append("The final image must look like it was drawn by the same artist as the style references, "
                 "not cleaner, smoother or more digital than them.")
    prompt = "\n".join(lines) + "\n\n\n\n" + prompt
    missing = [r for r in refs if not r.exists()]
    if missing:
        raise SystemExit(f"缺少垫图：{missing}")
    return prompt, refs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    modes = [k for k in json.loads((ROOT / "modes.json").read_text(encoding="utf-8")) if not k.startswith("_")]
    ap.add_argument("mode", choices=modes)
    ap.add_argument("scene")
    ap.add_argument("--no-beanie", action="store_true", help="生活形态这张不戴针织帽")
    ap.add_argument("--aspect", default="16:9", choices=list(FORMATS), help="插图画幅")
    ap.add_argument("--out", type=Path, help="把完整 prompt 写到文件")
    a = ap.parse_args()
    prompt, refs = build(a.mode, a.scene, beanie=not a.no_beanie, aspect=a.aspect)
    if a.out:
        a.out.write_text(prompt, encoding="utf-8")
    print(prompt)
    print("\n--- 垫图（按顺序）---")
    for i, r in enumerate(refs, 1):
        print(f"{i}. {r}")

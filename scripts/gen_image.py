"""用 Gemini API 生成角色图：固定 prompt + 当次场景 + 固定顺序的垫图。

两种认证方式（~/ip-content-skill/.env 或环境变量里配置，.env 不进 git）：
  - AI Studio：GEMINI_API_KEY=...
  - Vertex AI（ADC，适合组织禁用 API key 的项目）：GOOGLE_CLOUD_PROJECT=项目ID，
    并先在终端运行 gcloud auth application-default login。配置了项目 ID 时优先走 Vertex。
用法:
  python scripts/gen_image.py life "SCENE 文字" [--no-beanie] [-n 2] [--model gemini-3-pro-image-preview]
输出: outputs/images/<日期时间>-<形态>-<序号>.png，同目录保存当次完整 prompt。
"""
import argparse
import os
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

from build_prompt import build

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "gemini-3-pro-image"   # Nano Banana Pro 正式版；需要开通计费


def load_env() -> dict:
    env = {}
    f = REPO / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    env.update({k: v for k, v in os.environ.items() if k in ("GEMINI_API_KEY", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")})
    return env


def make_client() -> genai.Client:
    env = load_env()
    if env.get("GOOGLE_CLOUD_PROJECT"):
        return genai.Client(vertexai=True, project=env["GOOGLE_CLOUD_PROJECT"],
                            location=env.get("GOOGLE_CLOUD_LOCATION", "global"))
    if env.get("GEMINI_API_KEY"):
        return genai.Client(api_key=env["GEMINI_API_KEY"])
    raise SystemExit("没有找到认证信息：在 ~/ip-content-skill/.env 里配置 GEMINI_API_KEY 或 GOOGLE_CLOUD_PROJECT")


def generate(mode, scene, beanie=True, n=1, model=DEFAULT_MODEL, aspect="3:4"):
    prompt, refs = build(mode, scene, beanie=beanie, aspect=aspect)
    client = make_client()
    out_dir = REPO / "outputs" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (out_dir / f"{stamp}-{mode}-prompt.txt").write_text(prompt, encoding="utf-8")
    contents = [prompt] + [Image.open(r) for r in refs]   # 文字在前，垫图按固定顺序跟在后面
    saved = []
    for i in range(1, n + 1):
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect),
            ),
        )
        parts = [p for p in resp.candidates[0].content.parts if p.inline_data]
        if not parts:
            print(f"第 {i} 张没有返回图片：{resp.text if hasattr(resp, 'text') else resp}")
            continue
        path = out_dir / f"{stamp}-{mode}-{i}.png"
        path.write_bytes(parts[0].inline_data.data)
        saved.append(path)
        print("saved", path)
    return saved


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode")
    ap.add_argument("scene")
    ap.add_argument("--no-beanie", action="store_true")
    ap.add_argument("-n", type=int, default=1, help="生成几张")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--aspect", default="3:4")
    a = ap.parse_args()
    generate(a.mode, a.scene, beanie=not a.no_beanie, n=a.n, model=a.model, aspect=a.aspect)

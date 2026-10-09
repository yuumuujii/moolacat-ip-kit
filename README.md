# Moolacat IP Kit

[English](README.en.md) · 中文

> 用一个固定的个人 IP「moolacat」，稳定产出小红书封面、长文插图和角色设定图。
>
> A small toolkit that keeps one hand-drawn personal IP consistent across RedNote covers, article illustrations and character sheets.

<p align="center">
  <img src="docs/character-mode-sheet.jpg" width="100%">
</p>

## 它解决什么问题

AI 生图最难的是**角色每次长得不一样**，以及**中文标题总出错字**。这个仓库的做法：

- **角色一致**：固定 prompt + 分工明确的垫图（身份图学长相，画风锚点学笔触），每次只改“这一张在做什么”
- **零错字**：生图模型不画字，中文标题由脚本按手写字体精确排版
- **风格统一**：9 组双色配方 + 自适应纸底，每张封面自动挑一组，系列感来自规则而不是运气

## 角色：moolacat

80–90 年代日系少女漫画风，墨线 + 水彩。栗棕色及肩微卷发，额前一缕卷发。两种形态 + Q 版：

| 形态 | 标志 | 用于 |
|---|---|---|
| 科技金融 `tech` | 淡蓝反光全息护目镜 | Web3、AI、金融 |
| 生活随笔 `life` | 单边圆眼镜（画面右侧）+ 细长金属链，常戴针织帽 `#6B82A6` | 生活、旅行、随笔 |
| Q 版 `chibi-*` / 插图 `illus-*` | 约 2.5 头身，配饰同上 | 长文插图、轻松场景 |

### 表情

<p align="center">
  <img src="docs/expression-sheet.jpg" width="100%">
</p>

### Q 版

<p align="center">
  <img src="docs/chibi-sheet.jpg" width="100%">
</p>

## 能产出什么

### 小红书封面（3:4）

<p align="center">
  <img src="docs/cover-workflow.jpg" width="100%">
</p>

### 长文插图（16:9 / 小红书 3:4）

每篇只配 1–2 张，放在认知转折处，由 Q 版 moolacat 承担核心动作。方法改编自 [ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations)，详见 [`illustration/GUIDE.md`](illustration/GUIDE.md)。

<p align="center">
  <img src="docs/illustration-workflow.jpg" width="100%">
</p>

## 快速开始

```bash
git clone https://github.com/yuumuujii/moolacat-ip-kit.git
cd moolacat-ip-kit
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

生图认证二选一，写在根目录 `.env`（已在 `.gitignore` 中，不会上传）：

- **Vertex AI**：`GOOGLE_CLOUD_PROJECT=<项目ID>`，再运行一次 `gcloud auth application-default login`
- **AI Studio**：`GEMINI_API_KEY=<key>`

不想接 API 也可以只拼 prompt，拿去 Gemini 网页版手动生成（见下方 `build_prompt.py`）。

## 常用命令

```bash
# 1. 生成角色图：tech / life / chibi-tech / chibi-life；-n 张数；生活形态默认戴帽，--no-beanie 去掉
.venv/bin/python scripts/gen_image.py life "Front-facing close-up, gentle smile, hand on cheek." -n 2

# 2. 帽子颜色偏了时统一成 #6B82A6
.venv/bin/python scripts/recolor_beanie.py outputs/images/xxx.png

# 3. 排版封面：空格前主标题、空格后副标题；配色和纸底默认自动
.venv/bin/python scripts/compose_cover.py outputs/images/xxx.png outputs/covers/cover.jpg --title "G4签证 境内身份转换指南"
.venv/bin/python scripts/compose_cover.py outputs/images/xxx.png outputs/covers/cover.jpg --title "在美互惠 一年体验" --layout side

# 4. 长文插图（16:9）/ 小红书插图（3:4）
.venv/bin/python scripts/gen_image.py illus-tech "<SCENE>" --aspect 16:9 -n 2
.venv/bin/python scripts/gen_image.py illus-tech "<SCENE>" --aspect 3:4 -n 2

# 只拼 prompt + 列出垫图顺序，拿去网页版手动生成
.venv/bin/python scripts/build_prompt.py tech "Eyes wide in surprise, hand on cheek."
```

5 份完整 prompt 模板在 [`docs/prompts/`](docs/prompts)。

## 目录

```
identity/                 角色身份（生图的唯一依据）
├── prompt-base.txt       正常比例固定 prompt，只留 {{OUTFIT}} {{SCENE}} 两个空
├── chibi/prompt-base.txt Q 版固定 prompt
├── modes.json            6 个形态：配饰文字 + 垫图顺序与用途
├── anchors.md            生成后的检查清单（不进 prompt）
├── expressions/          已认可的表情库 + 可复用的 SCENE 文字
├── chibi-poses/          Q 版姿势图
└── refs/                 垫图：identity-*（身份图）· style/（画风锚点）· chibi-*（Q 版）· sources/（原图）
template/identity/        空白角色模板：用你自己的角色从这里开始（见 docs/MAKE-YOUR-OWN.md）
illustration/             长文插图：GUIDE.md + 插图 prompt + 示例
cover/                    colors.json（9 组双色配方）+ fonts/
scripts/                  生图、换色、封面排版、5 张概览图
docs/                     概览图、prompt 模板、色样、MAKE-YOUR-OWN 教程
```

## 用你自己的角色

moolacat 的形象和图片不开放使用，但整套方法可以直接拿去：复制 `template/identity/`，填上你的角色描述和垫图，设置 `IP_IDENTITY_DIR` 指向它即可。完整步骤（含 Q 版、插图、常见问题）见 **[docs/MAKE-YOUR-OWN.md](docs/MAKE-YOUR-OWN.md)**。

## 配色：双色配方（Two-ink recipes）

改编自 [mono-color-skill](https://github.com/yanliudesign/mono-color-skill)，定义在 `cover/colors.json`。**只作用于封面的文字与装饰**，角色图保持水彩原色。

| 色样 | 配方 | Hex（主色 + 强调色） | 默认纸底 | 适合 |
|---|---|---|---|---|
| <img src="docs/swatches/powder-blue-signal-red.svg" height="22"> | Powder Blue + Signal Red | `#9EB8D3` + `#C83232` | Neutral White | 攻略、信息密集 |
| <img src="docs/swatches/cobalt-terracotta.svg" height="22"> | Cobalt + Terracotta | `#2148B8` + `#C65F38` | Pale Beige | 生活、旅行 |
| <img src="docs/swatches/botanical-green-oxblood.svg" height="22"> | Botanical Green + Oxblood | `#008A4B` + `#8F3434` | Pale Beige | 读书、自然 |
| <img src="docs/swatches/charcoal-signal-red.svg" height="22"> | Charcoal + Signal Red | `#30343A` + `#C83232` | Cool Gray | 观点、复盘、报告 |
| <img src="docs/swatches/electric-blue-carbon.svg" height="22"> | Electric Blue + Carbon | `#173AE3` + `#242321` | Neutral White | 科技、高对比 |
| <img src="docs/swatches/mint-green-charcoal.svg" height="22"> | Mint Green + Charcoal | `#5EB783` + `#302D2E` | Neutral White | 随笔、长文 |
| <img src="docs/swatches/ultramarine-safety-orange.svg" height="22"> | Ultramarine + Safety Orange | `#263E99` + `#E55D2B` | Cool Gray | 科技金融、Web3、AI |
| <img src="docs/swatches/cyan-brick-red.svg" height="22"> | Cyan + Brick Red | `#159DDA` + `#B64032` | Neutral White | 工具、产品 |
| <img src="docs/swatches/tangerine-slate-blue.svg" height="22"> | Tangerine + Slate Blue | `#E46C2D` + `#4773A5` | Neutral White | 活动、轻松话题 |

| 色样 | 纸底 | Hex |
|---|---|---|
| <img src="docs/swatches/paper-neutral-white.svg" height="22"> | Neutral White | `#FAFAF7` |
| <img src="docs/swatches/paper-cool-gray.svg" height="22"> | Cool Gray | `#E9E9E5` |
| <img src="docs/swatches/paper-pale-beige.svg" height="22"> | Pale Beige | `#F5F1E8` |

- 每张封面只用一组双色；纸底和白色弧线不算墨色
- 主色约占 70–85%（主标题、波浪后层），强调色约占 15–30%（副标题、前层波浪）
- 主色偏浅（Powder Blue、Mint Green）时，主标题自动改用更深的那一色
- `--recipe auto`（默认）按标题固定挑一组；纸底跟随配方，可用 `--substrate` 覆盖

## 字体

| 字体 | 风格 | 用在哪里 | 授权 |
|---|---|---|---|
| **猫啃什锦黑** | 粗壮马克笔手写 | 封面标题（默认） | SIL OFL 1.1 |
| **站酷快乐体** | 细线马克笔手写，脚本描边加粗 | 概览图；补猫啃什锦黑缺的字 | SIL OFL 1.1 |
| PF频凡胡涂体 | 粗糙涂鸦笔触 | 封面备选 `--font pf-hutu` | 授权出处未核实，**不随仓库分发**，需自行放入 `cover/fonts/` |

## 授权

- **代码**（`scripts/`、配置与 prompt 文本）：[MIT](LICENSE)
- **moolacat 角色形象及所有图片**：保留所有权利，见 [ASSET-LICENSE.md](ASSET-LICENSE.md)。欢迎参考方法，请按 [MAKE-YOUR-OWN](docs/MAKE-YOUR-OWN.md) 换成你自己的角色
- 字体与参考项目的署名见 [NOTICE.md](NOTICE.md)

## 致谢

这个项目站在几个开源项目的肩膀上，感谢作者们的分享：

| 项目 | 借鉴了什么 |
|---|---|
| [helloianneo/ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations) | 长文插图方法：只在认知锚点配图、角色承担核心动作、原创隐喻三步法、检查清单（MIT） |
| [yanliudesign/mono-color-skill](https://github.com/yanliudesign/mono-color-skill) | 9 组双色配方与自适应纸底；“一个视觉焦点 + 缩略图检查”的封面思路 |
| [bozhouDev/personal-ip-scenes](https://github.com/bozhouDev/personal-ip-scenes) | 用个人 IP 替换固定角色的思路；身份漂移检查 |
| [Skr-ZERO/MaokenAssortedSans-TC](https://github.com/Skr-ZERO/MaokenAssortedSans-TC) | 猫啃什锦黑字体（SIL OFL 1.1） |
| [ZCOOL KuaiLe](https://fonts.google.com/specimen/ZCOOL+KuaiLe) | 站酷快乐体（SIL OFL 1.1） |

## Roadmap

- [ ] 把写作流程（长文 → 小红书笔记 → 封面文案）写成 `SKILL.md`
- [ ] 用新生成的满意图片更新画风锚点
- [ ] 科技形态换更高清的身份图

---

Made by **moolacat**（小红书 / X 昵称）· GitHub [@yuumuujii](https://github.com/yuumuujii) · X/Twitter [@yuumuujii](https://x.com/yuumuujii)

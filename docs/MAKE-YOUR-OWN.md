# 用你自己的角色

[English](MAKE-YOUR-OWN.en.md) · 中文

moolacat 的形象、名字和图片不开放使用（见 [ASSET-LICENSE.md](../ASSET-LICENSE.md)）。但这套方法——固定 prompt + 分工垫图、脚本排字、双色配方、插图流程——都可以拿去，用在**你自己的角色**上。

整个过程大约分 7 步，第一次做完需要半天到一天，之后每张图只要几分钟。

```
0 想清楚角色 → 1 复制模板 → 2 写固定 prompt → 3 定身份图
→ 4 选画风锚点 → 5 加形态 / Q 版 → 6 出图 + 检查 → 7 排封面、配插图
```

---

## 0. 先想清楚：你的角色是谁

在打开任何生图工具之前，先用一句话回答这四个问题：

| 问题 | 例子（虚构角色「Mochi」） |
|---|---|
| 是什么 | 一只拟人小狐狸，20 岁出头的感觉 |
| 一眼认出的 1–2 个特征 | 奶油色短发 + 左耳缺一角；总是背着一个小邮差包 |
| 画风 | 90 年代绘本风，彩铅 + 淡水彩 |
| 用在哪 | 读书笔记、城市散步 |

**特征越少越稳**。挑 1–2 个“遮住名字也能认出来”的点，其余都可以变。

## 1. 复制模板

```bash
cp -R template/identity my-identity
```

模板里有：

| 文件 | 用途 |
|---|---|
| `prompt-base.txt` | 正常比例的固定 prompt |
| `chibi-prompt-base.txt` | Q 版固定 prompt |
| `illustration-prompt-base.txt` | 长文插图固定 prompt |
| `modes.json` | 形态列表：每个形态用哪份 prompt、哪些垫图、什么配饰 |
| `anchors.md` | 生成后的检查清单 |
| `refs/README.md` | 垫图说明 |

## 2. 写固定 prompt

编辑 `my-identity/prompt-base.txt`，把方括号换成你的角色。四条原则：

1. **写具体，不写形容**：
   - ❌ “可爱的头发、好看的眼睛”
   - ✅ “奶油色齐耳短发，发尾微翘；杏仁眼，琥珀色瞳孔”
2. **写“不要变成什么”**：模型最常跑偏的方向，写进 `Do NOT` 和 `NEGATIVE`。比如“不要长直发”“不要大眼卡通脸”。
3. **有左右之分的特征，两种说法都写**：
   `on her LEFT ear (it appears on the RIGHT side of the image when she faces the viewer)`
4. **只留两个空**：`{{OUTFIT}}`（形态配饰）和 `{{SCENE}}`（这一张在做什么）。其余文字以后**一个字都不改**——稳定就来自这里。

> 小技巧：背景统一写成纯白（#FFFFFF），质感只作用在角色身上。后面抠图做封面会容易很多。

## 3. 定身份图（垫图一，最重要）

1. 先只用 prompt，在任意生图工具里出 5–10 张**正面头肩**图
2. 挑**最像你心里那个角色**的一张，存为 `my-identity/refs/identity.png`
3. 处理一下：
   - 背景抠成纯白
   - 去掉图上任何文字、标注、箭头（模型会照着画）
   - 配饰左右方向和 prompt 一致
4. **从此不再更换**。之后所有图都以它为准。

## 4. 选画风锚点（垫图二、三）

身份图管“长相”，画风锚点管“笔触”。

- 从之后生成的图里，挑 2 张**画风最满意**的，放进 `refs/style/`
- 锚点只学线条和上色，不学姿势——脚本会在 prompt 开头自动说明每张垫图的用途
- 2 张就够；太多会让姿势变僵

## 5. 加形态和 Q 版（可选）

**多个形态**（比如工作 / 生活两种造型）：在 `modes.json` 里照着 `main` 复制一份，改名字和 `outfit`。规则：

- 每个形态只靠 **1–2 个配饰** 区分
- 写清楚“这个形态**不戴**什么”，避免配饰串台

**Q 版 / 长文插图**：

1. 用 `chibi-prompt-base.txt` + 身份图生成 Q 版全身正面，挑一张存为 `refs/chibi.png`
2. `modes.json` 里的 `chibi` 和 `illus` 两个形态就能用了

## 6. 出图 + 检查

```bash
export IP_IDENTITY_DIR=my-identity

# 只拼 prompt（拿去任何网页版生图工具，按列出的顺序上传垫图）
.venv/bin/python scripts/build_prompt.py main "Smiling, waving at the viewer."

# 直接用 Gemini 生图（需要先配置 .env，见 README）
.venv/bin/python scripts/gen_image.py main "Smiling, waving at the viewer." -n 2
```

每张图对照 `my-identity/anchors.md` 检查，不合格就重生成。**满意的图可以替换画风锚点**，越用越稳。

## 7. 排封面、配插图

**小红书封面**：`compose_cover.py` 不依赖角色，任何纯白底的头肩图都能排。

```bash
.venv/bin/python scripts/compose_cover.py outputs/images/xxx.png outputs/covers/cover.jpg --title "主标题 副标题"
```

配色、纸底自动从 9 组双色配方里挑；字体用仓库自带的猫啃什锦黑（OFL，可商用）。

**长文插图**：每篇 1–2 张，方法见 [illustration/GUIDE.md](../illustration/GUIDE.md)。

```bash
.venv/bin/python scripts/gen_image.py illus "<SCENE>" --aspect 16:9   # 长文
.venv/bin/python scripts/gen_image.py illus "<SCENE>" --aspect 3:4    # 小红书
```

---

## 常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| 每张脸都不太一样 | prompt 太笼统 / 每次改了 prompt | 写具体特征；固定部分不再改动；确认身份图有上传 |
| 配饰一会儿左一会儿右 | 垫图方向不一致 | 统一垫图方向，prompt 里写“角色左 = 画面右” |
| 两个形态的配饰混在一起 | 没写“不要什么” | 每个形态的 outfit 里写明不戴哪些配饰 |
| 背景偏米黄 / 有纸纹 | 画风描述里有“纸张” | 质感限定在角色身上，NEGATIVE 加 beige background |
| 模型画出垫图里的字 | 垫图带文字或标注 | 换成干净无字的垫图 |
| 画风越来越“数码感” | 只有身份图，没有画风锚点 | 加 2 张满意的成品作画风锚点 |
| 图上的中文有错字 | 让模型画了字 | 标题交给 `compose_cover.py` 排；插图标注控制在 3–5 个短词 |

## 可以用 / 不能用

| 可以 | 不能 |
|---|---|
| 脚本、prompt 结构、模板、配色规则、工作流方法 | moolacat 角色形象、名字和任何图片 |
| 改编后用于你自己的角色和账号 | 把 `identity/` 里的图当垫图生成 moolacat |
| 在你的项目里注明参考了本仓库（欢迎，但不强制） | 把 moolacat 的图用于 AI 训练 |

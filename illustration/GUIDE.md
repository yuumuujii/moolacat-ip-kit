# 长文插图指南

改编自 [ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations)（MIT）：保留它“只在认知锚点配图、角色承担核心动作、怪诞但清爽”的方法，把固定角色“小黑”换成个人 IP 的 **Q 版形象**。

## 数量

- **每篇长文 1–2 张**，没有合适的锚点就不配。正文文字不转成图片。
- 插图放在认知转折处：核心判断、前后对比、输入→输出、分流、常见坑、角色状态变化。

## 流程

1. **读正文，找锚点**：核心观点是什么？哪段在做认知转折？哪段只适合文字？
2. **出 shot list**（每张写清楚）：
   - 放在哪段之后（正文里标 `[插图①]`）
   - 核心意思（一句话）
   - 结构类型（见下）
   - 她在做什么（核心动作）
   - 建议物件（1–2 个）
   - 中文标注 3–5 个，每个 2–6 字
3. **选形态**：科技 / Web3 / AI 用 `illus-tech`（护目镜），生活随笔用 `illus-life`（单边眼镜 + 链）。
4. **生成**：长文用横版 16:9，小红书笔记内页用竖版 3:4（prompt 会自动改成从上往下的构图，顶部留白）：

   ```bash
   .venv/bin/python scripts/gen_image.py illus-tech "<SCENE>" --aspect 16:9 -n 2   # 长文
   .venv/bin/python scripts/gen_image.py illus-tech "<SCENE>" --aspect 3:4 -n 2    # 小红书
   ```

   竖版 SCENE 里把流程写成“上 → 中 → 下”，而不是“左 → 右”。

5. **检查**（下方清单），不合格就重生成，或减少标注再试。

## 结构类型（选一种）

| 类型 | 适合 | 画法 |
|---|---|---|
| 流程 | 输入 → 处理 → 输出 | 左输入、中间她在操作、右输出，橙色箭头 |
| 前后对比 | 混乱 / 有序，手动 / 自动 | 左乱右稳，中间一个橙色箭头 |
| 概念隐喻 | 抽象判断 | 一个奇怪但成立的低科技物件，她在操作它 |
| 方法分层 | 框架、能力栈 | 几层粗糙的盒子，她在搭 / 扛 / 修其中一层 |
| 地图路线 | 学习路线、用户路径 | 一条弯曲路径，几个节点，她牵线或走路 |
| 角色状态 | 卡住 → 跑起来 | 2–3 个小场景，每个一个短标注 |

## 原创隐喻三步

1. 抽象概念 → 物理动作：卡住、漏掉、变重、分拣、沉淀、发酵、开门、拆包、回流
2. 系统结构 → 低科技物件：纸箱、抽屉、漏斗、秤、井、梯子、水管、线团、闸门、旧机器（只选 1–2 个）
3. 让她承担动作：拉、扛、塞、捞、称、缝、拧、守、推、接、拆、标记

**判断标准：去掉角色后这张图仍然完全成立，说明她只是装饰，要重写 SCENE。**

## SCENE 写法示例

```text
Structure: concept metaphor.
She sits cross-legged on a small stool, typing on a laptop. Floating holographic panels (a rising chart, a small padlock card, a ¥/$ card) rise from the screen and connect into a light node network on the right, ending in one orange dot.
Next to the stool: a stack of three books with a coffee mug on top.
Labels: "基本功" pointing at the books, "动力" pointing at the mug, "价值创造" pointing at the orange dot (orange).
```

## 检查清单

- [ ] 画幅正确（长文 16:9 / 小红书 3:4），纯白背景，大量留白（主体约占画面 40–60%）
- [ ] 一眼认得出是她：栗棕微卷发、圆脸腮红、Q 版约 2.5 头身
- [ ] 配饰正确：科技只有护目镜；生活只有单边眼镜（画面右侧）+ 链子；**两者不能同时出现**
- [ ] 她在做核心动作，不是站旁边
- [ ] 标注 3–5 个、字短、无错字；左上角没有标题
- [ ] 不像 PPT / 正式流程图 / 课件
- [ ] 没有照搬 `examples/` 里的构图和物件

## 示例

`examples/ipstudio-value-creation.jpg`：画风参考（留白、线条、标注方式）。注意它**同时画了护目镜和单边眼镜**，不符合配饰规则，只学画风，不学配饰。

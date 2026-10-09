# 表情库

已认可的夸张表情图。用途：

1. **复用场景**：下次想要同类表情，直接把对应的 SCENE 文字贴进 `scripts/gen_image.py`；
2. **封面素材**：可以直接拿去 `scripts/compose_cover.py` 排版；
3. **画风锚点候选**：画风特别满意的，可以复制到 `identity/refs/style/` 作为垫图二、三。

| 文件 | 形态 | 表情 / 动作 | 合规 |
|---|---|---|---|
| `life-nose-push.jpg` | life（不戴帽） | 双手食指把鼻子往上推，皱眉不服气 | ✅ 单边眼镜在画面右侧 + 链子 |
| `life-smirk-cheek.jpg` | life（不戴帽） | 自信坏笑，一只手托着脸颊 | ✅ 单边眼镜在画面右侧 + 链子 |
| `life-side-eye.jpg` | life（戴帽） | 斜眼瞟向一侧，皱眉抿嘴，一脸怀疑 | ✅ 帽子偏深，排版前用 `recolor_beanie.py` 统一成 #6B82A6 |
| `life-grin.jpg` | life（戴帽） | 眯眼咧嘴大笑，开朗 | ✅ 帽子偏深，同上 |
| `tech-pout-cheeks.jpg` | tech | 双手捧脸，嘟嘴鼓腮，一脸无奈 | ✅ |
| `tech-money-smug.jpg` | tech | 托腮得意笑、脸红，镜片里是 $ ¥ € 和上涨 K 线 | ⚠️ 左耳挂了链子（科技形态规则是不戴链子）；用作封面没问题，**不要当垫图** |
| `tech-puff-shock.jpg` | tech | 瞪眼鼓腮，双手贴脸 | ✅ |

## 复用用的 SCENE 文字

```text
life-nose-push:
Front-facing head-and-shoulders close-up. Both index fingers push the tip of her nose upward, pressing it into a funny upturned shape; brows furrowed, lips pressed together in a grumpy, defiant look.

life-smirk-cheek:
Front-facing head-and-shoulders close-up. A confident, slightly mischievous smirk with eyes narrowed knowingly; one hand rests against her cheek on the opposite side from the monocle.

life-side-eye:
Front-facing head-and-shoulders close-up. Eyes glancing sideways with a skeptical side-eye, brows slightly furrowed, lips pressed into a small flat line.

life-grin:
Front-facing head-and-shoulders close-up. A big, warm open grin with eyes narrowed into happy crescents, cheeks lifted.

tech-pout-cheeks:
Front-facing head-and-shoulders close-up. Both hands cup her cheeks and squish them; lips pushed into a small pout, eyes looking straight ahead with a helpless, unimpressed expression.

tech-money-smug:
Head-and-shoulders close-up, head tilted slightly. Blushing, smug little smile; one hand resting on her cheek. Glowing light-blue $ ¥ € symbols and a rising line chart reflected on the goggle lenses.

tech-puff-shock:
Front-facing head-and-shoulders close-up. Eyes wide open in shock, cheeks puffed full of air with lips pursed; both hands pressed flat against the sides of her face.
```

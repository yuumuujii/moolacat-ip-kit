# Make it your own character

English · [中文](MAKE-YOUR-OWN.md)

The moolacat character, name and images are **not** licensed for reuse (see [ASSET-LICENSE.md](../ASSET-LICENSE.md)). The method is: fixed prompt + role-split reference images, script-set titles, two-ink color recipes and the illustration workflow. Use it for **your own** character.

```
0 Define the character → 1 Copy the template → 2 Write the fixed prompt → 3 Pick the identity image
→ 4 Pick style anchors → 5 Add modes / chibi → 6 Generate + check → 7 Covers and illustrations
```

## 0. Define the character

Answer four questions in one line each (example: a fictional fox character, "Mochi"):

| Question | Example |
|---|---|
| What is it | An anthropomorphic young fox, early-20s vibe |
| 1–2 instantly recognizable traits | Cream-colored short hair + a notch in the left ear; always carries a small messenger bag |
| Art style | 90s picture-book, colored pencil + light watercolor |
| Used for | Reading notes, city walks |

**Fewer signature traits = more stable results.**

## 1. Copy the template

```bash
cp -R template/identity my-identity
```

It contains `prompt-base.txt` (normal proportions), `chibi-prompt-base.txt`, `illustration-prompt-base.txt`, `modes.json` (which prompt, references and accessories each mode uses), `anchors.md` (post-generation checklist) and `refs/README.md`.

## 2. Write the fixed prompt

Replace every bracket in `my-identity/prompt-base.txt`.

1. **Be specific, not adjectival**: "cream ear-length hair with flipped ends; almond eyes, amber irises", not "cute hair, pretty eyes".
2. **Say what it must not become**: put the model's usual mistakes in `Do NOT` and `NEGATIVE`.
3. **For left/right traits, state both frames**: `on her LEFT ear (it appears on the RIGHT side of the image when she faces the viewer)`.
4. **Leave only two blanks**: `{{OUTFIT}}` and `{{SCENE}}`. Never edit the rest again. That is where the consistency comes from.

Keep the background pure white (#FFFFFF) and apply texture to the character only. This makes cut-outs for covers much easier.

## 3. Pick the identity image (reference #1, the most important one)

Generate 5–10 front-facing head-and-shoulder images from the prompt alone. Pick the one that best matches the character you have in mind and save it as `refs/identity.png`. Before using it:

- cut the background to pure white;
- remove any text, labels or arrows;
- check that left/right accessories match the prompt.

**Never replace it.**

## 4. Pick style anchors (references #2 and #3)

The identity image controls the face; style anchors control the line work and coloring. Put your 2 favorite finished images in `refs/style/`. The script tells the model to copy their style, not their poses. Two anchors are enough. More than that makes poses stiff.

## 5. Add modes and chibi (optional)

- **Modes**: copy `main` in `modes.json` and give each mode 1–2 distinguishing accessories. Also write what that mode must **not** wear.
- **Chibi / illustrations**: generate a front-facing full-body chibi with `chibi-prompt-base.txt` and save it as `refs/chibi.png`. The `chibi` and `illus` modes then work.

## 6. Generate + check

```bash
export IP_IDENTITY_DIR=my-identity
.venv/bin/python scripts/build_prompt.py main "Smiling, waving at the viewer."   # prompt only, for any web tool
.venv/bin/python scripts/gen_image.py main "Smiling, waving at the viewer." -n 2  # generate via Gemini
```

Check every image against `anchors.md`. Swap your best results in as style anchors over time.

## 7. Covers and illustrations

```bash
.venv/bin/python scripts/compose_cover.py outputs/images/xxx.png outputs/covers/cover.jpg --title "Main Sub"
.venv/bin/python scripts/gen_image.py illus "<SCENE>" --aspect 16:9   # article
.venv/bin/python scripts/gen_image.py illus "<SCENE>" --aspect 3:4    # RedNote
```

The cover script works with any white-background head-and-shoulders image. For the illustration method, see [illustration/GUIDE.md](../illustration/GUIDE.md).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Face changes every time | Make the traits more specific, never edit the fixed prompt, and make sure the identity image is uploaded |
| Accessory flips left/right | Make all references face the same way and state both frames in the prompt |
| Modes mix accessories | List what each mode must not wear |
| Beige or paper-textured background | Limit texture to the character and add `beige background` to NEGATIVE |
| Model copies text from references | Use clean references without text |
| Style drifts toward glossy digital | Add 2 style anchors |
| Typos in Chinese titles | Let `compose_cover.py` set titles; keep illustration labels to 3–5 short words |

## OK / not OK

| OK | Not OK |
|---|---|
| Scripts, prompt structure, templates, color rules, the workflow | The moolacat character, name or any image |
| Adapting it for your own character and accounts | Using `identity/` images as references to generate moolacat |
| Crediting this repo (appreciated, not required) | Using moolacat images for AI training |

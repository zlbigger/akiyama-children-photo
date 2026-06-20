# Akiyama Children Photo

A Codex plugin and skill for generating prompt packs for candid, analog, child-centered documentary photographs: ordinary streets, schoolyards, courtyards, parks, natural light, imperfect framing, muted film color, and unposed childhood moments.

This project is inspired by the broad visual grammar of 1980s East Asian everyday-life documentary photography and references around *Dear Old Days* / *Hello, Little Friends*. It intentionally avoids asking models to copy a specific copyrighted photo or imitate a living photographer's exact style.

## What It Does

- Converts a short Chinese or English scene brief into ready-to-paste image prompts.
- Produces a main prompt, negative prompt, suggested camera parameters, and filename hint.
- Supports one-off prompts and batch packs.
- Includes a style guide for closer art direction and prompt repair.
- Keeps image generation backend-agnostic: use the output with Codex image generation, SDXL, Flux, Midjourney, ComfyUI, or your own workflow.

## Example

```bash
python3 skills/akiyama-children-photo/scripts/engine.py \
  --brief "1980年代中国 普通街头 一个小男孩 踢足球" \
  --count 1 \
  --format markdown
```

Example output:

```text
写实纪实摄影，儿童日常生活抓拍，非摆拍，非商业写真。
1980年代中国，居民区街头。主体是一个小男孩，正在踢足球，
表情自然、生动但不夸张。摄影机位接近孩子身高，距离很近，
允许画面边缘有路人、杂物、树影或半截身体进入，构图像真实街头瞬间。
35mm纪实镜头，自然光，轻微运动模糊但主体可辨，
细腻胶片颗粒，轻微欠曝，真实皮肤纹理，照片级真实。
```

## Install As A Codex Plugin

Clone the repository into your local plugin folder:

```bash
mkdir -p ~/plugins
git clone https://github.com/zlbigger/akiyama-children-photo.git ~/plugins/akiyama-children-photo
```

The plugin manifest is at:

```text
.codex-plugin/plugin.json
```

The skill is at:

```text
skills/akiyama-children-photo/SKILL.md
```

If you maintain a personal Codex marketplace file, point it at:

```json
{
  "name": "akiyama-children-photo",
  "source": {
    "source": "local",
    "path": "./plugins/akiyama-children-photo"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Creative"
}
```

## Prompt Engine Usage

Generate JSON:

```bash
python3 skills/akiyama-children-photo/scripts/engine.py \
  --brief "90年代南方小城 春天 小女孩 跳皮筋" \
  --count 3 \
  --format json
```

Generate Markdown:

```bash
python3 skills/akiyama-children-photo/scripts/engine.py \
  --brief "1980年代中国 学校操场 一群孩子 跳绳" \
  --count 4 \
  --format markdown
```

Use a built-in ten-image pack:

```bash
python3 skills/akiyama-children-photo/scripts/engine.py \
  --preset pack10 \
  --format markdown
```

Useful options:

- `--brief`: freeform scene description.
- `--count`: number of prompt items.
- `--preset pack10`: varied ten-image prompt pack.
- `--format json|markdown`: output format.
- `--seed`: deterministic variation.
- `--era`, `--scene`, `--season`, `--subject`, `--action`: structured overrides.

## Repository Structure

```text
.
├── .codex-plugin/plugin.json
├── README.md
└── skills/
    └── akiyama-children-photo/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/style-guide.md
        └── scripts/engine.py
```

## Reference Images

This public repository does not include third-party reference photos. If you have licensed or personal reference images, place them locally in:

```text
skills/akiyama-children-photo/assets/reference-gallery/
```

That folder is ignored by Git to avoid accidentally republishing copyrighted material.

## Safety And Rights

- Keep generated scenes benign, ordinary, and family-safe.
- Do not eroticize minors or depict abuse.
- Do not identify or recreate a real child.
- Do not recreate a specific reference photo frame-for-frame.
- Treat named photography references as subject-matter and documentary-language guidance, not as exact style cloning.

## Validation

Validate the skill:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/akiyama-children-photo
```

Validate the plugin:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

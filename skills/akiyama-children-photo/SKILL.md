---
name: akiyama-children-photo
description: Generate prompt packs and art direction for candid, analog, child-centered documentary photographs inspired by 1980s China everyday-life photography, "Dear Old Days" / "Hello, Little Friends" references, relaxed street snapshots, schoolyard scenes, hutong/rural childhood, and same-type image generation requests. Use when the user asks for 秋山亮二/你好小朋友/老照片/儿童纪实/胶片抓拍/同款类型照片 prompts or wants ready-to-use prompts for image generators; do not use to copy a specific copyrighted photo or to invoke an exact living photographer style.
---

# Akiyama Children Photo

Turn a user brief into image-generation prompts for relaxed, child-centered documentary photographs: candid everyday scenes, close human distance, natural light, analog color, and imperfect real-life edges. The skill is prompt-first: produce reusable prompts, negative prompts, and generation notes; only call an image generator if the user explicitly asks for actual images.

## Workflow

1. Identify the user's requested scene, era, place, season, subject, action, count, and output language. If missing, choose sensible defaults: 1980s China, street or schoolyard, natural daylight, children playing, 3:2 or 1:1 frame.
2. Avoid writing "in the style of Ryoji Akiyama" or "copy Dear Old Days" inside generated image prompts. Translate the reference into high-level visual language: candid 1980s East Asian color documentary photography, child-height viewpoint, natural light, analog film grain, unpolished everyday background.
3. For one-off prompt creation, write the prompt directly. For batches, run `scripts/engine.py` and adapt the JSON or Markdown output.
4. If the user asks for nuanced art direction, style repair, or generated images that should match the reference more closely, read `references/style-guide.md`.
5. If using reference images, inspect files in `assets/reference-gallery/` locally for composition and mood. Do not redistribute those images as outputs unless the user explicitly asks and rights are clear.

## Script

Use the prompt engine for repeatable packs:

```bash
python3 scripts/engine.py --brief "90年代南方小城 春天 小女孩 跳皮筋" --count 4 --format markdown
python3 scripts/engine.py --preset pack10 --format json
python3 scripts/engine.py --era 1980s --scene school --season autumn --subject group --action skipping --count 3
```

Useful options:

- `--brief`: freeform scene detail, kept as a human-authored texture layer.
- `--count`: number of prompt items.
- `--preset pack10`: a varied ten-image set.
- `--format json|markdown`: machine-readable or paste-ready output.
- `--seed`: deterministic variation.

## Prompt Recipe

Build prompts from these blocks:

- Scene: "1980s China, ordinary residential street / schoolyard / riverside / village lane / public park".
- Subject: "children in everyday clothes, natural expressions, unposed interaction".
- Camera: "child-height viewpoint, close documentary distance, 35mm or 50mm lens, slight subject motion, imperfect framing".
- Light and color: "available daylight, gentle shadows, muted analog color, fine grain, mild underexposure, real skin texture".
- Environment: "bicycles, hand-painted signs, laundry, stools, trees, old walls, passersby partly entering the frame".
- Realism guardrail: "photojournalistic, spontaneous, no fashion posing, no studio lighting, no glossy AI skin".

Negative prompt baseline:

```text
studio portrait, fashion editorial, cinematic teal orange, HDR, over-sharpened, plastic skin, beauty retouching, perfect symmetry, luxury set, anime, cartoon, illustration, 3D render, doll face, extra fingers, distorted hands, watermark, logo, text
```

## Safety And Rights

Keep generated scenes benign, ordinary, and non-sexualized. Children should be shown in everyday public or family-safe contexts such as school breaks, games, streets, parks, food stalls, farms, beaches, or courtyards. Do not create prompts that eroticize minors, depict abuse, identify a real child, or recreate a specific reference photo frame-for-frame.

When the user references 秋山亮二, treat that as a direction toward subject matter and documentary grammar, not a request to clone a living artist's exact style. Phrase outputs as "1980s East Asian color documentary photography" or "child-centered analog street documentary", not artist-name style imitation.

## Output Format

For each image, include:

- `title`: short Chinese title.
- `prompt`: ready-to-paste prompt.
- `negative_prompt`: anti-AI and anti-studio guardrails.
- `suggested_params`: aspect ratio, lens, aperture, shutter, grain, and notes.
- `filename_hint`: stable export name.

For actual image generation, pass only the `prompt` and important `suggested_params` to the image model. Keep the negative prompt for tools that support it.

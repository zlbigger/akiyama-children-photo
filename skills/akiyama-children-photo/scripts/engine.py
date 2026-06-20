#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt engine for candid analog children's documentary photos.

The script is intentionally prompt-only. It does not call an image API.

Examples:
  python3 scripts/engine.py --brief "90年代南方小城 春天 小女孩 跳皮筋" --count 3
  python3 scripts/engine.py --preset pack10 --format markdown
  python3 scripts/engine.py --era 1980s --scene school --subject group --action skipping --seed 7
"""

from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Iterable


NEGATIVE_PROMPT = (
    "影棚肖像, 商业写真, 时尚大片, 摆拍, 过度干净背景, 奢华布景, "
    "电影感青橙调色, HDR, 过度锐化, 过度磨皮, 塑料皮肤, AI脸, 娃娃脸, "
    "卡通, 插画, 动漫, 3D渲染, 畸形手指, 多手多脚, 扭曲脸, "
    "文字, 水印, logo, 过曝, 强闪光, 色情化, 成人化儿童"
)


ERAS = {
    "1980s": "1980年代中国",
    "1990s": "1990年代中国",
    "2000s": "2000年代中国",
    "2020s": "当代中国",
    "auto": "1980年代中国",
}

SCENES = {
    "street": "居民区街头",
    "hutong": "胡同巷子",
    "school": "学校操场或课间",
    "rural": "乡村院落",
    "river": "河边石阶",
    "park": "公园树荫下",
    "beach": "海边或江边沙滩",
    "canteen": "学校食堂或小饭铺门口",
    "auto": "居民区街头",
}

SEASONS = {
    "spring": "春天",
    "summer": "夏天",
    "autumn": "秋天",
    "winter": "冬天",
    "auto": "夏天",
}

SUBJECTS = {
    "boy": "一个小男孩",
    "girl": "一个小女孩",
    "group": "一群孩子",
    "siblings": "兄妹或姐弟两个孩子",
    "auto": "一群孩子",
}

ACTIONS = {
    "run": "追逐奔跑",
    "jump": "跳起来挥手",
    "skipping": "跳绳或跳皮筋",
    "kite": "奔跑放风筝",
    "snowball": "打雪仗",
    "fishing": "在河边捉鱼摸虾",
    "football": "踢足球",
    "balloon": "吹气球",
    "soda": "分喝汽水",
    "games": "围在一起玩小玩具或拍手游戏",
    "lunch": "端着饭盒吃午饭",
    "hide": "在树后或门洞边躲闪玩闹",
    "feed_chicks": "在院子里喂小鸡",
    "auto": "自然玩闹",
}

ENVIRONMENT_BITS = {
    "1980s": [
        "二八自行车靠在墙边",
        "手写招牌和搪瓷杯",
        "蓝灰色工作服路人从画面边缘经过",
        "晾衣绳、竹椅和斑驳水泥墙",
        "树影落在地面，空气里有一点尘土感",
    ],
    "1990s": [
        "老居民楼、铁栏杆和塑料凉鞋",
        "彩色发卡、校服外套和小卖部门口",
        "梧桐树新叶，墙面贴着褪色海报",
        "旧式公交站牌和自行车铃声的感觉",
    ],
    "2000s": [
        "小灵通广告、彩色书包和水泥操场",
        "街边小卖部、玻璃汽水瓶和塑料凳",
        "居民楼防盗窗和晾晒的被单",
    ],
    "2020s": [
        "现代社区、公园步道和共享单车远景",
        "普通运动鞋、儿童书包和城市楼宇背景",
        "自然生活化场景，避免网红摆拍感",
    ],
}

PALETTES = [
    "色彩朴素克制，绿色和灰蓝轻微偏冷",
    "暖黄日光，阴影柔软，整体轻微欠曝",
    "低饱和胶片色，红色点缀不过分鲜艳",
    "树荫下的青绿色偏色，肤色真实",
    "空气偏冷，人物衣物保留一点温暖色",
]

PALETTES_BY_SEASON = {
    "spring": [PALETTES[0], PALETTES[1], "春日柔光，绿色新叶偏青，肤色真实"],
    "summer": [PALETTES[1], PALETTES[3], "夏日强光被树荫压柔，色彩低饱和"],
    "autumn": [PALETTES[1], PALETTES[2], "秋日暖黄，阴影里有一点灰绿色"],
    "winter": [PALETTES[4], "冬季冷日光，衣物颜色保留温暖点缀"],
}


@dataclass
class Shot:
    era: str
    scene: str
    season: str
    subject: str
    action: str
    lens: str
    aperture: str
    shutter: str
    palette: str
    detail: str


def choice(options: dict[str, str], key: str) -> str:
    return options.get(key, key)


def clean_token(value: str) -> str:
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "_", value).strip("_")[:56]


def pick_palette(season: str, rng: random.Random) -> str:
    return rng.choice(PALETTES_BY_SEASON.get(season, PALETTES))


def infer_key(brief: str, options: dict[str, str], default: str) -> str:
    if not brief:
        return default
    brief_lower = brief.lower()
    aliases = {
        "80": "1980s",
        "八十": "1980s",
        "90": "1990s",
        "九十": "1990s",
        "当代": "2020s",
        "现代": "2020s",
        "普通街头": "street",
        "街头": "street",
        "街道": "street",
        "胡同": "hutong",
        "学校": "school",
        "操场": "school",
        "农村": "rural",
        "乡村": "rural",
        "河": "river",
        "公园": "park",
        "海": "beach",
        "食堂": "canteen",
        "春": "spring",
        "夏": "summer",
        "秋": "autumn",
        "冬": "winter",
        "男孩": "boy",
        "女孩": "girl",
        "一群": "group",
        "兄妹": "siblings",
        "姐弟": "siblings",
        "跳皮筋": "skipping",
        "跳绳": "skipping",
        "风筝": "kite",
        "雪": "snowball",
        "捉鱼": "fishing",
        "踢足球": "football",
        "足球": "football",
        "吹气球": "balloon",
        "气球": "balloon",
        "汽水": "soda",
        "游戏": "games",
        "午饭": "lunch",
        "饭盒": "lunch",
        "喂小鸡": "feed_chicks",
    }
    for needle, key in aliases.items():
        if needle in brief_lower and key in options:
            return key
    return default


def make_shot(args: argparse.Namespace, rng: random.Random) -> Shot:
    brief = args.brief or ""
    era = args.era if args.era != "auto" else infer_key(brief, ERAS, rng.choice(["1980s", "1980s", "1990s", "2020s"]))
    scene = args.scene if args.scene != "auto" else infer_key(brief, SCENES, rng.choice(["street", "school", "rural", "hutong", "river", "park"]))
    season = args.season if args.season != "auto" else infer_key(brief, SEASONS, rng.choice(["spring", "summer", "autumn", "winter"]))
    subject = args.subject if args.subject != "auto" else infer_key(brief, SUBJECTS, rng.choice(["boy", "girl", "group", "siblings"]))
    action = args.action if args.action != "auto" else infer_key(brief, ACTIONS, rng.choice(["run", "skipping", "football", "balloon", "games", "soda", "hide"]))

    lens = rng.choice(["35mm", "50mm"]) if subject in {"boy", "girl", "siblings"} else "35mm"
    aperture = "f/2.8" if scene in {"street", "school", "rural"} and subject == "group" else rng.choice(["f/2.0", "f/2.2", "f/2.8"])
    shutter = rng.choice(["1/500s", "1/800s", "1/1000s", "1/1250s"])
    palette = pick_palette(season, rng)
    era_bits = ENVIRONMENT_BITS.get(era, ENVIRONMENT_BITS["1980s"])
    detail = rng.choice(era_bits)
    if brief:
        detail = f"{detail}；用户补充：{brief}"
    return Shot(era, scene, season, subject, action, lens, aperture, shutter, palette, detail)


def pack10() -> list[Shot]:
    return [
        Shot("1980s", "street", "summer", "girl", "hide", "35mm", "f/2.8", "1/800s", PALETTES[3], "街边老人坐在小凳上，路人半身从画面边缘经过"),
        Shot("1980s", "school", "spring", "group", "skipping", "35mm", "f/2.8", "1/1000s", PALETTES[0], "操场边有单杠、树影和旧书包"),
        Shot("1980s", "river", "summer", "boy", "fishing", "50mm", "f/2.0", "1/800s", PALETTES[1], "河边石阶潮湿，远处有木船和洗衣人"),
        Shot("1990s", "hutong", "autumn", "siblings", "games", "35mm", "f/2.2", "1/500s", PALETTES[2], "门洞边贴着褪色年画，墙角有自行车"),
        Shot("1980s", "canteen", "summer", "group", "lunch", "35mm", "f/2.8", "1/500s", PALETTES[1], "孩子端着搪瓷饭盒，桌面不整齐但真实"),
        Shot("1990s", "park", "spring", "girl", "kite", "35mm", "f/2.2", "1/1250s", PALETTES[2], "草地边有家长模糊背影，风筝线穿过画面"),
        Shot("1980s", "rural", "spring", "girl", "feed_chicks", "50mm", "f/2.0", "1/500s", PALETTES[1], "土墙院落、杏花和旧木门"),
        Shot("1990s", "street", "winter", "group", "snowball", "35mm", "f/2.8", "1/1250s", PALETTES[4], "积雪街道和旧公交站牌，孩子衣服颜色跳出来"),
        Shot("2020s", "park", "summer", "boy", "jump", "35mm", "f/2.2", "1/1000s", PALETTES[0], "现代社区公园，但取景朴素，不做网红感"),
        Shot("1980s", "beach", "summer", "group", "run", "35mm", "f/2.8", "1/1000s", PALETTES[3], "海风、湿沙和远处模糊成年人背影"),
    ]


def build_prompt(shot: Shot) -> str:
    return (
        "写实纪实摄影，儿童日常生活抓拍，非摆拍，非商业写真。"
        f"{choice(ERAS, shot.era)}，{choice(SEASONS, shot.season)}，{choice(SCENES, shot.scene)}。"
        f"主体是{choice(SUBJECTS, shot.subject)}，正在{choice(ACTIONS, shot.action)}，表情自然、生动但不夸张。"
        "摄影机位接近孩子身高，距离很近，允许画面边缘有路人、杂物、树影或半截身体进入，构图像真实街头瞬间。"
        f"环境细节：{shot.detail}。"
        f"{shot.lens}纪实镜头，{shot.aperture}，{shot.shutter}，自然光，轻微运动模糊但主体可辨。"
        f"{shot.palette}，细腻胶片颗粒，轻微欠曝，真实皮肤纹理，照片级真实，高分辨率。"
    )


def title_for(shot: Shot, index: int) -> str:
    return f"{index:02d} {choice(SCENES, shot.scene)}里的{choice(SUBJECTS, shot.subject)}"


def suggested_params(shot: Shot) -> dict[str, object]:
    wants_wide = any(token in shot.detail.lower() for token in ["横版", "宽幅", "landscape", "horizontal", "wide"])
    aspect = "3:2 horizontal" if wants_wide else "1:1" if shot.era == "1980s" and shot.scene in {"street", "school", "rural"} else "3:2"
    return {
        "aspect_ratio": aspect,
        "lens": shot.lens,
        "aperture": shot.aperture,
        "shutter": shot.shutter,
        "exposure": "-0.3EV to -0.7EV",
        "grain": "fine analog color film grain",
        "notes": [
            "保留真实生活边缘和轻微不完美，不要清场。",
            "让动作和表情先于漂亮构图，避免影棚和摆拍感。",
            "提示词不直接写摄影师姓名，只使用高层纪实摄影语言。",
        ],
    }


def item_for(shot: Shot, index: int, stamp: str) -> dict[str, object]:
    slug = "_".join(clean_token(x) for x in [shot.era, shot.scene, shot.season, shot.subject, shot.action])
    return {
        "id": f"akiyama_children_photo_{stamp}_{index:02d}",
        "title": title_for(shot, index),
        "prompt": build_prompt(shot),
        "negative_prompt": NEGATIVE_PROMPT,
        "suggested_params": suggested_params(shot),
        "filename_hint": f"children_documentary_{stamp}_{index:02d}_{slug}.png",
        "shot": asdict(shot),
    }


def markdown(items: Iterable[dict[str, object]]) -> str:
    parts = []
    for item in items:
        params = item["suggested_params"]
        assert isinstance(params, dict)
        parts.append(
            "\n".join(
                [
                    f"## {item['title']}",
                    "",
                    "**Prompt**",
                    "",
                    str(item["prompt"]),
                    "",
                    "**Negative prompt**",
                    "",
                    str(item["negative_prompt"]),
                    "",
                    "**Suggested params**",
                    "",
                    f"- aspect_ratio: {params['aspect_ratio']}",
                    f"- lens: {params['lens']}",
                    f"- aperture: {params['aperture']}",
                    f"- shutter: {params['shutter']}",
                    f"- exposure: {params['exposure']}",
                    f"- grain: {params['grain']}",
                    f"- filename_hint: {item['filename_hint']}",
                ]
            )
        )
    return "\n\n".join(parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate candid analog children's documentary photo prompts.")
    parser.add_argument("--brief", default="", help="Freeform scene details.")
    parser.add_argument("--count", type=int, default=1, help="Number of prompt items.")
    parser.add_argument("--preset", choices=["", "pack10"], default="", help="Built-in prompt pack.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatability.")
    parser.add_argument("--era", choices=sorted(ERAS), default="auto")
    parser.add_argument("--scene", choices=sorted(SCENES), default="auto")
    parser.add_argument("--season", choices=sorted(SEASONS), default="auto")
    parser.add_argument("--subject", choices=sorted(SUBJECTS), default="auto")
    parser.add_argument("--action", choices=sorted(ACTIONS), default="auto")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    shots = pack10() if args.preset == "pack10" else [make_shot(args, rng) for _ in range(max(1, args.count))]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    items = [item_for(shot, index, stamp) for index, shot in enumerate(shots, start=1)]

    if args.format == "markdown":
        print(markdown(items))
        return

    print(
        json.dumps(
            {
                "skill": "akiyama-children-photo",
                "mode": "prompt_only",
                "rights_note": "Prompts use high-level documentary language and intentionally avoid direct living-artist style invocation.",
                "count": len(items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

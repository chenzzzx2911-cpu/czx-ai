"""紫微斗数知识库"""
from src.ziwei import GONG_MEANINGS, MAIN_STAR_MEANINGS, SIHUA_MEANINGS
import json, os

_VERNACULAR = None

def _load():
    global _VERNACULAR
    if _VERNACULAR is None:
        path = os.path.join(os.path.dirname(__file__), 'vernacular_data.json')
        with open(path, encoding='utf-8') as f:
            _VERNACULAR = json.load(f)
    return _VERNACULAR

def get_star_vernacular(star_name: str) -> dict:
    data = _load()
    return data.get("star_vernacular", {}).get(star_name, {})

def get_gong_vernacular(gong_name: str) -> str:
    data = _load()
    return data.get("gong_vernacular", {}).get(gong_name, "")

def get_sihua_vernacular(sihua_type: str) -> str:
    data = _load()
    return data.get("sihua_vernacular", {}).get(sihua_type, "")

# 星曜组合规则
STAR_COMBOS = {
    ("紫微","天府"): "紫府同宫格——帝王+库藏，贵气非常，适合做领导者和大管家。",
    ("紫微","七杀"): "紫杀格——威权极重，适合军警、创业，但需防刚过易折。",
    ("太阳","太阴"): "日月同宫——光明与柔美并存，人缘极好，适合外交公关。",
    ("武曲","七杀"): "武杀格——刚猛至极，执行力超强，适合武职和竞技。",
    ("廉贞","贪狼"): "廉贪格——桃花混杂，魅力四射但需洁身自好。",
    ("天机","天梁"): "机梁格——智谋+长寿，善谋划且有长者之风，适合咨询。",
}

def analyze_gong(gong) -> dict:
    """分析单宫"""
    stars = gong.main_stars
    analysis = {
        "宫名": gong.name,
        "解释": GONG_MEANINGS.get(gong.name, ""),
        "主星": stars,
        "四化": gong.sihua,
    }
    if len(stars) >= 2:
        combo_key = tuple(sorted(stars[:2]))
        if combo_key in STAR_COMBOS:
            analysis["格局"] = STAR_COMBOS[combo_key]
    if stars:
        star = stars[0]
        if star in MAIN_STAR_MEANINGS:
            analysis["星性"] = MAIN_STAR_MEANINGS[star]
    return analysis

def analyze_ming_gong(chart) -> dict:
    """命宫为重点分析对象"""
    for gong in chart.gongs:
        if gong.is_ming_gong:
            return analyze_gong(gong)
    return {}

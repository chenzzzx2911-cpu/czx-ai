"""
五行生克体系：金水木火土 — 生克乘侮关系
"""

from enum import Enum
from typing import Dict, List

class WuxingType(Enum):
    JIN = "金"
    SHUI = "水"
    MU = "木"
    HUO = "火"
    TU = "土"

# 五行相生: 金生水, 水生木, 木生火, 火生土, 土生金
SHENG_MAP: Dict[str, str] = {
    "金": "水",
    "水": "木",
    "木": "火",
    "火": "土",
    "土": "金",
}

# 五行相克: 金克木, 木克土, 土克水, 水克火, 火克金
KE_MAP: Dict[str, str] = {
    "金": "木",
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
}

# 八卦对应的五行
TRIGRAM_WUXING: Dict[str, str] = {
    "乾": "金", "兑": "金",
    "离": "火",
    "震": "木", "巽": "木",
    "坎": "水",
    "艮": "土", "坤": "土",
}

def sheng(source: str, target: str) -> bool:
    """source 生 target?"""
    return SHENG_MAP.get(source) == target

def ke(source: str, target: str) -> bool:
    """source 克 target?"""
    return KE_MAP.get(source) == target

def ti_yong_relation(ti_wuxing: str, yong_wuxing: str) -> dict:
    """
    体用生克关系判定（梅花易数核心）
    返回: {relation, level, meaning}

    用生体 → 大吉（外部助我）
    比和   → 吉（和谐顺畅）
    体克用 → 小吉（我能掌控）
    体生用 → 小凶/泄气（付出多回报少）
    用克体 → 大凶（受制于人）
    """
    if ti_wuxing == yong_wuxing:
        return {"relation": "比和", "level": 2, "meaning": "和谐顺畅，主客相安，万事顺遂。"}
    if sheng(yong_wuxing, ti_wuxing):
        return {"relation": "用生体", "level": 3, "meaning": "大吉之象！外部环境助我，贵人相助，事半功倍。"}
    if ke(ti_wuxing, yong_wuxing):
        return {"relation": "体克用", "level": 1, "meaning": "小吉。我能掌控局面，但需付出努力方可成事。"}
    if sheng(ti_wuxing, yong_wuxing):
        return {"relation": "体生用", "level": -1, "meaning": "小凶/泄气。付出多而回报少，宜守不宜攻。"}
    if ke(yong_wuxing, ti_wuxing):
        return {"relation": "用克体", "level": -2, "meaning": "大凶之兆！外部环境不利，受制于人。宜避其锋芒，静待时机。"}
    return {"relation": "未知", "level": 0, "meaning": "无法判定"}

# 五行颜色（用于 Web UI）
WUXING_COLORS = {
    "金": "#FFD700",  # 金色
    "水": "#1E90FF",  # 蓝色
    "木": "#228B22",  # 绿色
    "火": "#FF4500",  # 红色
    "土": "#D2691E",  # 棕色
}

# 五行对应的季节旺衰
WUXING_SEASON_POWER = {
    "金": {"旺": "秋", "相": "四季末", "休": "冬", "囚": "春", "死": "夏"},
    "水": {"旺": "冬", "相": "秋", "休": "春", "囚": "夏", "死": "四季末"},
    "木": {"旺": "春", "相": "冬", "休": "夏", "囚": "四季末", "死": "秋"},
    "火": {"旺": "夏", "相": "春", "休": "四季末", "囚": "秋", "死": "冬"},
    "土": {"旺": "四季末", "相": "夏", "休": "秋", "囚": "冬", "死": "春"},
}

"""
易传哲学模块 — 十翼核心思想结构化
阴阳/刚柔/中正/时位/象数 — 从原文到可计算规则
来源: 《系辞》《彖传》《象传》《说卦》《序卦》《杂卦》
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ═══════════════════════════════════════════
# 一、阴阳模型
# ═══════════════════════════════════════════

class YinYang(Enum):
    YANG = 1  # 阳
    YIN = 0   # 阴

@dataclass
class YinYangRelation:
    """阴阳关系判定"""
    upper_yin_yang: YinYang  # 上卦阴阳
    lower_yin_yang: YinYang  # 下卦阴阳
    is_balanced: bool        # 是否阴阳平衡
    is_pure_yang: bool       # 纯阳(乾)
    is_pure_yin: bool        # 纯阴(坤)
    interpretation: str      # 解读


def analyze_yinyang(binary: str) -> YinYangRelation:
    """分析卦的阴阳结构"""
    upper = binary[:3]
    lower = binary[3:]

    def tri_yinyang(b3: str) -> YinYang:
        yang_count = b3.count("1")
        if yang_count >= 2:
            return YinYang.YANG
        return YinYang.YIN

    uu = tri_yinyang(upper)
    lu = tri_yinyang(lower)

    is_pure_yang = binary == "111111"
    is_pure_yin = binary == "000000"
    is_balanced = uu != lu

    if is_pure_yang:
        interp = "纯阳之体，刚健至极。创造力巅峰，但需警惕亢龙有悔。"
    elif is_pure_yin:
        interp = "纯阴之体，柔顺至极。包容承载力最强，厚德载物。"
    elif is_balanced:
        interp = "阴阳平衡。上阳下阴为泰(通)，上阴下阳为否(塞)。刚柔互济，最为和谐。" if uu == YinYang.YANG else "阴阳倒置。外柔内刚或外刚内柔，需具体判断。"
    else:
        interp = "阴阳同向。过于单一则缺乏弹性。"

    return YinYangRelation(upper_yin_yang=uu, lower_yin_yang=lu,
                           is_balanced=is_balanced, is_pure_yang=is_pure_yang,
                           is_pure_yin=is_pure_yin, interpretation=interp)


# ═══════════════════════════════════════════
# 二、中正原则
# ═══════════════════════════════════════════

def analyze_zhongzheng(binary: str, position: int) -> dict:
    """
    中正分析
    「中」= 二爻或五爻（下卦中位/上卦中位）
    「正」= 阳爻居阳位(1/3/5) 或 阴爻居阴位(2/4/6)

    返回: {is_zhong, is_zheng, meaning}
    """
    is_zhong = position in (2, 5)

    pos_yang = position in (1, 3, 5)
    yao_is_yang = binary[6 - position] == "1"

    is_zheng = (pos_yang and yao_is_yang) or (not pos_yang and not yao_is_yang)

    meanings = []
    if is_zhong and is_zheng:
        meanings.append("中正之位！最佳状态，德位相配。")
    elif is_zhong and not is_zheng:
        meanings.append("居中不正。位置对但德行需调整。")
    elif not is_zhong and is_zheng:
        meanings.append("正而不中。有原则但时机不当。")
    else:
        meanings.append("不中不正。需等待更好时机。")

    return {"is_zhong": is_zhong, "is_zheng": is_zheng, "meaning": " ".join(meanings)}


# ═══════════════════════════════════════════
# 三、刚柔变化规则
# ═══════════════════════════════════════════

def analyze_gangrou(binary: str) -> dict:
    """
    刚柔分析
    刚=阳爻 柔=阴爻
    变化=阳变阴 或 阴变阳
    """
    yang_count = binary.count("1")
    yin_count = binary.count("0")

    if yang_count >= 4:
        nature = "偏刚"
        advice = "刚过则折，需柔来济。适当示弱反而更能成事。"
    elif yin_count >= 4:
        nature = "偏柔"
        advice = "柔过则弱，需刚来济。该坚持时不要一味退让。"
    else:
        nature = "刚柔并济"
        advice = "平衡态，阴阳调和。保持现状继续推进。"

    return {"yang_count": yang_count, "yin_count": yin_count,
            "nature": nature, "advice": advice}


# ═══════════════════════════════════════════
# 四、时位思想
# ═══════════════════════════════════════════

def analyze_shiwei(position: int, binary: str) -> dict:
    """
    时位分析
    六爻对应六个发展阶段:
    初爻=潜伏 二爻=初显 三爻=谨慎
    四爻=尝试 五爻=巅峰 上爻=衰退
    """
    STAGES = {
        1: {"name": "潜伏期", "advice": "初出茅庐，宜隐不宜显。打好基础，等待时机。", "risk": "low"},
        2: {"name": "初显期", "advice": "崭露头角，宜见大人。主动展示但要谦虚。", "risk": "low"},
        3: {"name": "警惕期", "advice": "终日乾乾，如履薄冰。反复检查，严防出错。", "risk": "medium"},
        4: {"name": "尝试期", "advice": "或跃在渊，进退均可。关键是判断清楚再动。", "risk": "medium"},
        5: {"name": "巅峰期", "advice": "飞龙在天，光芒四射。但注意：巅峰之后是下坡。", "risk": "high"},
        6: {"name": "衰退期", "advice": "亢龙有悔。盛极则衰，及时收敛。该退就退。", "risk": "critical"},
    }

    stage = STAGES.get(position, STAGES[1])

    # 时位与爻性匹配
    pos_yang = position in (1, 3, 5)
    yao_is_yang = binary[6 - position] == "1"
    match = (pos_yang and yao_is_yang) or (not pos_yang and not yao_is_yang)

    return {**stage, "position": position, "position_match": match,
            "match_note": "当位(德位相配)" if match else "不当位(德不配位)"}


# ═══════════════════════════════════════════
# 五、象数映射系统
# ═══════════════════════════════════════════

# 卦象↔数字映射
XIANG_NUMBER_MAP = {
    # 八卦对应数字（先天/后天/河图/洛书）
    "111": {"先天":1, "后天":6, "河图":4, "洛书":6},   # 乾
    "110": {"先天":2, "后天":7, "河图":4, "洛书":7},   # 兑
    "101": {"先天":3, "后天":9, "河图":2, "洛书":9},   # 离
    "100": {"先天":4, "后天":3, "河图":3, "洛书":3},   # 震
    "011": {"先天":5, "后天":4, "河图":3, "洛书":4},   # 巽
    "010": {"先天":6, "后天":1, "河图":1, "洛书":1},   # 坎
    "001": {"先天":7, "后天":8, "河图":5, "洛书":8},   # 艮
    "000": {"先天":8, "后天":2, "河图":5, "洛书":2},   # 坤
}

# 卦象↔自然现象
XIANG_NATURE_MAP = {
    "111": "天", "110": "泽", "101": "火", "100": "雷",
    "011": "风", "010": "水", "001": "山", "000": "地",
}

# 卦象↔品德
XIANG_VIRTUE_MAP = {
    "111": "健", "110": "说", "101": "丽", "100": "动",
    "011": "入", "010": "陷", "001": "止", "000": "顺",
}

# 八卦↔身体部位 (黄帝内经同源)
XIANG_BODY_MAP = {
    "111": ["头","骨","肺","大肠"],
    "110": ["口","舌","肺","气管"],
    "101": ["目","心","小肠"],
    "100": ["足","肝","胆","筋"],
    "011": ["股","胆","呼吸道"],
    "010": ["耳","肾","膀胱","血"],
    "001": ["手","鼻","胃","背"],
    "000": ["腹","脾","胃","肉"],
}

# 八卦↔家庭成员
XIANG_FAMILY_MAP = {
    "111": "父亲", "000": "母亲",
    "100": "长子", "011": "长女",
    "010": "中男", "101": "中女",
    "001": "少男", "110": "少女",
}


# ═══════════════════════════════════════════
# 六、综合易传分析
# ═══════════════════════════════════════════

@dataclass
class YizhuanAnalysis:
    yinyang: YinYangRelation
    gangrou: dict
    zhongzheng_assessment: List[dict]  # 每爻的中正分析
    shiwei_assessment: dict
    trigram_image_upper: dict
    trigram_image_lower: dict
    overall: str


def analyze_by_yizhuan(binary: str, changing_positions: List[int] = None) -> YizhuanAnalysis:
    """综合易传分析"""
    if changing_positions is None:
        changing_positions = []

    # 阴阳
    yy = analyze_yinyang(binary)

    # 刚柔
    gr = analyze_gangrou(binary)

    # 中正 (所有爻)
    zz = [analyze_zhongzheng(binary, p) for p in range(1, 7)]

    # 时位 (取最重要的变爻位置，没有变爻则看二爻)
    key_pos = changing_positions[0] if changing_positions else 2
    sw = analyze_shiwei(key_pos, binary)

    # 上下卦象意
    from src.data.trigram_map import get_trigram_by_binary
    upper = get_trigram_by_binary(binary[:3])
    lower = get_trigram_by_binary(binary[3:])
    upper_img = {"name": upper.name if upper else "?", "nature": XIANG_NATURE_MAP.get(binary[:3], "?"),
                 "virtue": XIANG_VIRTUE_MAP.get(binary[:3], "?"), "body": XIANG_BODY_MAP.get(binary[:3], []),
                 "family": XIANG_FAMILY_MAP.get(binary[:3], "?")}
    lower_img = {"name": lower.name if lower else "?", "nature": XIANG_NATURE_MAP.get(binary[3:], "?"),
                 "virtue": XIANG_VIRTUE_MAP.get(binary[3:], "?"), "body": XIANG_BODY_MAP.get(binary[3:], []),
                 "family": XIANG_FAMILY_MAP.get(binary[3:], "?")}

    # 综合
    parts = []
    parts.append(f"上{upper_img['name']}下{lower_img['name']}——上为{upper_img['nature']}({upper_img['virtue']})下为{lower_img['nature']}({lower_img['virtue']})。")
    parts.append(yy.interpretation)
    parts.append(f"整体{gr['nature']}——{gr['advice']}")
    parts.append(f"当前处于{sw['name']}——{sw['advice']}")

    return YizhuanAnalysis(
        yinyang=yy, gangrou=gr, zhongzheng_assessment=zz,
        shiwei_assessment=sw, trigram_image_upper=upper_img,
        trigram_image_lower=lower_img, overall=" ".join(parts)
    )

"""
八卦映射系统：先天八卦数、后天八卦数、五行、方位、人物、身体等
参考：梅花易数·八卦万物类象
"""

from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Trigram:
    """单个八卦的完整信息"""
    name: str              # 卦名
    symbol: str            # 卦符
    binary: str            # 3位二进制 (从下往上: 初爻/中爻/上爻)
    xiantian_num: int      # 先天八卦数 (乾1兑2离3震4巽5坎6艮7坤8)
    houtian_num: int       # 后天八卦数 (坎1坤2震3巽4中5乾6兑7艮8离9)
    wuxing: str            # 五行属性
    direction: str         # 方位
    nature: str            # 自然象征
    personality: str       # 人物象征
    body_part: str         # 身体部位
    animal: str            # 动物
    season: str            # 季节/时令

TRIGRAMS: Dict[str, Trigram] = {
    "111": Trigram(  # 乾 ☰ 三连
        name="乾", symbol="☰", binary="111",
        xiantian_num=1, houtian_num=6,
        wuxing="金", direction="西北", nature="天",
        personality="父、君、首领", body_part="头、骨、肺",
        animal="马、龙", season="秋末冬初"
    ),
    "110": Trigram(  # 兑 ☱ 上缺
        name="兑", symbol="☱", binary="110",
        xiantian_num=2, houtian_num=7,
        wuxing="金", direction="西", nature="泽",
        personality="少女、说客", body_part="口、舌、肺",
        animal="羊", season="秋"
    ),
    "101": Trigram(  # 离 ☲ 中虚
        name="离", symbol="☲", binary="101",
        xiantian_num=3, houtian_num=9,
        wuxing="火", direction="南", nature="火、日",
        personality="中女、文人", body_part="目、心",
        animal="雉、龟", season="夏"
    ),
    "100": Trigram(  # 震 ☳ 仰盂
        name="震", symbol="☳", binary="100",
        xiantian_num=4, houtian_num=3,
        wuxing="木", direction="东", nature="雷",
        personality="长男、将帅", body_part="足、肝",
        animal="龙", season="春"
    ),
    "011": Trigram(  # 巽 ☴ 下断
        name="巽", symbol="☴", binary="011",
        xiantian_num=5, houtian_num=4,
        wuxing="木", direction="东南", nature="风",
        personality="长女、商人", body_part="股、胆",
        animal="鸡", season="春夏之交"
    ),
    "010": Trigram(  # 坎 ☵ 中满
        name="坎", symbol="☵", binary="010",
        xiantian_num=6, houtian_num=1,
        wuxing="水", direction="北", nature="水、雨",
        personality="中男、盗贼", body_part="耳、肾",
        animal="猪、鱼", season="冬"
    ),
    "001": Trigram(  # 艮 ☶ 覆碗
        name="艮", symbol="☶", binary="001",
        xiantian_num=7, houtian_num=8,
        wuxing="土", direction="东北", nature="山",
        personality="少男、隐士", body_part="手、脾",
        animal="狗、鼠", season="冬末春初"
    ),
    "000": Trigram(  # 坤 ☷ 六断
        name="坤", symbol="☰", binary="000",
        xiantian_num=8, houtian_num=2,
        wuxing="土", direction="西南", nature="地",
        personality="母、臣民", body_part="腹、脾",
        animal="牛", season="夏末秋初"
    ),
}

# 快捷查询
def get_trigram_by_binary(binary: str) -> Optional[Trigram]:
    return TRIGRAMS.get(binary)

def get_trigram_by_name(name: str) -> Optional[Trigram]:
    for t in TRIGRAMS.values():
        if t.name == name:
            return t
    return None

def get_trigram_by_xiantian(num: int) -> Optional[Trigram]:
    for t in TRIGRAMS.values():
        if t.xiantian_num == num:
            return t
    return None

# 六十四卦的上卦/下卦映射表
# key: 6位binary, value: (下卦binary, 上卦binary)
def split_hexagram(binary_6: str) -> tuple[str, str]:
    """将6位binary拆分为下卦(初爻-三爻)和上卦(四爻-上爻)
    注意：binary从左到右是上爻到初爻，所以下卦=后3位，上卦=前3位
    """
    return binary_6[3:], binary_6[:3]

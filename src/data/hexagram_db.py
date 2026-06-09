"""
增强卦象数据库 — 封装 gua_yao_ci.json，提供完整查询接口
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .trigram_map import split_hexagram, get_trigram_by_binary
from .wuxing import TRIGRAM_WUXING

DATA_DIR = Path(__file__).parent.parent.parent / "data"


@dataclass
class YaoLine:
    """爻"""
    position: int        # 1-6 (初爻=1, 上爻=6)
    type_str: str        # "初九"/"六二" 等
    is_yang: bool        # True=阳, False=阴
    text: str            # 爻辞原文
    xiao_xiang: str      # 小象传


@dataclass
class Hexagram:
    """六十四卦完整数据"""
    id: int                          # 卦序 (1-64)
    name: str                        # 卦名
    binary: str                      # 6位二进制
    symbol: str                      # 卦符 Unicode
    upper_trigram: str               # 上卦名
    lower_trigram: str               # 下卦名
    upper_trigram_binary: str        # 上卦二进制
    lower_trigram_binary: str        # 下卦二进制
    upper_wuxing: str                # 上卦五行
    lower_wuxing: str                # 下卦五行
    gua_ci: str                      # 卦辞
    tuan_ci: str                     # 彖传
    da_xiang_ci: str                 # 大象传
    yao_lines: List[YaoLine] = field(default_factory=list)
    hu_gua_binary: str = ""          # 互卦binary
    hu_gua_name: str = ""            # 互卦名
    zong_gua_binary: str = ""        # 综卦binary（倒置）
    cuo_gua_binary: str = ""         # 错卦binary（全反）
    wuxing: str = ""                 # 卦的五行（取上卦为主）


class HexagramDB:
    """六十四卦数据库"""

    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            data_path = DATA_DIR / "gua_yao_ci.json"

        with open(data_path, encoding='utf-8') as f:
            raw = json.load(f)

        self._raw = raw
        self._hexagrams: Dict[str, Hexagram] = {}  # key: binary
        self._build()

    def _build(self):
        """构建增强的卦象对象"""
        for binary, raw_gua in self._raw.items():
            # 拆分上下卦
            lower_bin, upper_bin = split_hexagram(binary)
            lower_tri = get_trigram_by_binary(lower_bin)
            upper_tri = get_trigram_by_binary(upper_bin)

            lower_name = lower_tri.name if lower_tri else "?"
            upper_name = upper_tri.name if upper_tri else "?"

            # 五行
            lower_wx = TRIGRAM_WUXING.get(lower_name, "?")
            upper_wx = TRIGRAM_WUXING.get(upper_name, "?")

            # 构建爻列表
            yao_lines = []
            if "yao_ci" in raw_gua:
                yang_count = binary.count("1")
                for i, yao_text in enumerate(raw_gua["yao_ci"]):
                    pos = i + 1  # 初爻=1
                    is_yang = binary[5 - i] == "1"  # binary[5]=初爻, binary[0]=上爻

                    # 爻名
                    if is_yang:
                        yao_name = {1: "初九", 2: "九二", 3: "九三",
                                   4: "九四", 5: "九五", 6: "上九"}[pos]
                    else:
                        yao_name = {1: "初六", 2: "六二", 3: "六三",
                                   4: "六四", 5: "六五", 6: "上六"}[pos]

                    xiao_xiang = ""
                    if "xiao_xiang_ci" in raw_gua:
                        xx_list = raw_gua["xiao_xiang_ci"]
                        if i < len(xx_list):
                            xiao_xiang = xx_list[i]

                    yao_lines.append(YaoLine(
                        position=pos,
                        type_str=yao_name,
                        is_yang=is_yang,
                        text=yao_text,
                        xiao_xiang=xiao_xiang
                    ))

            # 互卦 (2-5爻): 下互=2,3,4爻, 上互=3,4,5爻
            hu_lower = binary[3] + binary[2] + binary[1]  # 第2,3,4爻
            hu_upper = binary[2] + binary[1] + binary[0]  # 第3,4,5爻
            hu_binary = hu_upper + hu_lower

            # 综卦 (倒置整个卦)
            zong_binary = binary[::-1]

            # 错卦 (阴阳全反)
            cuo_binary = "".join("1" if c == "0" else "0" for c in binary)

            hexagram = Hexagram(
                id=raw_gua.get("id", 0),
                name=raw_gua.get("name_cn", "?"),
                binary=binary,
                symbol=self._get_symbol(binary),
                upper_trigram=upper_name,
                lower_trigram=lower_name,
                upper_trigram_binary=upper_bin,
                lower_trigram_binary=lower_bin,
                upper_wuxing=upper_wx,
                lower_wuxing=lower_wx,
                gua_ci=raw_gua.get("gua_ci", ""),
                tuan_ci=raw_gua.get("tuan_ci", ""),
                da_xiang_ci=raw_gua.get("da_xiang_ci", ""),
                yao_lines=yao_lines,
                hu_gua_binary=hu_binary,
                zong_gua_binary=zong_binary,
                cuo_gua_binary=cuo_binary,
                wuxing=upper_wx,  # 默认以上卦五行代表全卦
            )
            self._hexagrams[binary] = hexagram

    @staticmethod
    def _get_symbol(binary: str) -> str:
        """获取卦符 Unicode — 64卦专属符号 (U+4DC0~U+4DFF, 按周易卦序)"""
        # 64卦二进制→卦序 映射表 (通行本周易序)
        BINARY_TO_ORDER = {
            "111111": 1,   # ䷀ 乾
            "000000": 2,   # ䷁ 坤
            "100010": 3,   # ䷂ 屯
            "010001": 4,   # ䷃ 蒙
            "010111": 5,   # ䷄ 需
            "111010": 6,   # ䷅ 讼
            "000010": 7,   # ䷆ 师
            "010000": 8,   # ䷇ 比
            "110111": 9,   # ䷈ 小畜
            "111011": 10,  # ䷉ 履
            "000111": 11,  # ䷊ 泰
            "111000": 12,  # ䷋ 否
            "111101": 13,  # ䷌ 同人
            "101111": 14,  # ䷍ 大有
            "000100": 15,  # ䷎ 谦
            "001000": 16,  # ䷏ 豫
            "011001": 17,  # ䷐ 随
            "100110": 18,  # ䷑ 蛊
            "000011": 19,  # ䷒ 临
            "110000": 20,  # ䷓ 观
            "101001": 21,  # ䷔ 噬嗑
            "100101": 22,  # ䷕ 贲
            "000001": 23,  # ䷖ 剥
            "100000": 24,  # ䷗ 复
            "111001": 25,  # ䷘ 无妄
            "100111": 26,  # ䷙ 大畜
            "100001": 27,  # ䷚ 颐
            "011110": 28,  # ䷛ 大过
            "010010": 29,  # ䷜ 坎
            "101101": 30,  # ䷝ 离
            "011100": 31,  # ䷞ 咸
            "001110": 32,  # ䷟ 恒
            "111100": 33,  # ䷠ 遁
            "001111": 34,  # ䷡ 大壮
            "101000": 35,  # ䷢ 晋
            "000101": 36,  # ䷣ 明夷
            "110101": 37,  # ䷤ 家人
            "101011": 38,  # ䷥ 睽
            "010100": 39,  # ䷦ 蹇
            "001010": 40,  # ䷧ 解
            "100011": 41,  # ䷨ 损
            "110001": 42,  # ䷩ 益
            "011111": 43,  # ䷪ 夬
            "111110": 44,  # ䷫ 姤
            "011000": 45,  # ䷬ 萃
            "000110": 46,  # ䷭ 升
            "011010": 47,  # ䷮ 困
            "010110": 48,  # ䷯ 井
            "011101": 49,  # ䷰ 革
            "101110": 50,  # ䷱ 鼎
            "001001": 51,  # ䷲ 震
            "100100": 52,  # ䷳ 艮
            "110100": 53,  # ䷴ 渐
            "001011": 54,  # ䷵ 归妹
            "001101": 55,  # ䷶ 丰
            "101100": 56,  # ䷷ 旅
            "110110": 57,  # ䷸ 巽
            "011011": 58,  # ䷹ 兑
            "010011": 59,  # ䷺ 涣
            "110010": 60,  # ䷻ 节
            "110011": 61,  # ䷼ 中孚
            "001100": 62,  # ䷽ 小过
            "010101": 63,  # ䷾ 既济
            "101010": 64,  # ䷿ 未济
        }
        order = BINARY_TO_ORDER.get(binary, 1)
        # Unicode Yijing block: U+4DC0 = ䷀ = 卦序1
        return chr(0x4DBF + order)

    def get(self, binary: str) -> Optional[Hexagram]:
        """按二进制key获取卦"""
        return self._hexagrams.get(binary)

    def get_by_id(self, id_val: int) -> Optional[Hexagram]:
        """按卦序ID获取"""
        for h in self._hexagrams.values():
            if h.id == id_val:
                return h
        return None

    def get_by_name(self, name: str) -> Optional[Hexagram]:
        """按卦名获取"""
        for h in self._hexagrams.values():
            if h.name == name:
                return h
        return None

    def all_hexagrams(self) -> List[Hexagram]:
        """所有卦（按ID排序）"""
        return sorted(self._hexagrams.values(), key=lambda h: h.id)

    def __len__(self) -> int:
        return len(self._hexagrams)

    def __contains__(self, binary: str) -> bool:
        return binary in self._hexagrams


# 全局单例
_db_instance: Optional[HexagramDB] = None

def get_db() -> HexagramDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = HexagramDB()
    return _db_instance

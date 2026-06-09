"""
起卦引擎 — 多种起卦方式，统一输出 CastResult
"""

from dataclasses import dataclass, field
from typing import List, Optional
import random
import time
from datetime import datetime


@dataclass
class CastResult:
    """起卦结果"""
    method: str                           # 起卦方式
    original_binary: str                  # 本卦二进制 (6位, 阳=1 阴=0)
    changing_lines: List[int]             # 变爻位置 (1-6)
    changed_binary: str                   # 变卦二进制 (无变爻则=本卦)
    hexagram_id: int = 0                  # 本卦ID
    changed_hexagram_id: int = 0          # 变卦ID
    lines_detail: List[dict] = field(default_factory=list)  # 每爻详情
    timestamp: str = ""                   # 起卦时间
    calc_detail: dict = field(default_factory=dict)  # 推算过程(时间卦/数字卦用)

    def has_changing_lines(self) -> bool:
        return len(self.changing_lines) > 0

    def __str__(self) -> str:
        return f"本卦: {self.original_binary} | 变爻: {self.changing_lines} | 变卦: {self.changed_binary}"


def _build_cast_result(method: str, lines: List[int],
                       lines_detail: List[dict]) -> CastResult:
    """从6次爻结果构建 CastResult"""
    # 本卦: 老阳(9)和老阴(6)是变爻，但本卦中 9→阳(1), 6→阴(0); 少阳(7)→阳(1), 少阴(8)→阴(0)
    original = ""
    changed = ""
    changing = []

    for i, ld in enumerate(lines_detail):
        pos = i + 1
        value = ld["value"]

        if value == 9:  # 老阳 → 变阴
            original += "1"
            changed += "0"
            changing.append(pos)
        elif value == 6:  # 老阴 → 变阳
            original += "0"
            changed += "1"
            changing.append(pos)
        elif value == 7:  # 少阳 → 不变
            original += "1"
            changed += "1"
        elif value == 8:  # 少阴 → 不变
            original += "0"
            changed += "0"

    # binary 顺序: 上爻...初爻（从高位到低位）
    # 我们按初爻到上爻的顺序收集，所以需要反转
    original = original[::-1]
    changed = changed[::-1]

    return CastResult(
        method=method,
        original_binary=original,
        changing_lines=changing,
        changed_binary=changed,
        lines_detail=lines_detail,
        timestamp=datetime.now().isoformat()
    )


def money_casting(tosses: Optional[List[int]] = None) -> CastResult:
    """
    金钱卦（金钱课）
    3枚铜钱抛6次，每次得一爻：
      3个正面(阳面) = 老阳(9) — 变爻
      2正1反 = 少阳(7) — 不变
      1正2反 = 少阴(8) — 不变
      3个反面 = 老阴(6) — 变爻
    如不提供 tosses，自动随机生成
    """
    lines_detail = []

    for i in range(6):
        if tosses and i < len(tosses):
            heads = tosses[i]  # 正面数
        else:
            # 模拟3枚铜钱：每枚 0.5 概率正面
            heads = sum(1 for _ in range(3) if random.random() > 0.5)

        value_map = {3: 9, 2: 7, 1: 8, 0: 6}
        name_map = {9: "老阳 ⚊○", 7: "少阳 ⚊", 8: "少阴 ⚋", 6: "老阴 ⚋×"}

        value = value_map[heads]
        pos_name = {1: "初", 2: "二", 3: "三", 4: "四", 5: "五", 6: "上"}[i + 1]
        is_yang = value in (9, 7)
        yao_name = f"{pos_name}{'九' if is_yang else '六'}"

        lines_detail.append({
            "position": i + 1,
            "name": yao_name,
            "heads": heads,
            "value": value,
            "is_changing": value in (9, 6),
            "desc": name_map[value],
        })

    return _build_cast_result("金钱卦", [], lines_detail)


# 先天八卦数映射 (余数→卦名+二进制)
NUM_TO_TRIGRAM = {0:("坤","000"), 1:("乾","111"), 2:("兑","110"), 3:("离","101"),
                  4:("震","100"), 5:("巽","011"), 6:("坎","010"), 7:("艮","001")}

def time_casting(dt: Optional[datetime] = None) -> CastResult:
    """
    时间卦（梅花易数·年月日时起卦法）
    上卦 = (年支数 + 月 + 日) % 8   → 先天八卦数
    下卦 = (年支数 + 月 + 日 + 时支数) % 8
    动爻 = (年支数 + 月 + 日 + 时支数) % 6

    地支序数: 子1丑2寅3卯4辰5巳6午7未8申9酉10戌11亥12
    先天八卦数: 1乾☰ 2兑☱ 3离☲ 4震☳ 5巽☴ 6坎☵ 7艮☶ 8坤☷
    """
    if dt is None:
        dt = datetime.now()

    # 年支序数 (以立春为界，此处简化按公历年计算，误差在立春前后)
    # 2024甲辰年 → 辰=5, 2025乙巳年→巳=6
    year_branch = (dt.year - 4) % 12 + 1
    month = dt.month
    day = dt.day
    hour = dt.hour

    # 时支序: 23-1→子=1, 1-3→丑=2, 3-5→寅=3, ..., 21-23→亥=12
    hour_branch = ((hour + 1) // 2) % 12
    if hour_branch == 0:
        hour_branch = 12

    # 上卦
    upper_raw = year_branch + month + day
    upper_num = upper_raw % 8  # 0→坤
    # 下卦
    lower_raw = year_branch + month + day + hour_branch
    lower_num = lower_raw % 8
    # 动爻
    moving_num = (year_branch + month + day + hour_branch) % 6  # 0→上爻

    upper_name, upper_bin = NUM_TO_TRIGRAM[upper_num]
    lower_name, lower_bin = NUM_TO_TRIGRAM[lower_num]

    original_bin = upper_bin + lower_bin

    # 动爻: 1-6，余数0→上爻(6)
    changing_pos = moving_num if moving_num != 0 else 6

    # 变卦
    changed_list = list(original_bin)
    idx = 6 - changing_pos
    changed_list[idx] = "1" if changed_list[idx] == "0" else "0"
    changed_bin = "".join(changed_list)

    # 地支名称
    ZHI_NAMES = {1:"子",2:"丑",3:"寅",4:"卯",5:"辰",6:"巳",7:"午",8:"未",9:"申",10:"酉",11:"戌",12:"亥"}

    # 构建 lines_detail
    lines_detail = []
    for i in range(6):
        pos = i + 1
        is_yang = original_bin[5 - i] == "1"
        pos_name = {1:"初",2:"二",3:"三",4:"四",5:"五",6:"上"}[pos]
        yao_name = f"{pos_name}{'九' if is_yang else '六'}"
        is_changing = (pos == changing_pos)
        lines_detail.append({
            "position": pos, "name": yao_name,
            "value": 9 if (is_yang and is_changing) else (6 if (not is_yang and is_changing) else (7 if is_yang else 8)),
            "is_changing": is_changing,
            "desc": f"{'老' if is_changing else '少'}{'阳' if is_yang else '阴'}",
        })

    # 附加推算过程
    calc_detail = {
        "year_branch_num": year_branch, "year_branch_name": ZHI_NAMES[year_branch],
        "month": month, "day": day,
        "hour_branch_num": hour_branch, "hour_branch_name": ZHI_NAMES[hour_branch],
        "upper_formula": f"({year_branch}+{month}+{day})%8 = {upper_raw}%8 = {upper_num}→{upper_name}☰" if upper_name=="乾" else f"({year_branch}+{month}+{day})%8 = {upper_raw}%8 = {upper_num}→{upper_name}",
        "lower_formula": f"({year_branch}+{month}+{day}+{hour_branch})%8 = {lower_raw}%8 = {lower_num}→{lower_name}",
        "moving_formula": f"({year_branch}+{month}+{day}+{hour_branch})%6 = {lower_raw}%6 = {moving_num}→第{changing_pos if changing_pos!=0 else 6}爻",
    }

    return CastResult(
        method="时间卦",
        original_binary=original_bin,
        changing_lines=[changing_pos],
        changed_binary=changed_bin,
        lines_detail=lines_detail,
        timestamp=dt.isoformat(),
        calc_detail=calc_detail
    )


def number_casting(n1: int, n2: int = 0, n3: int = 0) -> CastResult:
    """
    数字卦
    上卦 = n1 % 8, 下卦 = n2 % 8, 动爻 = n3 % 6
    只有一个数字时: n1 的前半部分为上卦，后半部分为下卦
    """
    if n2 == 0 and n3 == 0:
        # 只有一个数字，拆分
        s = str(n1)
        mid = len(s) // 2
        n2 = int(s[:mid]) if mid > 0 else 1
        n3_val = int(s[mid:]) if mid < len(s) else n1
        upper_n = n2 % 8
        lower_n = n3_val % 8
        moving_n = (n1 % 6)
    else:
        upper_n = n1 % 8
        lower_n = n2 % 8
        moving_n = n3 % 6

    xiantian_to_binary = {
        1: "111", 2: "110", 3: "101", 4: "100",
        5: "011", 6: "010", 7: "001", 8: "000",
    }
    upper_bin = xiantian_to_binary.get(upper_n if upper_n != 0 else 8, "000")
    lower_bin = xiantian_to_binary.get(lower_n if lower_n != 0 else 8, "000")

    original_bin = upper_bin + lower_bin
    changing_pos = moving_n if moving_n != 0 else 6

    changed_list = list(original_bin)
    idx = 6 - changing_pos
    changed_list[idx] = "1" if changed_list[idx] == "0" else "0"
    changed_bin = "".join(changed_list)

    lines_detail = []
    for i in range(6):
        pos = i + 1
        is_yang = original_bin[5 - i] == "1"
        pos_name = {1: "初", 2: "二", 3: "三", 4: "四", 5: "五", 6: "上"}[pos]
        yao_name = f"{pos_name}{'九' if is_yang else '六'}"
        is_changing = (pos == changing_pos)

        lines_detail.append({
            "position": pos,
            "name": yao_name,
            "value": 9 if (is_yang and is_changing) else (6 if (not is_yang and is_changing) else (7 if is_yang else 8)),
            "is_changing": is_changing,
            "desc": f"{'老' if is_changing else '少'}{'阳' if is_yang else '阴'}",
        })

    return CastResult(
        method=f"数字卦 ({n1},{n2},{n3 if n3 else n1%6})",
        original_binary=original_bin,
        changing_lines=[changing_pos],
        changed_binary=changed_bin,
        lines_detail=lines_detail,
        timestamp=datetime.now().isoformat(),
        calc_detail={
            "input": f"({n1},{n2},{n3})",
            "upper_formula": f"上卦: {n1}%8 = {upper_n}→{NUM_TO_TRIGRAM.get(upper_n if upper_n!=0 else 8,('?','000'))[0]}",
            "lower_formula": f"下卦: {n2}%8 = {lower_n}→{NUM_TO_TRIGRAM.get(lower_n if lower_n!=0 else 8,('?','000'))[0]}",
            "moving_formula": f"动爻: {n3}%6 = {moving_n}→第{changing_pos if changing_pos!=0 else 6}爻",
        }
    )


def random_casting() -> CastResult:
    """随机起卦 — 等同于金钱卦的随机模式"""
    return money_casting()

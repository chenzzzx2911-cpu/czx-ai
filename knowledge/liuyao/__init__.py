"""
六爻纳甲预测系统 v1 — 京房八宫纳甲 + 火珠林 + 增删卜易
完整装卦流程: 起卦→八宫定位→纳干支→装六亲→定世应→配六神→取用神→断旺衰
来源: 《火珠林》《增删卜易》《京房易传》、najia PyPI库、开源研究
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

# ═══════════════════════════════════════════
# 一、八宫六十四卦体系 (京房八宫)
# ═══════════════════════════════════════════

# 八宫: 每宫包括本宫卦→一世→二世→三世→四世→五世→游魂→归魂
EIGHT_PALACES = {
    "乾宫": {"wuxing": "金", "gua": ["111111","111110","111100","111000","110000","100000","101000","111101"]},
    "坎宫": {"wuxing": "水", "gua": ["010010","010011","010001","010000","000010","001010","110010","010111"]},
    "艮宫": {"wuxing": "土", "gua": ["001001","001011","001000","000001","100001","110001","111001","001010"]},
    "震宫": {"wuxing": "木", "gua": ["100100","100101","100001","100000","000100","001100","110100","100110"]},
    "巽宫": {"wuxing": "木", "gua": ["011011","011010","011000","010000","000011","001011","101011","011100"]},
    "离宫": {"wuxing": "火", "gua": ["101101","101100","101000","100000","000101","001101","111101","101001"]},
    "坤宫": {"wuxing": "土", "gua": ["000000","000001","000011","000111","001111","011111","010111","000010"]},
    "兑宫": {"wuxing": "金", "gua": ["110110","110111","110101","110001","100011","010011","000011","110010"]},
}

# 卦宫映射: binary → 宫名
GUA_TO_PALACE = {}
for palace_name, data in EIGHT_PALACES.items():
    for i, binary in enumerate(data["gua"]):
        GUA_TO_PALACE[binary] = (palace_name, data["wuxing"], i)  # i = 0本宫 1一世 2二世...

# 世应位置映射 (以第几个卦为准: 0本宫→世6应3, 1一世→世1应4, ...)
SHI_YING_POSITIONS = {
    0: (6, 3),   # 本宫
    1: (1, 4),   # 一世
    2: (2, 5),   # 二世
    3: (3, 6),   # 三世
    4: (4, 1),   # 四世
    5: (5, 2),   # 五世
    6: (4, 1),   # 游魂
    7: (3, 6),   # 归魂
}


# ═══════════════════════════════════════════
# 二、纳甲干支系统
# ═══════════════════════════════════════════

# 天干
TIAN_GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
# 地支
DI_ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

# 八卦纳天干规则
TRIGRAM_TIANGAN = {
    "111": ("甲", "壬"),  # 乾: 内甲外壬
    "000": ("乙", "癸"),  # 坤: 内乙外癸
    "100": ("庚", "庚"),  # 震: 纳庚
    "011": ("辛", "辛"),  # 巽: 纳辛
    "010": ("戊", "戊"),  # 坎: 纳戊
    "101": ("己", "己"),  # 离: 纳己
    "001": ("丙", "丙"),  # 艮: 纳丙
    "110": ("丁", "丁"),  # 兑: 纳丁
}

# 八卦纳地支规则 (初爻到上爻)
TRIGRAM_DIZHI = {
    "乾": ["子","寅","辰","午","申","戌"],  # 阳宫顺行
    "坎": ["寅","辰","午","申","戌","子"],
    "艮": ["辰","午","申","戌","子","寅"],
    "震": ["子","寅","辰","午","申","戌"],
    "巽": ["丑","亥","酉","未","巳","卯"],  # 阴宫逆行
    "离": ["卯","丑","亥","酉","未","巳"],
    "坤": ["未","巳","卯","丑","亥","酉"],
    "兑": ["巳","卯","丑","亥","酉","未"],
}

# 地支藏干
DIZHI_CANGGAN = {
    "子": ["癸"],
    "丑": ["己","癸","辛"],
    "寅": ["甲","丙","戊"],
    "卯": ["乙"],
    "辰": ["戊","乙","癸"],
    "巳": ["丙","庚","戊"],
    "午": ["丁","己"],
    "未": ["己","丁","乙"],
    "申": ["庚","壬","戊"],
    "酉": ["辛"],
    "戌": ["戊","辛","丁"],
    "亥": ["壬","甲"],
}

# 五行对应天干
GAN_WUXING = {
    "甲":"木","乙":"木","丙":"火","丁":"火",
    "戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"
}

# 五行对应地支
ZHI_WUXING = {
    "子":"水","丑":"土","寅":"木","卯":"木",
    "辰":"土","巳":"火","午":"火","未":"土",
    "申":"金","酉":"金","戌":"土","亥":"水"
}

# 天干五行阴阳
GAN_YINYANG = {
    "甲":"阳","乙":"阴","丙":"阳","丁":"阴",
    "戊":"阳","己":"阴","庚":"阳","辛":"阴","壬":"阳","癸":"阴"
}


# ═══════════════════════════════════════════
# 三、六亲系统
# ═══════════════════════════════════════════

def determine_liuqin(yao_wuxing: str, palace_wuxing: str) -> str:
    """
    六亲判定: 以卦宫五行为「我」
    生我者→父母  我生者→子孙
    克我者→官鬼  我克者→妻财
    同我者→兄弟
    """
    if yao_wuxing == palace_wuxing:
        return "兄弟"
    from src.data.wuxing import sheng, ke

    if sheng(palace_wuxing, yao_wuxing):
        return "子孙"  # 我生之
    if sheng(yao_wuxing, palace_wuxing):
        return "父母"  # 生我之
    if ke(palace_wuxing, yao_wuxing):
        return "妻财"  # 我克之
    if ke(yao_wuxing, palace_wuxing):
        return "官鬼"  # 克我之

    return "兄弟"


# ═══════════════════════════════════════════
# 四、六神系统
# ═══════════════════════════════════════════

LIUSHEN_ORDER = ["青龙","朱雀","勾陈","螣蛇","白虎","玄武"]
LIUSHEN_MEANING = {
    "青龙": {"吉凶":"大吉","象意":"贵人、喜事、酒色、财帛","颜色":"青","方向":"东"},
    "朱雀": {"吉凶":"平","象意":"口舌、文书、信息、火灾","颜色":"红","方向":"南"},
    "勾陈": {"吉凶":"平偏凶","象意":"田土、牢狱、迟滞、稳重","颜色":"黄","方向":"中"},
    "螣蛇": {"吉凶":"凶","象意":"虚惊、怪异、噩梦、阴邪","颜色":"紫","方向":"不定"},
    "白虎": {"吉凶":"大凶","象意":"血光、丧事、病伤、刑罚","颜色":"白","方向":"西"},
    "玄武": {"吉凶":"凶","象意":"盗贼、暗昧、隐私、水患","颜色":"黑","方向":"北"},
}

# 六神起法: 日干定初爻
RI_GAN_LIUSHEN_START = {
    "甲":"青龙","乙":"青龙",
    "丙":"朱雀","丁":"朱雀",
    "戊":"勾陈",
    "己":"螣蛇",
    "庚":"白虎","辛":"白虎",
    "壬":"玄武","癸":"玄武",
}


def get_liushen(day_gan: str) -> List[str]:
    """获取当日六神序列（初爻→上爻）"""
    start = RI_GAN_LIUSHEN_START.get(day_gan, "青龙")
    idx = LIUSHEN_ORDER.index(start)
    return [LIUSHEN_ORDER[(idx + i) % 6] for i in range(6)]


# ═══════════════════════════════════════════
# 五、用神选取系统
# ═══════════════════════════════════════════

YONGSHEN_MAP = {
    # (事项, 关键词) → 用神
    "财运": ("妻财", "妻财爻主钱财、利益、物资"),
    "投资": ("妻财", "妻财爻主投资收益"),
    "事业": ("官鬼", "官鬼爻主官职、事业、工作变动"),
    "考试": ("父母", "父母爻主文书、考试、学历"),
    "文书": ("父母", "父母爻主文书、合同、证件"),
    "感情": ("官鬼", "女测男取官鬼；男测女取妻财"),
    "婚姻": ("妻财", "妻财爻主妻室、婚姻"),
    "健康": ("子孙", "子孙爻主医药、健康、疾病能否治愈"),
    "疾病": ("官鬼", "官鬼爻主疾病、灾祸"),
    "子女": ("子孙", "子孙爻主子嗣、晚辈"),
    "出行": ("子孙", "子孙爻主旅途平安、解忧"),
    "官非": ("官鬼", "官鬼爻主官司、刑罚"),
    "竞争": ("兄弟", "兄弟爻主竞争、合伙"),
    "父母": ("父母", "父母爻主长辈、庇护"),
    "天气": ("妻财", "妻财爻主晴天(财=晴)，父母爻主雨(父=雨)"),
    "失物": ("子孙", "子孙爻主寻回、解忧"),
}

def select_yongshen(topic: str) -> dict:
    """根据问事主题选择用神"""
    for keyword, (yongshen, desc) in YONGSHEN_MAP.items():
        if keyword in topic:
            return {"yongshen": yongshen, "description": desc, "confidence": 0.85}
    return {"yongshen": "妻财", "description": "默认取妻财为用神", "confidence": 0.5}


# ═══════════════════════════════════════════
# 六、旺衰判断系统
# ═══════════════════════════════════════════

# 月建旺衰 (季节强度)
YUE_WANG_SHUAI = {
    "春": {"旺":"木","相":"火","休":"水","囚":"金","死":"土"},
    "夏": {"旺":"火","相":"土","休":"木","囚":"水","死":"金"},
    "秋": {"旺":"金","相":"水","休":"土","囚":"火","死":"木"},
    "冬": {"旺":"水","相":"木","休":"金","囚":"土","死":"火"},
    "四季末": {"旺":"土","相":"金","休":"火","囚":"水","死":"木"},
}

def get_season(month: int) -> str:
    """月→季节"""
    if 3 <= month <= 5: return "春"
    elif 6 <= month <= 8: return "夏"
    elif 9 <= month <= 11: return "秋"
    elif month in (12, 1, 2): return "冬"
    return "春"

def judge_wangshuai(wuxing: str, month: int, day_zhi: str = None) -> dict:
    """
    旺衰判断 - 综合月建和日辰
    返回: (旺衰等级, 得分, 说明)
    """
    season = get_season(month)
    season_power = YUE_WANG_SHUAI.get(season, {})

    # 找五行在当季的状态
    state = "休"
    for s, wx in season_power.items():
        if wx == wuxing:
            state = s
            break

    state_scores = {"旺": 10, "相": 7, "休": 4, "囚": 2, "死": 1}
    score = state_scores.get(state, 4)

    # 日辰调整
    day_effect = ""
    if day_zhi:
        day_wx = ZHI_WUXING.get(day_zhi)
        if day_wx:
            from src.data.wuxing import sheng, ke
            if day_wx == wuxing:
                score += 2
                day_effect = "日辰同五行+2"
            elif sheng(day_wx, wuxing):
                score += 1
                day_effect = "日辰生之+1"
            elif ke(day_wx, wuxing):
                score -= 2
                day_effect = "日辰克之-2"

    if score >= 10: level = "极旺"
    elif score >= 7: level = "旺相"
    elif score >= 4: level = "平和"
    elif score >= 2: level = "衰弱"
    else: level = "极衰"

    return {"level": level, "score": score, "season_state": state, "day_effect": day_effect, "confidence": min(score/10, 1.0)}


# ═══════════════════════════════════════════
# 七、完整装卦引擎
# ═══════════════════════════════════════════

@dataclass
class NajiaYao:
    """纳甲爻"""
    position: int          # 1-6
    binary_val: str        # "1" or "0"
    is_changing: bool      # 是否动爻
    tian_gan: str          # 天干
    di_zhi: str            # 地支
    liu_qin: str           # 六亲
    liu_shen: str          # 六神
    shi_ying: str          # "世"/"应"/""
    wuxing: str            # 地支五行
    cang_gan: List[str]    # 藏干


@dataclass
class NajiaResult:
    """纳甲装卦结果"""
    original_binary: str
    changed_binary: str = ""
    changing_lines: List[int] = field(default_factory=list)
    palace: str = ""
    palace_wuxing: str = ""
    gua_order: int = 0     # 在本宫中的位置(0-7)
    yao_list: List[NajiaYao] = field(default_factory=list)
    shi_position: int = 0
    ying_position: int = 0
    method: str = ""
    timestamp: str = ""


def install_najia(binary: str, changing_lines: List[int] = None,
                  day_gan: str = None, day_zhi: str = None,
                  month: int = None) -> NajiaResult:
    """
    完整纳甲装卦流程:
    1. 八宫定位 2. 纳干支 3. 装六亲 4. 定世应 5. 配六神
    """
    if changing_lines is None:
        changing_lines = []

    if day_gan is None:
        gan_idx = random.randint(0, 9)
        day_gan = TIAN_GAN[gan_idx]
    if day_zhi is None:
        day_zhi = DI_ZHI[random.randint(0, 11)]
    if month is None:
        month = datetime.now().month

    # 1. 八宫定位
    palace_info = GUA_TO_PALACE.get(binary)
    if not palace_info:
        # 尝试在八宫里找（变卦可能在）
        for bin_key in GUA_TO_PALACE:
            if bin_key == binary:
                palace_info = GUA_TO_PALACE[bin_key]
                break
        if not palace_info:
            # fallback
            palace_info = ("乾宫", "金", 0)

    palace_name, palace_wx, gua_order = palace_info
    shi_pos, ying_pos = SHI_YING_POSITIONS.get(gua_order, (3, 6))

    # 2. 纳干支
    upper_bin, lower_bin = binary[:3], binary[3:]
    from src.data.trigram_map import get_trigram_by_binary

    upper_tri = get_trigram_by_binary(upper_bin)
    lower_tri = get_trigram_by_binary(lower_bin)

    upper_name = upper_tri.name if upper_tri else "乾"
    lower_name = lower_tri.name if lower_tri else "乾"

    # 天干
    upper_gan = TRIGRAM_TIANGAN.get(upper_bin, ("甲","甲"))[1]  # 外卦用第二个
    lower_gan = TRIGRAM_TIANGAN.get(lower_bin, ("甲","甲"))[0]  # 内卦用第一个

    # 地支
    upper_zhi_list = TRIGRAM_DIZHI.get(upper_name, ["子","寅","辰","午","申","戌"])
    lower_zhi_list = TRIGRAM_DIZHI.get(lower_name, ["子","寅","辰","午","申","戌"])

    # 3. 装六亲 + 配六神
    liushen_list = get_liushen(day_gan)

    yao_list = []
    for pos in range(1, 7):
        is_yang = binary[6 - pos] == "1"
        is_changing = pos in changing_lines

        # 干支
        if pos <= 3:
            gan = lower_gan
            zhi = lower_zhi_list[pos - 1]
        else:
            gan = upper_gan
            zhi = upper_zhi_list[pos - 1]

        # 五行
        zhi_wx = ZHI_WUXING.get(zhi, "?")

        # 六亲
        liu_qin = determine_liuqin(zhi_wx, palace_wx)

        # 六神
        liu_shen = liushen_list[pos - 1]

        # 世应
        shi_ying = ""
        if pos == shi_pos:
            shi_ying = "世"
        elif pos == ying_pos:
            shi_ying = "应"

        # 藏干
        cang = DIZHI_CANGGAN.get(zhi, [])

        yao_list.append(NajiaYao(
            position=pos,
            binary_val="1" if is_yang else "0",
            is_changing=is_changing,
            tian_gan=gan,
            di_zhi=zhi,
            liu_qin=liu_qin,
            liu_shen=liu_shen,
            shi_ying=shi_ying,
            wuxing=zhi_wx,
            cang_gan=cang
        ))

    # 变卦
    changed_binary = list(binary)
    for pos in changing_lines:
        idx = 6 - pos
        changed_binary[idx] = "0" if changed_binary[idx] == "1" else "1"
    changed_binary = "".join(changed_binary)

    return NajiaResult(
        original_binary=binary,
        changed_binary=changed_binary,
        changing_lines=changing_lines,
        palace=palace_name,
        palace_wuxing=palace_wx,
        gua_order=gua_order,
        yao_list=yao_list,
        shi_position=shi_pos,
        ying_position=ying_pos,
        method="纳甲装卦",
        timestamp=datetime.now().isoformat()
    )


# ═══════════════════════════════════════════
# 八、应期推算 (六爻)
# ═══════════════════════════════════════════

def calculate_yingqi_liuyao(yong_shen_zhi: str, wangshuai: dict,
                            changing_lines: List[int] = None) -> dict:
    """
    六爻应期推算
    规则:
    - 值日应期: 用神所值地支之日
    - 冲应期: 用神被冲→逢合之日
    - 合应期: 用神被合→逢冲之日
    - 空应期: 旬空→出空之日
    """
    # 地支冲合关系
    ZHI_CHONG = {"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥","午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"}
    ZHI_HE = {"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}

    level = wangshuai.get("level", "平和")
    methods = []

    # 值日法
    methods.append({"method": "值日", "time": f"值{yong_shen_zhi}日", "detail": f"用神值{yong_shen_zhi}之日应验"})

    # 冲/合法
    chong_zhi = ZHI_CHONG.get(yong_shen_zhi)
    he_zhi = ZHI_HE.get(yong_shen_zhi)
    if chong_zhi:
        methods.append({"method": "逢冲", "time": f"逢{chong_zhi}日(冲动)", "detail": f"用神安静则逢冲之日应"})
    if he_zhi:
        methods.append({"method": "逢合", "time": f"逢{he_zhi}日(合住)", "detail": f"用神被冲则逢合之日应"})

    # 旺衰调整
    if level in ("极旺","旺相"):
        estimated = "近期(数日内)"
        confidence = 0.7
    elif level == "平和":
        estimated = "中期(数周内)"
        confidence = 0.5
    else:
        estimated = "远期(数月)"
        confidence = 0.3

    return {"methods": methods, "estimated": estimated, "confidence": confidence}


# ═══════════════════════════════════════════
# 九、动变分析
# ═══════════════════════════════════════════

def analyze_dongbian(yong_shen_pos: int, yao_list: List[NajiaYao]) -> dict:
    """
    动变分析: 看动爻与用神的关系
    """
    effects = []
    for yao in yao_list:
        if yao.is_changing and yao.position != yong_shen_pos:
            # 动爻对用神的影响
            from src.data.wuxing import sheng, ke
            dong_wx = yao.wuxing
            yong_yao = yao_list[yong_shen_pos - 1]
            yong_wx = yong_yao.wuxing

            if sheng(dong_wx, yong_wx):
                effects.append(f"动爻{yao.position}({yao.liu_qin})生动了用神→吉利")
            elif ke(dong_wx, yong_wx):
                effects.append(f"动爻{yao.position}({yao.liu_qin})克动了用神→不利")
            elif dong_wx == yong_wx:
                effects.append(f"动爻{yao.position}({yao.liu_qin})与用神同五行→帮扶")

    # 动爻本身是用神
    yong_yao = yao_list[yong_shen_pos - 1]
    if yong_yao.is_changing:
        effects.append(f"用神本身动→事有变动。{'动化回头生→吉' if yong_yao.wuxing != '?' else '需看化爻'} ")

    return {"effects": effects, "summary": "; ".join(effects) if effects else "无动爻影响用神"}

"""
紫微斗数排盘引擎 v1
核心: 命盘十二宫 + 十四主星 + 辅煞星 + 四化飞星
来源: 《紫微斗数全书》《十八飞星策天紫微斗数》
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# ═══════════════════════════════════════════
# 一、基础常量
# ═══════════════════════════════════════════

DI_ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
TIAN_GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]

# 十二宫名称 (从寅宫开始顺时针)
GONG_NAMES = ["命宫","兄弟宫","夫妻宫","子女宫","财帛宫","疾厄宫",
              "迁移宫","交友宫","官禄宫","田宅宫","福德宫","父母宫"]

# 十四主星
MAIN_STARS = [
    "紫微","天机","太阳","武曲","天同","廉贞",  # 紫微系(6)
    "天府","太阴","贪狼","巨门","天相","天梁","七杀","破军"  # 天府系(8)
]

# 辅星
AUX_STARS = ["文昌","文曲","左辅","右弼","天魁","天钺","禄存","擎羊","陀罗","火星","铃星","地空","地劫"]

# 五行局
WUXING_JU = {"水二局":2,"木三局":3,"金四局":4,"土五局":5,"火六局":6}

# ═══════════════════════════════════════════
# 二、紫微斗数排盘核心
# ═══════════════════════════════════════════

def get_ming_gong(month: int, hour: int) -> Tuple[int, str]:
    """
    命宫定位 (简化算法)
    从寅宫起正月，顺数到出生月
    再从该月起子时，逆数到出生时
    """
    hour_branch = ((hour + 1) // 2) % 12  # 时支
    # 命宫地支 = (寅(2) + month - 1 - hour_branch) % 12
    ming_zhi_idx = (2 + month - 1 - hour_branch) % 12
    return ming_zhi_idx, DI_ZHI[ming_zhi_idx]

def get_shen_gong(month: int, hour: int) -> Tuple[int, str]:
    """身宫定位 (与命宫对称)"""
    hour_branch = ((hour + 1) // 2) % 12
    shen_zhi_idx = (2 + month - 1 + hour_branch) % 12
    return shen_zhi_idx, DI_ZHI[shen_zhi_idx]

def get_wuxing_ju(ming_zhi: str, year_gan: str) -> Tuple[str, int]:
    """
    五行局判定
    命宫地支 + 年天干 → 纳音五行 → 五行局
    """
    # 纳音五行局查找表 (简化)
    NAYIN_JU_TABLE = {
        ("甲","子"):("金四局",4),("甲","丑"):("金四局",4),
        ("甲","寅"):("水二局",2),("甲","卯"):("水二局",2),
        ("甲","辰"):("火六局",6),("甲","巳"):("火六局",6),
        ("乙","子"):("金四局",4),("乙","丑"):("金四局",4),
        ("乙","寅"):("水二局",2),("乙","卯"):("水二局",2),
        ("乙","辰"):("火六局",6),("乙","巳"):("火六局",6),
        ("丙","子"):("水二局",2),("丙","丑"):("水二局",2),
        ("丙","寅"):("火六局",6),("丙","卯"):("火六局",6),
        ("丙","辰"):("木三局",3),("丙","巳"):("木三局",3),
        ("丁","子"):("水二局",2),("丁","丑"):("水二局",2),
        ("丁","寅"):("火六局",6),("丁","卯"):("火六局",6),
        ("丁","辰"):("木三局",3),("丁","巳"):("木三局",3),
        ("戊","子"):("火六局",6),("戊","丑"):("火六局",6),
        ("戊","寅"):("木三局",3),("戊","卯"):("木三局",3),
        ("戊","辰"):("土五局",5),("戊","巳"):("土五局",5),
        ("己","子"):("火六局",6),("己","丑"):("火六局",6),
        ("己","寅"):("木三局",3),("己","卯"):("木三局",3),
        ("己","辰"):("土五局",5),("己","巳"):("土五局",5),
        ("庚","子"):("木三局",3),("庚","丑"):("木三局",3),
        ("庚","寅"):("土五局",5),("庚","卯"):("土五局",5),
        ("庚","辰"):("金四局",4),("庚","巳"):("金四局",4),
        ("辛","子"):("木三局",3),("辛","丑"):("木三局",3),
        ("辛","寅"):("土五局",5),("辛","卯"):("土五局",5),
        ("辛","辰"):("金四局",4),("辛","巳"):("金四局",4),
        ("壬","子"):("土五局",5),("壬","丑"):("土五局",5),
        ("壬","寅"):("金四局",4),("壬","卯"):("金四局",4),
        ("壬","辰"):("水二局",2),("壬","巳"):("水二局",2),
        ("癸","子"):("土五局",5),("癸","丑"):("土五局",5),
        ("癸","寅"):("金四局",4),("癸","卯"):("金四局",4),
        ("癸","辰"):("水二局",2),("癸","巳"):("水二局",2),
    }
    # 补充缺失的映射
    default_map = {
        ("甲","午"):("金四局",4),("甲","未"):("金四局",4),("甲","申"):("水二局",2),("甲","酉"):("水二局",2),("甲","戌"):("火六局",6),("甲","亥"):("火六局",6),
        ("乙","午"):("金四局",4),("乙","未"):("金四局",4),("乙","申"):("水二局",2),("乙","酉"):("水二局",2),("乙","戌"):("火六局",6),("乙","亥"):("火六局",6),
        ("丙","午"):("水二局",2),("丙","未"):("水二局",2),("丙","申"):("火六局",6),("丙","酉"):("火六局",6),("丙","戌"):("木三局",3),("丙","亥"):("木三局",3),
        ("丁","午"):("水二局",2),("丁","未"):("水二局",2),("丁","申"):("火六局",6),("丁","酉"):("火六局",6),("丁","戌"):("木三局",3),("丁","亥"):("木三局",3),
        ("戊","午"):("火六局",6),("戊","未"):("火六局",6),("戊","申"):("木三局",3),("戊","酉"):("木三局",3),("戊","戌"):("土五局",5),("戊","亥"):("土五局",5),
        ("己","午"):("火六局",6),("己","未"):("火六局",6),("己","申"):("木三局",3),("己","酉"):("木三局",3),("己","戌"):("土五局",5),("己","亥"):("土五局",5),
        ("庚","午"):("木三局",3),("庚","未"):("木三局",3),("庚","申"):("土五局",5),("庚","酉"):("土五局",5),("庚","戌"):("金四局",4),("庚","亥"):("金四局",4),
        ("辛","午"):("木三局",3),("辛","未"):("木三局",3),("辛","申"):("土五局",5),("辛","酉"):("土五局",5),("辛","戌"):("金四局",4),("辛","亥"):("金四局",4),
        ("壬","午"):("土五局",5),("壬","未"):("土五局",5),("壬","申"):("金四局",4),("壬","酉"):("金四局",4),("壬","戌"):("水二局",2),("壬","亥"):("水二局",2),
        ("癸","午"):("土五局",5),("癸","未"):("土五局",5),("癸","申"):("金四局",4),("癸","酉"):("金四局",4),("癸","戌"):("水二局",2),("癸","亥"):("水二局",2),
    }
    NAYIN_JU_TABLE.update(default_map)

    key = (year_gan, ming_zhi)
    if key in NAYIN_JU_TABLE:
        return NAYIN_JU_TABLE[key]
    return ("土五局", 5)

def get_ziwei_position(ju_number: int, lunar_day: int) -> int:
    """
    紫微星落宫
    五行局数 + 农历日 = 紫微星位置
    例如: 水二局(2) + 初一日(1) = 3 → 寅宫(2)
    """
    quotient = lunar_day // ju_number
    remainder = lunar_day % ju_number

    # 紫微星从寅宫(2)开始偏移
    if remainder == 0:
        ziwei_idx = (2 + quotient - 1) % 12
    else:
        ziwei_idx = (2 + quotient) % 12

    # 调整（奇偶性修正）
    if remainder != 0:
        if (ju_number % 2 == 0 and remainder % 2 == 1) or (ju_number % 2 == 1 and remainder % 2 == 0):
            ziwei_idx = (ziwei_idx + 1) % 12

    return ziwei_idx

# 紫微系主星位置 (相对于紫微星的偏移)
ZIWEI_SERIES_OFFSET = {
    "紫微": 0, "天机": -1, "太阳": -3, "武曲": -4,
    "天同": -5, "廉贞": -8
}

# 天府系主星位置 (天府 = 紫微的对称位置)
TIANFU_SERIES_OFFSET = {
    "天府": 0, "太阴": 1, "贪狼": 2, "巨门": 3,
    "天相": 4, "天梁": 5, "七杀": 6, "破军": 10
}

def get_main_stars_positions(ziwei_idx: int) -> Dict[str, int]:
    """获取十四主星落宫位置"""
    positions = {}

    # 紫微系
    tianfu_idx = (ziwei_idx + 4) % 12  # 天府在紫微斜对面
    for star, offset in ZIWEI_SERIES_OFFSET.items():
        positions[star] = (ziwei_idx + offset) % 12

    # 天府系
    for star, offset in TIANFU_SERIES_OFFSET.items():
        positions[star] = (tianfu_idx + offset) % 12

    return positions

def get_sihua(year_gan: str) -> Dict[str, str]:
    """
    四化星 (基于年天干)
    化禄/化权/化科/化忌
    """
    SIHUA_TABLE = {
        "甲": {"化禄":"廉贞","化权":"破军","化科":"武曲","化忌":"太阳"},
        "乙": {"化禄":"天机","化权":"天梁","化科":"紫微","化忌":"太阴"},
        "丙": {"化禄":"天同","化权":"天机","化科":"文昌","化忌":"廉贞"},
        "丁": {"化禄":"太阴","化权":"天同","化科":"天机","化忌":"巨门"},
        "戊": {"化禄":"贪狼","化权":"太阴","化科":"右弼","化忌":"天机"},
        "己": {"化禄":"武曲","化权":"贪狼","化科":"天梁","化忌":"文曲"},
        "庚": {"化禄":"太阳","化权":"武曲","化科":"太阴","化忌":"天同"},
        "辛": {"化禄":"巨门","化权":"太阳","化科":"文曲","化忌":"文昌"},
        "壬": {"化禄":"天梁","化权":"紫微","化科":"左辅","化忌":"武曲"},
        "癸": {"化禄":"破军","化权":"巨门","化科":"太阴","化忌":"贪狼"},
    }
    return SIHUA_TABLE.get(year_gan, {})


# ═══════════════════════════════════════════
# 三、主数据结构
# ═══════════════════════════════════════════

@dataclass
class Gong:
    """一宫"""
    name: str           # 宫名
    zhi: str            # 地支
    zhi_idx: int        # 地支索引
    main_stars: List[str] = field(default_factory=list)
    aux_stars: List[str] = field(default_factory=list)
    sihua: str = ""     # 四化标记
    is_shen_gong: bool = False
    is_ming_gong: bool = False


@dataclass
class ZiweiChart:
    """紫微斗数命盘"""
    name: str = ""
    gender: str = "男"
    birth_date: str = ""
    birth_time: str = ""

    # 基础
    year_gan: str = ""
    year_zhi: str = ""
    month: int = 1
    hour: int = 0

    # 命宫/身宫
    ming_gong_idx: int = 0
    shen_gong_idx: int = 0

    # 五行局
    wuxing_ju_name: str = ""
    wuxing_ju_number: int = 5

    # 十二宫
    gongs: List[Gong] = field(default_factory=list)

    # 四化
    sihua_map: Dict[str, str] = field(default_factory=dict)

    # 主星位置
    star_positions: Dict[str, List[str]] = field(default_factory=dict)


# ═══════════════════════════════════════════
# 四、完整排盘
# ═══════════════════════════════════════════

def paipan_ziwei(date: datetime, gender: str = "男", name: str = "") -> ZiweiChart:
    """紫微斗数完整排盘"""
    chart = ZiweiChart(
        name=name, gender=gender,
        birth_date=date.strftime("%Y-%m-%d"),
        birth_time=f"{date.hour}:{date.minute:02d}",
        month=date.month, hour=date.hour
    )

    # 年干支
    year_g = TIAN_GAN[(date.year - 4) % 10]
    year_z = DI_ZHI[(date.year - 4) % 12]
    chart.year_gan = year_g
    chart.year_zhi = year_z

    # 命宫
    ming_idx, ming_zhi = get_ming_gong(date.month, date.hour)
    chart.ming_gong_idx = ming_idx

    # 身宫
    shen_idx, shen_zhi = get_shen_gong(date.month, date.hour)
    chart.shen_gong_idx = shen_idx

    # 五行局
    ju_name, ju_num = get_wuxing_ju(ming_zhi, year_g)
    chart.wuxing_ju_name = ju_name
    chart.wuxing_ju_number = ju_num

    # 农历日(简化为公历日)
    lunar_day = date.day

    # 紫微星位置
    ziwei_idx = get_ziwei_position(ju_num, lunar_day)

    # 十四主星
    star_pos = get_main_stars_positions(ziwei_idx)

    # 四化
    chart.sihua_map = get_sihua(year_g)

    # 构建十二宫 (从寅宫顺时针)
    gongs = []
    for i in range(12):
        gong_zhi_idx = (2 + i) % 12  # 寅=2,卯=3,...,丑=1
        gong_name = GONG_NAMES[(gong_zhi_idx - ming_idx) % 12]
        gong_zhi = DI_ZHI[gong_zhi_idx]

        gong = Gong(
            name=gong_name, zhi=gong_zhi, zhi_idx=gong_zhi_idx,
            is_ming_gong=(gong_zhi_idx == ming_idx),
            is_shen_gong=(gong_zhi_idx == shen_idx)
        )

        # 主星
        for star, pos in star_pos.items():
            if pos == gong_zhi_idx:
                gong.main_stars.append(star)

        # 四化标记
        for sihua_type, star in chart.sihua_map.items():
            if star in gong.main_stars:
                gong.sihua = sihua_type

        gongs.append(gong)

    # 辅星
    aux_pos = get_aux_stars(year_g, year_z, date.month, date.hour)
    for star, pos_idx in aux_pos.items():
        for gong in gongs:
            if gong.zhi_idx == pos_idx:
                gong.aux_stars.append(star)

    chart.gongs = gongs

    # 星位置映射
    chart.star_positions = {}
    for star, pos in star_pos.items():
        gong_name = GONG_NAMES[(pos - ming_idx) % 12]
        if gong_name not in chart.star_positions:
            chart.star_positions[gong_name] = []
        chart.star_positions[gong_name].append(star)

    return chart


# ═══════════════════════════════════════════
# 五、十二宫解读
# ═══════════════════════════════════════════

GONG_MEANINGS = {
    "命宫": "代表命主本人——性格、天赋、一生运势的缩影。命宫的好坏决定了整个命盘的基调。",
    "兄弟宫": "兄弟姐妹、同辈关系、合作伙伴。也代表命主的人际竞争力和社交能力。",
    "夫妻宫": "婚姻、配偶、感情生活。影响婚姻品质和配偶条件。",
    "子女宫": "子女生育、晚辈关系、创造力。也代表命主的才华和享受。",
    "财帛宫": "财富、收入、理财能力。决定财运好坏和财富获取方式。",
    "疾厄宫": "健康、疾病、意外。反映身体状况和潜在的疾病风险。",
    "迁移宫": "外出运、变动、旅行。代表命主在外的发展机会和适应能力。",
    "交友宫": "朋友、社交圈、下属。影响人际关系和团队协作。",
    "官禄宫": "事业、工作、官职。决定事业成就和职场发展。",
    "田宅宫": "房产、家庭、根基。代表居住环境、固定资产和家族运势。",
    "福德宫": "精神享受、福气、心态。影响命主的快乐程度和人生满足感。",
    "父母宫": "父母、长辈、上司。代表与长辈的关系和来自上级的帮助。",
}

MAIN_STAR_MEANINGS = {
    "紫微": {"nature":"帝王星","trait":"领导力强、自尊心高、有组织能力","career":"管理者、政府、大企业","risk":"孤傲、好面子"},
    "天机": {"nature":"智谋星","trait":"聪明灵活、善于分析、适应力强","career":"策划、咨询、IT","risk":"多变、缺乏耐心"},
    "太阳": {"nature":"光明星","trait":"热情大方、乐于助人、有正义感","career":"教育、公益、外交","risk":"过度消耗自己"},
    "武曲": {"nature":"财帛星","trait":"刚毅果断、理财能力强、执行力强","career":"金融、军警、工程","risk":"刚过易折、寡情"},
    "天同": {"nature":"福气星","trait":"温和善良、知足常乐、有艺术天赋","career":"艺术、服务、休闲","risk":"懒散、缺乏进取心"},
    "廉贞": {"nature":"复杂星","trait":"精于算计、有魅力、善交际","career":"法律、政治、商业","risk":"容易陷入是非"},
    "天府": {"nature":"库藏星","trait":"稳重可靠、善于管理、有包容心","career":"管理、财务、仓储","risk":"保守过度"},
    "太阴": {"nature":"阴柔星","trait":"温柔体贴、感情丰富、有美感","career":"艺术、设计、服务","risk":"敏感多愁"},
    "贪狼": {"nature":"桃花星","trait":"多才多艺、交际手腕强、有魅力","career":"娱乐、外交、销售","risk":"贪得无厌、沉迷享乐"},
    "巨门": {"nature":"暗曜星","trait":"深思熟虑、善于分析、口才好","career":"研究、法律、辩论","risk":"多疑、口舌是非"},
    "天相": {"nature":"印绶星","trait":"公正善良、乐于助人、有品位","career":"行政、公关、设计","risk":"优柔寡断"},
    "天梁": {"nature":"长寿星","trait":"老成持重、有智慧、乐于助人","career":"医疗、教育、顾问","risk":"过于保守、好管闲事"},
    "七杀": {"nature":"将星","trait":"勇猛果断、开拓精神强、有魄力","career":"创业、军警、竞技","risk":"冲动、刚过易折"},
    "破军": {"nature":"破旧立新星","trait":"创新改革、敢于突破、行动力强","career":"创业、研发、改革","risk":"破坏性、不稳定"},
}

# 辅星计算 (年干/年支/月/时)
def get_aux_stars(year_gan: str, year_zhi: str, month: int, hour: int) -> Dict[str, int]:
    """计算辅星落宫位置"""
    pos = {}
    hour_branch = ((hour + 1) // 2) % 12
    month_zhi = DI_ZHI[(month + 1) % 12]  # approximate

    # 文昌 (年干起)
    wenchang_map = {"甲":"巳","乙":"午","丙":"申","丁":"酉","戊":"申","己":"酉","庚":"亥","辛":"子","壬":"寅","癸":"卯"}
    pos["文昌"] = DI_ZHI.index(wenchang_map.get(year_gan, "巳"))

    # 文曲 (年干起)
    wenqu_map = {"甲":"亥","乙":"子","丙":"寅","丁":"卯","戊":"寅","己":"卯","庚":"巳","辛":"午","壬":"申","癸":"酉"}
    pos["文曲"] = DI_ZHI.index(wenqu_map.get(year_gan, "亥"))

    # 左辅 (月支起)
    pos["左辅"] = (month - 1) % 12  # simplified: month -> 寅=0

    # 右弼 (月支起)
    pos["右弼"] = (month + 10) % 12  # opposite side

    # 天魁 (年干起)
    tiankui_map = {"甲":"丑","戊":"丑","庚":"丑","乙":"子","己":"子","辛":"午","丙":"亥","丁":"酉","壬":"卯","癸":"巳"}
    pos["天魁"] = DI_ZHI.index(tiankui_map.get(year_gan, "丑"))

    # 天钺 (年干起)
    tianyue_map = {"甲":"未","戊":"未","庚":"未","乙":"申","己":"申","辛":"寅","丙":"酉","丁":"亥","壬":"巳","癸":"卯"}
    pos["天钺"] = DI_ZHI.index(tianyue_map.get(year_gan, "未"))

    # 禄存 (年干起)
    lucun_map = {"甲":"寅","乙":"卯","丙":"巳","丁":"午","戊":"巳","己":"午","庚":"申","辛":"酉","壬":"亥","癸":"子"}
    pos["禄存"] = DI_ZHI.index(lucun_map.get(year_gan, "寅"))

    # 擎羊/陀罗 (禄存前后)
    lucun_idx = pos.get("禄存", 2)
    pos["擎羊"] = (lucun_idx + 1) % 12
    pos["陀罗"] = (lucun_idx - 1) % 12

    # 火星/铃星 (年支+时支起，简化)
    pos["火星"] = (DI_ZHI.index(year_zhi) + hour_branch) % 12
    pos["铃星"] = (DI_ZHI.index(year_zhi) + hour_branch + 6) % 12

    # 地空/地劫 (时支起)
    pos["地空"] = (hour_branch + 4) % 12
    pos["地劫"] = (hour_branch + 10) % 12

    # 天马 (年支起)
    tianma_map = {"寅":"申","申":"寅","巳":"亥","亥":"巳","子":"午","午":"子","卯":"酉","酉":"卯","辰":"戌","戌":"辰","丑":"未","未":"丑"}
    pos["天马"] = DI_ZHI.index(tianma_map.get(year_zhi, "寅"))

    # 天刑 (月支起)
    pos["天刑"] = (month + 4) % 12

    # 天姚 (时支起)
    pos["天姚"] = (hour_branch + 2) % 12

    # 红鸾/天喜 (年支起)
    hongluan_map = {"子":"卯","丑":"寅","寅":"丑","卯":"子","辰":"亥","巳":"戌","午":"酉","未":"申","申":"未","酉":"午","戌":"巳","亥":"辰"}
    pos["红鸾"] = DI_ZHI.index(hongluan_map.get(year_zhi, "卯"))
    pos["天喜"] = (pos["红鸾"] + 6) % 12

    # 孤辰/寡宿 (年支起)
    guchen_map = {"子":"寅","丑":"寅","寅":"巳","卯":"巳","辰":"巳","巳":"申","午":"申","未":"申","申":"亥","酉":"亥","戌":"亥","亥":"寅"}
    pos["孤辰"] = DI_ZHI.index(guchen_map.get(year_zhi, "寅"))
    pos["寡宿"] = (pos["孤辰"] + 4) % 12

    return pos

AUX_STAR_MEANINGS = {
    "文昌":"学业星——主文书、考试、学识才华。入命者聪明好学，最适合做学问和考试。",
    "文曲":"才艺星——主艺术、口才、表达能力。入命者有艺术天赋，口才出众。",
    "左辅":"辅佐星——主贵人帮助。入命者一生多得贵人相助，遇困难有人帮。",
    "右弼":"助力星——主团队协作。入命者善于合作，在团队中如鱼得水。",
    "天魁":"贵人星——关键时刻总有贵人出现。坐命者逢凶化吉的运气特别好。",
    "天钺":"机遇星——主隐性助力。入命者常有意外的好运和不经意的机会。",
    "禄存":"财禄星——主财富积累。入命者一生财运不错，特别适合存钱和理财。",
    "擎羊":"刚强星——主竞争和冲劲。入命者性格刚烈有冲劲，但需防冲动惹祸。",
    "陀罗":"纠缠星——主拖延和反复。入命者做事容易反复，但适合需要持久力的工作。",
    "火星":"爆发星——主突然的行动和热情。入命者做事有爆发力，适合冲刺型任务。",
    "铃星":"暗火之星——主内心焦虑和急迫。需学会控制情绪，不急不躁。",
    "地空":"虚空星——主理想主义和不切实际。入命者适合创意工作而非务实工作。",
    "地劫":"波折星——主起伏不定。入命者人生多起伏，但每次低谷后都能反弹。",
    "天马":"奔波星——主变动和旅行。入命者一生多动少静，适合需要出差的工作。",
    "天刑":"约束星——主纪律和规则。入命者适合做执法、管理类工作。",
    "天姚":"桃花星——主魅力和感情。入命者异性缘好，但需防烂桃花。",
    "红鸾":"正桃花——主正缘和婚姻。入命者婚恋运好，容易遇到好对象。",
    "天喜":"喜庆星——主欢乐和好事。入命者一生多喜事，心态乐观。",
    "孤辰":"孤独星——主独立和独处。入命者适合需要专注力的工作。",
    "寡宿":"清静星——主清净和简单。入命者喜欢独处，适合研究型工作。",
}

SIHUA_MEANINGS = {
    "化禄": "财运亨通、机会多、人缘好。主吉利，代表获得和增加。",
    "化权": "掌权得势、有话语权、执行力强。主权威，代表掌控和主导。",
    "化科": "名望提升、考试顺利、贵人赏识。主名声，代表认可和提升。",
    "化忌": "波折坎坷、阻碍多、需注意避免。主不顺，代表损失和困扰。",
}

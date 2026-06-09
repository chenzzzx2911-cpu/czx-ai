"""
八字命理引擎 v1 — 子平法八字排盘系统
核心: 四柱(年月日时) + 十神 + 纳音 + 藏干 + 十二长生 + 格局 + 用神 + 大运流年
来源: 《渊海子平》《三命通会》《滴天髓》《子平真诠》
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

# ═══════════════════════════════════════════
# 一、天干地支基础
# ═══════════════════════════════════════════

TIAN_GAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DI_ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

GAN_WUXING = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
GAN_YINYANG = {"甲":"阳","乙":"阴","丙":"阳","丁":"阴","戊":"阳","己":"阴","庚":"阳","辛":"阴","壬":"阳","癸":"阴"}

ZHI_WUXING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
ZHI_YINYANG = {"子":"阳","丑":"阴","寅":"阳","卯":"阴","辰":"阳","巳":"阴","午":"阳","未":"阴","申":"阳","酉":"阴","戌":"阳","亥":"阴"}

# 藏干 (地支所藏天干)
ZHI_CANGGAN = {
    "子": [("癸", 1.0)],
    "丑": [("己", 0.6), ("癸", 0.25), ("辛", 0.15)],
    "寅": [("甲", 0.6), ("丙", 0.25), ("戊", 0.15)],
    "卯": [("乙", 1.0)],
    "辰": [("戊", 0.5), ("乙", 0.3), ("癸", 0.2)],
    "巳": [("丙", 0.5), ("庚", 0.3), ("戊", 0.2)],
    "午": [("丁", 0.6), ("己", 0.4)],
    "未": [("己", 0.5), ("丁", 0.3), ("乙", 0.2)],
    "申": [("庚", 0.5), ("壬", 0.3), ("戊", 0.2)],
    "酉": [("辛", 1.0)],
    "戌": [("戊", 0.5), ("辛", 0.3), ("丁", 0.2)],
    "亥": [("壬", 0.6), ("甲", 0.4)],
}

# 十二长生
CHANG_SHENG = {
    "甲": ["亥","子","丑","寅","卯","辰","巳","午","未","申","酉","戌"],
    "乙": ["午","巳","辰","卯","寅","丑","子","亥","戌","酉","申","未"],
    "丙": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    "丁": ["酉","申","未","午","巳","辰","卯","寅","丑","子","亥","戌"],
    "戊": ["寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"],
    "己": ["酉","申","未","午","巳","辰","卯","寅","丑","子","亥","戌"],
    "庚": ["巳","午","未","申","酉","戌","亥","子","丑","寅","卯","辰"],
    "辛": ["子","亥","戌","酉","申","未","午","巳","辰","卯","寅","丑"],
    "壬": ["申","酉","戌","亥","子","丑","寅","卯","辰","巳","午","未"],
    "癸": ["卯","寅","丑","子","亥","戌","酉","申","未","午","巳","辰"],
}

CHANG_SHENG_NAMES = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]

# 纳音 (六十甲子纳音)
NAYIN_TABLE = {
    "甲子":"海中金","乙丑":"海中金","丙寅":"炉中火","丁卯":"炉中火",
    "戊辰":"大林木","己巳":"大林木","庚午":"路旁土","辛未":"路旁土",
    "壬申":"剑锋金","癸酉":"剑锋金","甲戌":"山头火","乙亥":"山头火",
    "丙子":"涧下水","丁丑":"涧下水","戊寅":"城头土","己卯":"城头土",
    "庚辰":"白蜡金","辛巳":"白蜡金","壬午":"杨柳木","癸未":"杨柳木",
    "甲申":"泉中水","乙酉":"泉中水","丙戌":"屋上土","丁亥":"屋上土",
    "戊子":"霹雳火","己丑":"霹雳火","庚寅":"松柏木","辛卯":"松柏木",
    "壬辰":"长流水","癸巳":"长流水","甲午":"砂中金","乙未":"砂中金",
    "丙申":"山下火","丁酉":"山下火","戊戌":"平地木","己亥":"平地木",
    "庚子":"壁上土","辛丑":"壁上土","壬寅":"金箔金","癸卯":"金箔金",
    "甲辰":"覆灯火","乙巳":"覆灯火","丙午":"天河水","丁未":"天河水",
    "戊申":"大驿土","己酉":"大驿土","庚戌":"钗钏金","辛亥":"钗钏金",
    "壬子":"桑柘木","癸丑":"桑柘木","甲寅":"大溪水","乙卯":"大溪水",
    "丙辰":"沙中土","丁巳":"沙中土","戊午":"天上火","己未":"天上火",
    "庚申":"石榴木","辛酉":"石榴木","壬戌":"大海水","癸亥":"大海水",
}


# ═══════════════════════════════════════════
# 二、八字排盘核心算法
# ═══════════════════════════════════════════

def get_year_gz(year: int) -> Tuple[str, str]:
    """年柱天干地支 (以立春为界)"""
    stem = TIAN_GAN[(year - 4) % 10]
    branch = DI_ZHI[(year - 4) % 12]
    return stem, branch

def get_month_gz(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    月柱天干地支 (以节气为界)
    寅月为正月(立春→惊蛰), 卯月为二月...
    月干 = (年干序*2 + 月序) % 10
    """
    # Approximate solar term boundaries (simplified)
    # 立春 approximately Feb 4
    solar_terms = [
        (1, 4), (2, 4), (3, 6), (4, 5), (5, 6), (6, 6),
        (7, 7), (8, 8), (9, 8), (10, 8), (11, 7), (12, 7)
    ]
    month_index = month - 1  # 0=寅...11=丑
    # Adjust for solar terms
    term_day = solar_terms[month_index][1]
    if day < term_day:
        month_index = (month_index - 1) % 12

    year_stem_idx = (year - 4) % 10
    month_branch = DI_ZHI[(month_index + 2) % 12]  # 寅=>index 2
    month_stem = TIAN_GAN[(year_stem_idx * 2 + month_index) % 10]
    return month_stem, month_branch

def get_day_gz(date: datetime) -> Tuple[str, str]:
    """
    日柱天干地支 (基于公历日期固定公式)
    基准: 1900-01-01 = 甲戌日 (stem=0 branch=10)
    """
    base_date = datetime(1900, 1, 1)
    delta = (date - base_date).days
    stem = TIAN_GAN[delta % 10]
    branch = DI_ZHI[delta % 12]
    return stem, branch

def get_hour_gz(day_stem: str, hour: int) -> Tuple[str, str]:
    """
    时柱天干地支
    时辰: 23-1=子时, 1-3=丑时, ..., 21-23=亥时
    时干 = (日干序*2 + 时支序) % 10
    """
    hour_branch_idx = ((hour + 1) // 2) % 12
    hour_branch = DI_ZHI[hour_branch_idx]
    day_stem_idx = TIAN_GAN.index(day_stem)
    hour_stem = TIAN_GAN[(day_stem_idx * 2 + hour_branch_idx) % 10]
    return hour_stem, hour_branch


# ═══════════════════════════════════════════
# 三、十神系统
# ═══════════════════════════════════════════

def calc_shishen(day_stem: str, other_stem: str) -> dict:
    """
    十神计算: 以日干为「我」
    同我→比肩/劫财  生我→正印/偏印  我生→食神/伤官
    克我→正官/七杀  我克→正财/偏财
    阴阳相同→偏(劫/偏印/伤/七杀/偏财) 阴阳相反→正(比/正印/食/正官/正财)
    """
    day_yin = GAN_YINYANG[day_stem]
    day_wx = GAN_WUXING[day_stem]
    other_yin = GAN_YINYANG[other_stem]
    other_wx = GAN_WUXING[other_stem]

    same_yin = day_yin == other_yin

    from src.data.wuxing import sheng, ke

    if day_wx == other_wx:
        return {"name":"比肩" if same_yin else "劫财","type":"比劫","relation":"同我"}
    if sheng(other_wx, day_wx):
        return {"name":"偏印" if same_yin else "正印","type":"印星","relation":"生我"}
    if sheng(day_wx, other_wx):
        return {"name":"食神" if same_yin else "伤官","type":"食伤","relation":"我生"}
    if ke(other_wx, day_wx):
        return {"name":"七杀" if same_yin else "正官","type":"官杀","relation":"克我"}
    if ke(day_wx, other_wx):
        return {"name":"偏财" if same_yin else "正财","type":"财星","relation":"我克"}

    return {"name":"未知","type":"未知","relation":"?"}

SHISHEN_MEANINGS = {
    "正官": "事业、官职、上司、纪律、丈夫(女命)",
    "七杀": "压力、挑战、小人、武职、偏夫(女命)",
    "正印": "学业、母亲、庇护、文书、贵人",
    "偏印": "偏门学问、继母、独特思维、宗教",
    "正财": "正当收入、妻子(男命)、稳定财富",
    "偏财": "意外之财、投资、父亲、慷慨",
    "比肩": "同辈、朋友、竞争、自我",
    "劫财": "竞争、破财、兄弟姐妹、冲动",
    "食神": "才华、口福、子女、悠闲",
    "伤官": "聪明、创造力、反叛、口舌",
}

# ═══════════════════════════════════════════
# 四、主数据结构
# ═══════════════════════════════════════════

@dataclass
class Pillar:
    """一柱 (年/月/日/时)"""
    name: str            # 年柱/月柱/日柱/时柱
    tian_gan: str        # 天干
    di_zhi: str          # 地支
    wuxing_g: str        # 天干五行
    wuxing_z: str        # 地支五行
    naying: str          # 纳音
    cang_gan: List[Tuple[str, float]]  # 藏干
    shishen: str = ""    # 十神(日柱无)


@dataclass
class BaziChart:
    """完整八字命盘"""
    name: str = ""
    gender: str = "男"
    birth_date: str = ""     # 公历出生日期
    birth_time: str = ""     # 出生时间

    # 四柱
    year: Optional[Pillar] = None
    month: Optional[Pillar] = None
    day: Optional[Pillar] = None
    hour: Optional[Pillar] = None

    # 日主
    day_master: str = ""          # 日干
    day_master_wuxing: str = ""   # 日主五行

    # 五行统计
    wuxing_count: Dict[str, int] = field(default_factory=dict)

    # 格局
    patterns: List[dict] = field(default_factory=list)

    # 用神
    yong_shen: dict = field(default_factory=dict)

    # 大运
    dayun: List[dict] = field(default_factory=list)

    def get_four_pillars_str(self) -> str:
        """四柱八字字符串"""
        parts = [
            f"{self.year.tian_gan}{self.year.di_zhi}" if self.year else "????",
            f"{self.month.tian_gan}{self.month.di_zhi}" if self.month else "????",
            f"{self.day.tian_gan}{self.day.di_zhi}" if self.day else "????",
            f"{self.hour.tian_gan}{self.hour.di_zhi}" if self.hour else "????",
        ]
        return " ".join(parts)

    def get_shishen_str(self) -> dict:
        """十神分布"""
        result = {}
        for pillar_name, p in [("年",self.year),("月",self.month),("日",self.day),("时",self.hour)]:
            if p and p.shi_shen:
                result[f"{pillar_name}干"] = p.shi_shen
        return result


# ═══════════════════════════════════════════
# 五、排盘函数
# ═══════════════════════════════════════════

def paipan(date: datetime, gender: str = "男", name: str = "") -> BaziChart:
    """
    完整八字排盘
    """
    chart = BaziChart(name=name, gender=gender,
                      birth_date=date.strftime("%Y-%m-%d"),
                      birth_time=date.strftime("%H:%M"))

    year_g, year_z = get_year_gz(date.year)
    month_g, month_z = get_month_gz(date.year, date.month, date.day)
    day_g, day_z = get_day_gz(date)
    hour_g, hour_z = get_hour_gz(day_g, date.hour)

    # 日主
    chart.day_master = day_g
    chart.day_master_wuxing = GAN_WUXING[day_g]

    # 构建四柱
    chart.year = Pillar("年柱", year_g, year_z, GAN_WUXING[year_g], ZHI_WUXING[year_z],
                        NAYIN_TABLE.get(f"{year_g}{year_z}","?"),
                        ZHI_CANGGAN.get(year_z, []),
                        calc_shishen(day_g, year_g)["name"])
    chart.month = Pillar("月柱", month_g, month_z, GAN_WUXING[month_g], ZHI_WUXING[month_z],
                         NAYIN_TABLE.get(f"{month_g}{month_z}","?"),
                         ZHI_CANGGAN.get(month_z, []),
                         calc_shishen(day_g, month_g)["name"])
    chart.day = Pillar("日柱", day_g, day_z, GAN_WUXING[day_g], ZHI_WUXING[day_z],
                       NAYIN_TABLE.get(f"{day_g}{day_z}","?"),
                       ZHI_CANGGAN.get(day_z, []), "日主")
    chart.hour = Pillar("时柱", hour_g, hour_z, GAN_WUXING[hour_g], ZHI_WUXING[hour_z],
                        NAYIN_TABLE.get(f"{hour_g}{hour_z}","?"),
                        ZHI_CANGGAN.get(hour_z, []),
                        calc_shishen(day_g, hour_g)["name"])

    # 五行统计
    wuxing_count = {"木":0,"火":0,"土":0,"金":0,"水":0}
    for p in [chart.year, chart.month, chart.day, chart.hour]:
        wuxing_count[p.wuxing_g] = wuxing_count.get(p.wuxing_g, 0) + 1
        wuxing_count[p.wuxing_z] = wuxing_count.get(p.wuxing_z, 0) + 1
        for cg, weight in p.cang_gan:
            cg_wx = GAN_WUXING.get(cg, "")
            if cg_wx:
                wuxing_count[cg_wx] = wuxing_count.get(cg_wx, 0) + weight
    chart.wuxing_count = wuxing_count

    # 格局判断
    chart.patterns = _identify_patterns(chart)

    # 用神推荐
    chart.yong_shen = _recommend_yongshen(chart)

    # 大运计算
    chart.dayun = _calculate_dayun(chart, date, gender)

    return chart


# ═══════════════════════════════════════════
# 六、格局识别
# ═══════════════════════════════════════════

def _identify_patterns(chart: BaziChart) -> List[dict]:
    """识别八字格局"""
    patterns = []
    shishen_map = {}
    for p in [chart.year, chart.month, chart.hour]:
        if p:
            info = calc_shishen(chart.day_master, p.tian_gan)
            shishen_map[p.name] = info["name"]

    # 月令格局 (月支藏干透出即入格)
    month_cang = chart.month.cang_gan if chart.month else []
    for cg, _ in month_cang:
        cg_info = calc_shishen(chart.day_master, cg)
        type_name = cg_info["type"]
        if type_name not in [p.get("type","") for p in patterns]:
            patterns.append({"source":"月令透干","type":cg_info["type"],"name":f"{cg_info['name']}格","confidence":0.7})

    # 特殊格局
    dw = chart.day_master_wuxing
    wc = chart.wuxing_count
    total = sum(wc.values())

    # 从强格 (日主极旺)
    dw_ratio = wc.get(dw, 0) / max(total, 1)
    if dw_ratio > 0.6:
        patterns.append({"source":"从强","type":"从强","name":f"从{dw}格","confidence":0.6})

    # 从弱格 (日主极弱)
    if dw_ratio < 0.15:
        patterns.append({"source":"从弱","type":"从弱","name":"从弱格","confidence":0.5})

    return patterns


# ═══════════════════════════════════════════
# 七、用神推荐
# ═══════════════════════════════════════════

def _recommend_yongshen(chart: BaziChart) -> dict:
    """
    用神推荐 - 基于旺衰平衡+调候
    规则: 日主旺则克泄耗,日主弱则生扶
    调候: 冬生喜火,夏生喜水
    """
    dw = chart.day_master_wuxing
    wc = chart.wuxing_count
    total = sum(wc.values())
    dw_score = wc.get(dw, 0)

    from src.data.wuxing import SHENG_MAP, KE_MAP

    # 旺衰判断
    if total > 0 and dw_score / total > 0.4:
        level = "偏旺"
        strategy = "克泄耗"
        # 需要克我或我生或我克的五行
        candidates = []
        for wx in ["金","水","木","火","土"]:
            if KE_MAP.get(wx) == dw:  # 克日主的
                candidates.append((wx, "克"))
            if SHENG_MAP.get(dw) == wx:  # 日主生的
                candidates.append((wx, "泄"))
        recommended = candidates[0][0] if candidates else "水"
    elif total > 0 and dw_score / total < 0.2:
        level = "偏弱"
        strategy = "生扶"
        # 需要生我或同我的五行
        candidates = []
        for wx in ["金","水","木","火","土"]:
            if SHENG_MAP.get(wx) == dw:
                candidates.append((wx, "生"))
            if wx == dw:
                candidates.append((wx, "扶"))
        recommended = candidates[0][0] if candidates else "木"
    else:
        level = "中和"
        strategy = "调候为先"
        recommended = dw

    # 调候: 看月支
    if chart.month:
        month_zhi = chart.month.di_zhi
        if month_zhi in ("亥","子","丑"):
            recommended = "火" if recommended != "火" else recommended + "+火"
            level += "(寒局需调候)"
        elif month_zhi in ("巳","午","未"):
            recommended = "水" if recommended != "水" else recommended + "+水"
            level += "(暖局需调候)"

    return {"level": level, "strategy": strategy, "recommended_wuxing": recommended, "confidence": 0.7}


# ═══════════════════════════════════════════
# 八、大运计算
# ═══════════════════════════════════════════

def _calculate_dayun(chart: BaziChart, birth_date: datetime, gender: str) -> List[dict]:
    """
    大运计算 - 顺排/逆排
    阳男阴女顺排, 阴男阳女逆排
    起运岁数 = (出生日到下一个/上一个节气的天数) / 3
    """
    is_yang_year = GAN_YINYANG.get(chart.year.tian_gan if chart.year else "甲","阳") == "阳"
    shun_pai = (is_yang_year and gender == "男") or (not is_yang_year and gender == "女")

    # 简化的起运年龄计算 (实际需要精确节气)
    if shun_pai:
        start_age = max(1, (birth_date.day + 6) // 3)
    else:
        start_age = max(1, (30 - birth_date.day + 6) // 3)

    # 生成大运 (10年一运)
    dayun_list = []
    month_stem = chart.month.tian_gan if chart.month else "甲"
    month_branch = chart.month.di_zhi if chart.month else "子"
    stem_idx = TIAN_GAN.index(month_stem)
    branch_idx = DI_ZHI.index(month_branch)

    for i in range(8):  # 8步大运, 80年
        if shun_pai:
            stem_idx = (stem_idx + 1) % 10
            branch_idx = (branch_idx + 1) % 12
        else:
            stem_idx = (stem_idx - 1) % 10
            branch_idx = (branch_idx - 1) % 12

        start_yr = start_age + i * 10
        end_yr = start_yr + 9

        dayun_list.append({
            "step": i + 1,
            "ganzhi": f"{TIAN_GAN[stem_idx]}{DI_ZHI[branch_idx]}",
            "wuxing": GAN_WUXING[TIAN_GAN[stem_idx]],
            "start_age": start_yr,
            "end_age": end_yr,
            "period": f"{start_yr}-{end_yr}岁",
            "shishen": calc_shishen(chart.day_master, TIAN_GAN[stem_idx])["name"]
        })

    return dayun_list


# ═══════════════════════════════════════════
# 九、便捷函数
# ═══════════════════════════════════════════

def quick_bazi(year: int, month: int, day: int, hour: int = 0,
               gender: str = "男", name: str = "") -> BaziChart:
    """快速排盘"""
    dt = datetime(year, month, day, hour, 0)
    return paipan(dt, gender, name)

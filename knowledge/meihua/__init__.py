"""
梅花易数知识库 v2 — 万物类象扩展 + 多种起卦 + 体用深化推理
来源: 梅花易数(邵雍)、meihua-yishu开源项目、现代研究
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

# ═══════════════════════════════════════════
# 一、万物类象扩展库 (Extended Wanwu Leixiang)
# ═══════════════════════════════════════════

@dataclass
class TrigramImage:
    """八卦万物类象 - 完整版"""
    name: str
    symbol: str
    binary: str
    xiantian: int  # 先天数
    houtian: int   # 后天数
    wuxing: str    # 五行
    direction: str # 方位

    # 天象地理
    heaven: List[str] = field(default_factory=list)
    earth: List[str] = field(default_factory=list)

    # 人物身份
    person: List[str] = field(default_factory=list)
    body_part: List[str] = field(default_factory=list)

    # 动物植物
    animal: List[str] = field(default_factory=list)
    plant: List[str] = field(default_factory=list)

    # 器物建筑
    objects: List[str] = field(default_factory=list)
    buildings: List[str] = field(default_factory=list)

    # 时间颜色
    season: str = ""
    color: List[str] = field(default_factory=list)

    # 卦德属性
    virtue: str = ""
    emotion: str = ""

    # 现代社会映射
    modern: List[str] = field(default_factory=list)


WANWU_LEIXIANG: Dict[str, TrigramImage] = {
    "111": TrigramImage(  # 乾 ☰
        name="乾", symbol="☰", binary="111", xiantian=1, houtian=6,
        wuxing="金", direction="西北",
        heaven=["天", "冰", "雹", "霰", "晴"],
        earth=["京都", "大郡", "高亢之所", "形胜之地", "办公楼"],
        person=["君", "父", "大人", "老人", "长官", "CEO", "一把手", "主管", "名人", "权威人士"],
        body_part=["头", "骨", "肺", "大脑", "面部"],
        animal=["马", "天鹅", "狮", "象"],
        plant=["银杏", "松柏", "参天大树"],
        objects=["金玉", "珠宝", "圆物", "钟表", "镜", "冠", "高级轿车", "飞机", "电脑主机"],
        buildings=["政府大楼", "银行总部", "皇宫", "高塔", "写字楼"],
        season="秋冬之交",
        color=["赤红", "金色", "白色"],
        virtue="健、刚、创造、领导",
        emotion="自信、傲慢",
        modern=["国家元首", "企业总部", "CPU处理器", "航天器", "权威认证"]
    ),
    "110": TrigramImage(  # 兑 ☱
        name="兑", symbol="☱", binary="110", xiantian=2, houtian=7,
        wuxing="金", direction="西",
        heaven=["雨", "泽", "新月", "露"],
        earth=["沼泽", "水边", "缺口之地", "池塘", "娱乐场所"],
        person=["少女", "巫师", "说客", "翻译", "歌手", "讲师", "销售", "主播", "网红"],
        body_part=["口", "舌", "肺", "喉咙", "牙齿"],
        animal=["羊", "鱼", "水鸟"],
        plant=["水生植物", "莲", "水草"],
        objects=["金属乐器", "铃铛", "话筒", "手机", "社交媒体", "喇叭"],
        buildings=["剧院", "KTV", "酒吧", "演讲厅"],
        season="秋",
        color=["白色", "银色"],
        virtue="悦、说、表达、交流",
        emotion="快乐、忧愁",
        modern=["媒体平台", "直播", "社交网络", "发布会", "公关"]
    ),
    "101": TrigramImage(  # 离 ☲
        name="离", symbol="☲", binary="101", xiantian=3, houtian=9,
        wuxing="火", direction="南",
        heaven=["日", "电", "彩虹", "霓虹", "极光"],
        earth=["南方", "干燥之地", "火山", "火电厂", "灯会"],
        person=["中女", "文人", "大腹人", "目疾人", "设计师", "艺术家", "程序员", "网红", "导演"],
        body_part=["目", "心", "上焦", "眼睛", "心脏"],
        animal=["雉", "龟", "火烈鸟", "萤火虫"],
        plant=["花", "红辣椒", "向日葵"],
        objects=["文书", "灯", "电脑屏幕", "画", "电视", "手机屏幕", "霓虹灯"],
        buildings=["图书馆", "画廊", "电影院", "数据中心"],
        season="夏",
        color=["红", "紫", "橙"],
        virtue="明、丽、智慧、依附",
        emotion="热情、焦躁",
        modern=["显示器", "激光", "光纤", "社交媒体", "视频平台"]
    ),
    "100": TrigramImage(  # 震 ☳
        name="震", symbol="☳", binary="100", xiantian=4, houtian=3,
        wuxing="木", direction="东",
        heaven=["雷", "地震", "闪电", "轰鸣"],
        earth=["东方", "大路", "闹市", "机场", "高铁站"],
        person=["长男", "将帅", "司机", "运动员", "军人", "CEO", "创业者", "主播"],
        body_part=["足", "肝", "神经系统", "声带"],
        animal=["龙", "马", "鸣禽"],
        plant=["竹", "苇", "速生植物"],
        objects=["车", "鼓", "音响", "发动机", "电话", "火箭", "扩音器"],
        buildings=["机场", "车站", "体育场"],
        season="春",
        color=["青绿", "碧色"],
        virtue="动、起、奋、震",
        emotion="激动、愤怒",
        modern=["火箭", "引擎", "音响系统", "快递", "5G网络"]
    ),
    "011": TrigramImage(  # 巽 ☴
        name="巽", symbol="☴", binary="011", xiantian=5, houtian=4,
        wuxing="木", direction="东南",
        heaven=["风", "台风", "气流", "云"],
        earth=["东南方", "草木茂盛之所", "花园", "通风处"],
        person=["长女", "商人", "僧道", "教师", "咨询师", "外交官", "中介", "心理咨询师"],
        body_part=["股", "胆", "呼吸道", "鼻子"],
        animal=["鸡", "鸟", "蝴蝶"],
        plant=["藤蔓", "柳", "竹", "一切柔韧植物"],
        objects=["绳", "尺", "风扇", "空调", "写字笔", "WiFi信号", "无人机"],
        buildings=["学校", "咨询所", "花园"],
        season="春夏之交",
        color=["青绿", "碧"],
        virtue="入、顺、谦、渗透",
        emotion="温和、犹豫",
        modern=["无线通信", "互联网", "咨询行业", "教育平台", "无人机"]
    ),
    "010": TrigramImage(  # 坎 ☵
        name="坎", symbol="☵", binary="010", xiantian=6, houtian=1,
        wuxing="水", direction="北",
        heaven=["月", "雨", "雪", "霜", "暗夜"],
        earth=["北方", "江河", "湖海", "沟渠", "下水道", "码头"],
        person=["中男", "盗贼", "船夫", "律师", "侦探", "心理咨询师", "黑客", "潜水员"],
        body_part=["耳", "肾", "泌尿系统", "血液"],
        animal=["猪", "鱼", "水族", "蝙蝠"],
        plant=["水生植物", "藻", "莲"],
        objects=["水容器", "锁", "密码锁", "潜艇", "酒", "墨", "暗房", "加密软件"],
        buildings=["水厂", "码头", "地下室", "保险库"],
        season="冬",
        color=["黑色", "蓝色"],
        virtue="险、陷、隐、智",
        emotion="恐惧、深沉",
        modern=["密码学", "网络安全", "深海技术", "冷链物流", "隐私保护"]
    ),
    "001": TrigramImage(  # 艮 ☶
        name="艮", symbol="☶", binary="001", xiantian=7, houtian=8,
        wuxing="土", direction="东北",
        heaven=["雾", "山岚", "阴霾"],
        earth=["山", "丘陵", "高地", "堤坝", "停车场"],
        person=["少男", "隐士", "保安", "门卫", "守门人", "仓库管理员", "收藏家"],
        body_part=["手", "鼻", "背", "关节", "骨头"],
        animal=["狗", "虎", "鼠", "龟"],
        plant=["松", "柏", "山果", "坚果"],
        objects=["门", "锁", "石", "拐杖", "保险柜", "防火墙", "密码"],
        buildings=["仓库", "寺庙", "监狱", "档案馆"],
        season="冬末春初",
        color=["黄", "棕"],
        virtue="止、静、守、稳",
        emotion="固执、沉稳",
        modern=["防火墙", "保险箱", "数据库", "档案馆", "密码锁"]
    ),
    "000": TrigramImage(  # 坤 ☷
        name="坤", symbol="☷", binary="000", xiantian=8, houtian=2,
        wuxing="土", direction="西南",
        heaven=["阴天", "云", "雾", "霾"],
        earth=["大地", "平原", "田野", "乡村", "农场"],
        person=["母", "臣民", "众人", "员工", "后勤", "护士", "保姆", "群众"],
        body_part=["腹", "脾", "肉", "消化系统"],
        animal=["牛", "马", "母兽"],
        plant=["五谷", "蔬菜", "草本植物"],
        objects=["布", "容器", "大车", "棉被", "土地证", "粮食"],
        buildings=["仓库", "农舍", "养老院", "生产基地"],
        season="夏末秋初",
        color=["黄", "黑", "土色"],
        virtue="顺、柔、厚、载",
        emotion="包容、忍耐",
        modern=["农业科技", "仓储物流", "大众平台", "基层管理", "日用品"]
    ),
}


# ═══════════════════════════════════════════
# 二、体用关系深化推理
# ═══════════════════════════════════════════

@dataclass
class TiYongResult:
    ti_trigram: str      # 体卦
    yong_trigram: str    # 用卦
    ti_wuxing: str
    yong_wuxing: str
    relation: str         # 关系类型
    level: int            # -2到3
    meaning: str
    advice: str
    confidence: float     # 0-1


def analyze_tiyong_deep(upper_binary: str, lower_binary: str, changing_pos: Optional[int] = None) -> TiYongResult:
    """体用深度分析 - 含梅花易数全部规则"""
    from src.data.trigram_map import get_trigram_by_binary
    from src.data.wuxing import ti_yong_relation, TRIGRAM_WUXING, SHENG_MAP, KE_MAP

    upper = get_trigram_by_binary(upper_binary)
    lower = get_trigram_by_binary(lower_binary)
    if not upper or not lower:
        return None

    # 体用判定：有动爻的卦为用，无动爻的卦为体
    if changing_pos and changing_pos <= 3:
        ti_name = upper.name
        yong_name = lower.name
    else:
        ti_name = lower.name
        yong_name = upper.name

    ti_wx = TRIGRAM_WUXING.get(ti_name, "?")
    yong_wx = TRIGRAM_WUXING.get(yong_name, "?")

    rel = ti_yong_relation(ti_wx, yong_wx)

    # 深化建议
    advice_map = {
        "用生体": "大吉之象！外界环境正在帮助你，贵人运强。此时适合主动出击，借力发展。",
        "体克用": "小吉。你能掌控局面，但需要付出努力。适合坚持自己的想法，但要避免过于强势。",
        "比和": "吉。主客和谐顺遂，事情自然发展。保持现状，稳中求进。",
        "体生用": "小凶/泄气。你付出多而回报少。建议转为防守，减少投入，等待时机。",
        "用克体": "大凶之兆。外部环境不利，受制于人。建议避开锋芒，保存实力，静待时机。"
    }

    return TiYongResult(
        ti_trigram=ti_name, yong_trigram=yong_name,
        ti_wuxing=ti_wx, yong_wuxing=yong_wx,
        relation=rel["relation"], level=rel["level"],
        meaning=rel["meaning"],
        advice=advice_map.get(rel["relation"], "保持警觉"),
        confidence=0.8 if rel["level"] != 0 else 0.5
    )


# ═══════════════════════════════════════════
# 三、方位起卦法 (新增)
# ═══════════════════════════════════════════

# 后天八卦方位映射
DIRECTION_TO_TRIGRAM = {
    "北": "010", "东北": "001", "东": "100", "东南": "011",
    "南": "101", "西南": "000", "西": "110", "西北": "111",
    "中": "000",  # 中对应坤
}

# 方位对应后天数
DIRECTION_TO_HOUTIAN = {
    "北": 1, "东北": 8, "东": 3, "东南": 4,
    "南": 9, "西南": 2, "西": 7, "西北": 6,
    "中": 5,
}


def direction_casting(direction: str, sub_direction: Optional[str] = None) -> dict:
    """
    方位起卦法 - 梅花易数独有
    上卦 = 来方
    下卦 = 去方(或所属方位)
    动爻 = 时支%6
    """
    now = datetime.now()
    hour_branch = ((now.hour + 1) // 2) % 12 + 1

    upper_bin = DIRECTION_TO_TRIGRAM.get(direction, "000")
    lower_bin = DIRECTION_TO_TRIGRAM.get(sub_direction, upper_bin)
    moving = hour_branch % 6
    if moving == 0:
        moving = 6

    return {
        "upper_binary": upper_bin,
        "lower_binary": lower_bin,
        "original_binary": upper_bin + lower_bin,
        "changing_pos": moving,
        "method": f"方位卦({direction})"
    }


# ═══════════════════════════════════════════
# 四、应期推算 (梅花易数)
# ═══════════════════════════════════════════

def calculate_yingqi_meihua(wuxing: str, season: str = None) -> Dict[str, str]:
    """
    梅花易数应期推算
    根据体卦五行和当前季节推算应验时间

    应期规则:
    - 旺则近期（数日/数周）
    - 衰则远期（数月/数年）
    - 以五行属性数字为准（金4，水6，木8，火2，土10）
    """
    if season is None:
        month = datetime.now().month
        if 3 <= month <= 5: season = "春"
        elif 6 <= month <= 8: season = "夏"
        elif 9 <= month <= 11: season = "秋"
        else: season = "冬"

    wuxing_season_power = {
        "金": {"旺": "秋", "相": "四季末", "休": "冬", "囚": "春", "死": "夏"},
        "水": {"旺": "冬", "相": "秋", "休": "春", "囚": "夏", "死": "四季末"},
        "木": {"旺": "春", "相": "冬", "休": "夏", "囚": "四季末", "死": "秋"},
        "火": {"旺": "夏", "相": "春", "休": "四季末", "囚": "秋", "死": "冬"},
        "土": {"旺": "四季末", "相": "夏", "休": "秋", "囚": "冬", "死": "春"},
    }

    power = wuxing_season_power.get(wuxing, {})
    current_state = "平"
    for state, s in power.items():
        if season in s:
            current_state = state
            break

    wuxing_numbers = {"金": 4, "水": 6, "木": 8, "火": 2, "土": 5}
    base_num = wuxing_numbers.get(wuxing, 5)

    if current_state in ("旺", "相"):
        period = f"近期({base_num}天内/周内)"
        confidence = 0.7
    elif current_state in ("休",):
        period = f"中期({base_num}周至{base_num}月内)"
        confidence = 0.5
    else:
        period = f"远期({base_num}月至{base_num*2}月内)"
        confidence = 0.3

    return {
        "wuxing": wuxing,
        "current_state": current_state,
        "base_number": base_num,
        "estimated_period": period,
        "confidence": confidence
    }


# ═══════════════════════════════════════════
# 五、便捷函数
# ═══════════════════════════════════════════

def get_trigram_image(binary: str) -> Optional[TrigramImage]:
    """获取八卦万物类象"""
    return WANWU_LEIXIANG.get(binary)

def get_trigram_by_xiantian_num(num: int) -> Optional[TrigramImage]:
    """按先天数获取八卦"""
    for t in WANWU_LEIXIANG.values():
        if t.xiantian == num or (num == 0 and t.xiantian == 8):
            return t
    return None

def get_trigram_by_wuxing(wx: str) -> List[TrigramImage]:
    """按五行获取八卦列表"""
    return [t for t in WANWU_LEIXIANG.values() if t.wuxing == wx]

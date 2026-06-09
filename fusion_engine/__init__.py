"""
AI融合推理引擎 v2 — 三系统深度交叉对话
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class UnifiedInsight:
    domain: str
    iching_reading: str
    bazi_reading: str
    ziwei_reading: str
    agreement_score: float
    common_thread: str
    divergence: str
    fused_interpretation: str
    confidence: float
    short_term: str
    long_term: str


def _dm_personality(dm):
    m = {
        "甲":"你是参天大树型人格——成长慢但根基深，力量在于稳和久。",
        "乙":"你是藤蔓花草型人格——柔韧灵活善借势，力量在于柔和美。",
        "丙":"你是太阳之火型人格——热情奔放感染力强，力量在于光和热。",
        "丁":"你是灯烛之火型人格——细腻持久专注深耕，力量在于精和专。",
        "戊":"你是城墙之土型人格——厚重稳健可靠可信，力量在于稳和信。",
        "己":"你是田园之土型人格——温和包容滋养一切，力量在于养和容。",
        "庚":"你是斧钺之金型人格——锋利果断执行力强，力量在于刚和断。",
        "辛":"你是珠宝之金型人格——精致完美追求卓越，力量在于精和美。",
        "壬":"你是江河之水型人格——奔流不息适应一切，力量在于智和变。",
        "癸":"你是雨露之水型人格——润物无声渗透一切，力量在于深和灵。",
    }
    return m.get(dm, "独特个性")

def _star_personality(star):
    m = {
        "紫微":"天生领袖，不怒自威，自信不需要证明。",
        "天府":"稳重可靠，团队的定心石，什么交给你都放心。",
        "太阳":"热情大方，照亮周围，大家都喜欢和你在一起。",
        "武曲":"果断刚毅，对钱敏感执行力强，天生实干家。",
        "天同":"温和有福，心态好知足常乐，真正的有福之人。",
        "廉贞":"洞察人心，能看透别人看不透的东西，直觉比逻辑更准。",
        "天机":"聪明灵活，脑子快想法多适应力超强。",
        "太阴":"温柔细腻，美是月光那种柔和但持久的美。",
        "贪狼":"多才多艺，什么都懂和谁都能聊，魅力来自杂和博。",
        "巨门":"深邃思考，不喜欢表面总想看真相，深度无人能及。",
        "天相":"公正善良，最好的协调者，团队中有你就是有压舱石。",
        "天梁":"智慧老成，从小比同龄人成熟，年轻人喜欢找你拿主意。",
        "七杀":"勇猛开拓，天生拓荒者越难越来劲，勇猛是最大武器也是最大风险。",
        "破军":"创新突破，最不喜欢被约束，你的创新在变革时代最珍贵。",
    }
    return m.get(star, "独特个性")

def _wx_trait(wx):
    m = {"木":"仁慈宽厚、积极向上、有成长力","火":"热情大方、光明磊落、有感染力","土":"诚信稳重、脚踏实地、有承载力","金":"果断刚毅、勇于开拓、有决断力","水":"智慧灵活、善于变通、有洞察力"}
    return m.get(wx,wx)

def _wx_career(wx):
    m = {"木":"教育、出版、医疗、环保、农林","火":"能源、餐饮、娱乐、传媒、互联网","土":"房地产、建筑、农业、矿产、仓储","金":"金融、机械、法律、军警、工程","水":"贸易、物流、旅游、咨询、水产"}
    return m.get(wx,"综合行业")

def _dm_love_style(dm):
    m = {
        "甲":"在感情中像一棵大树，可靠但不浪漫。你需要学会偶尔开花——浪漫也需要练习。",
        "乙":"在感情中柔韧迷人，但别太依赖对方。藤蔓虽美，自己也要能独立生长。",
        "丙":"爱得热烈直接，喜欢就追。但要学会恒温——持久的温暖比短暂炽热更重要。",
        "丁":"感情细腻但容易多疑。对方十分钟没回消息你就开始胡思乱想。学会信任。",
        "戊":"稳重靠谱但不浪漫。你不会说甜言蜜语但会把工资卡给对方。偶尔学学表达。",
        "己":"温柔体贴但别失去自我。田地可以滋养庄稼但不能被庄稼吸干。",
        "庚":"直接果断不拐弯。喜欢就说不喜欢也直说。这有好有坏——需要磨磨棱角。",
        "辛":"追求完美眼光很高。但完美的人不存在——别因为一根头发放弃整颗珠宝。",
        "壬":"洒脱自由不喜欢被束缚。找到一个理解你需要空间的人——管太紧的不适合你。",
        "癸":"深情细腻，爱最深也伤最深。学会保护自己——不是所有人都值得你那么深。",
    }
    return m.get(dm,"感情中保持真诚和包容。")


def _build_rich_insight(domain, iching_bin, bazi_dm, bazi_wx, bazi_ys, bazi_pat, ziwei_star):
    """为每个领域生成深度融合解读"""
    from src.data import get_db
    from src.interpretation.vernacular import get_vernacular
    from knowledge.bazi import get_day_master_vernacular
    from knowledge.ziwei import get_star_vernacular

    db = get_db()
    h = db.get(iching_bin)
    v = get_vernacular(iching_bin) if h else {}
    dm_v = get_day_master_vernacular(bazi_dm) if bazi_dm else {}
    sv = get_star_vernacular(ziwei_star) if ziwei_star else {}

    # 各系统视角
    if h and v:
        advice = v.get('life_advice', {})
        iching_view = advice.get(domain, h.name + "卦提示谨慎行事")
    else:
        iching_view = "周易数据不足"

    if dm_v:
        advice = dm_v.get('advice', {})
        bazi_view = advice.get(domain, bazi_dm + "日主平稳发展")
    else:
        bazi_view = "八字数据不足"

    if sv:
        advice = sv.get('advice', {})
        ziwei_view = advice.get(domain, "命宫" + ziwei_star + "主" + domain + "运势")
    else:
        ziwei_view = "紫微数据不足"

    # 一致性
    pos_words = ["好","吉","利","顺","旺","强","成","升","主动","把握","机会","发展","佳"]
    neg_words = ["凶","不顺","难","弱","慎","等","伤","困","险","退","守"]
    readings = [iching_view, bazi_view, ziwei_view]
    pos_count = sum(1 for r in readings for w in pos_words if w in r)
    neg_count = sum(1 for r in readings for w in neg_words if w in r)
    agreement = 0.85 if (pos_count >= 2 and neg_count == 0) or (neg_count >= 2 and pos_count == 0) else (0.7 if pos_count > neg_count else 0.55)

    if pos_count > neg_count + 1:
        common = "三系统在" + domain + "领域趋于一致——运势向好，宜主动推进。"
    elif neg_count > pos_count + 1:
        common = "三系统在" + domain + "领域趋于一致——当前不宜冒进，宜保守观望。"
    else:
        common = "三系统在" + domain + "领域信号不一致——需要根据具体情况灵活应对。"

    div = ""
    if pos_count > 0 and neg_count > 0:
        div = "周易和八字侧重积极面，紫微提示需要谨慎。短期和长期策略可能需要不同的力度。"

    dw = max(bazi_wx, key=bazi_wx.get) if bazi_wx else "土"
    trait = _wx_trait(dw)
    career_field = _wx_career(dw)

    # 深度融合解读
    DOMAIN_PARTS = {
        "事业": [
            "## 三维透视你的事业",
            "",
            "### 周易指引",
            iching_view,
            "",
            "### 八字根基",
            bazi_view,
            "你是" + bazi_dm + "命人——" + _dm_personality(bazi_dm),
            "用神为" + bazi_ys + "，格局" + bazi_pat + "。五行属" + dw + "——" + trait,
            "最适合的行业领域: " + career_field,
            "",
            "### 紫微补充",
            ziwei_view,
            "命宫" + ziwei_star + "——" + _star_personality(ziwei_star),
            "紫微揭示你的出厂设置——天生擅长什么、不擅长什么。",
            "",
            "### 融合结论",
            "八字告诉你该往哪走（" + career_field + "），紫微告诉你用什么方式走。",
            "你的核心竞争力是" + trait[:4] + "。职业方向优先考虑" + career_field + "相关领域。",
            "当前策略：" + ("果断行动把握上升期" if pos_count > neg_count else "稳扎稳打不要急于求成" if neg_count > pos_count else "审时度势灵活调整") + "。",
        ],
        "感情": [
            "## 三维透视你的感情",
            "",
            "### 周易指引",
            iching_view,
            "",
            "### 八字根基",
            bazi_view,
            _dm_love_style(bazi_dm),
            "五行属" + dw + "——" + ("感情中需要耐心和时间来培养，不急不躁" if dw in ('土','木') else "感情中保持热情和真诚，但别太炽热" if dw in ('火','金') else "感情中学会变通和包容，别太固执"),
            "",
            "### 紫微补充",
            ziwei_view,
            "命宫" + ziwei_star + "决定了你在感情中的基本模式。" + _star_personality(ziwei_star),
            "",
            "### 融合结论",
            "你在感情中的核心需求是" + ("稳定和被理解" if dw in ('土','木') else "热情和被关注" if dw in ('火','金') else "空间和深度连接") + "。",
            "对的人——" + ("能包容你稳重性格、理解你不太会表达的人" if bazi_dm in ('甲','戊','庚') else "能给你空间、欣赏你独特个性的人") + "。",
        ],
        "健康": [
            "## 三维透视你的健康",
            "",
            "### 周易指引",
            iching_view,
            "",
            "### 八字根基",
            bazi_view,
            "日主" + bazi_dm + "——重点保养" + ("肝胆，少喝酒多运动" if bazi_dm in ('甲','乙') else "心脏血压，情绪平稳最重要" if bazi_dm in ('丙','丁') else "脾胃消化，规律饮食是根本" if bazi_dm in ('戊','己') else "肺和呼吸系统，秋冬特别注意" if bazi_dm in ('庚','辛') else "肾和泌尿系统，多喝水别熬夜") + "。",
            "五行" + ("偏旺，注意平衡" if sum(bazi_wx.values()) > 10 else "较均衡，保持即可"),
            "",
            "### 紫微补充",
            ziwei_view,
            "",
            "### 融合结论",
            ("规律作息、清淡饮食、保持运动——这三点是终身健康基础" if dw in ('土','金') else "保持心情愉快、避免情绪大起大落——你最大的健康敌人是情绪" if dw in ('火','水') else "均衡饮食、充足睡眠——你的身体需要稳定的节奏") + "。",
        ],
        "财运": [
            "## 三维透视你的财运",
            "",
            "### 周易指引",
            iching_view,
            "",
            "### 八字根基",
            bazi_view,
            "日主" + bazi_dm + "命——" + ("适合长期投资和固定资产，不擅长快速投机" if bazi_dm in ('甲','乙','戊','己') else "有投资眼光适合多元化经营" if bazi_dm in ('丙','丁','庚','辛') else "财富来自流动和变通，适合贸易物流投资" if bazi_dm in ('壬','癸') else "按自己的节奏积累"),
            "格局" + bazi_pat + "——" + ("正财宜稳偏财宜活" if '财' in bazi_pat else "官印相生靠能力和地位积累" if '官' in bazi_pat or '印' in bazi_pat else "食伤生财靠才华和创意赚钱" if '食' in bazi_pat or '伤' in bazi_pat else "靠自己的努力和判断"),
            "用神为" + bazi_ys + "——" + ("多接触自然绿色环境" if bazi_ys=='木' else "多做展现自己的工作" if bazi_ys=='火' else "多实际动手做事" if bazi_ys=='土' else "果断行动把握机会" if bazi_ys=='金' else "多学习多旅行开阔眼界" if bazi_ys=='水' else "均衡发展") + "。",
            "",
            "### 紫微补充",
            ziwei_view,
            "",
            "### 融合结论",
            "你的财富密码——" + ("长期积累加复利" if bazi_ys in ('土','木') else "抓住风口加果断出手" if bazi_ys in ('火','金') else "灵活变通加多元配置" if bazi_ys in ('水') else "专业深耕加技术变现") + "。",
        ],
    }

    parts = DOMAIN_PARTS.get(domain, ["综合分析: " + iching_view])
    fused = "\n".join(parts)

    return UnifiedInsight(
        domain=domain,
        iching_reading=iching_view,
        bazi_reading=bazi_view,
        ziwei_reading=ziwei_view,
        agreement_score=agreement,
        common_thread=common,
        divergence=div,
        fused_interpretation=fused,
        confidence=0.7 + agreement * 0.15,
        short_term=("积极行动" if pos_count > neg_count else "谨慎观望") + "，重点补" + bazi_ys + "能量",
        long_term="长期发展适合" + career_field + "相关领域。核心是发挥" + trait[:4] + "的天然优势。"
    )


def generate_fusion_report(iching_binary=None, bazi_day_gan=None, bazi_wx=None,
                           bazi_ys=None, bazi_pat=None, ziwei_star=None, name="命主"):
    """生成融合报告"""
    if bazi_wx is None:
        bazi_wx = {"木":1,"火":1,"土":1,"金":1,"水":1}
    dw = max(bazi_wx, key=bazi_wx.get) if bazi_wx else "土"

    insights = [_build_rich_insight(d, iching_binary, bazi_day_gan, bazi_wx,
                                     bazi_ys, bazi_pat, ziwei_star)
                for d in ["事业", "感情", "健康", "财运"]]

    conflicts = _detect_conflicts(bazi_day_gan, ziwei_star, bazi_wx)

    consistency = sum(ins.agreement_score for ins in insights) / len(insights) if insights else 0.7

    # 最终画像
    iching_name = ""
    try:
        from src.data import get_db
        db = get_db()
        h = db.get(iching_binary)
        if h: iching_name = h.symbol + " " + h.name + "卦"
    except:
        pass

    final_summary_parts = [
        "## " + name + "的三维命理画像",
        "",
        "### 八字告诉我：你是" + bazi_day_gan + "命人",
        _dm_personality(bazi_day_gan),
        "用神为" + bazi_ys + "，格局" + bazi_pat + "。五行属" + dw + "——" + _wx_trait(dw) + "。",
        "",
        "### 紫微告诉我：你命宫坐" + ziwei_star,
        _star_personality(ziwei_star),
        "",
        "### 周易告诉我：参考" + (iching_name if iching_name else "卦象") + "指引",
        "",
        "### 三系统融合",
        "八字是你的操作系统——决定了底层性格和天赋。",
        "紫微是你的出厂设置——决定了天生擅长什么模式。",
        "周易是你的实时导航——告诉你在当前情境下怎么做。",
        "三把钥匙合在一起——你是" + bazi_day_gan + "命人，天生" + _wx_trait(dw)[:8] + "，",
        "命宫" + ziwei_star + "赋予你独特的行事风格。",
        "核心优势是" + _wx_trait(dw)[:10] + "。命理是指南针，你自己才是舵手。",
    ]

    return {
        "iching_hexagram_name": iching_name,
        "bazi_daymaster": bazi_day_gan,
        "bazi_pattern": bazi_pat,
        "ziwei_minggong_star": ziwei_star,
        "dominant_wuxing": dw,
        "consistency_score": consistency,
        "insights": insights,
        "conflicts": conflicts,
        "final_summary": "\n".join(final_summary_parts),
    }


def _detect_conflicts(bazi_dm, ziwei_star, bazi_wx):
    conflicts = []
    star_wx_map = {"紫微":"土","天机":"木","太阳":"火","武曲":"金","天同":"水","廉贞":"火","天府":"土","太阴":"水","贪狼":"木","巨门":"水","天相":"水","天梁":"土","七杀":"金","破军":"水"}
    star_wx = star_wx_map.get(ziwei_star)
    from src.bazi import GAN_WUXING
    day_wx = GAN_WUXING.get(bazi_dm)

    if star_wx and day_wx:
        from src.data.wuxing import ke
        if ke(star_wx, day_wx):
            conflicts.append({"type":"紫微vs八字·自我冲突","detail":"命宫"+ziwei_star+"("+star_wx+")克日主"+bazi_dm+"("+day_wx+")——外在表现和内在本质存在矛盾。别人眼中的你和你真实的自己可能是两个人。接纳差异而非强行统一。","severity":"medium"})
        elif ke(day_wx, star_wx):
            conflicts.append({"type":"紫微vs八字·内在主导","detail":"日主"+bazi_dm+"("+day_wx+")克命宫"+ziwei_star+"("+star_wx+")——内在本质会主导外在表现。表里如一，但有时不够灵活。","severity":"low"})

    total = sum(bazi_wx.values())
    if total > 0:
        for wx, c in bazi_wx.items():
            if c / total > 0.45:
                fix = {"木":"补金克制","火":"补水滋润","土":"补木疏通","金":"补火温暖","水":"补土稳固"}.get(wx,"均衡")
                conflicts.append({"type":"五行偏枯","detail":"五行"+wx+"占比"+str(int(c/total*100))+"%明显过旺。需要"+fix+"来平衡。","severity":"high"})
    return conflicts


def detect_conflicts(profile):
    return profile.get("conflicts", [])


class WuxingUnified:
    WX_PROFILE = {"木":{"color":"青绿","direction":"东","season":"春","organ":"肝","virtue":"仁","number":8},"火":{"color":"赤红","direction":"南","season":"夏","organ":"心","virtue":"礼","number":7},"土":{"color":"黄棕","direction":"中","season":"四季末","organ":"脾","virtue":"信","number":5},"金":{"color":"白","direction":"西","season":"秋","organ":"肺","virtue":"义","number":9},"水":{"color":"黑蓝","direction":"北","season":"冬","organ":"肾","virtue":"智","number":6}}
    @classmethod
    def get_profile(cls, wx): return cls.WX_PROFILE.get(wx, {})
    @classmethod
    def check_balance(cls, counts):
        total = sum(counts.values())
        if total == 0: return {"balanced": True, "excess": [], "deficit": [], "ratios": {}, "advice": ""}
        ratios = {wx: c/total for wx, c in counts.items()}
        excess = [wx for wx, r in ratios.items() if r > 0.4]
        deficit = [wx for wx, r in ratios.items() if r < 0.05]
        return {"balanced": not excess and not deficit, "excess": excess, "deficit": deficit, "ratios": ratios, "advice": ("、".join(excess) if excess else "") + "过旺" if excess else "" + ("、".join(deficit) if deficit else "") + "不足" if deficit else "五行平衡"}

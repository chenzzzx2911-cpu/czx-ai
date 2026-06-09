"""
断卦AI推理引擎 v1 — 多层推理链 + 置信度评分
整合: 梅花易数体用分析 + 六爻纳甲判断 + 易传哲学解释
架构: 古法(火珠林飞伏) + 今法(增删卜易) 双轨推理
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import get_db
from src.data.wuxing import ti_yong_relation, TRIGRAM_WUXING, SHENG_MAP, KE_MAP
from src.interpretation.vernacular import get_vernacular
from knowledge.meihua import analyze_tiyong_deep, calculate_yingqi_meihua, get_trigram_image
from knowledge.liuyao import (
    install_najia, select_yongshen, judge_wangshuai,
    analyze_dongbian, calculate_yingqi_liuyao, get_liushen
)
from knowledge.yizhuan import analyze_by_yizhuan


# ═══════════════════════════════════════════
# 一、推理步骤定义
# ═══════════════════════════════════════════

@dataclass
class ReasoningStep:
    """单步推理"""
    step_id: int
    step_name: str        # 步骤名称
    engine: str            # 引擎来源 (meihua/liuyao/yizhuan)
    input_data: dict       # 输入
    output_data: dict      # 输出
    confidence: float      # 该步置信度 0-1
    rule_source: str       # 规则来源
    explanation: str       # 解释


@dataclass
class FinalReport:
    """最终断卦报告"""
    timestamp: str
    original_hexagram_name: str
    original_hexagram_symbol: str
    changing_lines: List[int]
    changed_hexagram_name: str
    changed_hexagram_symbol: str

    # 推理链
    reasoning_chain: List[ReasoningStep] = field(default_factory=list)

    # 各引擎结论
    meihua_conclusion: dict = field(default_factory=dict)
    liuyao_conclusion: dict = field(default_factory=dict)
    yizhuan_conclusion: dict = field(default_factory=dict)

    # 融合结论
    final_judgment: str = ""           # 综合判语
    auspiciousness: str = ""           # 吉凶: 大吉/吉/平/小凶/凶/大凶
    overall_confidence: float = 0.0    # 总体置信度
    risk_level: str = ""               # 风险等级
    advice: List[str] = field(default_factory=list)  # 建议
    rule_citations: List[str] = field(default_factory=list)  # 规则引用

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "本卦": f"{self.original_hexagram_symbol} {self.original_hexagram_name}卦",
            "变爻": self.changing_lines,
            "变卦": f"{self.changed_hexagram_symbol} {self.changed_hexagram_name}卦",
            "综合判语": self.final_judgment,
            "吉凶": self.auspiciousness,
            "置信度": f"{self.overall_confidence:.0%}",
            "风险": self.risk_level,
            "建议": self.advice,
            "梅花易数": self.meihua_conclusion,
            "六爻纳甲": self.liuyao_conclusion,
            "易传": self.yizhuan_conclusion,
        }


# ═══════════════════════════════════════════
# 二、主推理引擎
# ═══════════════════════════════════════════

class DivinationReasoningEngine:
    """断卦推理引擎"""

    def __init__(self, topic: str = "综合运势"):
        self.db = get_db()
        self.topic = topic
        self.steps: List[ReasoningStep] = []
        self._step_counter = 0

    def _add_step(self, name: str, engine: str, input_data: dict,
                  output_data: dict, confidence: float,
                  rule_source: str, explanation: str) -> ReasoningStep:
        self._step_counter += 1
        step = ReasoningStep(
            step_id=self._step_counter, step_name=name, engine=engine,
            input_data=input_data, output_data=output_data,
            confidence=confidence, rule_source=rule_source,
            explanation=explanation
        )
        self.steps.append(step)
        return step

    def reason(self, original_binary: str, changing_lines: List[int],
               month: int = None, day_gan: str = None,
               day_zhi: str = None) -> FinalReport:
        """主推理流程: 多层推理链"""
        if month is None:
            month = datetime.now().month

        original = self.db.get(original_binary)
        changed_bin = list(original_binary)
        for pos in changing_lines:
            idx = 6 - pos
            changed_bin[idx] = "0" if changed_bin[idx] == "1" else "1"
        changed_bin = "".join(changed_bin)
        changed = self.db.get(changed_bin)

        # ═══════ Step 1: 梅花易数体用分析 ═══════
        ti_yong = analyze_tiyong_deep(original_binary[:3], original_binary[3:],
                                       changing_lines[0] if changing_lines else None)
        meihua_yingqi = calculate_yingqi_meihua(ti_yong.ti_wuxing)
        upper_img = get_trigram_image(original_binary[:3])
        lower_img = get_trigram_image(original_binary[3:])

        self._add_step(
            "梅花易数·体用生克", "meihua",
            {"本卦": original_binary, "变爻": changing_lines},
            {"体卦": ti_yong.ti_trigram, "用卦": ti_yong.yong_trigram,
             "体五行": ti_yong.ti_wuxing, "用五行": ti_yong.yong_wuxing,
             "关系": ti_yong.relation, "等级": ti_yong.level},
            ti_yong.confidence,
            "《梅花易数》体用篇",
            f"体卦{ti_yong.ti_trigram}({ti_yong.ti_wuxing})代表自己，"
            f"用卦{ti_yong.yong_trigram}({ti_yong.yong_wuxing})代表事物。"
            f"{ti_yong.relation}——{ti_yong.meaning}"
        )

        # ═══════ Step 2: 六爻纳甲装卦 ═══════
        najia = install_najia(original_binary, changing_lines, day_gan, day_zhi, month)

        self._add_step(
            "六爻·纳甲装卦", "liuyao",
            {"本卦": original_binary, "变爻": changing_lines},
            {"卦宫": najia.palace, "宫五行": najia.palace_wuxing,
             "世爻位": najia.shi_position, "应爻位": najia.ying_position},
            0.95,
            "《火珠林》《京房易传》八宫纳甲体系",
            f"本卦属{najia.palace}({najia.palace_wuxing})。"
            f"世爻在第{najia.shi_position}爻(代表自己)，应爻在第{najia.ying_position}爻(代表对方)。"
        )

        # ═══════ Step 3: 六爻用神选取 ═══════
        ys_info = select_yongshen(self.topic)

        self._add_step(
            "六爻·用神选取", "liuyao",
            {"问事": self.topic},
            {"用神": ys_info["yongshen"], "说明": ys_info["description"]},
            ys_info["confidence"],
            "《增删卜易》用神章",
            f"问{self.topic}取{ys_info['yongshen']}为用神。{ys_info['description']}。"
        )

        # ═══════ Step 4: 六爻旺衰判断 ═══════
        ws = judge_wangshuai(najia.palace_wuxing, month, day_zhi)

        self._add_step(
            "六爻·旺衰判断", "liuyao",
            {"宫五行": najia.palace_wuxing, "月": month},
            {"旺衰等级": ws["level"], "得分": ws["score"], "季节状态": ws["season_state"]},
            ws["confidence"],
            "《增删卜易》四时旺衰章",
            f"当前季节{najia.palace_wuxing}处于「{ws['season_state']}」状态。"
            f"综合评级「{ws['level']}」(得分{ws['score']}/10)。{ws.get('day_effect','')}"
        )

        # ═══════ Step 5: 动变分析 ═══════
        dongbian = analyze_dongbian(najia.shi_position, najia.yao_list)

        self._add_step(
            "六爻·动变分析", "liuyao",
            {"变爻": changing_lines, "世爻": najia.shi_position},
            {"影响": dongbian["effects"]},
            0.7,
            "《增删卜易》动变章 + 《火珠林》飞伏原理",
            dongbian["summary"]
        )

        # ═══════ Step 6: 易传哲学分析 ═══════
        yz = analyze_by_yizhuan(original_binary, changing_lines)

        self._add_step(
            "易传·象数时位分析", "yizhuan",
            {"本卦": original_binary, "变爻": changing_lines},
            {"阴阳": yz.yinyang.interpretation,
             "刚柔": yz.gangrou["nature"],
             "时位": yz.shiwei_assessment["name"]},
            0.75,
            "《系辞》《彖传》《象传》",
            yz.overall
        )

        # ═══════ Step 7: 融合判语 ═══════
        # 综合置信度 = 各引擎置信度的加权平均
        weights = {"meihua_step": 0.35, "liuyao_steps": 0.45, "yizhuan_step": 0.20}
        meihua_conf = ti_yong.confidence
        liuyao_conf = (ws["confidence"] + 0.7 + ys_info["confidence"]) / 3
        yizhuan_conf = 0.75

        overall_conf = (meihua_conf * 0.35 + liuyao_conf * 0.45 + yizhuan_conf * 0.20)

        # 吉凶判断
        ti_yong_level = ti_yong.level
        wangshuai_level = ws["score"]

        if ti_yong_level >= 2 and wangshuai_level >= 7:
            ausp = "大吉"
            risk = "低"
        elif ti_yong_level >= 0 and wangshuai_level >= 4:
            ausp = "吉"
            risk = "中低"
        elif ti_yong_level >= -1 and wangshuai_level >= 3:
            ausp = "平"
            risk = "中"
        elif ti_yong_level >= -2 and wangshuai_level >= 2:
            ausp = "小凶"
            risk = "中高"
        else:
            ausp = "凶"
            risk = "高"

        # 生成建议
        advices = []
        if ti_yong.relation == "用生体":
            advices.append("外部环境助你，宜主动出击")
        elif ti_yong.relation == "用克体":
            advices.append("受外部压制，宜避锋芒等待时机")
        elif ti_yong.relation == "体生用":
            advices.append("付出多回报少，宜减少投入转型")

        if ws["level"] in ("极旺","旺相"):
            advices.append("当前旺相有力，适合积极推进")
        elif ws["level"] == "衰弱":
            advices.append("力量不足，宜养精蓄锐")
        advices.append(ti_yong.advice)

        # 综合判语
        v = get_vernacular(original_binary)
        judgment_parts = [
            f"本卦得{original.symbol}{original.name}卦——{v.get('summary','')[:80]}",
            f"体用关系为「{ti_yong.relation}」({ti_yong.meaning})",
            f"卦宫旺衰评为「{ws['level']}」，整体态势{'有利' if ausp in ('大吉','吉') else '需谨慎'}。",
        ]
        if changing_lines:
            judgment_parts.append(f"第{changing_lines}爻发动,提示有变动。变卦为{changed.symbol if changed else '?'}{changed.name if changed else '?'}卦。")

        report = FinalReport(
            timestamp=datetime.now().isoformat(),
            original_hexagram_name=original.name,
            original_hexagram_symbol=original.symbol,
            changing_lines=changing_lines,
            changed_hexagram_name=changed.name if changed else "",
            changed_hexagram_symbol=changed.symbol if changed else "",
            reasoning_chain=self.steps,
            meihua_conclusion={
                "体卦": ti_yong.ti_trigram, "用卦": ti_yong.yong_trigram,
                "关系": ti_yong.relation, "等级": ti_yong.level,
                "应期": meihua_yingqi["estimated_period"],
                "万物类象": f"上{upper_img.name if upper_img else '?'}({', '.join(upper_img.modern[:2]) if upper_img else '?'}) 下{lower_img.name if lower_img else '?'}({', '.join(lower_img.modern[:2]) if lower_img else '?'})"
            },
            liuyao_conclusion={
                "卦宫": najia.palace, "宫五行": najia.palace_wuxing,
                "用神": ys_info["yongshen"], "旺衰": ws["level"],
                "世爻": najia.shi_position, "应爻": najia.ying_position,
                "动变": dongbian["summary"]
            },
            yizhuan_conclusion={
                "阴阳": yz.yinyang.interpretation,
                "刚柔": yz.gangrou["nature"],
                "时位": yz.shiwei_assessment["name"],
                "上下卦象": f"上{upper_img.name if upper_img else '?'}({upper_img.virtue if upper_img else '?'})下{lower_img.name if lower_img else '?'}({lower_img.virtue if lower_img else '?'})"
            },
            final_judgment=" ".join(judgment_parts),
            auspiciousness=ausp,
            overall_confidence=overall_conf,
            risk_level=risk,
            advice=advices,
            rule_citations=[
                "《梅花易数》体用生克篇",
                "《增删卜易》用神章 + 四时旺衰章",
                "《火珠林》纳甲装卦法",
                "《系辞》阴阳时位",
            ]
        )

        return report


# ═══════════════════════════════════════════
# 三、便捷接口
# ═══════════════════════════════════════════

def divine(original_binary: str, changing_lines: List[int] = None,
           topic: str = "综合运势") -> FinalReport:
    """快速断卦入口"""
    if changing_lines is None:
        changing_lines = []
    engine = DivinationReasoningEngine(topic)
    return engine.reason(original_binary, changing_lines)

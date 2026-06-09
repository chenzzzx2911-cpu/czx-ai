"""
解卦引擎 v2 — 集成白话解读、生活启示、分领域分析
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

from ..data import get_db, HexagramDB, Hexagram, split_hexagram, TRIGRAMS
from ..data.wuxing import ti_yong_relation, TRIGRAM_WUXING
from ..casting import CastResult
from .vernacular import get_vernacular


@dataclass
class InterpretationSection:
    """解读报告的一个段落"""
    title: str
    content: str
    source: str = ""
    importance: int = 0  # 0-5, 越高越重要


@dataclass
class FullReport:
    """完整的解卦报告"""
    cast_result: CastResult
    original_hexagram: Optional[Hexagram] = None
    changed_hexagram: Optional[Hexagram] = None
    mutual_hexagram: Optional[Hexagram] = None
    zong_hexagram: Optional[Hexagram] = None
    cuo_hexagram: Optional[Hexagram] = None
    ti_yong: Optional[Dict] = None
    vernacular: Optional[Dict] = None
    sections: List[InterpretationSection] = field(default_factory=list)
    summary: str = ""

    def to_markdown(self) -> str:
        lines = [f"# 🔮 周易占卜报告\n",
                 f"**起卦方式**: {self.cast_result.method}",
                 f"**起卦时间**: {self.cast_result.timestamp}\n"]

        if self.original_hexagram:
            lines.append(f"## 本卦: {self.original_hexagram.symbol} {self.original_hexagram.name}卦")
            lines.append(f"上卦: {self.original_hexagram.upper_trigram} | 下卦: {self.original_hexagram.lower_trigram}")
            lines.append(f"五行: 上{self.original_hexagram.upper_wuxing} 下{self.original_hexagram.lower_wuxing}\n")

        # 白话解读放在最前面
        if self.vernacular:
            lines.append("## 📖 白话解读")
            lines.append(f"**{self.vernacular.get('summary', '')}**\n")
            if self.vernacular.get('vernacular_gua_ci'):
                lines.append(f"**卦辞白话**: {self.vernacular['vernacular_gua_ci']}\n")
            # 分领域
            advice = self.vernacular.get('life_advice', {})
            if advice:
                lines.append("### 💼 事业")
                lines.append(advice.get('事业', ''))
                lines.append("\n### 💕 感情")
                lines.append(advice.get('感情', ''))
                lines.append("\n### 🏥 健康")
                lines.append(advice.get('健康', ''))
                lines.append("\n### 💰 财运")
                lines.append(advice.get('财运', ''))
                lines.append("")
            if self.vernacular.get('life_lesson'):
                lines.append(f"> **人生启示**: {self.vernacular['life_lesson']}\n")

        if self.cast_result.changing_lines:
            lines.append(f"### ⚡ 变爻: 第{', '.join(str(p) for p in self.cast_result.changing_lines)}爻\n")

        if self.changed_hexagram and self.changed_hexagram != self.original_hexagram:
            lines.append(f"## 变卦: {self.changed_hexagram.symbol} {self.changed_hexagram.name}卦\n")

        if self.mutual_hexagram:
            lines.append(f"## 互卦: {self.mutual_hexagram.symbol} {self.mutual_hexagram.name}卦")
            lines.append("揭示事物发展过程中的内在变化。\n")

        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append(section.content)
            if section.source:
                lines.append(f"> 📚 {section.source}")
            lines.append("")

        if self.ti_yong:
            lines.append("## ⚖️ 体用生克分析")
            ty = self.ti_yong
            rel = ty.get("relation", {})
            lines.append(f"- **体卦**: {ty.get('ti_name','?')} ({ty.get('ti_wuxing','?')}) — 代表你自己/主体")
            lines.append(f"- **用卦**: {ty.get('yong_name','?')} ({ty.get('yong_wuxing','?')}) — 代表事物/对方")
            lines.append(f"- **关系**: {rel.get('relation','?')} ({rel.get('meaning','')})")
            lines.append("")

        if self.summary:
            lines.append(f"## 📜 综合判语\n{self.summary}\n")

        lines.append("---\n*以上解读仅供参考，请理性对待。*")
        return "\n".join(lines)


class Interpreter:
    """解卦解释器 v2"""

    def __init__(self, db: Optional[HexagramDB] = None):
        self.db = db or get_db()

    def interpret(self, cast_result: CastResult) -> FullReport:
        report = FullReport(cast_result=cast_result)

        original = self.db.get(cast_result.original_binary)
        report.original_hexagram = original

        if original:
            # 白话解读（最重要！放前面）
            report.vernacular = get_vernacular(original.binary)

            # 变卦
            if cast_result.has_changing_lines():
                changed = self.db.get(cast_result.changed_binary)
                if changed and changed.binary != original.binary:
                    report.changed_hexagram = changed

            # 互卦
            mutual = self.db.get(original.hu_gua_binary)
            if mutual:
                report.mutual_hexagram = mutual

            # 综卦
            zong = self.db.get(original.zong_gua_binary)
            if zong and zong.binary != original.binary:
                report.zong_hexagram = zong

            # 错卦
            cuo = self.db.get(original.cuo_gua_binary)
            if cuo and cuo.binary != original.binary:
                report.cuo_hexagram = cuo

            # 原文段落
            self._add_original_section(report, original)
            self._add_changing_lines_section(report, original, cast_result)
            self._add_mutual_section(report, report.mutual_hexagram)
            self._add_ti_yong(report, original, cast_result)

        report.summary = self._build_summary(report)
        return report

    def _add_original_section(self, report: FullReport, h: Hexagram):
        content = f"**卦辞原文**: {h.gua_ci}\n\n**《彖》曰**: {h.tuan_ci}\n\n**《象》曰**: {h.da_xiang_ci}"
        report.sections.append(InterpretationSection(
            title=f"📜 原文 — {h.name}卦",
            content=content,
            source=f"《周易·{h.name}卦》"
        ))

    def _add_changing_lines_section(self, report: FullReport, h: Hexagram, cr: CastResult):
        if not cr.changing_lines:
            return
        parts = []
        for pos in cr.changing_lines:
            yao = h.yao_lines[pos - 1] if pos <= len(h.yao_lines) else None
            if yao:
                parts.append(f"**{yao.type_str}**: {yao.text}\n> 《象》曰: {yao.xiao_xiang}")
        report.sections.append(InterpretationSection(
            title=f"🔀 变爻分析 ({', '.join(str(p) for p in cr.changing_lines)}爻)",
            content="\n\n---\n\n".join(parts),
            source=f"《周易·{h.name}卦》爻辞"
        ))

    def _add_mutual_section(self, report: FullReport, mutual: Optional[Hexagram]):
        if not mutual:
            return
        content = f"互卦揭示事物内在变化趋势。\n\n**{mutual.name}卦**: {mutual.gua_ci}\n\n**《彖》曰**: {mutual.tuan_ci}"
        report.sections.append(InterpretationSection(
            title=f"🔄 互卦 — {mutual.symbol} {mutual.name}",
            content=content,
            source=f"《周易·{mutual.name}卦》"
        ))

    def _add_ti_yong(self, report: FullReport, h: Hexagram, cr: CastResult):
        ti_name, yong_name = h.lower_trigram, h.upper_trigram
        if cr.changing_lines:
            for pos in cr.changing_lines:
                ti_name, yong_name = (h.upper_trigram, h.lower_trigram) if pos <= 3 else (h.lower_trigram, h.upper_trigram)
                break
        ti_wx = TRIGRAM_WUXING.get(ti_name, "?")
        yong_wx = TRIGRAM_WUXING.get(yong_name, "?")
        rel = ti_yong_relation(ti_wx, yong_wx)
        report.ti_yong = {"ti_name": ti_name, "ti_wuxing": ti_wx, "yong_name": yong_name, "yong_wuxing": yong_wx, "relation": rel}

    def _build_summary(self, report: FullReport) -> str:
        h = report.original_hexagram
        if not h:
            return "无法生成判语。"

        parts = []
        if report.vernacular:
            parts.append(f"**{h.symbol} {h.name}卦**: {report.vernacular.get('summary', '')}")
        else:
            parts.append(f"本卦得 **{h.symbol} {h.name}**：「{h.gua_ci[:50]}...」")

        if report.cast_result.changing_lines:
            parts.append(f"卦中第{report.cast_result.changing_lines}爻发动，提示事有变动。")

        if report.ti_yong:
            rel = report.ti_yong.get("relation", {})
            parts.append(f"**体用关系**: {rel.get('relation', '?')}。{rel.get('meaning', '')}")

        if report.vernacular and report.vernacular.get('life_lesson'):
            parts.append(f"**人生启示**: {report.vernacular['life_lesson']}")

        return "\n\n".join(parts)


def interpret_cast(cast_result: CastResult) -> FullReport:
    return Interpreter().interpret(cast_result)

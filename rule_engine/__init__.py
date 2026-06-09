"""
规则引擎 — 统一规则管理、冲突检测、可信度评估
管理所有知识模块的规则,实现规则注册/查询/冲突检测/优先级排序
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class RuleCategory(Enum):
    MEIHUA = "梅花易数"
    LIUYAO = "六爻纳甲"
    YIZHUAN = "易传"
    FUSION = "融合规则"


class RuleSeverity(Enum):
    CRITICAL = "critical"   # 必须遵守
    HIGH = "high"           # 高优先级
    MEDIUM = "medium"       # 中等
    LOW = "low"             # 参考
    DEPRECATED = "deprecated"  # 已弃用


@dataclass
class Rule:
    """单条规则"""
    id: str
    category: RuleCategory
    source: str             # 规则来源古籍
    description: str        # 规则描述
    severity: RuleSeverity  # 优先级
    condition: str          # 触发条件(自然语言或Python表达式)
    action: str             # 执行动作
    confidence: float       # 可信度 0-1
    citations: List[str] = field(default_factory=list)  # 古籍引用
    conflicts_with: List[str] = field(default_factory=list)  # 冲突的规则ID


class RuleEngine:
    """规则引擎"""

    def __init__(self):
        self._rules: Dict[str, Rule] = {}
        self._register_core_rules()

    def _register_core_rules(self):
        """注册核心规则库"""

        # ═══ 体用规则 ═══
        self.register(Rule(
            id="MEIHUA-001", category=RuleCategory.MEIHUA,
            source="《梅花易数》体用生克篇",
            description="用生体为吉,外助我也;体生用为泄,付出多回报少",
            severity=RuleSeverity.CRITICAL, condition="体用关系判定",
            action="计算体用五行生克,输出关系等级(用生体>比和>体克用>体生用>用克体)",
            confidence=0.95,
            citations=["大抵用生体，百事成。体生用，事难成，须费力。"]
        ))

        self.register(Rule(
            id="MEIHUA-002", category=RuleCategory.MEIHUA,
            source="《梅花易数》",
            description="动爻所在卦为用,不动者为体",
            severity=RuleSeverity.CRITICAL, condition="卦中有动爻",
            action="动爻在上卦则上为用下为体；动在下卦则下为用上为体；无动爻则上为用下为体",
            confidence=0.95
        ))

        # ═══ 纳甲规则 ═══
        self.register(Rule(
            id="LIUYAO-001", category=RuleCategory.LIUYAO,
            source="《京房易传》《火珠林》",
            description="八纯卦为本宫,一世到五世按序变爻,游魂归魂定世应",
            severity=RuleSeverity.CRITICAL, condition="纳甲装卦",
            action="按八宫六十四卦表定位,查表得世应位",
            confidence=0.98
        ))

        self.register(Rule(
            id="LIUYAO-002", category=RuleCategory.LIUYAO,
            source="《增删卜易》用神章",
            description="六亲取用:问财取妻财,问官取官鬼,问文书取父母,问子孙取子孙,自问吉凶取世爻",
            severity=RuleSeverity.CRITICAL, condition="选取用神",
            action="按问事类别匹配用神六亲",
            confidence=0.90
        ))

        self.register(Rule(
            id="LIUYAO-003", category=RuleCategory.LIUYAO,
            source="《增删卜易》四时旺衰章",
            description="春木旺夏火旺秋金旺冬水旺四季末土旺;月建权重>日辰>动爻",
            severity=RuleSeverity.HIGH, condition="判断旺衰",
            action="先查月建季节定旺相休囚死,再查日辰生克调整",
            confidence=0.85
        ))

        self.register(Rule(
            id="LIUYAO-004", category=RuleCategory.LIUYAO,
            source="《火珠林》飞伏篇",
            description="飞伏原理:本宫伏神为体,飞神为用;飞来生伏得长生,飞来克伏被压制",
            severity=RuleSeverity.MEDIUM, condition="用神不现",
            action="查本宫同位爻作为伏神,判断飞伏生克关系",
            confidence=0.70
        ))

        # ═══ 动变规则 ═══
        self.register(Rule(
            id="DONGBIAN-001", category=RuleCategory.LIUYAO,
            source="《增删卜易》动变章",
            description="动爻重于静爻;动爻生用神则吉克用神则凶;动化回头生吉化回头克凶",
            severity=RuleSeverity.CRITICAL, condition="卦中有动爻",
            action="逐个检查动爻与用神的关系,综合判定",
            confidence=0.88
        ))

        # ═══ 应期规则 ═══
        self.register(Rule(
            id="YINGQI-001", category=RuleCategory.MEIHUA,
            source="《梅花易数》应期篇",
            description="旺则近期应,衰则远期应;以卦数推算具体时间",
            severity=RuleSeverity.MEDIUM, condition="推算应期",
            action="根据体用五行旺衰和先天数推算",
            confidence=0.55
        ))

        self.register(Rule(
            id="YINGQI-002", category=RuleCategory.LIUYAO,
            source="《增删卜易》应期章",
            description="用神值日应/逢冲应/逢合应/出空应",
            severity=RuleSeverity.MEDIUM, condition="推算应期",
            action="检查用神地支与日辰关系,择应期",
            confidence=0.60
        ))

        # ═══ 易传规则 ═══
        self.register(Rule(
            id="YIZHUAN-001", category=RuleCategory.YIZHUAN,
            source="《系辞》《彖传》",
            description="中正原则:二爻五爻为「中」,阳居阳位/阴居阴位为「正」;中正者德位相配",
            severity=RuleSeverity.HIGH, condition="判断爻位吉凶",
            action="检查关键爻是否中正,用于调整吉凶判断",
            confidence=0.80
        ))

        self.register(Rule(
            id="YIZHUAN-002", category=RuleCategory.YIZHUAN,
            source="《系辞》",
            description="时位思想:六爻对应六个阶段—初潜二见三惕四跃五飞上亢",
            severity=RuleSeverity.MEDIUM, condition="判断当前阶段",
            action="根据世爻或变爻位置判断所处阶段",
            confidence=0.75
        ))

    def register(self, rule: Rule):
        self._rules[rule.id] = rule

    def get(self, rule_id: str) -> Optional[Rule]:
        return self._rules.get(rule_id)

    def get_by_category(self, category: RuleCategory) -> List[Rule]:
        return [r for r in self._rules.values() if r.category == category]

    def get_critical_rules(self) -> List[Rule]:
        return [r for r in self._rules.values() if r.severity == RuleSeverity.CRITICAL]

    def check_conflicts(self) -> List[Tuple[Rule, Rule]]:
        """检测规则冲突"""
        conflicts = []
        for r1 in self._rules.values():
            for conflict_id in r1.conflicts_with:
                if conflict_id in self._rules:
                    r2 = self._rules[conflict_id]
                    conflicts.append((r1, r2))
        return conflicts

    def list_all(self) -> List[Rule]:
        return list(self._rules.values())


# 全局单例
_engine = None
def get_rule_engine() -> RuleEngine:
    global _engine
    if _engine is None:
        _engine = RuleEngine()
    return _engine

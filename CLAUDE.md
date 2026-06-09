# 🌀 周易系统 — 项目总规则

> **铁规则**: 每次新会话必须首先读取 `memory.md`，基于其中状态继续工作。
> **单一真相源**: `D:\ClaudeCode\STATE.md` 为全局进度索引。

---

## 项目目标

构建一套完整的周易占卜与解读系统，包含：起卦（多种方式）、解卦（卦辞/爻辞/变卦/互卦/体用生克）、Web界面。数据基于《周易》原文（繁体），拓展梅花易数体系。

## 系统架构

```
web/app.py (Streamlit UI)
     ↓
src/casting/                  起卦引擎
├── money_casting.py          金钱卦（3铜钱×6次）
├── time_casting.py           时间卦（年月日时）
├── number_casting.py         数字卦（用户输入）
└── random_casting.py         随机卦
     ↓ CastResult (本卦binary + 变爻位置)
     ↓
src/interpretation/           解卦引擎
├── hexagram_reader.py        本卦解读（卦辞/彖传/象传）
├── line_analyzer.py          变爻分析（爻辞/小象传）
├── changed_hexagram.py       变卦解读
├── mutual_hexagram.py        互卦分析
├── ti_yong.py                体用生克（梅花易数）
└── report_builder.py         综合报告生成
     ↓
src/data/                     数据层
├── hexagram_db.py            64卦数据库（结构化JSON）
├── trigram_map.py            八卦映射（数/象/五行/方位）
└── wuxing.py                 五行生克体系
```

## 数据来源

- **主源**: Jason-W507/I_Ching_Divination 的 `gua_yao_ci.json`（繁体原文，64卦384爻完整）
- **体系补充**: 梅花易数（体用生克、万物类象）、增删卜易（六爻纳甲）

## 编码规范

1. Python 3.10+
2. 核心数据用 JSON，不引入数据库依赖
3. 类型标注推荐（dataclass 优先）
4. 所有中文输出用繁体（与原文一致）
5. 解卦报告结构化，可追溯来源

## 关键设施

- **卦象数据库**: `data/gua_yao_ci.json`（66KB, 64卦）
- **八卦映射**: 乾兑离震巽坎艮坤 × 先天数/后天数/五行/方位
- **五行生克**: 金水木火土 生克乘侮关系

## 永久不变的核心规则

1. ✅ 原文不可篡改（以通行本《周易》为准）
2. ✅ 解卦必须标注引用来源（卦辞/爻辞/彖传/象传）
3. ✅ 禁止神化预测——所有输出必须注明"仅供参考"
4. ✅ 起卦逻辑必须可重现（相同输入→相同输出）
5. ❌ 不允许编造卦辞爻辞
6. ❌ 不预测具体事件（只提供卦象解读，不代做决策）

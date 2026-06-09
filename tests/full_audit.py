"""全系统深度体检"""
import sys, os, json
sys.path.insert(0, 'D:/ClaudeCode/zhouyi-system')
os.environ['PYTHONIOENCODING'] = 'utf-8'

errors = []
warnings = []

def check(label, condition, msg):
    if not condition: errors.append(f"[{label}] {msg}")

# 1. Data Layer
print("[1/8] Data Layer...")
from src.data import get_db
db = get_db()
check("Data.Count", len(db)==64, f"Got {len(db)}")
for h in db.all_hexagrams():
    check(f"Data.{h.name}", len(h.yao_lines)==6, "Bad yao_lines")
    check(f"Data.{h.name}", h.hu_gua_binary and len(h.hu_gua_binary)==6, "Bad hu_gua")
    check(f"Data.{h.name}", len(h.symbol)>=2, f"Symbol short: {h.symbol}")
print(f"  OK: {len(db)} hexagrams, all fields present")

# 2. Vernacular
print("[2/8] Vernacular...")
from src.interpretation.vernacular import get_vernacular
for h in db.all_hexagrams():
    v = get_vernacular(h.binary)
    if not v or len(v.get('summary','')) < 10:
        errors.append(f"Vernacular.{h.name}: summary too short")
print(f"  OK: 64/64 vernacular loaded")

# 3. Casting
print("[3/8] Casting Engine...")
from src.casting import money_casting, time_casting, number_casting, random_casting
for fn, name in [(money_casting,"money"),(time_casting,"time"),(number_casting,"num"),(random_casting,"random")]:
    cr = fn() if name!="num" else number_casting(42,15,3)
    check(f"Casting.{name}", len(cr.original_binary)==6, "Bad binary")
    check(f"Casting.{name}", len(cr.lines_detail)==6, "Bad lines_detail")
cr2 = time_casting()
check("Casting.CalcDetail", cr2.calc_detail and 'upper_formula' in cr2.calc_detail, "Missing calc_detail")
print(f"  OK: 4 methods work, calc_detail present")

# 4. Interpretation
print("[4/8] Interpretation...")
from src.interpretation import interpret_cast
report = interpret_cast(time_casting())
check("Interp.Hexagram", report.original_hexagram is not None, "No hexagram")
check("Interp.Vernacular", report.vernacular is not None, "No vernacular")
check("Interp.TiYong", report.ti_yong is not None, "No ti_yong")
check("Interp.Sections", len(report.sections)>=2, f"Only {len(report.sections)} sections")
print(f"  OK: {len(report.sections)} sections, ti_yong+vernacular present")

# 5. Bazi
print("[5/8] Bazi System...")
from src.bazi import quick_bazi
bazi = quick_bazi(1990,5,15,8,"男")
check("Bazi.Pillars", bazi.get_four_pillars_str()!="", "Empty")
check("Bazi.Dayun", len(bazi.dayun)>=8, f"Dayun: {len(bazi.dayun)}")
for p in [bazi.year,bazi.month,bazi.day,bazi.hour]:
    check(f"Bazi.{p.name}", p.naying and p.shishen, f"Missing naying/shishen")

from knowledge.bazi import get_day_master_vernacular, get_pattern_vernacular, get_dayun_template, SHISHEN_DATABASE, PATTERN_DATABASE, TIAOHOU_RULES
check("Bazi.SS", len(SHISHEN_DATABASE)==10, f"SS: {len(SHISHEN_DATABASE)}")
check("Bazi.PT", len(PATTERN_DATABASE)>=10, f"PT: {len(PATTERN_DATABASE)}")
check("Bazi.TH", len(TIAOHOU_RULES)==10, f"TH: {len(TIAOHOU_RULES)}")
for gan in ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]:
    check(f"Bazi.DM.{gan}", get_day_master_vernacular(gan) and 'advice' in get_day_master_vernacular(gan), f"No vernacular for {gan}")
check("Bazi.PV", get_pattern_vernacular("正官格") and len(get_pattern_vernacular("正官格"))>10, "No pattern vernacular")
check("Bazi.DT", len(get_dayun_template("财星运"))>10, "No dayun template")
print(f"  OK: {len(SHISHEN_DATABASE)} shishen, {len(PATTERN_DATABASE)} patterns, 10 DM all vernacular")

# 6. Ziwei
print("[6/8] Ziwei System...")
from src.ziwei import paipan_ziwei
zw = paipan_ziwei(__import__('datetime').datetime(1990,5,15,8,0),"男")
check("Ziwei.Gongs", len(zw.gongs)==12, f"Gongs: {len(zw.gongs)}")
total_stars = sum(len(g.main_stars) for g in zw.gongs)
check("Ziwei.Stars", total_stars==14, f"Stars: {total_stars}")
check("Ziwei.Sihua", len(zw.sihua_map)==4, f"Sihua: {len(zw.sihua_map)}")

from knowledge.ziwei import get_star_vernacular, get_gong_vernacular, get_sihua_vernacular
for star in ["紫微","天机","太阳","武曲","天同","廉贞","天府","太阴","贪狼","巨门","天相","天梁","七杀","破军"]:
    check(f"Ziwei.Star.{star}", get_star_vernacular(star) and 'summary' in get_star_vernacular(star), f"No vernacular for {star}")
for gong in ["命宫","财帛宫","官禄宫","夫妻宫"]:
    check(f"Ziwei.Gong.{gong}", get_gong_vernacular(gong) and len(get_gong_vernacular(gong))>10, f"No vernacular for {gong}")
for sh in ["化禄","化权","化科","化忌"]:
    check(f"Ziwei.Sihua.{sh}", len(get_sihua_vernacular(sh))>5, f"No vernacular for {sh}")
print(f"  OK: {total_stars} stars, 14+4+4 vernacular all present")

# 7. Knowledge + Reasoning
print("[7/8] Knowledge + Reasoning...")
from knowledge.meihua import WANWU_LEIXIANG, get_trigram_image
from knowledge.yizhuan import analyze_by_yizhuan
from reasoning_engine import divine
from rule_engine import get_rule_engine
check("Meihua", len(WANWU_LEIXIANG)==8, f"Meihua: {len(WANWU_LEIXIANG)}")
check("Meihua.Image", get_trigram_image('111') is not None, "No trigram image")
check("Yizhuan", analyze_by_yizhuan('111111').yinyang is not None, "No yinyang")
rep = divine('100010',[1],'事业')
check("Reasoning.Steps", len(rep.reasoning_chain)>=5, f"Steps: {len(rep.reasoning_chain)}")
check("Reasoning.Conf", 0<=rep.overall_confidence<=1, f"Conf: {rep.overall_confidence}")
re = get_rule_engine()
check("RuleEngine", len(re.list_all())>=10 and len(re.get_critical_rules())>=4, "Rules insufficient")
print(f"  OK: {len(WANWU_LEIXIANG)} trigrams, {len(rep.reasoning_chain)} reasoning steps, {len(re.list_all())} rules")

# 8. Fusion
print("[8/8] Fusion Engine...")
from fusion_engine import generate_fusion_report, WuxingUnified
profile = generate_fusion_report('111111','甲',{'木':5,'火':2,'土':1,'金':1,'水':1},'木','正官格','紫微')
check("Fusion.Profile", profile.get("bazi_daymaster","")!="", "No bazi")
check("Fusion.Insights", len(profile.get("insights",[]))>=3, f"Insights: {len(profile.get('insights',[]))}")
wxb = WuxingUnified.check_balance({'木':5,'火':2,'土':1,'金':1,'水':1})
check("Fusion.Wuxing", wxb and 'ratios' in wxb, "No wuxing balance")
print(f"  OK: {len(profile.get('insights',[]))} insights, wuxing balance working")

# Summary
print("\n" + "="*50)
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors: print(f"  ❌ {e}")
else:
    print("✅ ZERO ERRORS - ALL SYSTEMS GO")
if warnings:
    for w in warnings: print(f"  ⚠️ {w}")
print("="*50)

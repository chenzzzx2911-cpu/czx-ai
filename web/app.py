"""
AI东方命理平台 - 单文件多页面 (session_state切换)
"""

import streamlit as st
import sys, random
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
from src.data import get_db
from src.interpretation.vernacular import get_vernacular

st.set_page_config(
    page_title="AI命理平台",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AI东方命理平台 - 周易/八字/紫微/融合推理"
    }
)
# PWA meta injection
st.markdown("""
<link rel="manifest" href="/static/manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="命理平台">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/static/service-worker.js')}
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&display=swap');
html,body,[class*="css"]{font-family:'Noto Serif SC','SimSun',serif;background:linear-gradient(135deg,#0a0a1a 0%,#1a1a2e 100%);color:#e0d5c1}
.system-card{border:1px solid #333;border-radius:16px;padding:1.5rem;text-align:center;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);transition:all 0.3s;min-height:240px;cursor:pointer}
.system-card:hover{border-color:#D4A017;box-shadow:0 0 30px rgba(212,160,23,0.2);transform:translateY(-2px)}
.report-box{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);border:1px solid #D4A017;border-radius:12px;padding:1.5rem;margin:1rem 0;color:#e0d5c1}
.hexagram-symbol{font-size:4rem;text-align:center;margin:0.3rem 0}
.hexagram-name{font-size:1.5rem;text-align:center;font-weight:700}
.yao-line{padding:0.4rem 0.8rem;margin:0.2rem 0;border-radius:4px;font-size:1rem}
.yao-yang{background:rgba(255,215,0,0.15);border-left:3px solid #FFD700}
.yao-yin{background:rgba(100,100,100,0.15);border-left:3px solid #666}
.yao-changing{border-right:3px solid #FF4500;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.7}}
.keyword-tag{display:inline-block;background:rgba(212,160,23,0.2);border:1px solid #D4A017;border-radius:20px;padding:0.1rem 0.6rem;margin:0.1rem;font-size:0.8rem;color:#D4A017}
/* 手机适配 */
@media (max-width:768px){
  .system-card{min-height:auto;padding:1rem;margin-bottom:0.5rem}
  .hexagram-symbol{font-size:3rem}
  .hexagram-name{font-size:1.2rem}
  .report-box{padding:1rem}
  h1{font-size:1.8rem!important}
  h2{font-size:1.3rem!important}
  .stButton>button{font-size:1rem!important;padding:0.4rem 1rem!important}
}
/* 桌面按钮 */
.stButton>button{background:linear-gradient(135deg,#8B0000,#B22222);color:white;border:1px solid #D4A017;border-radius:8px;font-size:1rem;padding:0.4rem 1.2rem;transition:all 0.3s}
.stButton>button:hover{border-color:#FFD700;box-shadow:0 0 20px rgba(255,215,0,0.3)}
/* 导航按钮 */
div[data-testid="stHorizontalBlock"] button{font-size:0.9rem;padding:0.3rem 0.6rem}
/* 卡片文字 */
@media (max-width:768px){div[data-testid="column"]{flex:1 1 100%!important;max-width:100%!important}}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_db(): return get_db()

#页面状态管理
if "app_page" not in st.session_state:
    st.session_state["app_page"] = "home"

def go(page):
    st.session_state["app_page"] = page
    st.rerun()

#导航栏
cols_nav = st.columns([1,1,1,1,1,2])
with cols_nav[0]:
    if st.button("🏛️ 首页", use_container_width=True): go("home")
with cols_nav[1]:
    if st.button("☯️ 周易", use_container_width=True): go("iching")
with cols_nav[2]:
    if st.button("📊 八字", use_container_width=True): go("bazi")
with cols_nav[3]:
    if st.button("🔮 紫微", use_container_width=True): go("ziwei")
with cols_nav[4]:
    if st.button("🧬 分析", use_container_width=True): go("fusion")

# 公共变量
HOUR_NAMES = ["子时","丑时","寅时","卯时","辰时","巳时","午时","未时","申时","酉时","戌时","亥时"]

st.markdown("---")

page = st.session_state["app_page"]

# ══════════════════════════════════════════
# HOME
# ══════════════════════════════════════════
if page == "home":
    st.markdown('<h1 style="text-align:center;font-size:3rem;font-weight:900;color:#D4A017">🏛️ AI 东方命理平台</h1>',unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#888">周易占卜 · 八字命理 · 紫微斗数 · AI融合推理</p>',unsafe_allow_html=True)
    st.markdown("---")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown('<div class="system-card"><div style="font-size:4rem">☯️</div><div style="font-size:1.5rem;font-weight:700;color:#D4A017">周易占卜</div><div style="color:#999;font-size:0.9rem">金钱卦·时间卦·数字卦<br>64卦白话·纳甲·万物类象<br>体用生克·应期推算</div><div style="color:#0c0;font-size:0.8rem;margin-top:0.5rem">Phase 1 ✅</div></div>',unsafe_allow_html=True)
        if st.button("进入 →", key="home_iching", use_container_width=True): go("iching")
    with c2:
        st.markdown('<div class="system-card"><div style="font-size:4rem">📊</div><div style="font-size:1.5rem;font-weight:700;color:#D4A017">八字命理</div><div style="color:#999;font-size:0.9rem">四柱·十神·纳音藏干<br>格局·用神·大运流年<br>10日主白话解读</div><div style="color:#0c0;font-size:0.8rem;margin-top:0.5rem">Phase 2 ✅</div></div>',unsafe_allow_html=True)
        if st.button("进入 →", key="home_bazi", use_container_width=True): go("bazi")
    with c3:
        st.markdown('<div class="system-card"><div style="font-size:4rem">🔮</div><div style="font-size:1.5rem;font-weight:700;color:#D4A017">紫微斗数</div><div style="color:#999;font-size:0.9rem">十二宫·十四主星<br>四化飞星·宫位分析<br>命宫深度解读</div><div style="color:#0c0;font-size:0.8rem;margin-top:0.5rem">Phase 3 ✅</div></div>',unsafe_allow_html=True)
        if st.button("进入 →", key="home_ziwei", use_container_width=True): go("ziwei")
    with c4:
        st.markdown('<div class="system-card"><div style="font-size:4rem">🧬</div><div style="font-size:1.5rem;font-weight:700;color:#D4A017">综合分析</div><div style="color:#999;font-size:0.9rem">三系统统一融合<br>冲突检测·置信度<br>四领域深度画像</div><div style="color:#0c0;font-size:0.8rem;margin-top:0.5rem">Phase 5 ✅</div></div>',unsafe_allow_html=True)
        if st.button("进入 →", key="home_fusion", use_container_width=True): go("fusion")

    st.markdown("---")
    st.markdown("### 💬 命理问答")
    st.caption("用白话提问，AI从周易·八字·紫微知识库中检索答案")
    ai_q = st.text_input("提问", placeholder="例如: 甲木命人适合做什么工作？乾卦是什么意思？命宫紫微的人性格如何？", key="ai_question", label_visibility="collapsed")
    if ai_q:
        with st.spinner("检索中..."):
            from knowledge.bazi import get_day_master_vernacular, get_pattern_vernacular, get_day_pillar_info
            from knowledge.ziwei import get_star_vernacular
            from src.interpretation.vernacular import get_vernacular as gzv
            from fusion_engine import _wx_trait, _wx_career, _dm_personality

            response = []
            matched = False

            # 1. 日主+命
            for gan, wx in [("甲","木"),("乙","木"),("丙","火"),("丁","火"),("戊","土"),("己","土"),("庚","金"),("辛","金"),("壬","水"),("癸","水")]:
                if gan in ai_q and ("命" in ai_q or "人" in ai_q):
                    dmv = get_day_master_vernacular(gan)
                    if dmv:
                        nm = gan + wx + "命人"
                        response.append(f"## {nm}")
                        response.append(dmv.get('nature',''))
                        response.append("**优势**: " + dmv.get('strength',''))
                        response.append("**注意**: " + dmv.get('weakness',''))
                        if "事业" in ai_q or "工作" in ai_q or "适合" in ai_q:
                            response.append("**事业**: " + dmv.get('advice',{}).get('事业',''))
                        if "感情" in ai_q or "恋爱" in ai_q or "婚姻" in ai_q:
                            response.append("**感情**: " + dmv.get('advice',{}).get('感情',''))
                        if "健康" in ai_q:
                            response.append("**健康**: " + dmv.get('advice',{}).get('健康',''))
                        if "财" in ai_q or "钱" in ai_q:
                            response.append("**财运**: " + dmv.get('advice',{}).get('财运',''))
                    matched = True; break

            # 2. 五行属性
            if not matched:
                for wx in ["木","火","土","金","水"]:
                    if wx in ai_q and ("属性" in ai_q or "适合" in ai_q or "特点" in ai_q or "行业" in ai_q):
                        response.append(f"## 五行属{wx}")
                        response.append("**特质**: " + _wx_trait(wx))
                        response.append("**适合行业**: " + _wx_career(wx))
                        matched = True; break

            # 3. 卦名查询
            if not matched:
                for h in db.all_hexagrams():
                    if h.name in ai_q:
                        v = gzv(h.binary)
                        response.append(f"## {h.symbol} {h.name}卦")
                        response.append(v.get('summary',''))
                        if v.get('life_advice'):
                            for d,dn in [("事业","💼"),("感情","💕"),("健康","🏥"),("财运","💰")]:
                                response.append(f"{dn}: " + v['life_advice'].get(d,'')[:80])
                        if v.get('life_lesson'): response.append("**启示**: " + v['life_lesson'])
                        matched = True; break

            # 4. 紫微主星
            if not matched:
                for star in ["紫微","天机","太阳","武曲","天同","廉贞","天府","太阴","贪狼","巨门","天相","天梁","七杀","破军"]:
                    if star in ai_q:
                        sv = get_star_vernacular(star)
                        if sv:
                            response.append(f"## 命宫{star}")
                            response.append(sv.get('summary',''))
                            response.append("**优势**: " + sv.get('trait',''))
                            response.append("**注意**: " + sv.get('weakness',''))
                        matched = True; break

            # 5. 格局查询
            if not matched:
                for pat in ["正官格","七杀格","正财格","偏财格","正印格","偏印格","食神格","伤官格"]:
                    if pat.replace('格','') in ai_q:
                        pv = get_pattern_vernacular(pat)
                        if pv:
                            response.append(f"## {pat}")
                            response.append(pv)
                        matched = True; break

            if response:
                for r in response:
                    st.markdown(r)
            else:
                st.info("试试: '甲木命人特点' / '五行属火适合什么工作' / '乾卦是什么意思' / '紫微坐命的人性格' / '正官格'")

    st.caption("基于《周易》《渊海子平》《三命通会》《滴天髓》《紫微斗数全书》等经典·结构化推理系统")

    with st.expander("📱 手机端安装指南"):
        st.markdown("""
        **添加到手机桌面（像App一样用）**
        - iPhone: Safari打开 → 点分享按钮 → 「添加到主屏幕」
        - Android: Chrome打开 → 点右上角菜单 → 「添加到主屏幕」
        - 添加后桌面出现🏛️图标，全屏使用
        **局域网访问**（电脑手机同WiFi）: http://10.151.97.139:8504
        """)

    st.caption("基于《周易》《渊海子平》《三命通会》《滴天髓》《紫微斗数全书》等经典·结构化推理系统")

# ══════════════════════════════════════════
# ICHING
# ══════════════════════════════════════════
elif page == "iching":
    from src.casting import money_casting, time_casting, number_casting, random_casting
    from src.interpretation import interpret_cast

    st.markdown('<h1 style="text-align:center;font-size:2.5rem;font-weight:900;color:#D4A017">☯️ 周易占卜</h1>',unsafe_allow_html=True)
    mode = st.radio("模式", ["🔮 起卦占卜", "📚 浏览六十四卦"], horizontal=True, label_visibility="collapsed")
    db = load_db()

    if mode == "🔮 起卦占卜":
        st.caption("静心、观想、起卦、解卦")
        st.markdown("### ❶ 起卦方式")
        method = st.radio("方式", ["🪙 金钱卦","🕐 时间卦","🔢 数字卦","🎲 随缘一卦"], horizontal=True, label_visibility="collapsed", index=None)
        num1=num2=num3=0; time_date=None; time_hour=None
        if method == "🔢 数字卦":
            c1,c2,c3=st.columns(3)
            with c1: num1=st.number_input("第一个数",value=1,step=1,min_value=1)
            with c2: num2=st.number_input("第二个数",value=0,step=1,min_value=0)
            with c3: num3=st.number_input("第三个数",value=0,step=1,min_value=0)
        if method == "🕐 时间卦":
            tc1,tc2=st.columns(2)
            with tc1: time_date=st.date_input("日期",value=datetime.today())
            with tc2: time_hour=st.slider("时辰 0-23",0,23,datetime.now().hour)
            st.caption(f"{HOUR_NAMES[((time_hour+1)//2)%12]}时")

        st.markdown("### ❷ 起卦")
        if method == "🪙 金钱卦":
            st.markdown("**三枚铜钱，抛掷六次。**")
            if "coin_tosses" not in st.session_state: st.session_state["coin_tosses"]=[]
            if "coin_step" not in st.session_state: st.session_state["coin_step"]=0
            tosses=st.session_state["coin_tosses"]; step=st.session_state["coin_step"]
            if tosses:
                for i,h in enumerate(tosses):
                    pn={0:"初",1:"二",2:"三",3:"四",4:"五",5:"上"}[i]
                    rn={3:"三个正面(老阳○)",2:"两正一反(少阳)",1:"一正二反(少阴)",0:"三个反面(老阴×)"}
                    yang=h in (3,2); bar=("━━━━━" if yang else "━━ ╌╌")+(" ○" if h==3 else " ×" if h==0 else "")
                    st.markdown(f"第{i+1}次({pn}爻): {bar} — {rn[h]}")
            if step < 6:
                st.markdown(f"### 🪙 第{step+1}次（{'初'if step==0 else'二'if step==1 else'三'if step==2 else'四'if step==3 else'五'if step==4 else'上'}爻）")
                cc1,cc2,cc3,cc4=st.columns(4)
                with cc1:
                    if st.button("三个正面\n(老阳○)",use_container_width=True,key="tc3"): st.session_state["coin_tosses"].append(3); st.session_state["coin_step"]+=1; st.rerun()
                with cc2:
                    if st.button("两正一反\n(少阳)",use_container_width=True,key="tc2"): st.session_state["coin_tosses"].append(2); st.session_state["coin_step"]+=1; st.rerun()
                with cc3:
                    if st.button("一正二反\n(少阴)",use_container_width=True,key="tc1"): st.session_state["coin_tosses"].append(1); st.session_state["coin_step"]+=1; st.rerun()
                with cc4:
                    if st.button("三个反面\n(老阴×)",use_container_width=True,key="tc0"): st.session_state["coin_tosses"].append(0); st.session_state["coin_step"]+=1; st.rerun()
                if st.button("🎲 自动摇卦",use_container_width=True):
                    st.session_state["coin_tosses"]=[sum(1 for _ in range(3) if random.random()>0.5) for _ in range(6)]
                    st.session_state["coin_step"]=6; st.rerun()
            if st.session_state["coin_step"]>=6:
                cr=money_casting(st.session_state["coin_tosses"][:6])
                st.session_state["cr"]=cr; st.session_state.pop("coin_tosses",None); st.session_state.pop("coin_step",None); st.rerun()

        elif method and method!="🪙 金钱卦":
            if st.button("🔮 起卦",type="primary",use_container_width=True):
                with st.spinner("推演中..."):
                    if method=="🕐 时间卦":
                        dt=datetime(time_date.year,time_date.month,time_date.day,time_hour,0) if time_date else datetime.now()
                        cr=time_casting(dt)
                    elif method=="🔢 数字卦":
                        if num1==0 and num2==0 and num3==0: st.warning("请输入数字"); st.stop()
                        cr=number_casting(num1,num2,num3)
                    else: cr=random_casting()
                    st.session_state["cr"]=cr; st.rerun()

        if "cr" in st.session_state:
            cr=st.session_state["cr"]; h=db.get(cr.original_binary)
            ch=db.get(cr.changed_binary) if cr.changing_lines else None
            v=get_vernacular(cr.original_binary) if h else {}

            if hasattr(cr,'calc_detail') and cr.calc_detail:
                with st.expander("🧮 推算过程"):
                    cd=cr.calc_detail
                    for k in ['year_branch_name','month','day','hour_branch_name','upper_formula','lower_formula','moving_formula']:
                        if k in cd: st.markdown(f"{cd[k]}")

            st.markdown("---"); st.markdown("### ☯ 卦象")
            _,gc,_=st.columns([1,2,1])
            with gc:
                st.markdown('<div class="report-box">',unsafe_allow_html=True)
                if h:
                    st.markdown(f'<div class="hexagram-symbol">{h.symbol}</div>',unsafe_allow_html=True)
                    st.markdown(f'<div class="hexagram-name">{h.name}卦 · 第{h.id}卦</div>',unsafe_allow_html=True)
                    st.markdown(f"**卦辞**: {h.gua_ci}")
                    if v.get('vernacular_gua_ci'): st.caption(v['vernacular_gua_ci'])
                    if v.get('keywords'): st.markdown(" ".join([f'<span class="keyword-tag">{k}</span>' for k in v['keywords']]),unsafe_allow_html=True)
                st.markdown("**六爻**")
                for ld in cr.lines_detail:
                    yang=ld["value"] in (9,7); chg=ld["is_changing"]
                    cls="yao-line "+("yao-yang" if yang else "yao-yin")+(" yao-changing" if chg else "")
                    bar=("━━━━━" if yang else "━━ ╌╌")+(" ○" if chg and yang else " ×" if chg else "")
                    st.markdown(f'<div class="{cls}">{ld["name"]}: {bar} — {ld["desc"]}</div>',unsafe_allow_html=True)
                if cr.changing_lines:
                    st.markdown(f"⚡ **变爻**: 第{', '.join(str(p) for p in cr.changing_lines)}爻")
                    if ch and ch.binary!=h.binary: st.markdown(f"→ **变卦**: {ch.symbol} {ch.name}卦")
                st.markdown("</div>",unsafe_allow_html=True)

            st.markdown("---"); st.markdown("### ❸ 解读")
            if st.button("📜 展开完整解读",type="primary",use_container_width=True):
                with st.spinner("解读中..."):
                    report=interpret_cast(cr)
                    if report.vernacular:
                        st.markdown(f"## 📖 白话解读"); st.markdown(f"**{report.vernacular.get('summary','')}**")
                        advice=report.vernacular.get('life_advice',{})
                        if advice:
                            tabs=st.tabs(["💼 事业","💕 感情","🏥 健康","💰 财运"])
                            with tabs[0]: st.markdown(advice.get('事业',''))
                            with tabs[1]: st.markdown(advice.get('感情',''))
                            with tabs[2]: st.markdown(advice.get('健康',''))
                            with tabs[3]: st.markdown(advice.get('财运',''))
                        if report.vernacular.get('life_lesson'): st.info(f"💡 {report.vernacular['life_lesson']}")
                    if report.ti_yong:
                        ty=report.ti_yong; rel=ty.get("relation",{}); level=rel.get("level",0)
                        lt={3:"大吉",2:"吉",1:"小吉",-1:"小凶",-2:"大凶"}.get(level,"平")
                        st.markdown("---"); st.markdown("## ⚖️ 体用生克")
                        ct,cm,cy=st.columns(3)
                        with ct: st.metric("体卦(你)",f"{ty.get('ti_name','?')}({ty.get('ti_wuxing','?')})")
                        with cm: st.metric("关系",rel.get("relation","?"),delta=lt)
                        with cy: st.metric("用卦(事)",f"{ty.get('yong_name','?')}({ty.get('yong_wuxing','?')})")
                        st.info(rel.get("meaning",""))
                    for sec in report.sections:
                        with st.expander(sec.title):
                            st.markdown(sec.content)
                            if sec.source: st.caption(f"📚 {sec.source}")
                    if report.summary:
                        st.markdown("---"); st.markdown("## 📜 综合判语"); st.markdown(report.summary)
                    #增强分析
                    from knowledge.liuyao import install_najia
                    from knowledge.meihua import get_trigram_image, calculate_yingqi_meihua
                    from knowledge.yizhuan import analyze_by_yizhuan
                    with st.expander("🔮 六爻纳甲装卦"):
                        try:
                            najia=install_najia(cr.original_binary,cr.changing_lines)
                            for y in najia.yao_list:
                                chg="⚡" if y.is_changing else "  "; ss="世" if y.shi_ying=="世" else "应" if y.shi_ying=="应" else ""
                                st.markdown(f"- {chg}{y.position}爻:{y.tian_gan}{y.di_zhi}({y.wuxing}) {y.liu_qin} {y.liu_shen} {ss}")
                        except: st.caption("暂不可用")
                    with st.expander("🌿 万物类象"):
                        ui=get_trigram_image(cr.original_binary[:3]); li=get_trigram_image(cr.original_binary[3:])
                        if ui and li: st.markdown(f"上{ui.name}:{','.join(ui.modern[:5])} | 下{li.name}:{','.join(li.modern[:5])}")
                    with st.expander("📖 易传哲学"):
                        yz=analyze_by_yizhuan(cr.original_binary,cr.changing_lines)
                        st.markdown(f"{yz.yinyang.interpretation} | {yz.gangrou['nature']} | {yz.shiwei_assessment['name']}")
                    with st.expander("⏰ 应期推算"):
                        try:
                            yq=calculate_yingqi_meihua(ty.get('ti_wuxing','金') if report.ti_yong else '金')
                            st.markdown(f"{yq['estimated_period']}(置信{yq['confidence']:.0%})")
                        except: st.caption("暂不可用")
                    #综合总结
                    st.markdown("---"); st.markdown("## 📜 综合总结")
                    if report.vernacular:
                        vv=report.vernacular; lesson=vv.get('life_lesson','')
                        st.markdown(f"**{report.original_hexagram.symbol} {report.original_hexagram.name}卦**——{vv.get('summary','')}")
                        if report.ti_yong:
                            rr=report.ti_yong.get('relation',{})
                            st.markdown(f"体用: **{rr.get('relation','?')}**——{rr.get('meaning','')}")
                        st.success(f"💡 {lesson}")
                    st.caption("⚠️ 以上解读仅供参考。")

    else:
        st.caption("六十四卦全览")
        sc,fc=st.columns([2,1])
        with sc: search=st.text_input("🔍 搜索")
        with fc: wf=st.selectbox("五行",["全部","金","水","木","火","土"])
        all_hex=db.all_hexagrams()
        if search:
            matched=[]
            for h in all_hex:
                v=get_vernacular(h.binary)
                if search in h.name or search in h.gua_ci or search in " ".join(v.get("keywords",[])): matched.append(h)
            all_hex=matched
        if wf!="全部": all_hex=[h for h in all_hex if h.upper_wuxing==wf or h.lower_wuxing==wf]
        st.markdown(f"共 **{len(all_hex)}** 卦")
        cols=st.columns(8)
        for i,h in enumerate(all_hex):
            with cols[i%8]:
                st.markdown(f'<div style="background:#1a1a2e;border:1px solid #444;border-radius:8px;padding:0.5rem;text-align:center"><div style="font-size:2rem">{h.symbol}</div><div style="color:#D4A017;font-weight:700">{h.name}</div></div>',unsafe_allow_html=True)
                if st.button("查看",key=f"v_{h.id}",use_container_width=True): st.session_state["view_hex"]=h
        if "view_hex" in st.session_state:
            h=st.session_state["view_hex"]; v=get_vernacular(h.binary)
            st.markdown("---"); st.markdown(f"## {h.symbol} {h.name}卦 · 第{h.id}卦")
            t1,t2=st.tabs(["📖 白话","📜 原文"])
            with t1:
                st.markdown(f"**{v.get('summary','')}**")
                advice=v.get('life_advice',{})
                if advice:
                    ac1,ac2=st.columns(2)
                    with ac1: st.markdown("💼 事业"); st.markdown(advice.get('事业','')); st.markdown("🏥 健康"); st.markdown(advice.get('健康',''))
                    with ac2: st.markdown("💕 感情"); st.markdown(advice.get('感情','')); st.markdown("💰 财运"); st.markdown(advice.get('财运',''))
                if v.get('life_lesson'): st.info(f"💡 {v['life_lesson']}")
            with t2:
                st.markdown(f"**卦辞**: {h.gua_ci}\n**《彖》**: {h.tuan_ci}\n**《象》**: {h.da_xiang_ci}")
                for yao in h.yao_lines: st.markdown(f"- **{yao.type_str}**: {yao.text}")

# ══════════════════════════════════════════
# BAZI
# ══════════════════════════════════════════
elif page == "bazi":
    from src.bazi import paipan as bazi_paipan
    from knowledge.bazi import get_day_master_vernacular, get_pattern_vernacular, get_dayun_template

    st.markdown('<h1 style="text-align:center;font-size:2.5rem;font-weight:900;color:#D4A017">📊 八字命理</h1>',unsafe_allow_html=True)
    st.caption("子平法八字排盘 · 四柱十神 · 格局用神 · 大运流年")

    c1,c2,c3=st.columns([1,1,1])
    with c1: name=st.text_input("姓名",value="",key="bz_name")
    with c2: gender=st.selectbox("性别",["男","女"],key="bz_gender")
    with c3: bdate=st.date_input("出生日期",value=datetime(1990,1,1),min_value=datetime(1900,1,1),max_value=datetime.today(),key="bz_date")
    bhour=st.slider("出生时辰 (0-23)",0,23,8,key="bz_hour")
    st.caption(f"{HOUR_NAMES[((bhour+1)//2)%12]}时")

    if st.button("🔮 排盘分析",type="primary",use_container_width=True):
        dt=datetime(bdate.year,bdate.month,bdate.day,bhour,0)
        chart=bazi_paipan(dt,gender,name or "匿名")
        st.markdown("---"); st.markdown("## 📋 八字命盘")
        pillars=[("年柱",chart.year),("月柱",chart.month),("日柱",chart.day),("时柱",chart.hour)]
        cols=st.columns(4)
        for i,(pn,p) in enumerate(pillars):
            with cols[i]:
                st.markdown(f"**{pn}**"); st.markdown(f"# {p.tian_gan}{p.di_zhi}")
                st.caption(f"纳音:{p.naying} | 十神:{p.shishen}")
                st.caption(f"藏干:{' '.join([g for g,_ in p.cang_gan])}")
        # 日柱详解（60甲子）
        from knowledge.bazi import get_day_pillar_info as gdpi
        day_gz = chart.day.tian_gan + chart.day.di_zhi
        dp_info = gdpi(day_gz)
        if dp_info:
            with st.expander(f"📖 日柱详解 — {day_gz}日"):
                st.markdown(f"**{dp_info.get('summary','')}**")
                st.markdown(f"💼 事业: {dp_info.get('career','')}")
                st.markdown(f"💕 感情: {dp_info.get('love','')}")
                st.markdown(f"🏥 健康: {dp_info.get('health','')}")
        st.markdown("---")
        cd1,cd2,cd3=st.columns(3)
        with cd1: st.metric("日主",f"{chart.day_master}({chart.day_master_wuxing})")
        tw=max(sum(chart.wuxing_count.values()),1)
        with cd2: st.metric("日主占比",f"{chart.wuxing_count.get(chart.day_master_wuxing,0)/tw:.0%}")
        with cd3: st.metric("五行总计",f"{sum(chart.wuxing_count.values()):.1f}")
        st.markdown("### 🎨 五行统计")
        wx_cols=st.columns(5)
        for i,(wx,emoji) in enumerate([("木","🌿"),("火","🔥"),("土","🏔"),("金","💎"),("水","💧")]):
            with wx_cols[i]: c=chart.wuxing_count.get(wx,0); st.metric(f"{emoji}{wx}",f"{c:.1f}"); st.progress(min(c/tw,1.0))
        dm_v=get_day_master_vernacular(chart.day_master)
        if dm_v:
            st.markdown("---"); st.markdown(f"## 👤 日主解读 — {chart.day_master}命")
            st.markdown(f"**{dm_v.get('nature','')}**")
            st.markdown(f"✅ {dm_v.get('strength','')}"); st.markdown(f"⚠️ {dm_v.get('weakness','')}")
            adv=dm_v.get('advice',{})
            if adv:
                tabs=st.tabs(["💼 事业","💕 感情","🏥 健康","💰 财运"])
                with tabs[0]: st.markdown(adv.get('事业',''))
                with tabs[1]: st.markdown(adv.get('感情',''))
                with tabs[2]: st.markdown(adv.get('健康',''))
                with tabs[3]: st.markdown(adv.get('财运',''))
        st.markdown("---"); st.markdown("## 🏛️ 格局分析")
        if chart.patterns:
            for pat in chart.patterns:
                pv=get_pattern_vernacular(pat['name'])
                if pv: st.markdown(f"### {pat['name']}"); st.markdown(pv)
                else: st.markdown(f"- **{pat['name']}**")
        else: st.info("未识别出明显格局")
        st.markdown("---"); st.markdown("## 💎 用神分析")
        ys=chart.yong_shen
        cy1,cy2=st.columns(2)
        with cy1: st.metric("推荐五行",ys['recommended_wuxing']); st.caption(ys['strategy'])
        with cy2: st.metric("旺衰",ys['level'])
        ys_exp={"木":"多接触自然/读书/绿色·东·春","火":"多社交表达/红色·南·夏","土":"脚踏实地/黄色·中·四季末","金":"果断竞争/白色·西·秋","水":"灵活学习/黑色·北·冬"}
        if ys.get('recommended_wuxing','') in ys_exp: st.info(f"用神为{ys['recommended_wuxing']}——{ys_exp[ys['recommended_wuxing']]}")
        st.markdown("---"); st.markdown("## 🚀 大运流年")
        dy_cols=st.columns(4)
        for i,dy in enumerate(chart.dayun[:8]):
            with dy_cols[i%4]:
                sc={"正官":"官杀运","七杀":"官杀运","正财":"财星运","偏财":"财星运","正印":"印星运","偏印":"印星运","食神":"食伤运","伤官":"食伤运","比肩":"比劫运","劫财":"比劫运"}.get(dy['shishen'],"平稳运")
                st.markdown(f"**{dy['period']}**"); st.markdown(f"### {dy['ganzhi']}"); st.caption(f"{dy['wuxing']}|{dy['shishen']}")
                with st.expander("解读"): st.caption(get_dayun_template(sc))
        st.markdown("---"); st.markdown("## 📜 综合总结")
        mp=chart.patterns[0]['name'] if chart.patterns else "普通格局"
        ys_wx=chart.yong_shen.get('recommended_wuxing','')
        cur_dy=chart.dayun[0] if chart.dayun else None
        parts=[f"**{chart.name}**，日主**{chart.day_master}命**，格局**{mp}**，用神**{ys_wx}**。"]
        if cur_dy: parts.append(f"当前大运{cur_dy['period']}({cur_dy['ganzhi']})。")
        wx_map={"木":"仁慈向上","火":"热情大方","土":"诚信稳重","金":"果断刚毅","水":"智慧变通"}
        parts.append(f"核心特质: **{wx_map.get(chart.day_master_wuxing,'')}**。")
        st.markdown(" ".join(parts))
        st.success(f"💡 {chart.name}是{chart.day_master}命人——八字决定底色，选择决定高度。")
    st.caption("八字命理基于《渊海子平》《三命通会》等经典，仅供研究参考。")

# ══════════════════════════════════════════
# ZIWEI
# ══════════════════════════════════════════
elif page == "ziwei":
    from src.ziwei import paipan_ziwei, MAIN_STAR_MEANINGS, SIHUA_MEANINGS
    from knowledge.ziwei import get_star_vernacular, get_gong_vernacular, get_sihua_vernacular

    st.markdown('<h1 style="text-align:center;font-size:2.5rem;font-weight:900;color:#D4A017">🔮 紫微斗数</h1>',unsafe_allow_html=True)
    st.caption("十二宫命盘 · 十四主星 · 四化飞星 · 宫位分析")

    c1,c2,c3=st.columns([1,1,1])
    with c1: name=st.text_input("姓名",value="",key="zw_name")
    with c2: gender=st.selectbox("性别",["男","女"],key="zw_gender")
    with c3: bdate=st.date_input("出生日期",value=datetime(1990,1,1),min_value=datetime(1900,1,1),max_value=datetime.today(),key="zw_date")
    bhour=st.slider("出生时辰 (0-23)",0,23,8,key="zw_hour")
    st.caption(f"{HOUR_NAMES[((bhour+1)//2)%12]}时")

    if st.button("🔮 紫微排盘",type="primary",use_container_width=True):
        dt=datetime(bdate.year,bdate.month,bdate.day,bhour,0)
        chart=paipan_ziwei(dt,gender,name or "匿名")
        st.markdown("---"); st.markdown("## 📋 紫微命盘")
        st.caption(f"五行局: {chart.wuxing_ju_name} | 四化: {' '.join([f'{k}={v}' for k,v in chart.sihua_map.items()])}")
        for row in range(4):
            cols=st.columns(3)
            for ci in range(3):
                gi=row*3+ci; display_order=[0,5,10,3,8,1,6,11,4,9,2,7]
                if gi<12:
                    ix=display_order[gi]; gong=chart.gongs[ix]
                    with cols[ci]:
                        flags=[]
                        if gong.is_ming_gong: flags.append("👤命")
                        if gong.is_shen_gong: flags.append("🏠身")
                        st.markdown(f"**{gong.name}** {' '.join(flags)}")
                        st.markdown(f"*{gong.zhi}*")
                        if gong.main_stars:
                            for s in gong.main_stars:
                                clr="🟢" if s in ["紫微","天府","太阳"] else ("🔵" if s in ["天机","太阴","天同"] else "🟡")
                                st.markdown(f"{clr} {s}")
                        else: st.caption("—")
                        if gong.aux_stars:
                            st.caption("⭐ " + " ".join(gong.aux_stars))
                        if gong.sihua:
                            se={"化禄":"💰","化权":"⚡","化科":"📚","化忌":"⚠️"}; st.caption(f"{se.get(gong.sihua,'')} {gong.sihua}")
                        with st.expander("解读"):
                            gv=get_gong_vernacular(gong.name)
                            if gv: st.caption(gv)
                            for s in gong.main_stars[:2]:
                                sv=get_star_vernacular(s)
                                if sv: st.caption(f"{s}:{sv.get('summary','')[:60]}...")
                        st.markdown("---")
        st.markdown("---"); st.markdown("## 🔄 四化飞星")
        sh_cols=st.columns(4)
        for i,(stype,star) in enumerate(chart.sihua_map.items()):
            with sh_cols[i]:
                emoji={"化禄":"💰","化权":"⚡","化科":"📚","化忌":"⚠️"}
                st.markdown(f"### {emoji.get(stype,'')} {stype}"); st.markdown(f"**{star}**")
                sv=get_sihua_vernacular(stype); st.caption(sv if sv else SIHUA_MEANINGS.get(stype,""))
        st.markdown("---"); st.markdown("## 👤 命宫分析")
        mg=None
        for g in chart.gongs:
            if g.is_ming_gong: mg=g; break
        if mg:
            st.markdown(f"**命宫在{mg.zhi}**")
            if mg.main_stars:
                for s in mg.main_stars:
                    sv=get_star_vernacular(s)
                    if sv:
                        st.markdown(f"### {s}"); st.markdown(f"**{sv.get('summary','')}**")
                        st.markdown(f"✅ {sv.get('trait','')}"); st.markdown(f"⚠️ {sv.get('weakness','')}")
                        adv=sv.get('advice',{})
                        if adv:
                            tabs=st.tabs(["💼 事业","💕 感情","🏥 健康","💰 财运"])
                            with tabs[0]: st.markdown(adv.get('事业',''))
                            with tabs[1]: st.markdown(adv.get('感情',''))
                            with tabs[2]: st.markdown(adv.get('健康',''))
                            with tabs[3]: st.markdown(adv.get('财运',''))
            else: st.info("命宫无主星，借对宫(迁移宫)来看。")
        st.markdown("---"); st.markdown("## 📜 综合总结")
        if mg and mg.main_stars:
            ms=mg.main_stars[0]
            st_types={"紫微":"天生领袖","天府":"稳重可靠","太阳":"热情大方","武曲":"果断刚毅","天同":"温和有福","廉贞":"洞察力强","天机":"聪明灵活","太阴":"温柔细腻","贪狼":"多才多艺","巨门":"善于思考","天相":"公正善良","天梁":"智慧老成","七杀":"勇猛果断","破军":"创新敢为"}
            st.success(f"💡 命宫{ms}——{st_types.get(ms,'个性独特')}。命盘是地图，走路的是你自己。")
    st.caption("紫微斗数基于《紫微斗数全书》等经典，仅供研究参考。")

# ══════════════════════════════════════════
# FUSION
# ══════════════════════════════════════════
elif page == "fusion":
    from src.bazi import paipan as bazi_paipan
    from src.ziwei import paipan_ziwei
    from src.casting import time_casting, random_casting
    from fusion_engine import generate_fusion_report, WuxingUnified

    st.markdown('<h1 style="text-align:center;font-size:2.5rem;font-weight:900;color:#D4A017">🧬 综合分析</h1>',unsafe_allow_html=True)
    st.caption("周易+八字+紫微 · 三系统统一融合 · 冲突检测 · 置信度评分")

    st.markdown("### 输入基本信息")
    fc1,fc2,fc3=st.columns(3)
    with fc1: f_name=st.text_input("姓名",value="",key="fz_name")
    with fc2: f_gender=st.selectbox("性别",["男","女"],key="fz_gender")
    with fc3: f_date=st.date_input("出生日期",value=datetime(1990,1,1),min_value=datetime(1900,1,1),max_value=datetime.today(),key="fz_date")
    f_hour=st.slider("出生时辰 (0-23)",0,23,8,key="fz_hour")
    st.caption(f"{HOUR_NAMES[((f_hour+1)//2)%12]}时")
    st.markdown("---")
    f_method=st.radio("周易起卦",["🕐 时间卦","🎲 随机卦"],horizontal=True,key="fz_method")

    if st.button("🧬 生成融合报告",type="primary",use_container_width=True):
        with st.spinner("三系统交叉分析中..."):
            dt=datetime(f_date.year,f_date.month,f_date.day,f_hour,0)
            bazi_chart=bazi_paipan(dt,f_gender,f_name or "匿名")
            ziwei_chart=paipan_ziwei(dt,f_gender,f_name or "匿名")
            if f_method=="🕐 时间卦": iching_bin=time_casting(dt).original_binary
            else: iching_bin=random_casting().original_binary
            zw_star=""
            for g in ziwei_chart.gongs:
                if g.is_ming_gong and g.main_stars: zw_star=g.main_stars[0]; break
            if not zw_star: zw_star="无主星"
            bazi_pat=bazi_chart.patterns[0]['name'] if bazi_chart.patterns else "普通格"

            profile=generate_fusion_report(
                iching_binary=iching_bin,
                bazi_day_gan=bazi_chart.day_master,
                bazi_wx=bazi_chart.wuxing_count,
                bazi_ys=bazi_chart.yong_shen.get('recommended_wuxing','木'),
                bazi_pat=bazi_pat,
                ziwei_star=zw_star,
                name=f_name or "命主"
            )

            h=None
            try:
                db2=get_db(); h=db2.get(iching_bin)
            except: pass

            # ═══ 总览 ═══
            st.markdown("---"); st.markdown("## 🧬 三系统融合报告")
            st.markdown("### 📊 系统总览 · 三把钥匙")
            oc1,oc2,oc3=st.columns(3)
            with oc1: st.metric("☯️ 周易",f"{h.symbol} {h.name}卦" if h else "—",help="实时导航：当前情境下的策略指引")
            with oc2: st.metric("📊 八字",f"{profile['bazi_daymaster']}命·{profile['bazi_pattern']}",help="操作系统：你的底层性格和天赋")
            with oc3: st.metric("🔮 紫微",f"命宫{profile['ziwei_minggong_star']}",help="出厂设置：你天生擅长什么模式")

            # 五行平衡可视化
            st.markdown(f"**主导五行**: {profile['dominant_wuxing']} | **三系统一致性**: {profile['consistency_score']:.0%}")
            with st.expander("🎨 五行平衡详情"):
                wxb=WuxingUnified.check_balance(bazi_chart.wuxing_count)
                for wx,r in wxb.get('ratios',{}).items():
                    bar="█"*int(r*30)+"░"*(30-int(r*30))
                    st.markdown(f"**{wx}** {bar} {r:.0%}")
                st.caption(wxb.get('advice','五行平衡'))

            # 冲突检测
            if profile.get('conflicts'):
                st.markdown("---"); st.markdown("### ⚠️ 深层冲突检测")
                for c in profile['conflicts']:
                    sev_icon={"high":"🔴","medium":"🟡","low":"🟢"}.get(c.get('severity',''),"⚪")
                    st.warning(f"{sev_icon} **{c['type']}**: {c['detail']}")
            else: st.success("✅ 三系统高度一致，结论可信度较高。")

            # ═══ 分领域深度分析 ═══
            st.markdown("---"); st.markdown("## 🔍 四领域深度交叉分析")
            for ins in profile['insights']:
                with st.expander(f"{'💼' if ins.domain=='事业' else '💕' if ins.domain=='感情' else '🏥' if ins.domain=='健康' else '💰'} **{ins.domain}** · 三系统一致度{ins.agreement_score:.0%}", expanded=(ins.domain=="事业")):
                    # 共同指向
                    st.markdown(f"**🎯 共同指向**: {ins.common_thread}")
                    # 分歧
                    if ins.divergence:
                        st.caption(f"⚠️ {ins.divergence}")
                    # 深度融合（长篇）
                    st.markdown(ins.fused_interpretation)
                    # 行动建议
                    st.markdown("---")
                    sc1,sc2=st.columns(2)
                    with sc1: st.markdown(f"**⚡ 近期建议**: {ins.short_term}")
                    with sc2: st.markdown(f"**🌱 长期建议**: {ins.long_term}")
                    st.caption(f"置信度: {ins.confidence:.0%}")

            # ═══ 最终总结 ═══
            st.markdown("---"); st.markdown("## 📜 三维命理画像")
            st.markdown(profile['final_summary'])
    st.caption("融合引擎基于三系统统一知识图谱生成。仅供研究参考。")

st.markdown("---")
st.caption("🏛️ AI东方命理平台 · 结构化推理系统 · 非迷信 · 仅供研究参考")

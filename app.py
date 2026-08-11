import streamlit as st
import json
import pandas as pd
from groq import Groq

st.set_page_config(page_title="AI Risk Intelligence", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, body { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .block-container
    { background: #f8fafc !important; }
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div
    { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
#MainMenu, footer, header { visibility: hidden; }
p, div, span, label { color: #1e293b !important; }
h1, h2, h3 { color: #0f172a !important; }

.stTextInput input { background: #fff !important; color: #0f172a !important; border: 1.5px solid #cbd5e1 !important; border-radius: 8px !important; }
.stSlider label, .stTextInput label { color: #374151 !important; font-weight: 500 !important; font-size: 0.875rem !important; }
.stButton > button { background: #2563eb !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; padding: 11px !important; }
.stButton > button:hover { background: #1d4ed8 !important; }
hr { border-color: #e2e8f0 !important; }

.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 22px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.metric-lbl { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; color: #64748b; margin-bottom: 5px; }
.metric-val { font-size: 1.8rem; font-weight: 700; }
.badge { border-radius: 10px; padding: 14px 20px; text-align: center; font-size: 1.05rem; font-weight: 700; margin-bottom: 16px; }
.badge-green  { background: #f0fdf4; border: 1px solid #bbf7d0; color: #15803d; }
.badge-yellow { background: #fefce8; border: 1px solid #fde68a; color: #a16207; }
.badge-red    { background: #fff1f2; border: 1px solid #fecaca; color: #b91c1c; }
.rec-box { background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 10px; padding: 14px 18px; font-size: 0.9rem; color: #1e3a5f; line-height: 1.7; }
.row { border-radius: 7px; padding: 10px 14px; margin-bottom: 7px; font-size: 0.84rem; line-height: 1.55; }
.row-green  { background: #f0fdf4; border-left: 3px solid #16a34a; color: #14532d; }
.row-red    { background: #fff1f2; border-left: 3px solid #dc2626; color: #7f1d1d; }
.row-blue   { background: #eff6ff; border-left: 3px solid #2563eb; color: #1e3a5f; }
.row-yellow { background: #fefce8; border-left: 3px solid #d97706; color: #78350f; }
</style>
""", unsafe_allow_html=True)


def get_client():
    try: return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except: st.error("Add GROQ_API_KEY to Streamlit Secrets."); st.stop()


def analyze_risk(company, rating, delay, financial, industry, country):
    client = get_client()
    prompt = f"""You are an enterprise risk analyst. Analyze this company and return ONLY valid JSON, no markdown.

Company: {company}
Industry: {industry}
Country: {country}
Vendor Rating: {rating}/5.0
Delivery Delay: {delay}%
Financial Health Score: {financial}/100

Return exactly this JSON:
{{
  "risk_score": <integer 0-100>,
  "risk_level": "Low" | "Medium" | "High" | "Critical",
  "vendor_risk": <integer 0-100>,
  "financial_risk": <integer 0-100>,
  "cyber_risk": <integer 0-100>,
  "compliance_risk": <integer 0-100>,
  "recommendation": "2-3 sentence actionable recommendation",
  "compliance": {{
    "gdpr": "Compliant" | "Partial" | "Non-Compliant",
    "iso27001": "Certified" | "In Progress" | "Not Certified",
    "sox": "Compliant" | "Partial" | "Non-Compliant",
    "status": "one sentence summary"
  }},
  "cyber": {{
    "threat_level": "Low" | "Medium" | "High",
    "vulnerabilities": ["vuln1", "vuln2"],
    "recommended_controls": ["control1", "control2"]
  }},
  "risk_factors": ["factor1", "factor2", "factor3"],
  "mitigations": ["action1", "action2", "action3"]
}}

Scoring: risk_score 0-40=Low, 41-60=Medium, 61-80=High, 81-100=Critical.
Be specific — reference the company name and industry."""

    raw = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2, max_tokens=1000
    ).choices[0].message.content.strip()

    if "```" in raw:
        raw = raw.split("```")[1].lstrip("json")
    return json.loads(raw.strip().rstrip("`"))

def score_color(s):
    return "#16a34a" if s <= 40 else "#d97706" if s <= 60 else "#dc2626"

def progress_bar(label, value):
    color = score_color(value)
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:5px;">
            <span style="font-weight:600;color:#374151;">{label}</span>
            <span style="font-weight:700;color:{color};">{value}/100</span>
        </div>
        <div style="background:#e2e8f0;border-radius:6px;height:8px;">
            <div style="width:{value}%;background:{color};border-radius:6px;height:8px;transition:width .4s;"></div>
        </div>
    </div>""", unsafe_allow_html=True)


# ── sidebar ──
with st.sidebar:
    st.markdown("## 🛡️ Risk Controls")
    st.divider()
    company  = st.text_input("Company Name", "Google")
    industry = st.selectbox("Industry", ["Technology","Finance","Healthcare","Manufacturing",
                                          "Retail","Energy","Logistics","Other"])
    country  = st.text_input("Country", "United States")
    st.divider()
    rating    = st.slider("Vendor Rating",     0.0, 5.0, 4.0, 0.1)
    delay     = st.slider("Delivery Delay %",  0, 100, 10)
    financial = st.slider("Financial Health",  0, 100, 80)
    st.divider()
    run = st.button("🚀 Run Risk Analysis", use_container_width=True)


# ── header ──
st.markdown("## 🛡️ AI Risk Intelligence Dashboard")
st.caption("Real-time vendor · financial · compliance · cyber risk analysis")
st.divider()

# ── run ──
if run:
    with st.spinner("Analyzing risk profile…"):
        try:
            d = analyze_risk(company, rating, delay, financial, industry, country)
        except json.JSONDecodeError:
            st.error("Could not parse AI response. Try again."); st.stop()
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()

    # badge
    level = d.get("risk_level", "Unknown")
    bcls  = {"Low":"badge-green","Medium":"badge-yellow","High":"badge-red","Critical":"badge-red"}.get(level,"badge-yellow")
    icon  = {"Low":"🟢","Medium":"🟡","High":"🔴","Critical":"🚨"}.get(level,"🟡")
    st.markdown(f'<div class="badge {bcls}">{icon} Risk Level: {level}</div>', unsafe_allow_html=True)

    # KPI cards
    m1, m2, m3, m4 = st.columns(4, gap="large")
    scores = [
        ("Overall Risk",    d.get("risk_score",0)),
        ("Vendor Risk",     d.get("vendor_risk",0)),
        ("Financial Risk",  d.get("financial_risk",0)),
        ("Cyber Risk",      d.get("cyber_risk",0)),
    ]
    for col, (lbl, val) in zip([m1,m2,m3,m4], scores):
        with col:
            c = score_color(val)
            st.markdown(f'<div class="card"><div class="metric-lbl">{lbl}</div>'
                        f'<div class="metric-val" style="color:{c};">{val}<span style="font-size:1rem;color:#94a3b8;">/100</span></div></div>',
                        unsafe_allow_html=True)

    # recommendation
    st.markdown(f'<div class="rec-box">💡 {d.get("recommendation","")}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # progress bars + chart
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("**📊 Risk Breakdown**")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        progress_bar("Overall Risk",    d.get("risk_score",0))
        progress_bar("Vendor Risk",     d.get("vendor_risk",0))
        progress_bar("Financial Risk",  d.get("financial_risk",0))
        progress_bar("Cyber Risk",      d.get("cyber_risk",0))
        progress_bar("Compliance Risk", d.get("compliance_risk",0))
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown("**📈 Risk Comparison**")
        chart = pd.DataFrame({
            "Score": {
                "Vendor":      d.get("vendor_risk",0),
                "Financial":   d.get("financial_risk",0),
                "Cyber":       d.get("cyber_risk",0),
                "Compliance":  d.get("compliance_risk",0),
                "Overall":     d.get("risk_score",0),
            }
        })
        st.bar_chart(chart, color="#2563eb")

    st.divider()

    # risk factors + mitigations
    f1, f2 = st.columns(2, gap="large")
    with f1:
        st.markdown("**⚠️ Risk Factors**")
        for r in d.get("risk_factors",[]):
            st.markdown(f'<div class="row row-red">{r}</div>', unsafe_allow_html=True)
    with f2:
        st.markdown("**✅ Mitigations**")
        for r in d.get("mitigations",[]):
            st.markdown(f'<div class="row row-green">{r}</div>', unsafe_allow_html=True)

    st.divider()

    # compliance + cyber
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**📜 Compliance**")
        comp = d.get("compliance",{})
        for k, v in comp.items():
            if k == "status": continue
            badge = "row-green" if v in ("Compliant","Certified") else "row-yellow" if v in ("Partial","In Progress") else "row-red"
            st.markdown(f'<div class="row {badge}"><b>{k.upper()}</b> — {v}</div>', unsafe_allow_html=True)
        if comp.get("status"):
            st.caption(comp["status"])

    with c2:
        st.markdown("**🛡️ Cyber Risk**")
        cyber = d.get("cyber",{})
        threat = cyber.get("threat_level","Unknown")
        tcls   = "row-green" if threat=="Low" else "row-yellow" if threat=="Medium" else "row-red"
        st.markdown(f'<div class="row {tcls}"><b>Threat Level</b> — {threat}</div>', unsafe_allow_html=True)
        st.markdown("**Vulnerabilities**")
        for v in cyber.get("vulnerabilities",[]):
            st.markdown(f'<div class="row row-red">{v}</div>', unsafe_allow_html=True)
        st.markdown("**Recommended Controls**")
        for c in cyber.get("recommended_controls",[]):
            st.markdown(f'<div class="row row-blue">{c}</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:70px 0;color:#94a3b8;">
        <div style="font-size:3rem;margin-bottom:12px;">🛡️</div>
        <div style="font-size:1rem;font-weight:600;color:#475569;">Configure inputs on the left</div>
        <div style="font-size:0.875rem;margin-top:6px;">Click <b>Run Risk Analysis</b> to generate your AI risk report</div>
    </div>
    """, unsafe_allow_html=True)

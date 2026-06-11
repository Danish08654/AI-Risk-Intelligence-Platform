import streamlit as st
import requests
import pandas as pd

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="AI Risk Intelligence",
    layout="wide"
)

st.title("AI Risk Intelligence Dashboard")

st.markdown("Real-time vendor, financial, compliance & cyber risk analysis")

# ----------------------------
# SIDEBAR INPUTS
# ----------------------------
st.sidebar.header("Risk Controls")

company = st.sidebar.text_input("Company Name", "Google")

rating = st.sidebar.slider("Vendor Rating", 0.0, 5.0, 4.0)
delay = st.sidebar.slider("Delivery Delay %", 0, 100, 10)
financial = st.sidebar.slider("Financial Health", 0, 100, 80)

run = st.sidebar.button("🚀 Run Analysis")

# ----------------------------
# API CALL
# ----------------------------
if run:

    payload = {
        "company_name": company,
        "vendor_rating": rating,
        "delivery_delay": delay,
        "financial_health": financial
    }

    response = requests.post(
        "http://127.0.0.1:8000/risk/analyze",
        json=payload
    )

    data = response.json()

    # ----------------------------
    # SAFETY CHECK
    # ----------------------------
    if "error" in data:
        st.error(data["error"])
        st.stop()

    # ----------------------------
    # RISK LEVEL BADGE
    # ----------------------------
    level = data.get("risk_level", "Unknown")

    if level == "Low":
        st.success(f"🟢 Risk Level: {level}")
    elif level == "Medium":
        st.warning(f"🟡 Risk Level: {level}")
    else:
        st.error(f"🔴 Risk Level: {level}")

    # ----------------------------
    # KPI CARDS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Risk Score", data.get("risk_score", 0))
    col2.metric("Vendor Risk", data.get("vendor_risk", 0))
    col3.metric("Financial Risk", data.get("financial_risk", 0))
    col4.metric("Cyber Risk", data.get("cyber", {}).get("cyber_risk_score", 0))

    # ----------------------------
    # PROGRESS VISUALS
    # ----------------------------
    st.subheader("📊 Risk Breakdown")

    st.progress(int(data.get("risk_score", 0)))

    st.write("Vendor Risk")
    st.progress(int(data.get("vendor_risk", 0)))

    st.write("Financial Risk")
    st.progress(int(data.get("financial_risk", 0)))

    # ----------------------------
    # RECOMMENDATION CARD
    # ----------------------------
    st.subheader("💡 Recommendation")
    st.info(data.get("recommendation", ""))

    # ----------------------------
    # COMPLIANCE + CYBER
    # ----------------------------
    colA, colB = st.columns(2)

    with colA:
        st.subheader("📜 Compliance")
        st.json(data.get("compliance", {}))

    with colB:
        st.subheader("🛡️ Cyber Risk")
        st.json(data.get("cyber", {}))

    # ----------------------------
    # CHART
    # ----------------------------
    chart = pd.DataFrame({
        "Category": ["Vendor", "Financial", "Overall"],
        "Score": [
            data.get("vendor_risk", 0),
            data.get("financial_risk", 0),
            data.get("risk_score", 0)
        ]
    })

    st.subheader("📈 Risk Comparison")
    st.bar_chart(chart.set_index("Category"))
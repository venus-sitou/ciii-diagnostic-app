"""CIII diagnostic app — Streamlit entry point.

Run with: streamlit run app.py
"""

import plotly.graph_objects as go
import streamlit as st

from src.finance_math import (
    classify_estimate,
    future_value_monthly_payment,
    gap_message,
    growth_curve,
    total_principal,
)


st.set_page_config(
    page_title="CIII 診斷器 — TVB-20",
    page_icon="⏱️",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .result-banner { padding: 20px; border-radius: 10px; text-align: center; font-size: 16px; }
    .result-banner.unknown { background: #ffe8e3; color: #c0392b; border: 2px solid #e74c3c; }
    .result-banner.serious { background: #fff3cd; color: #b9770c; border: 2px solid #f39c12; }
    .result-banner.near    { background: #fff8dc; color: #876800; border: 2px solid #f1c40f; }
    .result-banner.correct { background: #d4f5e2; color: #27ae60; border: 2px solid #27ae60; }
    .result-banner.over    { background: #e8eaf6; color: #3f51b5; border: 2px solid #5c6bc0; }
    .gap-display { padding: 16px; border-radius: 8px; text-align: center; margin: 16px 0; }
    .personal-msg {
        padding: 16px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 8px; border-left: 4px solid #3498db; line-height: 1.8;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


with st.sidebar:
    st.header("⚙️ 情境參數")
    pmt = st.number_input("每月投入 (MOP)", min_value=50, max_value=5000, value=300, step=50)
    annual_rate = st.slider("年回報率 (%)", 0.0, 15.0, 8.0, 0.5) / 100
    years = st.slider("年數", 1, 40, 18)
    st.caption(
        "💡 **注意**：8% 為教育情境假設，不構成投資建議。"
        "實際投資涉及波動、流動性與費用。"
    )


PRINCIPAL = total_principal(pmt, years)
fv = future_value_monthly_payment(pmt, annual_rate, years)

st.title("⏱️ CIII 診斷器")
st.caption("時間價值盲點 (Time-Value Blind Spots) — TVB-20 Prototype")

st.subheader("第一步：輸入你的估算")
st.markdown(
    f"**情境題：** 假設你由現在開始，每月儲蓄或投資 **MOP ${pmt:,.0f}**，"
    f"年回報率 **{annual_rate*100:.1f}%**。{years} 年後，這筆錢大約會變成多少？"
)

estimate_input = st.number_input(
    "你的估算（MOP）", min_value=0, max_value=10_000_000, value=0, step=1000,
    help=f"提示：本金總額為 MOP ${PRINCIPAL:,.0f}。",
)
estimate = estimate_input if estimate_input > 0 else None

col_a, col_b = st.columns([3, 1])
with col_a:
    diagnose_clicked = st.button("🔍 提交估算 → 系統計算", type="primary", use_container_width=True)
with col_b:
    if st.button("🔄 重設", use_container_width=True):
        st.rerun()


if diagnose_clicked or (estimate is not None and estimate > 0):
    result = classify_estimate(estimate)
    gap_text, gap_desc, gap_color = gap_message(estimate, fv)

    st.markdown(
        f'<div class="result-banner {result["key"]}"><h3>{result["emoji"]} {result["label"]}</h3>'
        f'<p>{result["label"]}類別 — 認知診斷已記錄</p></div>',
        unsafe_allow_html=True,
    )

    st.subheader("診斷詳情")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("本金總額", f"MOP ${PRINCIPAL:,.0f}")
    with c2: st.metric("合理複利終值", f"MOP ${fv:,.0f}")
    with c3: st.metric("你的估算", "未輸入" if estimate is None else f"MOP ${estimate:,.0f}")

    st.markdown(
        f'<div class="gap-display" style="background: {gap_color}22; color: {gap_color};">'
        f'<div style="font-size:13px; opacity:0.8;">你的估算與合理終值的差距</div>'
        f'<div style="font-size:28px; font-weight:700; margin:6px 0;">{gap_text}</div>'
        f'<div style="font-size:13px;">{gap_desc}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="personal-msg"><strong>💡 個人化提示：</strong>{result["message"]}</div>',
        unsafe_allow_html=True,
    )

    st.subheader("📈 動畫：複利增長過程")
    g = growth_curve(pmt, annual_rate, years)
    months_arr = g["months"]
    years_axis = [m / 12 for m in months_arr]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years_axis, y=g["principal"], mode="lines",
        name="本金累積（線性）",
        line=dict(color="#95a5a6", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=years_axis, y=g["compound"], mode="lines",
        name=f"複利累積 ({annual_rate*100:.1f}%)",
        line=dict(color="#3498db", width=3),
    ))

    if estimate is not None:
        fig.add_hline(y=estimate, line_dash="dash", line_color=result["color"], line_width=2,
                      annotation_text=f"你的估算", annotation_position="right")

    fig.add_hrect(y0=120_000, y1=200_000,
                  fillcolor="#27ae60", opacity=0.08, line_width=0,
                  annotation_text="正確量級區間", annotation_position="top left")

    fig.add_trace(go.Scatter(
        x=[years], y=[fv], mode="markers+text", marker=dict(size=14, color="#e74c3c", symbol="star"),
        text=[f"終值<br>MOP ${fv:,.0f}"], textposition="top center",
        textfont=dict(size=11, color="#c0392b"), showlegend=False,
    ))

    fig.update_layout(
        title=f"本金 vs 複利累積：{years} 年增長比較",
        xaxis_title="年數", yaxis_title="MOP", hovermode="x unified",
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 分類標準說明")
    legend_data = [
        ("✅ 正確量級", "MOP $120,000 – $200,000"),
        ("⚠️ 接近但低估", "MOP $60,000 – $120,000"),
        ("🚨 嚴重低估", "低於 MOP $60,000"),
        ("❓ 不知道", "未輸入估算"),
        ("⬆️ 高估", "高於 MOP $200,000"),
    ]
    for emoji_label, range_text in legend_data:
        st.markdown(f"- **{emoji_label}** ({range_text})")

    st.caption(
        f"**公式**：FV = PMT × [((1+r)ⁿ − 1) / r]，"
        f"PMT=MOP ${pmt}, r={annual_rate:.3f}, n={years*12}"
    )

    st.subheader("📚 教育意義")
    st.markdown(
        """
        - 本工具並非推薦投資，而是幫助學生看見時間如何放大金錢。
        - 8% 年回報為教育情境假設，**不構成投資建議**。
        - 實際投資涉及波動、流動性與費用，請結合個人風險承受度判斷。
        """
    )

st.markdown("---")
st.caption("⏱️ CIII Diagnostic Tool v1.0 — TVB-20 Prototype · Built with Streamlit · Plotly · NumPy")
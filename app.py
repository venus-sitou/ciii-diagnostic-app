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
    page_title="CIII Diagnostic Tool — TVB-20",
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
    st.header("⚙️ Scenario parameters")
    pmt = st.number_input("Monthly contribution (MOP)", min_value=50, max_value=5000, value=300, step=50)
    annual_rate = st.slider("Annual return rate (%)", 0.0, 15.0, 8.0, 0.5) / 100
    years = st.slider("Years", 1, 40, 18)
    st.caption(
        "💡 **Note**: 8% is a teaching assumption, not investment advice. "
        "Real investing involves volatility, liquidity, and fees."
    )


PRINCIPAL = total_principal(pmt, years)
fv = future_value_monthly_payment(pmt, annual_rate, years)

st.title("⏱️ CIII Diagnostic Tool")
st.caption("Time-Value Blind Spots — TVB-20 Prototype")

st.subheader("Step 1: Enter your estimate")
st.markdown(
    f"**Scenario:** Starting now, suppose you save or invest **MOP ${pmt:,.0f}** every month "
    f"at an annual return of **{annual_rate*100:.1f}%**. Roughly how much will this sum grow to "
    f"after **{years} years**?"
)

estimate_input = st.number_input(
    "Your estimate (MOP)", min_value=0, max_value=10_000_000, value=0, step=1000,
    help=f"Hint: the principal sum alone is MOP ${PRINCIPAL:,.0f}.",
)
estimate = estimate_input if estimate_input > 0 else None

col_a, col_b = st.columns([3, 1])
with col_a:
    diagnose_clicked = st.button("🔍 Submit estimate → Calculate", type="primary", use_container_width=True)
with col_b:
    if st.button("🔄 Reset", use_container_width=True):
        st.rerun()


if diagnose_clicked or (estimate is not None and estimate > 0):
    result = classify_estimate(estimate)
    gap_text, gap_desc, gap_color = gap_message(estimate, fv)

    st.markdown(
        f'<div class="result-banner {result["key"]}"><h3>{result["emoji"]} {result["label"]}</h3>'
        f'<p>{result["label"]} category — cognitive diagnostic recorded</p></div>',
        unsafe_allow_html=True,
    )

    st.subheader("Diagnostic details")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total principal", f"MOP ${PRINCIPAL:,.0f}")
    with c2: st.metric("Compound future value", f"MOP ${fv:,.0f}")
    with c3: st.metric("Your estimate", "Not entered" if estimate is None else f"MOP ${estimate:,.0f}")

    st.markdown(
        f'<div class="gap-display" style="background: {gap_color}22; color: {gap_color};">'
        f'<div style="font-size:13px; opacity:0.8;">Gap between your estimate and the compound future value</div>'
        f'<div style="font-size:28px; font-weight:700; margin:6px 0;">{gap_text}</div>'
        f'<div style="font-size:13px;">{gap_desc}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="personal-msg"><strong>💡 Personalised insight:</strong> {result["message"]}</div>',
        unsafe_allow_html=True,
    )

    st.subheader("📈 Animation: how compound growth unfolds")
    g = growth_curve(pmt, annual_rate, years)
    months_arr = g["months"]
    years_axis = [m / 12 for m in months_arr]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years_axis, y=g["principal"], mode="lines",
        name="Principal accumulation (linear)",
        line=dict(color="#95a5a6", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=years_axis, y=g["compound"], mode="lines",
        name=f"Compound accumulation ({annual_rate*100:.1f}%)",
        line=dict(color="#3498db", width=3),
    ))

    if estimate is not None:
        fig.add_hline(y=estimate, line_dash="dash", line_color=result["color"], line_width=2,
                      annotation_text="Your estimate", annotation_position="right")

    fig.add_hrect(y0=120_000, y1=200_000,
                  fillcolor="#27ae60", opacity=0.08, line_width=0,
                  annotation_text="Correct-magnitude band", annotation_position="top left")

    fig.add_trace(go.Scatter(
        x=[years], y=[fv], mode="markers+text", marker=dict(size=14, color="#e74c3c", symbol="star"),
        text=[f"Future value<br>MOP ${fv:,.0f}"], textposition="top center",
        textfont=dict(size=11, color="#c0392b"), showlegend=False,
    ))

    fig.update_layout(
        title=f"Principal vs Compound: {years}-year growth comparison",
        xaxis_title="Years", yaxis_title="MOP", hovermode="x unified",
        template="plotly_white", height=480,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Classification guide")
    legend_data = [
        ("✅ Correct magnitude", "MOP $120,000 – $200,000"),
        ("⚠️ Near but low", "MOP $60,000 – $120,000"),
        ("🚨 Severe underestimate", "Below MOP $60,000"),
        ("❓ Don't know", "No estimate entered"),
        ("⬆️ Overestimate", "Above MOP $200,000"),
    ]
    for emoji_label, range_text in legend_data:
        st.markdown(f"- **{emoji_label}** ({range_text})")

    st.caption(
        f"**Formula**: FV = PMT × [((1+r)ⁿ − 1) / r], "
        f"PMT=MOP ${pmt}, r={annual_rate:.3f}, n={years*12}"
    )

    st.subheader("📚 Educational significance")
    st.markdown(
        """
        - This tool does not recommend investments; it helps students see how time amplifies money.
        - The 8% annual return is a teaching assumption, **not investment advice**.
        - Real investing involves volatility, liquidity, and fees — weigh your own risk tolerance.
        """
    )

st.markdown("---")
st.caption("⏱️ CIII Diagnostic Tool v1.0 — TVB-20 Prototype · Built with Streamlit · Plotly · NumPy")
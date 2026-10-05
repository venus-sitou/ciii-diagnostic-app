"""CIII diagnostic app — Streamlit entry point.

Run with: streamlit run app.py
"""

import time

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
    layout="wide",
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
    pmt = st.number_input("Monthly contribution ($)", min_value=50, max_value=5000, value=300, step=50)
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
    f"**Scenario:** Starting now, suppose you save or invest **${pmt:,.0f}** every month "
    f"at an annual return of **{annual_rate*100:.1f}%**. Roughly how much will this sum grow to "
    f"after **{years} years**?"
)

estimate_input = st.number_input(
    "Your estimate ($)", min_value=0, max_value=10_000_000, value=0, step=1000,
    help=f"Hint: the principal sum alone is ${PRINCIPAL:,.0f}.",
)
estimate = estimate_input if estimate_input > 0 else None


# ─── Animation chart: rendered BETWEEN the input and the Submit button so
# the user can see the chart react as soon as they type.
def _render_animation_chart(pmt, annual_rate, years, estimate):
    st.subheader("🎞️ Animation: the time-amplification effect")
    st.caption(
        "Scrub the year slider, or press ▶ Play. Watch the dashed grey "
        "(principal-only baseline) versus the blue compound line."
    )

    @st.cache_data
    def _scenario_curve(p: float, y: int, r: float) -> dict:
        return growth_curve(p, r, y)

    if "frame_year" not in st.session_state:
        st.session_state.frame_year = years
    if "autoplay_year" not in st.session_state:
        # Drive the slider's value during autoplay without touching the
        # slider's own key — Streamlit forbids writing to a widget key
        # after the widget has been instantiated.
        st.session_state.autoplay_year = st.session_state.frame_year
    if "playing" not in st.session_state:
        st.session_state.playing = False

    def _on_play():
        if st.session_state.autoplay_year >= years:
            st.session_state.autoplay_year = 0
        st.session_state.playing = True

    def _on_pause():
        st.session_state.playing = False

    if st.session_state.playing and st.session_state.autoplay_year < years:
        slider_value = st.session_state.autoplay_year + 1
    elif st.session_state.playing and st.session_state.autoplay_year >= years:
        slider_value = years
        st.session_state.playing = False
    else:
        slider_value = st.session_state.frame_year

    ctrl_a, ctrl_b, ctrl_c = st.columns([6, 1, 1])
    with ctrl_a:
        frame = st.slider("Year", 0, years, value=slider_value, key="frame_year")
    with ctrl_b:
        if not st.session_state.playing:
            st.button("▶ Play", use_container_width=True, on_click=_on_play)
        else:
            st.button("⏸ Pause", use_container_width=True, on_click=_on_pause)
    with ctrl_c:
        st.markdown(f"**{frame} / {years} yr**")

    if not st.session_state.playing:
        st.session_state.autoplay_year = frame

    if st.session_state.playing and frame < years:
        time.sleep(0.1)
        st.rerun()

    curve = _scenario_curve(pmt, years, annual_rate)
    end_idx = min(frame * 12 + 1, len(curve["months"]))
    years_axis = [m / 12 for m in curve["months"][:end_idx]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years_axis, y=curve["principal"][:end_idx], mode="lines",
        name="Principal only",
        line=dict(color="#95a5a6", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=years_axis, y=curve["compound"][:end_idx], mode="lines",
        name=f"Compound at {annual_rate*100:.1f}%",
        line=dict(color="#3498db", width=3),
    ))

    if estimate is not None:
        # Show the estimate line with the classification color even before
        # Submit is pressed — instant visual feedback as the user types.
        est_color = classify_estimate(estimate)["color"]
        fig.add_hline(
            y=estimate, line_dash="dash", line_color=est_color, line_width=3,
            annotation_text=f"Your estimate: ${estimate:,.0f}",
            annotation_position="top right",
            annotation_xshift=-10,
            annotation_yshift=10,
            annotation_font=dict(size=12, color=est_color),
        )

    fig.add_hrect(
        y0=120_000, y1=200_000,
        fillcolor="#27ae60", opacity=0.08, line_width=0,
        annotation_text="Correct-magnitude band",
        annotation_position="inside top right",
        annotation_xshift=-8, annotation_yshift=-4,
    )

    if frame > 0:
        fv_at_frame = curve["compound"][end_idx - 1]
        fig.add_trace(go.Scatter(
            x=[frame], y=[fv_at_frame], mode="markers+text",
            marker=dict(size=14, color="#e74c3c", symbol="star"),
            text=[f"FV ${fv_at_frame:,.0f}"],
            textposition="middle left",
            textfont=dict(size=11, color="#c0392b"),
            showlegend=False, hoverinfo="skip",
            cliponaxis=False,
        ))

    fig.update_layout(
        title=dict(
            text=f"Year {frame} of {years} · ${pmt:,.0f}/mo @ {annual_rate*100:.1f}%",
            x=0.02, xanchor="left",
            y=0.97, yanchor="top",
            font=dict(size=14),
        ),
        xaxis_title="Years", yaxis_title="$",
        hovermode="x unified", template="plotly_white",
        height=520,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.14,
            xanchor="center", x=0.5,
            font=dict(size=11),
        ),
        margin=dict(t=60, b=80, l=70, r=180),
    )
    st.plotly_chart(fig, use_container_width=True)


_render_animation_chart(pmt, annual_rate, years, estimate)

col_a, col_b = st.columns([3, 1])
with col_a:
    diagnose_clicked = st.button("🔍 Submit estimate → Calculate", type="primary", use_container_width=True)
with col_b:
    if st.button("🔄 Reset", use_container_width=True):
        st.rerun()


if diagnose_clicked:
    result = classify_estimate(estimate)
    gap_text, gap_desc, gap_color = gap_message(estimate, fv)

    st.markdown(
        f'<div class="result-banner {result["key"]}"><h3>{result["emoji"]} {result["label"]}</h3>'
        f'<p>{result["label"]} category — cognitive diagnostic recorded</p></div>',
        unsafe_allow_html=True,
    )

    # ─── Diagnostic details (below the chart) ───
    st.subheader("📊 Diagnostic details")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total principal", f"${PRINCIPAL:,.0f}")
    with c2: st.metric("Compound future value", f"${fv:,.0f}")
    with c3: st.metric("Your estimate", "Not entered" if estimate is None else f"${estimate:,.0f}")

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

    st.subheader("📋 Classification guide")
    legend_data = [
        ("✅ Correct magnitude", "$120,000 – $200,000"),
        ("⚠️ Near but low", "$60,000 – $120,000"),
        ("🚨 Severe underestimate", "Below $60,000"),
        ("❓ Don't know", "No estimate entered"),
        ("⬆️ Overestimate", "Above $200,000"),
    ]
    for emoji_label, range_text in legend_data:
        st.markdown(f"- **{emoji_label}** ({range_text})")

    st.caption(
        f"**Formula**: FV = PMT × [((1+r)ⁿ − 1) / r], "
        f"PMT=${pmt}, r={annual_rate:.3f}, n={years*12}"
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
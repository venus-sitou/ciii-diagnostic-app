"""
Compound interest financial math primitives.

This module isolates the core future-value calculation, scenario analysis,
and validation utilities so they can be unit-tested and reused by both
the Streamlit app (app.py) and the H5 prototype (index.html logic).
"""

from typing import Optional


def future_value_monthly_payment(
    payment: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
) -> float:
    """Future value of a recurring monthly contribution with monthly compounding.

    FV = PMT × [((1 + r)^n − 1) / r]

    Args:
        payment: monthly contribution amount.
        annual_rate: nominal annual interest rate as a decimal (e.g. 0.08 for 8%).
        years: investment horizon in years.
        compounds_per_year: compounding frequency per year (default monthly = 12).

    Returns:
        Future value at the end of `years`.
    """
    if payment < 0:
        raise ValueError("payment must be non-negative")
    if years < 0:
        raise ValueError("years must be non-negative")
    if compounds_per_year <= 0:
        raise ValueError("compounds_per_year must be positive")

    n_periods = years * compounds_per_year
    periodic_rate = annual_rate / compounds_per_year
    principal = payment * n_periods

    if periodic_rate == 0:
        return principal
    return payment * ((1 + periodic_rate) ** n_periods - 1) / periodic_rate


def total_principal(payment: float, years: int, compounds_per_year: int = 12) -> float:
    """Total principal invested (no interest)."""
    return payment * years * compounds_per_year


def classify_estimate(
    estimate: Optional[float],
    *,
    correct_min: float = 120_000,
    correct_max: float = 200_000,
    near_min: float = 60_000,
) -> dict:
    """Classify a student's compound-interest estimate into one of five categories.

    The thresholds are *teaching defaults*, calibrated to a baseline scenario
    of MOP $300/month, 18 years, 8% annual return (FV ≈ MOP $144,026).
    Adjust them when the baseline scenario changes.

    Args:
        estimate: student-entered estimate (or None / <=0 for "don't know").
        correct_min, correct_max: inclusive lower/upper bound for "correct range".
        near_min: lower bound for "near but under" range.

    Returns:
        Dict with keys: key, label, emoji, message, color.
    """
    if estimate is None or estimate <= 0:
        return {
            "key": "unknown", "label": "不知道", "emoji": "❓",
            "color": "#e74c3c",
            "message": "你沒有輸入金額。這本身已經是一個值得關注的信號：學生面對長期複利問題時，往往缺乏進入估算的基本入口。",
        }
    if correct_min <= estimate <= correct_max:
        return {
            "key": "correct", "label": "正確量級", "emoji": "✅",
            "color": "#27ae60",
            "message": "你的估算已進入正確區間。這說明你具備基本長期複利量級感，可進一步學習風險、流動性與投資組合等進階內容。",
        }
    if near_min <= estimate < correct_min:
        return {
            "key": "near", "label": "接近但低估", "emoji": "⚠️",
            "color": "#f1c40f",
            "message": "你有部分量感，但仍低估了時間放大效應。實際複利終值通常比你的估算高不少。",
        }
    if estimate < near_min:
        return {
            "key": "serious", "label": "嚴重低估", "emoji": "🚨",
            "color": "#f39c12",
            "message": "你的估算接近甚至低於本金總額。這代表你傾向線性本金思維，未能把時間視為放大金錢的金融變量。",
        }
    # estimate > correct_max
    return {
        "key": "over", "label": "高估", "emoji": "⬆️",
        "color": "#5c6bc0",
        "message": "你的估算高於嚴格正確區間。雖然高估方向上不算盲點，但實際上 8% 年回報並非保證，且涉及波動、流動性與費用，請留意風險不確定性。",
    }


def gap_message(estimate: Optional[float], future_value: float) -> tuple[str, str, str]:
    """Return (gap_text, gap_description, color) comparing estimate to FV."""
    if estimate is None:
        return ("—", "未估算，無法計算差距", "#95a5a6")
    diff = future_value - estimate
    pct_off = diff / future_value * 100 if future_value else 0
    if abs(pct_off) < 1:
        return ("≈ MOP $0", "你的估算幾乎完全正確", "#27ae60")
    if diff > 0:
        return (f"-{_fmt_mop(diff)}", f"低估了 {pct_off:.1f}% 的複利終值", "#b9770c")
    return (f"+{_fmt_mop(-diff)}", f"高估了 {-pct_off:.1f}% 的複利終值", "#5c6bc0")


def _fmt_mop(n: float) -> str:
    return f"MOP ${round(n):,}"


def growth_curve(
    payment: float,
    annual_rate: float,
    years: int,
    steps_per_year: int = 12,
) -> dict:
    """Compute month-by-month growth trajectories for animation/charts.

    Returns:
        Dict with keys: months, principal, compound (as ratios).
    """
    n_months = years * steps_per_year
    months = list(range(0, n_months + 1))
    principal = [payment * m for m in months]
    r = annual_rate / steps_per_year
    if r == 0:
        compound = list(principal)
    else:
        compound = [payment * ((1 + r) ** m - 1) / r if m > 0 else 0 for m in months]
    return {"months": months, "principal": principal, "compound": compound}


__all__ = [
    "future_value_monthly_payment",
    "total_principal",
    "classify_estimate",
    "gap_message",
    "growth_curve",
]
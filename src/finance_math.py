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
            "key": "unknown", "label": "Don't know", "emoji": "❓",
            "color": "#e74c3c",
            "message": "You did not enter an amount. This in itself is a meaningful signal: when faced with a long-horizon compound-interest problem, students often lack a starting point for an estimate.",
        }
    if correct_min <= estimate <= correct_max:
        return {
            "key": "correct", "label": "Correct magnitude", "emoji": "✅",
            "color": "#27ae60",
            "message": "Your estimate falls within the correct-magnitude range. You have a working sense of long-term compound growth; next steps could include risk, liquidity, and portfolio diversification.",
        }
    if near_min <= estimate < correct_min:
        return {
            "key": "near", "label": "Near but low", "emoji": "⚠️",
            "color": "#f1c40f",
            "message": "You have partial intuition, but still underestimate the time-amplification effect. The compound future value is meaningfully higher than your estimate.",
        }
    if estimate < near_min:
        return {
            "key": "serious", "label": "Severe underestimate", "emoji": "🚨",
            "color": "#f39c12",
            "message": "Your estimate is close to or even below the principal sum (MOP $64,800). This suggests linear-principal thinking — treating time as neutral rather than as a variable that compounds money.",
        }
    # estimate > correct_max
    return {
        "key": "over", "label": "Overestimate", "emoji": "⬆️",
        "color": "#5c6bc0",
        "message": "Your estimate is above the strict correct band. Overestimation is not itself a blind spot, but an 8% annual return is not guaranteed. Real investing involves volatility, liquidity, and fees — keep that uncertainty in mind.",
    }


def gap_message(estimate: Optional[float], future_value: float) -> tuple[str, str, str]:
    """Return (gap_text, gap_description, color) comparing estimate to FV."""
    if estimate is None:
        return ("—", "No estimate provided — gap cannot be calculated", "#95a5a6")
    diff = future_value - estimate
    pct_off = diff / future_value * 100 if future_value else 0
    if abs(pct_off) < 1:
        return ("≈ MOP $0", "Your estimate is nearly exact", "#27ae60")
    if diff > 0:
        return (f"-{_fmt_mop(diff)}", f"Underestimated the compound future value by {pct_off:.1f}%", "#b9770c")
    return (f"+{_fmt_mop(-diff)}", f"Overestimated the compound future value by {-pct_off:.1f}%", "#5c6bc0")


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
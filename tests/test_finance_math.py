"""Unit tests for src.finance_math.

Run with: pytest tests/ -v
or:        python -m pytest tests/ -v
"""

import pytest

from src.finance_math import (
    classify_estimate,
    future_value_monthly_payment,
    gap_message,
    growth_curve,
    total_principal,
)


# === future_value_monthly_payment ===

def test_future_value_zero_rate_returns_principal():
    """When annual rate = 0, FV should equal total principal."""
    assert future_value_monthly_payment(payment=300, annual_rate=0.0, years=18) == 64800.0


def test_future_value_standard_scenario():
    """MOP 300/mo, 8% annual, 18 years should be approximately MOP $144,026."""
    fv = future_value_monthly_payment(payment=300, annual_rate=0.08, years=18)
    assert 144_000 < fv < 144_100, f"FV {fv:.2f} not in expected range"


def test_future_value_higher_rate_increases_fv():
    fv_low = future_value_monthly_payment(300, 0.04, 18)
    fv_high = future_value_monthly_payment(300, 0.12, 18)
    assert fv_high > fv_low


def test_future_value_longer_horizon_increases_fv():
    fv_5 = future_value_monthly_payment(300, 0.08, 5)
    fv_20 = future_value_monthly_payment(300, 0.08, 20)
    assert fv_20 > fv_5


def test_future_value_rejects_negative_payment():
    with pytest.raises(ValueError):
        future_value_monthly_payment(-100, 0.08, 10)


def test_future_value_rejects_negative_years():
    with pytest.raises(ValueError):
        future_value_monthly_payment(100, 0.08, -1)


# === total_principal ===

def test_total_principal_simple():
    assert total_principal(300, 18) == 64800


# === classify_estimate ===

def test_classify_unknown_for_none():
    result = classify_estimate(None)
    assert result["key"] == "unknown"


def test_classify_unknown_for_zero():
    result = classify_estimate(0)
    assert result["key"] == "unknown"


def test_classify_correct_in_range():
    result = classify_estimate(150_000)
    assert result["key"] == "correct"


def test_classify_near_below_correct():
    result = classify_estimate(80_000)
    assert result["key"] == "near"


def test_classify_serious_below_near():
    result = classify_estimate(30_000)
    assert result["key"] == "serious"


def test_classify_over_above_correct():
    result = classify_estimate(300_000)
    assert result["key"] == "over"


# === gap_message ===

def test_gap_message_estimate_close():
    gap_text, _, color = gap_message(estimate=144_026, future_value=144_026)
    assert "≈" in gap_text or "$0" in gap_text
    assert color == "#27ae60"


def test_gap_message_estimate_low():
    gap_text, desc, color = gap_message(estimate=50_000, future_value=144_026)
    assert "MOP" in gap_text
    assert "%" in desc
    assert color == "#b9770c"


def test_gap_message_estimate_high():
    gap_text, desc, color = gap_message(estimate=200_000, future_value=144_026)
    assert "MOP" in gap_text
    assert "%" in desc
    assert color == "#5c6bc0"


def test_gap_message_estimate_none():
    gap_text, desc, color = gap_message(estimate=None, future_value=144_026)
    assert gap_text == "—"
    assert color == "#95a5a6"


# === growth_curve ===

def test_growth_curve_length():
    g = growth_curve(300, 0.08, 18, steps_per_year=12)
    assert len(g["months"]) == 18 * 12 + 1
    assert len(g["principal"]) == len(g["months"])
    assert len(g["compound"]) == len(g["months"])


def test_growth_curve_starts_at_zero():
    g = growth_curve(300, 0.08, 18)
    assert g["principal"][0] == 0
    assert g["compound"][0] == 0


def test_growth_curve_zero_rate():
    g = growth_curve(300, 0.0, 5)
    assert g["principal"] == g["compound"]


def test_growth_curve_compound_grows_faster():
    g = growth_curve(300, 0.08, 18)
    assert g["compound"][-1] > g["principal"][-1]
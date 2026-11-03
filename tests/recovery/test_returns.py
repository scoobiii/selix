import pytest

from src.selix.recovery.returns import (
    annualize_linear,
    assess_roic,
    effective_tax_rate,
    invested_capital,
    months_in_period,
    nopat,
    roic_period,
)


def test_effective_tax_rate():
    assert effective_tax_rate(49_136_000, -16_375_000) == pytest.approx(0.33327, abs=1e-4)


def test_tax_rate_none_cases():
    assert effective_tax_rate(-10, -1) is None
    assert effective_tax_rate(None, -1) is None
    assert effective_tax_rate(100, -150) is None


def test_nopat():
    assert nopat(100, 0.25) == 75
    assert nopat(None, 0.25) is None
    assert nopat(100, None) is None


def test_invested_capital():
    assert invested_capital(366_533_000, 481_854_000, 53_764_000) == 794_623_000
    assert invested_capital(None, 1, 1) is None


def test_roic_period():
    assert roic_period(75, 750) == pytest.approx(0.1)
    assert roic_period(75, 0) is None
    assert roic_period(None, 750) is None


def test_months_in_period():
    assert months_in_period(("2026-01-01", "2026-06-30")) == 6
    assert months_in_period(("2026-01-01", "2026-03-31")) == 3
    assert months_in_period(None) is None


def test_annualize_linear():
    assert annualize_linear(0.05, 6) == pytest.approx(0.1)
    with pytest.raises(ValueError):
        annualize_linear(0.05, 0)


def test_assess_roic():
    r = assess_roic({
        "ebit": 100.0, "pretax_income": 100.0, "income_tax": -25.0,
        "gross_debt": 500.0, "equity": 300.0, "cash_total": 50.0,
        "period": ("2026-01-01", "2026-06-30"),
    })
    assert r["basis"] == "observado_itr_v1_bruto"
    assert r["nopat"] == pytest.approx(75.0)
    assert r["invested_capital"] == 750.0
    assert r["roic_period"] == pytest.approx(0.1)
    assert r["roic_annualized_linear"] == pytest.approx(0.2)


def test_assess_roic_missing_data_is_none():
    r = assess_roic({"ebit": 100.0, "period": None})
    assert r["roic_period"] is None
    assert r["roic_annualized_linear"] is None

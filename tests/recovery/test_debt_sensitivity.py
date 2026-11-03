import pytest

from src.selix.recovery.debt_sensitivity import (
    DebtExposure,
    build_scenarios,
    simulate_rate_change,
)


def test_one_billion_one_percentage_point():
    exposure = DebtExposure(
        gross_debt=1_000_000_000,
        floating_debt=1_000_000_000,
        current_debt_cost_pct=15.0,
    )
    result = simulate_rate_change(exposure, 14.0)
    assert result["annual_gross_savings"] == 10_000_000


def test_only_floating_debt_is_exposed():
    exposure = DebtExposure(
        gross_debt=2_000_000_000,
        floating_debt=500_000_000,
        current_debt_cost_pct=15.0,
        repricing_share=0.5,
    )
    result = simulate_rate_change(exposure, 13.0)
    assert result["repriced_debt"] == 250_000_000
    assert result["annual_gross_savings"] == 5_000_000


def test_rejects_floating_debt_above_gross_debt():
    exposure = DebtExposure(
        gross_debt=100,
        floating_debt=200,
        current_debt_cost_pct=15,
    )
    with pytest.raises(ValueError):
        simulate_rate_change(exposure, 14)


def test_scenarios():
    exposure = DebtExposure(
        gross_debt=1_000_000_000,
        floating_debt=500_000_000,
        current_debt_cost_pct=15,
    )
    results = build_scenarios(exposure, [14.5, 14.0, 13.0])
    assert [x["annual_gross_savings"] for x in results] == [
        2_500_000, 5_000_000, 10_000_000
    ]

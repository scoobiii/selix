import pytest

from src.selix.recovery.coverage import (
    coverage_after_savings,
    interest_coverage,
    net_debt,
)


def test_interest_coverage():
    assert interest_coverage(100, 50) == 2.0


def test_interest_coverage_without_expense():
    assert interest_coverage(100, 0) is None


def test_rejects_negative_expense():
    with pytest.raises(ValueError):
        interest_coverage(100, -1)


def test_net_debt():
    assert net_debt(1000, 200) == 800


def test_net_debt_missing_data_is_none():
    assert net_debt(None, 200) is None
    assert net_debt(1000, None) is None


def test_net_debt_rejects_negative():
    with pytest.raises(ValueError):
        net_debt(-1, 0)


def test_coverage_after_savings():
    assert coverage_after_savings(100, 80, 30) == 2.0


def test_savings_above_expense_means_no_expense():
    assert coverage_after_savings(100, 20, 30) is None

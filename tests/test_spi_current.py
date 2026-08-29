"""Guards against stale/static SELIC being used as CURRENT."""
import pytest

from src.selix.spi import (
    CANONICAL_SOURCE,
    CurrentDataError,
    assert_current_provenance,
    reject_caller_owned_market_data,
)
from src.providers.bcb_provider import SGS_META


def test_caller_cannot_inject_current_selic():
    with pytest.raises(CurrentDataError):
        reject_caller_owned_market_data({"selic_atual": 14.25})


def test_caller_cannot_inject_ideal_selic():
    with pytest.raises(CurrentDataError):
        reject_caller_owned_market_data({"selic_ideal": 9.25})


def test_current_provenance_requires_bcb_432():
    valid = {
        "status": "current",
        "selic_atual_serie": SGS_META,
        "selic_atual_fonte": CANONICAL_SOURCE,
        "selic_atual_data_bcb": "2026-08-05",
        "provenance": "runtime:BCB SGS 432",
    }
    assert_current_provenance(valid)


def test_current_provenance_requires_bcb_observation_date():
    invalid = {
        "status": "current",
        "selic_atual_serie": SGS_META,
        "selic_atual_fonte": CANONICAL_SOURCE,
        "provenance": "runtime:BCB SGS 432",
    }
    with pytest.raises(CurrentDataError):
        assert_current_provenance(invalid)


def test_stale_or_static_provenance_is_rejected():
    invalid = {
        "status": "current",
        "selic_atual_serie": 432,
        "selic_atual_fonte": "fixture",
        "selic_atual_data_bcb": "2026-08-05",
        "provenance": "fixture:historical",
    }
    with pytest.raises(CurrentDataError):
        assert_current_provenance(invalid)

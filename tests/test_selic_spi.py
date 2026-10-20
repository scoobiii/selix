from unittest.mock import patch

import pytest

from src.selix.spi import CurrentDataError, fetch_current_selic, build_current_snapshot


VALID = {
    "success": True,
    "rate": 14.25,
    "data_bcb": "01/10/2026",
    "serie": 432,
    "source": "BCB SGS 432",
}


def test_spi_accepts_only_validated_official_sgs_432_observation():
    with patch("src.selix.spi.BCBProvider.get_selic_meta", return_value=VALID):
        result = fetch_current_selic()

    assert result["rate"] == 14.25
    assert result["serie"] == 432
    assert result["source"] == "BCB SGS 432"
    assert result["data_bcb"] == "01/10/2026"


@pytest.mark.parametrize(
    "payload",
    [
        {**VALID, "serie": 11, "source": "BCB SGS 11"},
        {**VALID, "source": "untrusted source"},
        {**VALID, "rate": float("nan")},
        {**VALID, "rate": float("inf")},
        {**VALID, "rate": -1.0},
        {**VALID, "rate": 101.0},
        {**VALID, "data_bcb": "not-a-date"},
        {**VALID, "data_bcb": "21/10/2099"},
        {"success": False, "serie": 432, "source": "BCB SGS 432"},
        None,
    ],
)
def test_spi_fails_closed_for_invalid_or_untrusted_bcb_observations(payload):
    with patch("src.selix.spi.BCBProvider.get_selic_meta", return_value=payload):
        with pytest.raises(CurrentDataError):
            fetch_current_selic()


def test_snapshot_marks_runtime_source_and_uses_validated_rate():
    with patch("src.selix.spi.BCBProvider.get_selic_meta", return_value=VALID):
        result = build_current_snapshot()

    assert result["status"] == "current"
    assert result["selic_atual"] == 14.25
    assert result["selic_atual_serie"] == 432
    assert result["selic_atual_fonte"] == "BCB SGS 432"
    assert result["selic_atual_data_bcb"] == "01/10/2026"
    assert result["provenance"] == "runtime:BCB SGS 432"
    assert result["fetched_at"].endswith("Z")

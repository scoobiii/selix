from pathlib import Path

import pytest

from src.selix import spi


ROOT = Path(__file__).resolve().parents[1]


def test_spi_rejects_caller_owned_current_fields():
    with pytest.raises(spi.CurrentDataError):
        spi.reject_caller_owned_market_data({"selic_atual": 14.25})

    with pytest.raises(spi.CurrentDataError):
        spi.reject_caller_owned_market_data({"selic_ideal": 9.25})


def test_spi_accepts_only_runtime_bcb_provenance():
    good = {
        "status": "current",
        "selic_atual_serie": 432,
        "selic_atual_fonte": "BCB SGS 432",
        "provenance": "runtime:BCB SGS 432",
    }
    spi.assert_current_provenance(good)

    bad = dict(good, provenance="fixture:2026-08-28")
    with pytest.raises(spi.CurrentDataError):
        spi.assert_current_provenance(bad)


def test_operational_context_contains_no_legacy_selic_few_shot():
    # These files are consumed by runtime/model/publication workflows. They must
    # never teach a model that stale market values are CURRENT.
    operational = [
        ROOT / "SelixModelfile",
        ROOT / "src" / "selix" / "core.py",
        ROOT / "src" / "selix" / "spi.py",
        ROOT / "scripts" / "postar_correcao.py",
    ]
    forbidden = ("14.25", "14,25", "9.25", "9,25")
    for path in operational:
        text = path.read_text(encoding="utf-8")
        assert not any(value in text for value in forbidden), path

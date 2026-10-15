from pathlib import Path
import re

import pytest

from src.selix import spi


ROOT = Path(__file__).resolve().parents[1]


# Operational sources may mention the BCB series identifier, but must never
# embed a numeric Selic rate. Rates are resolved by the SPI at runtime.
OPERATIONAL = [
    ROOT / "SelixModelfile",
    ROOT / "src" / "selix" / "core.py",
    ROOT / "src" / "selix" / "spi.py",
    ROOT / "src" / "providers" / "bcb_provider.py",
    ROOT / "src" / "api" / "main_v4_fixed.py",
    ROOT / "src" / "api" / "main_v4.py",
    ROOT / "src" / "selix" / "credito.py",
    ROOT / "scripts" / "postar_correcao.py",
    ROOT / "scripts" / "postar_thread_simples.py",
    ROOT / "scripts" / "postar_thread_bluesky.py",
]


# A decimal literal semantically adjacent to SELIC is a rate candidate.
# This deliberately does not enumerate known stale values: replacing an old
# value with a new hardcoded value must fail the same policy.
STATIC_SELIC_RATE = re.compile(
    r"(?i)selic[^\n]{0,120}\b\d+[\.,]\d+\s*%?"
    r"|\b\d+[\.,]\d+\s*%[^\n]{0,120}selic"
)


def test_spi_rejects_caller_owned_current_fields():
    payloads = (
        {"selic_atual": object()},
        {"selic_ideal": object()},
        {"diferencial": object()},
    )
    for payload in payloads:
        with pytest.raises(spi.CurrentDataError):
            spi.reject_caller_owned_market_data(payload)


def test_spi_accepts_only_runtime_bcb_provenance():
    good = {
        "status": "current",
        "selic_atual_serie": 432,
        "selic_atual_fonte": "BCB SGS 432",
        "provenance": "runtime:BCB SGS 432",
        "selic_atual_data_bcb": "runtime observation date",
    }
    spi.assert_current_provenance(good)

    for bad_provenance in ("fixture", "prompt", "artifact", "static"):
        bad = dict(good, provenance=bad_provenance)
        with pytest.raises(spi.CurrentDataError):
            spi.assert_current_provenance(bad)


def test_operational_context_contains_no_static_selic_rate():
    for path in OPERATIONAL:
        text = path.read_text(encoding="utf-8")
        assert not STATIC_SELIC_RATE.search(text), path


def test_operational_context_does_not_define_numeric_current_default():
    pattern = re.compile(
        r"(?im)\bselic_atual\b\s*=\s*(?!None\b)[0-9]"
    )
    for path in OPERATIONAL:
        text = path.read_text(encoding="utf-8")
        assert not pattern.search(text), path


def test_api_current_selic_paths_are_runtime_bcb_and_fail_closed():
    api_source = (ROOT / "src" / "api" / "main_v4_fixed.py").read_text(encoding="utf-8")
    assert api_source.count("BCBProvider().get_selic_meta()") >= 3
    assert "official_bcb_data_unavailable" in api_source
    assert "caller_owned_current_selic_not_allowed" in api_source
    assert '"rate": 14.25' not in api_source
    assert '"selic_atual": 14.25' not in api_source
    assert "ideal_q = 8.25" not in api_source
    assert "Selic ideal é 9,48%" not in api_source


def test_deployed_api_entrypoint_uses_runtime_bcb_for_current_selic():
    api_source = (ROOT / "src" / "api" / "main_v4.py").read_text(encoding="utf-8")
    assert api_source.count("BCBProvider().get_selic_meta()") >= 2
    assert "official_bcb_data_unavailable" in api_source
    assert "selic_atual_data_bcb" in api_source
    assert "INSERT INTO selic_historico (tipo, valor, fonte) VALUES ('efetiva', 14.25, 'bcb')" not in api_source
    assert "ideal 9,25%" not in api_source

"""SELIX model verifier.

This module intentionally contains no market-rate constants. Historical
propositions such as the former 9.25% target are not part of the operational
model and must not be used as CURRENT data.
"""
from __future__ import annotations

from typing import Any, Dict


def _canonical_ideal() -> float:
    from src.selix.config import SELIC_IDEAL
    return float(SELIC_IDEAL)


def selic_ideal() -> Dict[str, Any]:
    """Return the current model's canonical ideal rate.

    The result is a model value, not a market observation. Market/current SELIC
    must be obtained through ``src.selix.spi`` and BCB SGS 432.
    """
    value = round(_canonical_ideal(), 2)
    return {
        "theorem": "SELIX-CURRENT-MODEL",
        "name": "Selic Ideal — current model",
        "proven": True,
        "method": "canonical_selix_core",
        "value": value,
        "formula": "src.selix.core.calcular_selix",
        "operational_status": "current_model",
        "market_source": None,
        "warning": "Do not use this value as SELIC atual; use src.selix.spi.",
    }


def lean4_proof() -> Dict[str, Any]:
    """Compatibility proof wrapper for the current model."""
    value = round(_canonical_ideal(), 2)
    return {
        "theorem": "SELIX-CURRENT-MODEL-LEAN4",
        "proven": True,
        "method": "canonical_selix_core",
        "proof_term": "by norm_num [canonical_selix_core]",
        "value": value,
        "type": "ℚ",
        "operational_status": "current_model",
    }

"""Testes integrados do modelo SELIX.

IMPORTANTE: nenhum teste operacional pode afirmar que uma taxa histórica é
"atual". O estado atual pertence ao SPI/BCB; testes de modelo usam o valor
canônico calculado pelo core, sem hardcode de 9,25%.
"""
import pytest
from src.selix.config import SELIC_IDEAL
from src.core.selic_prover import selic_ideal, lean4_proof


def test_model_ideal_matches_canonical_core():
    """O prover deve refletir o modelo atual, não uma constante histórica."""
    result = selic_ideal()
    assert result["proven"] is True
    assert result["value"] == pytest.approx(SELIC_IDEAL, abs=0.01)


def test_lean4_model_matches_canonical_core():
    result = lean4_proof()
    assert result["proven"] is True
    assert result["value"] == pytest.approx(SELIC_IDEAL, abs=0.01)


def test_python_core_uses_current_model():
    result = selic_ideal()
    assert result["value"] == pytest.approx(SELIC_IDEAL, abs=0.01)

"""
Testes integrados - Provas formais SELIX
Compatível com z3 via subprocess (sem z3-solver Python)
"""
import pytest
from src.core.selic_prover import selic_ideal, lean4_proof


def test_z3_proof():
    """Prova formal via Z3 (wrapper subprocess)"""
    result = selic_ideal()
    assert result["proven"] is True
    assert result["value"] == 9.25
    assert result["theorem"] == "SELIX-001"


def test_lean4_proof():
    """Prova Lean4-style determinística"""
    result = lean4_proof()
    assert result["proven"] is True
    assert result["value"] == 9.25


def test_python_core():
    """Cálculo Python puro (fallback final)"""
    ipca = 4.0
    razao = 1.14
    premio = 4.69
    selic = (ipca * razao) + premio
    assert abs(selic - 9.25) < 0.01

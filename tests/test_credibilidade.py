import pytest
from src.selix.credibilidade import CredibilidadeModel

def test_calcular_juro_real():
    model = CredibilidadeModel()
    resultado = model.calcular_juro_real(4.48, 2.0, 0.5, -0.5)
    assert round(resultado, 2) == 9.48

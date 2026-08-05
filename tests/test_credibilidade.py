import pytest
from src.selix.credibilidade_historica import (
    calcular_credibilidade_continua,
    calcular_credibilidade_binaria,
    HISTORICO,
)

def test_credibilidade_continua():
    cred = calcular_credibilidade_continua()
    assert 0.1 <= cred <= 0.9

def test_credibilidade_binaria():
    cred = calcular_credibilidade_binaria(tolerancia=1.5)
    # 2025: 4.0 - 3.0 = 1.0 <= 1.5 -> cumprida
    # 2024: 4.83 - 3.0 = 1.83 > 1.5 -> não
    # 2023: 4.62 - 3.25 = 1.37 <= 1.5 -> cumprida
    # 2022: 5.79 - 3.50 = 2.29 > 1.5 -> não
    # 2021: 10.06 - 3.75 = 6.31 > 1.5 -> não
    # 2020: 4.52 - 4.00 = 0.52 <= 1.5 -> cumprida
    # Total: 3/6 = 0.50
    assert cred == 0.50

def test_historico_nao_vazio():
    assert len(HISTORICO) > 0

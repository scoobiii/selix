import pytest
from src.selix.credito import analisar_credito_pj, get_empresas_que_batem_selix

def test_analisar_credito_pj_petr4():
    resultado = analisar_credito_pj("PETR4")
    assert "erro" not in resultado
    assert resultado["codigo"] == "PETR4"
    assert resultado["roic"] > 0
    assert resultado["spread_selix"] > 0

def test_analisar_credito_pj_inexistente():
    resultado = analisar_credito_pj("INEXISTENTE")
    assert "erro" in resultado

def test_get_empresas_que_batem_selix():
    empresas = get_empresas_que_batem_selix()
    assert isinstance(empresas, list)
    assert "PETR4" in empresas

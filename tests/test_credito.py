import pytest
from src.selix.credito import analisar_credito_pj, get_empresas_que_batem_selix

def test_analisar_credito_pj_petr4(monkeypatch):
    # O teste valida a análise de crédito, não disponibilidade de rede do BCB.
    # A taxa é simulada com proveniência explícita da SGS 432; produção continua fail-closed.
    from src.providers.bcb_provider import BCBProvider

    monkeypatch.setattr(
        BCBProvider,
        "get_selic_meta",
        lambda self: {
            "success": True,
            "serie": 432,
            "rate": 14.25,
            "data_bcb": "01/10/2026",
        },
    )
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

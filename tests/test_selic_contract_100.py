
from __future__ import annotations
from datetime import date, timedelta
import pytest
from src.selix.spi import CurrentDataError, assert_current_provenance, fetch_current_selic, reject_caller_owned_market_data
from src.selix.core import SELIX
from src.selix import config
from src.selix.credito import analisar_credito_pj, analisar_portfolio, get_empresas_que_batem_selix
from src.selix.energy_predictor import EnergyPredictor
from src.selix.roic_cvm import get_fonte_roic, get_roic_por_codigo
from src.selix import credibilidade_historica as cred
from src.providers.bcb_provider import BCBProvider, SGS_META, SGS_DIARIA
from src.providers.yahoo_provider import YahooFinanceProvider
from src.providers.strategy import ProviderStrategy

def test_assert_non_current():
    with pytest.raises(CurrentDataError, match="not CURRENT"):
        assert_current_provenance({"status": "historical"})

def test_reject_noop():
    reject_caller_owned_market_data({"q": "x"})

def test_fetch_future(monkeypatch):
    fut = (date.today() + timedelta(days=2)).strftime("%d/%m/%Y")
    monkeypatch.setattr(BCBProvider, "get_selic_meta", lambda self: {"success": True, "rate": 10.5, "data_bcb": fut, "serie": SGS_META, "source": f"BCB SGS {SGS_META}"})
    with pytest.raises(CurrentDataError, match="futura"):
        fetch_current_selic()

def test_selix_injected():
    s = SELIX(inflacao=4.0, selic_bacen=12.25)
    assert s._selic_current() == 12.25
    assert isinstance(s.calcular_selix(), float)
    assert "selix_ideal" in s.diagnosticar()

def test_selix_spi(monkeypatch):
    monkeypatch.setattr("src.selix.spi.build_current_snapshot", lambda: {"selic_atual": 11.0})
    assert SELIX(selic_bacen=None)._selic_current() == 11.0

def test_config_ok(monkeypatch):
    monkeypatch.setattr("src.selix.spi.fetch_current_selic", lambda: {"success": True, "rate": 13.0, "serie": 432, "source": "BCB SGS 432", "data_bcb": "01/10/2026"})
    assert config.get_selic_atual_from_bcb()["rate"] == 13.0

def test_config_err(monkeypatch):
    def boom():
        raise CurrentDataError("offline")
    monkeypatch.setattr("src.selix.spi.fetch_current_selic", boom)
    assert config.get_selic_atual_from_bcb()["success"] is False

def test_dif():
    assert isinstance(config.get_diferencial(15.0), float)

def test_dif_bcb_ok(monkeypatch):
    monkeypatch.setattr(config, "get_selic_atual_from_bcb", lambda: {"success": True, "rate": 14.0})
    assert config.get_diferencial(None) == round(14.0 - float(config.SELIC_IDEAL), 2)

def test_dif_bcb_fail(monkeypatch):
    monkeypatch.setattr(config, "get_selic_atual_from_bcb", lambda: {"success": False})
    assert config.get_diferencial(None) is None

def test_credito_unavail(monkeypatch):
    monkeypatch.setattr(BCBProvider, "get_selic_meta", lambda self: {"success": False})
    assert analisar_credito_pj("PETR4")["status"] == "unavailable"

def test_credito_class(monkeypatch):
    monkeypatch.setattr(BCBProvider, "get_selic_meta", lambda self: {"success": True, "rate": 10.0, "serie": 432, "data_bcb": "01/01/2026"})
    monkeypatch.setattr("src.selix.credito.get_roic_por_codigo", lambda c: 50.0)
    assert "baixo risco" in analisar_credito_pj("X")["classificacao"]
    monkeypatch.setattr("src.selix.credito.get_roic_por_codigo", lambda c: float(config.SELIC_IDEAL) - 1.0)
    assert "moderado" in analisar_credito_pj("X")["classificacao"]
    monkeypatch.setattr("src.selix.credito.get_roic_por_codigo", lambda c: 0.1)
    assert "alto risco" in analisar_credito_pj("X")["classificacao"]

def test_portfolio():
    assert analisar_portfolio([]) == []
    assert isinstance(get_empresas_que_batem_selix(), list)

def test_energy_neg():
    assert "mistura" in EnergyPredictor.get_mistura_e(-1.0)
    assert "mistura" in EnergyPredictor.get_mistura_b(-1.0)

def test_roic_fonte():
    assert "CVM" in get_fonte_roic()
    assert get_roic_por_codigo("ZZZZ") is None

def test_cred_empty(monkeypatch):
    monkeypatch.setattr(cred, "HISTORICO", [])
    assert cred.calcular_credibilidade_continua() == 0.50
    assert cred.calcular_credibilidade_binaria() == 0.50
    assert "BCB" in cred.get_fonte_credibilidade()

def test_cred_meta0(monkeypatch):
    monkeypatch.setattr(cred, "HISTORICO", [(2020, 0.0, 1.0)])
    assert cred.calcular_credibilidade_continua() == 0.50

def test_bcb_brent():
    assert BCBProvider().get_brent()["success"] is False

def test_bcb_bad_row(monkeypatch):
    class R:
        def raise_for_status(self): pass
        def json(self): return [{"data": "01/01/2026"}]
    monkeypatch.setattr("src.providers.bcb_provider.requests.get", lambda *a, **k: R())
    with pytest.raises(ValueError):
        BCBProvider()._fetch_sgs(432)

def test_bcb_future(monkeypatch):
    fut = (date.today() + timedelta(days=3)).strftime("%d/%m/%Y")
    class R:
        def raise_for_status(self): pass
        def json(self): return [{"data": fut, "valor": "10.5"}]
    monkeypatch.setattr("src.providers.bcb_provider.requests.get", lambda *a, **k: R())
    with pytest.raises(ValueError, match="future"):
        BCBProvider()._fetch_sgs(432)

def test_bcb_fallback(monkeypatch):
    monkeypatch.setattr(BCBProvider, "get_selic_meta", lambda self: {"success": False})
    monkeypatch.setattr(BCBProvider, "_fetch_sgs", lambda self, codigo: {"success": True, "rate": 11.0, "data_bcb": "01/01/2026", "serie": SGS_DIARIA, "source": f"BCB SGS {SGS_DIARIA}"} if codigo == SGS_DIARIA else (_ for _ in ()).throw(RuntimeError("x")))
    assert BCBProvider().get_selic().get("success") is True

def test_bcb_both_fail(monkeypatch):
    monkeypatch.setattr(BCBProvider, "get_selic_meta", lambda self: {"success": False})
    monkeypatch.setattr(BCBProvider, "_fetch_sgs", lambda self, c: (_ for _ in ()).throw(RuntimeError("down")))
    assert BCBProvider().get_selic()["success"] is False

def test_yahoo(monkeypatch):
    import pandas as pd
    class T:
        def history(self, period="1d"):
            return pd.DataFrame()
    monkeypatch.setattr("src.providers.yahoo_provider.yf.Ticker", lambda s: T())
    assert YahooFinanceProvider().get_brent()["success"] is False
    assert YahooFinanceProvider().get_selic()["success"] is False

def test_strategy_all_fail():
    class P:
        def get_selic(self): return {"success": False}
        def get_brent(self): return {"success": False}
    s = ProviderStrategy()
    s.selic_providers = [P()]
    s.brent_providers = [P()]
    s.circuits = {}
    assert s.get_selic()["success"] is False
    assert s.get_brent()["success"] is False

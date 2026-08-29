import pytest

import fetch_ipca
from fetch_ipca import IPCAFetchError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_realizado_12m_uses_sgs_13522(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse([{"data": "01/07/2026", "valor": "4.44"}])

    monkeypatch.setattr(fetch_ipca.requests, "get", fake_get)
    result = fetch_ipca.fetch_ipca_realizado_12m()

    assert result.valor_pct == 4.44
    assert result.data_referencia == "2026-07"
    assert "SGS 13522" in result.fonte
    assert calls[0][0] == fetch_ipca.SGS_IPCA_12M_URL


def test_esperado_12m_uses_focus_median(monkeypatch):
    def fake_get(url, **kwargs):
        assert url == fetch_ipca.FOCUS_IPCA_12M_URL
        return FakeResponse({
            "value": [{"Data": "2026-08-28", "Indicador": "IPCA", "Mediana": "4.10"}]
        })

    monkeypatch.setattr(fetch_ipca.requests, "get", fake_get)
    result = fetch_ipca.fetch_ipca_esperado_12m()

    assert result.valor_pct == 4.10
    assert result.data_referencia == "2026-08"
    assert "Focus" in result.fonte


def test_realizado_fails_closed_on_empty_response(monkeypatch):
    monkeypatch.setattr(
        fetch_ipca.requests,
        "get",
        lambda *args, **kwargs: FakeResponse([]),
    )
    with pytest.raises(IPCAFetchError):
        fetch_ipca.fetch_ipca_realizado_12m()


def test_esperado_fails_closed_on_empty_response(monkeypatch):
    monkeypatch.setattr(
        fetch_ipca.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"value": []}),
    )
    with pytest.raises(IPCAFetchError):
        fetch_ipca.fetch_ipca_esperado_12m()


def test_build_snapshot_is_not_partial(monkeypatch):
    def fail_realizado(*args, **kwargs):
        raise IPCAFetchError("BCB indisponível")

    monkeypatch.setattr(fetch_ipca, "fetch_ipca_realizado_12m", fail_realizado)
    with pytest.raises(IPCAFetchError):
        fetch_ipca.build_snapshot_fields()

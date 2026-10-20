from fastapi.testclient import TestClient

from src.api import main_v4_fastapi
from src.selix import spi


client = TestClient(main_v4_fastapi.app)


def test_selic_snapshot_uses_spi_current_payload(monkeypatch):
    expected = {
        "status": "current",
        "selic_atual": 14.0,
        "selic_ideal": 8.25,
        "diferencial": 5.75,
        "selic_atual_fonte": "BCB SGS 432",
        "selic_atual_serie": 432,
        "selic_atual_data_bcb": "15/08/2026",
        "fetched_at": "2026-10-20T12:00:00Z",
        "provenance": "runtime:BCB SGS 432",
    }
    monkeypatch.setattr(spi, "build_current_snapshot", lambda: expected)

    response = client.get("/v1/selic/snapshot")

    assert response.status_code == 200
    assert response.json() == expected


def test_selic_snapshot_fails_closed_when_bcb_unavailable(monkeypatch):
    def unavailable():
        raise spi.CurrentDataError("BCB indisponível")

    monkeypatch.setattr(spi, "build_current_snapshot", unavailable)

    response = client.get("/v1/selic/snapshot")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["error"] == "official_bcb_data_unavailable"
    assert body["source"] == "BCB SGS 432"
    assert "selic_atual" not in body
    assert response.headers["cache-control"] == "no-store"

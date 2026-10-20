from src.api import main_v4
from src.selix import spi


def test_deployed_flask_snapshot_returns_spi_current_payload(monkeypatch):
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

    response = main_v4.app.test_client().get("/v1/selic/snapshot")

    assert response.status_code == 200
    assert response.get_json() == expected
    assert response.headers["Cache-Control"] == "no-store"


def test_deployed_flask_snapshot_fails_closed_when_bcb_unavailable(monkeypatch):
    def unavailable():
        raise spi.CurrentDataError("BCB indisponível")

    monkeypatch.setattr(spi, "build_current_snapshot", unavailable)

    response = main_v4.app.test_client().get("/v1/selic/snapshot")

    assert response.status_code == 503
    body = response.get_json()
    assert body["status"] == "unavailable"
    assert body["error"] == "official_bcb_data_unavailable"
    assert "selic_atual" not in body
    assert response.headers["Cache-Control"] == "no-store"

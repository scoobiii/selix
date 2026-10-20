from src.api import server_v4


CURRENT = {
    "status": "current",
    "selic_atual": 14.25,
    "selic_ideal": 8.25,
    "diferencial": 6.0,
    "selic_atual_fonte": "BCB SGS 432",
    "selic_atual_serie": 432,
    "selic_atual_data_bcb": "01/10/2026",
    "fetched_at": "2026-10-20T12:00:00Z",
    "provenance": "runtime:BCB SGS 432",
}


def test_legacy_v4_current_endpoint_uses_spi(monkeypatch):
    monkeypatch.setattr(
        "src.selix.spi.build_current_snapshot",
        lambda: CURRENT,
    )
    response = server_v4.app.test_client().get("/current")

    assert response.status_code == 200
    data = response.get_json()
    assert data["parameters"]["selic_bcb"] == 14.25
    assert data["parameters"]["selic_series"] == 432
    assert data["result"]["provenance"] == "runtime:BCB SGS 432"


def test_legacy_v4_current_endpoint_fails_closed(monkeypatch):
    def unavailable():
        raise RuntimeError("BCB unavailable")

    monkeypatch.setattr("src.selix.spi.build_current_snapshot", unavailable)
    response = server_v4.app.test_client().get("/current")

    assert response.status_code == 503
    data = response.get_json()
    assert data["status"] == "unavailable"
    assert "selic_bcb" not in data


def test_legacy_v4_score_endpoint_fails_closed(monkeypatch):
    def unavailable():
        raise RuntimeError("BCB unavailable")

    monkeypatch.setattr("src.selix.spi.build_current_snapshot", unavailable)
    response = server_v4.app.test_client().get("/score")

    assert response.status_code == 503
    assert response.get_json()["status"] == "unavailable"

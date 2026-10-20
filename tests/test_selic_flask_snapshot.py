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


def test_legacy_selic_endpoint_uses_same_spi_validation(monkeypatch):
    from src.selix import spi

    monkeypatch.setattr(main_v4, "verify_api_key", lambda _key: {
        "id": 1, "rate_limit_per_minute": 100
    })
    monkeypatch.setattr(spi, "fetch_current_selic", lambda: {
        "success": True,
        "rate": 14.25,
        "data_bcb": "01/10/2026",
        "serie": 432,
        "source": "BCB SGS 432",
    })

    response = main_v4.app.test_client().get(
        "/v1/selic", headers={"X-API-Key": "test-key"}
    )

    assert response.status_code == 200
    assert response.get_json()["rate"] == 14.25
    assert response.get_json()["series"] == 432
    assert response.get_json()["source"] == "BCB SGS 432"
    assert response.headers["Cache-Control"] == "no-store"


def test_legacy_selic_endpoint_fails_closed_on_spi_error(monkeypatch):
    from src.selix import spi

    monkeypatch.setattr(main_v4, "verify_api_key", lambda _key: {
        "id": 1, "rate_limit_per_minute": 100
    })

    def unavailable():
        raise spi.CurrentDataError("untrusted BCB response")

    monkeypatch.setattr(spi, "fetch_current_selic", unavailable)
    response = main_v4.app.test_client().get(
        "/v1/selic", headers={"X-API-Key": "test-key"}
    )

    assert response.status_code == 503
    assert response.get_json()["status"] == "unavailable"
    assert "rate" not in response.get_json()
    assert response.headers["Cache-Control"] == "no-store"

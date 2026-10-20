from fastapi.testclient import TestClient

from src.api.main_v4_fastapi import app


def test_missing_optional_dsge_module_returns_503_without_breaking_app():
    response = TestClient(app).get("/v1/dsge/rstar")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "error": "dsge_model_unavailable",
    }
    assert response.headers["cache-control"] == "no-store"

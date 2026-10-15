from unittest.mock import Mock, patch

import pytest

from src.providers.bcb_provider import BCBProvider


def test_fetch_sgs_uses_last_observations_endpoint_and_latest_date():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [
        {"data": "01/10/2026", "valor": "14.25"},
        {"data": "15/09/2026", "valor": "14.50"},
    ]
    with patch("src.providers.bcb_provider.requests.get", return_value=response) as get:
        result = BCBProvider().get_selic_meta()

    assert result["success"] is True
    assert result["serie"] == 432
    assert result["rate"] == 14.25
    assert result["data_bcb"] == "01/10/2026"
    args, kwargs = get.call_args
    assert args[0].endswith("/dados/ultimos/10")
    assert kwargs["params"] == {"formato": "json"}
    assert "dataInicial" not in kwargs["params"]
    assert "dataFinal" not in kwargs["params"]


def test_fetch_sgs_fails_closed_on_empty_response():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = []
    with patch("src.providers.bcb_provider.requests.get", return_value=response):
        result = BCBProvider().get_selic_meta()
    assert result["success"] is False
    assert result["serie"] == 432


def test_fetch_sgs_fails_closed_on_invalid_rate():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [{"data": "01/10/2026", "valor": "NaN"}]
    with patch("src.providers.bcb_provider.requests.get", return_value=response):
        result = BCBProvider().get_selic_meta()
    assert result["success"] is False

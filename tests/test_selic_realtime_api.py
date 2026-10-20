from unittest.mock import patch

from agents.monitor.apis_reais import APIsReais


def test_selic_real_reads_official_bcb_value_with_provenance():
    provider_result = {
        "success": True,
        "rate": 14.25,
        "data_bcb": "01/10/2026",
        "serie": 432,
        "source": "BCB SGS 432",
    }
    with patch(
        "src.providers.bcb_provider.BCBProvider.get_selic_meta",
        return_value=provider_result,
    ) as get_rate:
        result = APIsReais().selic_real()

    get_rate.assert_called_once_with()
    assert result["selic"] == 14.25
    assert result["tipo"] == "selic_meta_bcb"
    assert result["fonte"] == "BCB SGS 432"
    assert result["serie"] == 432
    assert result["observed_at"] == "2026-10-01"
    assert result["fetched_at"]
    assert result["unidade"] == "% a.a."
    assert result["periodo_vigencia_desde"] == "2026-10-01"
    assert result["status"] == "REAL"


def test_selic_real_fails_closed_without_using_cached_or_static_rate():
    failure = {
        "success": False,
        "serie": 432,
        "source": "BCB SGS 432",
        "error": "offline",
    }
    apis = APIsReais()
    apis.cache["selic"] = ({"selic": 14.5, "status": "REAL"}, None)

    with patch(
        "src.providers.bcb_provider.BCBProvider.get_selic_meta",
        return_value=failure,
    ) as get_rate:
        result = apis.selic_real()

    get_rate.assert_called_once_with()
    assert result["status"] == "ERRO"
    assert "selic" not in result
    assert "BCB SGS 432 indisponível" in result["erro"]
    assert result["serie"] == 432


def test_selic_real_rejects_wrong_series():
    with patch(
        "src.providers.bcb_provider.BCBProvider.get_selic_meta",
        return_value={
            "success": True,
            "rate": 14.25,
            "data_bcb": "01/10/2026",
            "serie": 11,
            "source": "BCB SGS 11",
        },
    ):
        result = APIsReais().selic_real()

    assert result["status"] == "ERRO"
    assert "selic" not in result


def test_selic_real_rejects_invalid_rate_or_observation_date():
    cases = [
        {
            "success": True,
            "rate": float("nan"),
            "data_bcb": "01/10/2026",
            "serie": 432,
            "source": "BCB SGS 432",
        },
        {
            "success": True,
            "rate": 14.25,
            "data_bcb": "not-a-date",
            "serie": 432,
            "source": "BCB SGS 432",
        },
    ]
    for provider_result in cases:
        with patch(
            "src.providers.bcb_provider.BCBProvider.get_selic_meta",
            return_value=provider_result,
        ):
            result = APIsReais().selic_real()
        assert result["status"] == "ERRO"
        assert "selic" not in result

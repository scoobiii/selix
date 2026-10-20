from unittest.mock import patch

from agents.monitor.monitor_selic import MonitorSelic


VALID = {
    "success": True,
    "rate": 14.25,
    "data_bcb": "01/10/2026",
    "serie": 432,
    "source": "BCB SGS 432",
}


def test_monitor_reads_validated_official_rate_and_provenance():
    with patch("agents.monitor.monitor_selic.fetch_current_selic", return_value=VALID):
        result = MonitorSelic().buscar_selic_real()

    assert result["selic"] == 14.25
    assert result["fonte"] == "BCB SGS 432"
    assert result["serie"] == 432
    assert result["observed_at"] == "01/10/2026"
    assert result["status"] == "REAL"


def test_monitor_does_not_produce_alert_when_bcb_is_unavailable():
    with patch(
        "agents.monitor.monitor_selic.fetch_current_selic",
        side_effect=RuntimeError("BCB indisponível"),
    ):
        try:
            MonitorSelic().gerar_alerta_copom()
        except RuntimeError as exc:
            assert "BCB indisponível" in str(exc)
        else:
            raise AssertionError("monitor must fail closed when official data is unavailable")


def test_monitor_labels_ideal_as_model_not_copom_decision():
    with (
        patch("agents.monitor.monitor_selic.fetch_current_selic", return_value=VALID),
        patch("agents.monitor.monitor_selic.get_selic_ideal", return_value=8.25),
    ):
        alert = MonitorSelic().gerar_alerta_copom()

    assert "14.25% a.a." in alert
    assert "8.25% a.a." in alert
    assert "não uma previsão ou decisão do COPOM" in alert

import json
from unittest.mock import patch
import pytest
from scripts import build_official_snapshot as snapshot

def _fake_provider(result):
    class FakeBCB:
        def get_selic_meta(self):
            return result
    return FakeBCB

def test_snapshot_uses_official_series_and_derives_differential():
    response = {"success": True, "rate": 13.75, "data_bcb": "01/10/2026", "serie": 432, "source": "BCB SGS 432"}
    with patch("src.providers.bcb_provider.BCBProvider", _fake_provider(response)), patch("src.selix.config.SELIC_IDEAL", 8.25), patch("src.selix.config.TAU", 0.7), patch("src.selix.config.CREDIBILIDADE", 0.4):
        data = snapshot.build_snapshot()
    assert data["market"]["selic_atual"] == 13.75
    assert data["market"]["diferencial_pp"] == 5.5
    assert data["source"]["series"] == 432
    assert data["status"] == "verified"
    assert data["content_sha256"]

def test_snapshot_fails_closed_when_api_unavailable():
    with patch("src.providers.bcb_provider.BCBProvider", _fake_provider({"success": False})):
        with pytest.raises(RuntimeError):
            snapshot.build_snapshot()

def test_snapshot_rejects_wrong_series():
    response = {"success": True, "rate": 13.75, "data_bcb": "01/10/2026", "serie": 11}
    with patch("src.providers.bcb_provider.BCBProvider", _fake_provider(response)):
        with pytest.raises(ValueError, match="SGS 432"):
            snapshot.build_snapshot()

def test_snapshot_rejects_missing_observation_date():
    response = {"success": True, "rate": 13.75, "serie": 432}
    with patch("src.providers.bcb_provider.BCBProvider", _fake_provider(response)):
        with pytest.raises(ValueError, match="date missing"):
            snapshot.build_snapshot()

def test_publisher_rejects_snapshot_without_provenance(tmp_path):
    from scripts import bluesky_ci_publisher as publisher
    target = publisher.SNAPSHOT_PATH
    old = target.read_text(encoding="utf-8") if target.exists() else None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"selic_atual": 14.0}), encoding="utf-8")
        with pytest.raises((ValueError, KeyError)):
            publisher.load_snapshot()
    finally:
        if old is None:
            target.unlink(missing_ok=True)
        else:
            target.write_text(old, encoding="utf-8")

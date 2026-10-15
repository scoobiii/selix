import hashlib
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


def _publisher_snapshot():
    data = {
        "schema_version": "1",
        "status": "verified",
        "source": {"provider": "Banco Central do Brasil", "series": 432, "observation_date": "01/10/2026"},
        "generated_at": "2026-10-14T00:00:00+00:00",
        "model": {"selic_ideal": 8.25, "tau": 0.7, "credibilidade": 0.4},
        "market": {"selic_atual": 13.75, "diferencial_pp": 5.5},
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    data["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return data


def test_publisher_accepts_matching_snapshot_hash(tmp_path):
    from scripts import bluesky_ci_publisher as publisher
    target = tmp_path / "snapshot.json"
    target.write_text(json.dumps(_publisher_snapshot()), encoding="utf-8")
    with patch.object(publisher, "SNAPSHOT_PATH", target):
        assert publisher.load_snapshot()["market"]["selic_atual"] == 13.75


def test_publisher_rejects_snapshot_when_content_changes_without_hash_update(tmp_path):
    from scripts import bluesky_ci_publisher as publisher
    data = _publisher_snapshot()
    # Change metadata that does not affect the arithmetic invariant so this
    # test specifically exercises content-hash verification.
    data["model"]["tau"] = 0.8
    target = tmp_path / "snapshot.json"
    target.write_text(json.dumps(data), encoding="utf-8")
    with patch.object(publisher, "SNAPSHOT_PATH", target):
        with pytest.raises(ValueError, match="content_sha256 mismatch"):
            publisher.load_snapshot()


def test_publisher_rejects_snapshot_without_provenance(tmp_path):
    from scripts import bluesky_ci_publisher as publisher
    target = tmp_path / "snapshot.json"
    target.write_text(json.dumps({"selic_atual": 14.0}), encoding="utf-8")
    with patch.object(publisher, "SNAPSHOT_PATH", target):
        with pytest.raises((ValueError, KeyError)):
            publisher.load_snapshot()

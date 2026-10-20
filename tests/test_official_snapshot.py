import hashlib
import json
from unittest.mock import patch

import pytest

from scripts import build_official_snapshot as snapshot
from src.selix.spi import CurrentDataError


CURRENT = {
    "status": "current",
    "selic_atual": 13.75,
    "selic_ideal": 8.25,
    "diferencial": 5.5,
    "selic_atual_fonte": "BCB SGS 432",
    "selic_atual_serie": 432,
    "selic_atual_data_bcb": "01/10/2026",
    "fetched_at": "2026-10-20T12:00:00Z",
    "provenance": "runtime:BCB SGS 432",
}


def test_snapshot_uses_official_series_and_derives_differential():
    with (
        patch("src.selix.spi.build_current_snapshot", return_value=CURRENT.copy()),
        patch("src.selix.spi.assert_current_provenance"),
    ):
        data = snapshot.build_snapshot()

    assert data["market"]["selic_observada_snapshot"] == 13.75
    assert data["market"]["diferencial_snapshot_pp"] == 5.5
    assert data["source"]["series"] == 432
    assert data["status"] == "historical_snapshot"
    assert data["is_current"] is False
    assert data["content_sha256"]


def test_snapshot_fails_closed_when_spi_unavailable():
    with patch(
        "src.selix.spi.build_current_snapshot",
        side_effect=CurrentDataError("BCB indisponível"),
    ):
        with pytest.raises(CurrentDataError):
            snapshot.build_snapshot()


def test_snapshot_rejects_wrong_series():
    wrong = {**CURRENT, "selic_atual_serie": 11}
    with patch("src.selix.spi.build_current_snapshot", return_value=wrong):
        with pytest.raises(CurrentDataError, match="BCB SGS 432"):
            snapshot.build_snapshot()


def test_snapshot_rejects_missing_observation_date():
    missing = {**CURRENT, "selic_atual_data_bcb": None}
    with patch("src.selix.spi.build_current_snapshot", return_value=missing):
        with pytest.raises(CurrentDataError, match="observation date"):
            snapshot.build_snapshot()


def test_publisher_builds_payload_from_live_spi_and_hashes_it():
    from scripts import bluesky_ci_publisher as publisher

    with (
        patch("src.selix.spi.build_current_snapshot", return_value=CURRENT.copy()),
        patch("src.selix.spi.assert_current_provenance"),
    ):
        data = publisher.load_live_snapshot()

    assert data["selic_atual"] == 13.75
    assert data["provenance"] == "runtime:BCB SGS 432"
    assert data["content_sha256"]
    canonical = json.dumps(
        {key: value for key, value in data.items() if key != "content_sha256"},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    assert data["content_sha256"] == hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_publisher_rejects_untrusted_provenance():
    from scripts import bluesky_ci_publisher as publisher

    wrong = {**CURRENT, "provenance": "static:snapshot"}
    with patch("src.selix.spi.build_current_snapshot", return_value=wrong):
        with pytest.raises(CurrentDataError):
            publisher.load_live_snapshot()

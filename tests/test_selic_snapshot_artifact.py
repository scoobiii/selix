import json

from scripts import build_official_snapshot


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


def test_generated_snapshot_is_never_marked_current(monkeypatch):
    monkeypatch.setattr("src.selix.spi.build_current_snapshot", lambda: CURRENT.copy())
    monkeypatch.setattr("src.selix.spi.assert_current_provenance", lambda _data: None)

    artifact = build_official_snapshot.build_snapshot()

    assert artifact["status"] == "historical_snapshot"
    assert artifact["is_current"] is False
    assert artifact["market"]["selic_observada_snapshot"] == 14.25
    assert "selic_atual" not in artifact
    assert "selic_atual" not in artifact["market"]


def test_snapshot_writer_rejects_current_payload(monkeypatch, tmp_path):
    target_a = tmp_path / "selix-official.json"
    target_b = tmp_path / "public" / "selix-official.json"
    monkeypatch.setattr(build_official_snapshot, "OUTPUTS", (target_a, target_b))

    try:
        build_official_snapshot.write_snapshot({"status": "current", "is_current": True})
    except ValueError as exc:
        assert "historical-only" in str(exc)
    else:
        raise AssertionError("writer must reject an artifact marked CURRENT")

    assert not target_a.exists()
    assert not target_b.exists()


def test_public_committed_snapshot_is_historical_only():
    path = build_official_snapshot.ROOT / "public" / "selix-official.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))

    assert artifact["status"] == "historical_snapshot"
    assert artifact["is_current"] is False
    assert "selic_atual" not in artifact

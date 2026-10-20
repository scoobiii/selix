#!/usr/bin/env python3
"""Build an explicitly historical artifact; never label a committed JSON as CURRENT."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUTPUTS = (ROOT / "selix-official.json", ROOT / "public" / "selix-official.json")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_rate(value: Any, field: str) -> float:
    import math

    rate = float(value)
    if not math.isfinite(rate) or not 0.0 < rate < 100.0:
        raise ValueError(f"{field} outside valid percentage range")
    return round(rate, 4)


def build_snapshot() -> dict[str, Any]:
    from src.selix.spi import build_current_snapshot, assert_current_provenance

    current = build_current_snapshot()
    assert_current_provenance(current)

    observed = _validate_rate(current["selic_atual"], "selic_observada_snapshot")
    ideal = _validate_rate(current["selic_ideal"], "selic_ideal_snapshot")
    differential = round(observed - ideal, 2)
    if abs(differential - float(current["diferencial"])) > 0.001:
        raise ValueError("SELIX differential does not reconcile")

    payload: dict[str, Any] = {
        "schema_version": "2",
        "status": "historical_snapshot",
        "is_current": False,
        "warning": (
            "Versioned artifact for archival/distribution only. It is not a live API "
            "response and MUST NOT be used as a CURRENT fallback."
        ),
        "source": {
            "provider": "Banco Central do Brasil",
            "series": 432,
            "url": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados",
            "observation_date": current["selic_atual_data_bcb"],
        },
        "snapshot_created_at": _iso_now(),
        "fetched_at": current["fetched_at"],
        "model": {
            "selic_ideal_snapshot": ideal,
        },
        "market": {
            "selic_observada_snapshot": observed,
            "diferencial_snapshot_pp": differential,
        },
        "provenance": current["provenance"],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def write_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("status") != "historical_snapshot" or snapshot.get("is_current") is not False:
        raise ValueError("refusing to write artifact without historical-only marker")
    encoded = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    for target in OUTPUTS:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=target.name, dir=target.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        except Exception:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise


def main() -> None:
    snapshot = build_snapshot()
    write_snapshot(snapshot)
    print(json.dumps({
        "status": snapshot["status"],
        "is_current": snapshot["is_current"],
        "source": snapshot["source"],
        "content_sha256": snapshot["content_sha256"],
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

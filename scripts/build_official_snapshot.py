#!/usr/bin/env python3
"""Build the canonical SELIX public snapshot from live official data.

No market-rate fallback is permitted. Output files are deterministic except for
observation/build timestamps and are written only after all inputs validate.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (ROOT / "selix-official.json", ROOT / "public" / "selix-official.json")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _validate_rate(value: Any, field: str) -> float:
    rate = float(value)
    if not (0.0 < rate < 100.0):
        raise ValueError(f"{field} outside valid percentage range")
    return round(rate, 4)


def build_snapshot() -> dict[str, Any]:
    from src.selix.config import SELIC_IDEAL, TAU, CREDIBILIDADE
    from src.providers.bcb_provider import BCBProvider

    result = BCBProvider().get_selic_meta()
    if not result.get("success"):
        raise RuntimeError(f"Official BCB SGS 432 observation unavailable: {result!r}")
    if result.get("serie") != 432:
        raise ValueError("Selic meta must come from BCB SGS 432 only")
    if not result.get("data_bcb"):
        raise ValueError("BCB observation date missing")

    selic_atual = _validate_rate(result.get("rate"), "selic_atual")
    selic_ideal = _validate_rate(SELIC_IDEAL, "selic_ideal")
    diferencial = round(selic_atual - selic_ideal, 2)
    tau = float(TAU)
    credibilidade = float(CREDIBILIDADE)
    if not 0.0 <= tau <= 1.0:
        raise ValueError("tau outside valid range")
    if not 0.0 <= credibilidade <= 1.0:
        raise ValueError("credibilidade outside valid range")

    payload: dict[str, Any] = {
        "schema_version": "1",
        "status": "verified",
        "source": {
            "provider": "Banco Central do Brasil",
            "series": 432,
            "url": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados",
            "observation_date": result["data_bcb"],
        },
        "generated_at": _iso_now(),
        "model": {
            "selic_ideal": selic_ideal,
            "tau": round(tau, 6),
            "credibilidade": round(credibilidade, 6),
        },
        "market": {
            "selic_atual": selic_atual,
            "diferencial_pp": diferencial,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def write_snapshot(snapshot: dict[str, Any]) -> None:
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
        "source": snapshot["source"],
        "content_sha256": snapshot["content_sha256"],
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

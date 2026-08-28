#!/usr/bin/env python3
"""Cross-repository validation: SELIX model -> Vortex SELIX runtime."""
from __future__ import annotations

import json
import os
import subprocess
import sys

from src.selix.config import get_selic_ideal
from src.selix.core import BASELINE_ATUAL


def main() -> int:
    vortex = os.environ.get("VORTEX_DIR", "vortex-source")
    ideal = get_selic_ideal()
    ipca = BASELINE_ATUAL.inflacao_esperada
    request = {
        "invocation_id": "selix-repo-vortex-validation",
        "agent": "selix",
        "action": "selix.selic1d",
        "payload": {
            "selic_atual": 14.25,
            "selic_ideal": ideal,
            "ipca": ipca,
            "source": "scoobiii/selix@HEAD",
        },
        "context": {"sandbox": True},
    }
    env = os.environ.copy()
    env["SELIX_INVOCATION_JSON"] = json.dumps(request, separators=(",", ":"))
    proc = subprocess.run(
        ["npm", "run", "selix:selic1d"],
        cwd=vortex,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")
    if proc.returncode != 0:
        return proc.returncode
    result = json.loads(proc.stdout)
    if result.get("gate") != "PASS" or result.get("executed") is not True:
        print("CROSS-REPO GATE: FAIL", file=sys.stderr)
        return 1
    if result.get("evidence", {}).get("exit_code") != 0:
        print("CROSS-REPO PROOF: FAIL", file=sys.stderr)
        return 1
    if result.get("result", {}).get("selic_ideal") != round(ideal, 2):
        print("SELIX/Vortex result mismatch", file=sys.stderr)
        return 1
    print("CROSS-REPO GATE: PASS")
    print(f"SELIX model ideal: {ideal:.2f}")
    print(f"Vortex output hash: {result['evidence']['output_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

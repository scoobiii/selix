#!/usr/bin/env python3
"""Run the SELIX model through the real VUC governed execution pipeline."""
from __future__ import annotations

import json
import os
import subprocess
import sys

from src.selix.config import get_selic_ideal
from src.selix.core import BASELINE_ATUAL


def main() -> int:
    vuc = os.environ.get("VUC_DIR", "vuc-source")
    ideal = round(get_selic_ideal(), 2)
    payload = {
        "selic_ideal": ideal,
        "ipca": float(BASELINE_ATUAL.inflacao_esperada),
        "source": "scoobiii/selix",
    }
    env = os.environ.copy()
    env["SELIX_RESULT_JSON"] = json.dumps(payload, separators=(",", ":"))

    # Run inside the checked-out VUC repository. The SELIX result is passed
    # through VUC's governed execution pipeline and its proof is verified.
    js = r'''
import { executeVortexPipeline } from "./src/vortex/gateway.ts";
import { verifyExecutionProof } from "./src/vortex/verifier.ts";

const selix = JSON.parse(process.env.SELIX_RESULT_JSON);
const response = await executeVortexPipeline(
  {
    request_id: `selix-ci-${process.env.GITHUB_RUN_ID || "local"}-${Date.now()}`,
    operation: "inspect",
    target: { resource: "selix://model" },
    input: { selix, source: "scoobiii/selix" }
  },
  async () => ({ selix, source: "scoobiii/selix" })
);
const proof = response.execution_proof;
const verification = proof ? verifyExecutionProof(proof) : { valid: false, reasons: ["missing proof"] };
console.log(JSON.stringify({
  status: response.status,
  output: response.output,
  proof: proof ? { executed: proof.executed, status: proof.status, output_hash: proof.output_hash, proof_hash: proof.proof_hash } : null,
  proof_valid: verification.valid,
  verification_reasons: verification.reasons
}));
if (response.status !== "EXECUTION_SUCCESS" || !proof || proof.executed !== true ||
    !verification.valid || response.output?.selix?.selic_ideal !== selix.selic_ideal) {
  process.exitCode = 1;
}
'''
    proc = subprocess.run(
        ["node", "--import", "tsx", "--input-type=module", "-e", js],
        cwd=vuc, env=env, text=True, capture_output=True, check=False,
    )
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")
    if proc.returncode != 0:
        print("SELIX → VUC governed execution: FAIL", file=sys.stderr)
        return proc.returncode

    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        print("VUC did not emit a parseable JSON result", file=sys.stderr)
        return 1

    if result.get("status") != "EXECUTION_SUCCESS":
        print(f"VUC status mismatch: {result.get('status')}", file=sys.stderr)
        return 1
    if result.get("proof_valid") is not True or result.get("proof", {}).get("executed") is not True:
        print("VUC execution proof invalid or execution not confirmed", file=sys.stderr)
        return 1
    if result.get("output", {}).get("selix", {}).get("selic_ideal") != ideal:
        print("SELIX/VUC output mismatch", file=sys.stderr)
        return 1

    print("SELIX → VUC: PASS")
    print(f"SELIX ideal: {ideal:.2f}%")
    print(f"VUC proof hash: {result['proof']['proof_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

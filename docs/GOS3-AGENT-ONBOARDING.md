# GOS3 Agent Onboarding — SELIX CURRENT data

SELIX is a decision-support model. Its ideal rate is a model output, not a BCB decision.

## Canonical runtime input

A versioned JSON file in GitHub is an archival snapshot, never a live source. To claim a value is CURRENT, configure `SELIX_API_BASE_URL` with the actual deployed service URL and request:

`GET {SELIX_API_BASE_URL}/v1/selic/snapshot`

The deployment URL is environment-specific; this repository does not assert that a custom public hostname exists.

## Required validation

Accept a response as CURRENT only when all of these hold:

- HTTP status is 200;
- `status === "current"`;
- `selic_atual_fonte === "BCB SGS 432"`;
- `selic_atual_serie === 432`;
- `provenance === "runtime:BCB SGS 432"`;
- `selic_atual_data_bcb` is present;
- `selic_atual` is finite and in the valid percentage range;
- `diferencial` reconciles with `selic_atual - selic_ideal` under the documented rounding policy.

If the service returns 503, malformed data, or fails any check, stop. Do not fall back to GitHub Raw, a prior response, a fixture, a prompt, or a hardcoded rate.

## Minimal JavaScript consumer

```js
export async function getCurrentSelixSnapshot() {
  const base = process.env.SELIX_API_BASE_URL;
  if (!base) throw new Error("SELIX_API_BASE_URL is required");

  const response = await fetch(
    `${base.replace(/\\/$/, "")}/v1/selic/snapshot`,
    { cache: "no-store", headers: { Accept: "application/json" } }
  );
  if (!response.ok) throw new Error(`SELIX HTTP ${response.status}`);

  const data = await response.json();
  if (
    data.status !== "current" ||
    data.selic_atual_fonte !== "BCB SGS 432" ||
    data.selic_atual_serie !== 432 ||
    data.provenance !== "runtime:BCB SGS 432" ||
    !data.selic_atual_data_bcb ||
    !Number.isFinite(data.selic_atual) ||
    !(data.selic_atual > 0 && data.selic_atual < 100)
  ) {
    throw new Error("SELIX response lacks valid live BCB provenance");
  }

  const differential = Number((data.selic_atual - data.selic_ideal).toFixed(2));
  if (differential !== Number(data.diferencial)) {
    throw new Error("SELIX differential does not reconcile");
  }
  return data;
}
```

## SELIX → Vortex

The Vortex execution payload must be derived from the validated runtime response. The proof must bind to the payload actually executed, and the verifier must use an explicit trust store. A generated key identifier alone is not a trusted public key.

## Historical snapshot

`public/selix-official.json` is marked `status=historical_snapshot` and `is_current=false`. It is for archival/distribution only and must not be accepted as a CURRENT input.

## Security rule

Never turn a value observed in a previous run, README, chat, fixture, screenshot, or historical log into the current official input.

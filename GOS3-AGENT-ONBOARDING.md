# GOS3 Agent Onboarding — SELIX official snapshot

SELIX is a decision-support tool. It does not replace COPOM decisions.

## Canonical input contract

Users and agents MUST obtain the current SELIX snapshot from the canonical public endpoint:

https://raw.githubusercontent.com/scoobiii/selix/main/public/selix-official.json

Do not embed economic observations in agent code, tests, prompts, fixtures, or documentation. Read the JSON at execution time and validate its provenance fields.

## Required validation

A consumer MUST validate at least:

- the HTTP request succeeded;
- the response is valid JSON;
- required fields exist: `selic_ideal`, `diferencial`, `selic_atual`, `selic_atual_fonte`, `selic_atual_serie`, `selic_atual_data_bcb`, `versao`;
- `selic_atual_fonte` identifies the BCB source;
- `selic_atual_serie` identifies the BCB series;
- `selic_atual_data_bcb` is present;
- `diferencial` equals `selic_atual - selic_ideal`, using the repository's documented rounding policy.

If validation fails, stop. Do not substitute a remembered or hardcoded value.

## Minimal JavaScript consumer

```js
const SNAPSHOT_URL =
  "https://raw.githubusercontent.com/scoobiii/selix/main/public/selix-official.json";

export async function getOfficialSelixSnapshot() {
  const response = await fetch(SNAPSHOT_URL, { cache: "no-store" });
  if (!response.ok) throw new Error(`SELIX snapshot HTTP ${response.status}`);

  const snapshot = await response.json();
  const required = [
    "selic_ideal",
    "diferencial",
    "selic_atual",
    "selic_atual_fonte",
    "selic_atual_serie",
    "selic_atual_data_bcb",
    "versao",
  ];

  for (const field of required) {
    if (!(field in snapshot)) throw new Error(`Missing snapshot field: ${field}`);
  }

  const expected = Number(
    (Number(snapshot.selic_atual) - Number(snapshot.selic_ideal)).toFixed(2)
  );

  if (expected !== Number(snapshot.diferencial)) {
    throw new Error("SELIX snapshot inconsistent: diferencial does not match inputs");
  }

  return snapshot;
}
```

## SELIX → Vortex validation

The Vortex integration MUST pass the snapshot-derived payload through the invocation boundary. The runtime MUST NOT replace snapshot fields with constants.

The proof MUST bind to the payload actually executed:

1. fetch official snapshot;
2. validate snapshot;
3. construct invocation payload from snapshot fields;
4. execute SELIX through Vortex;
5. validate `gate`, `executed`, `exit_code`, `input_hash`, and `output_hash`;
6. verify that the proof input corresponds to the invocation payload.

## Snapshot generation

The repository's snapshot generator obtains the current rate from the BCB integration and writes `public/selix-official.json`. The generated file is the public machine-readable contract; consumers should not reconstruct it from README prose.

## Fallbacks

If the canonical raw endpoint is unavailable, use the repository's GitHub Pages publication if available, or query the BCB source directly according to the SELIX data policy. A fallback MUST remain live/dynamic and MUST NOT be replaced by a hardcoded observation.

## Security / anti-hallucination rule

Never turn a value observed in a previous run, README, chat, fixture, screenshot, or historical log into the current official input. The snapshot is the machine-readable source of truth for the execution being performed.

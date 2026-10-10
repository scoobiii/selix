# Brazil long-term economic targets — SELIX

**Owner:** Zeh Sobrinho  
**Version:** 1.0.0  
**Status:** Draft target specification; not a forecast or a change to the official SELIX rate.

## Purpose

Keep three long-run ambitions in one machine-readable contract while separating observed data, policy targets, and model estimates:

- Nominal GDP per capita: approximately US$10,000 to an aspirational US$130,000 (13×).
- Selic: from two-digit to single-digit nominal annual rates (below 10%); this is not a forecast that the rate will reach 6.25%.
- Electricity use per capita: approximate reference of 2,300 to an aspirational 20,000 kWh/person/year (about 8.70×), pending confirmation that the baseline and target use the same total-versus-residential definition.

The contract lives in [`data/national_targets_br.json`](../data/national_targets_br.json).

## Integration rules

1. **Do not overwrite the SELIX official/ideal Selic value.** The target contract is a separate long-horizon policy scenario.
2. **Do not present approximate baselines as current official observations.** Unknown observation year is explicitly `null`; populate it only after fetching and recording the source vintage.
3. **GDP per capita:** use World Bank indicator `NY.GDP.PCAP.CD`. A credible pathway needs explicit population, real GDP growth, inflation, and exchange-rate assumptions. Current US dollars can change materially without equivalent real-income gains.
4. **Electricity per capita:** use World Bank indicator `EG.USE.ELEC.KH.PC` for total electricity use. Do not compare it directly with residential-only EPE series. Track firm generation, transmission, storage, cost, reliability, and curtailment.
5. **Selic:** source observed policy-rate data from BCB/SGS. Keep observed Selic, SELIX-estimated ideal rate, and the single-digit goal as three separate fields.
6. **Scenario horizons:** 2035 and 2050 are analysis horizons, not commitments or model predictions. No interpolated annual path is asserted in this initial schema.

## Acceptance checks

- All indicators carry units, provenance, status, and assumptions.
- Missing baseline years and missing observed Selic values remain null rather than being fabricated.
- Targets are explicitly labeled aspirational.
- Energy scope and nominal-USD caveats are visible to consumers.
- Any future API/dashboard integration adds schema validation and tests before exposing these fields.

## Sources

- [World Bank — GDP per capita (current US$)](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=BR)
- [World Bank — electricity use per capita](https://data.worldbank.org/indicator/EG.USE.ELEC.KH.PC?locations=BR)
- [Banco Central do Brasil — SGS time series](https://www3.bcb.gov.br/sgspub/)
- [EPE — residential electricity consumption by income class](https://epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/fact-sheet-consumo-residencial-de-energia-por-classes-de-renda)

Closes #3.

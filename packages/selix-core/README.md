# SELIX Core (npm MVP)

Deterministic JavaScript implementation of the SELIX v7.2 calculation core. Zero runtime dependencies. Node.js 20+.

> **MVP status:** this package is a JS implementation of the deterministic model, not a complete port of the Python application. It does not fetch BCB data, call an LLM, provide a financial recommendation, or claim that a supplied market value is current.

## Install

After publication:

```bash
npm install selix-core
```

Until published, test from the repository:

```bash
cd packages/selix-core
npm test
npm pack --dry-run
```

## API

```js
import { calcularSelix } from "selix-core";

const result = calcularSelix({
  inflacaoEsperada: 4.48,
  premioRisco: 1.25,
  credibilidade: 0.5,
  gapProduto: 0.5
});

console.log(result.selic_ideal_quantizada);
console.log(result.selic_atual); // null unless supplied explicitly
console.log(result.diferencial_pp); // null unless current Selic supplied
```

Optional inputs: `selicAtual`, `mix`, and `choqueEnergia`. The default energy mix is 32% ethanol in gasoline and 15% biodiesel in diesel, weighted 0.42 / 0.58. `selicAtual` must only be supplied by a caller that independently validates the BCB observation and provenance.

## CLI

Reads a JSON request from stdin:

```bash
echo '{"inputs":{"inflacaoEsperada":4.48,"premioRisco":1.25,"credibilidade":0.5,"gapProduto":0.5}}' | npx selix-core
```

Shape: `{"inputs":{...},"options":{"choqueEnergia":0}}`. The CLI does not retrieve live data. Errors are emitted as JSON on stderr and exit nonzero.

## Model

Mirrors the deterministic functions in `src/selix/core.py`:

- `tau = clamp(1 - (pesoGasolina × etanol + pesoDiesel × biodiesel), 0, 1)`
- `juro_real_necessario = inflação_efetiva + prêmio_risco / credibilidade + 0.5 × gap_produto`
- `selic_ideal_quantizada` floors the result to the 0.25 p.p. COPOM grid.

This implementation should be kept in parity with the Python core by shared golden test vectors before a stable 1.0.0 release.

## Safety and limitations

- No live data adapter is included in this MVP.
- No stale data can become “current” inside this package because it does not fetch or infer current observations.
- The JS implementation is not yet proven bit-for-bit equivalent to Python for every floating-point edge case.
- Outputs are model estimates for research/decision support, not financial advice or a substitute for professional review.

## Development

```bash
npm test
npm pack --dry-run
```

Repository: https://github.com/scoobiii/selix

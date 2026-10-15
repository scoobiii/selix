/**
 * SELIX deterministic economic core.
 *
 * This package calculates the model only. It never fetches market data and
 * never fabricates a current Selic observation. Supply selicAtual only when
 * the caller has independently validated its current-data provenance.
 */

export const COPOM_GRID = 0.25;

function finiteNumber(name, value) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new TypeError(`${name} must be a finite number`);
  }
}

function validateInputs(inputs) {
  if (!inputs || typeof inputs !== "object" || Array.isArray(inputs)) {
    throw new TypeError("inputs must be an object");
  }
  for (const key of ["inflacaoEsperada", "premioRisco", "credibilidade", "gapProduto"]) {
    finiteNumber(key, inputs[key]);
  }
  if (inputs.credibilidade <= 0) {
    throw new RangeError("credibilidade must be > 0");
  }
}

function validateMix(mix) {
  for (const key of ["etanolGasolina", "biodieselDiesel", "pesoGasolina", "pesoDiesel"]) {
    finiteNumber(key, mix[key]);
  }
  for (const key of ["etanolGasolina", "biodieselDiesel"]) {
    if (mix[key] < 0 || mix[key] > 100) {
      throw new RangeError(`${key} must be between 0 and 100`);
    }
  }
  if (mix.pesoGasolina < 0 || mix.pesoDiesel < 0) {
    throw new RangeError("energy weights must be >= 0");
  }
}

export function calcularTau(mix = {}) {
  const normalized = {
    etanolGasolina: mix.etanolGasolina ?? 32,
    biodieselDiesel: mix.biodieselDiesel ?? 15,
    pesoGasolina: mix.pesoGasolina ?? 0.42,
    pesoDiesel: mix.pesoDiesel ?? 0.58,
  };
  validateMix(normalized);
  const renewableWeight =
    normalized.pesoGasolina * (normalized.etanolGasolina / 100) +
    normalized.pesoDiesel * (normalized.biodieselDiesel / 100);
  return Math.round(Math.max(0, Math.min(1, 1 - renewableWeight)) * 10000) / 10000;
}

export function quantizarCopom(valor, grid = COPOM_GRID) {
  finiteNumber("valor", valor);
  finiteNumber("grid", grid);
  if (grid <= 0) throw new RangeError("grid must be > 0");
  return Math.round(Math.floor(valor / grid) * grid * 100) / 100;
}

export function calcularJuroRealNecessario(inputs, { tau = 0.67, choqueEnergia = 0 } = {}) {
  validateInputs(inputs);
  finiteNumber("tau", tau);
  finiteNumber("choqueEnergia", choqueEnergia);
  if (tau < 0 || tau > 1) throw new RangeError("tau must be between 0 and 1");
  const inflacaoEfetiva = inputs.inflacaoEsperada + tau * choqueEnergia;
  return inflacaoEfetiva + inputs.premioRisco / inputs.credibilidade + 0.5 * inputs.gapProduto;
}

/**
 * @param {{inflacaoEsperada:number,premioRisco:number,credibilidade:number,gapProduto:number}} inputs
 * @param {{selicAtual?:number|null,mix?:object,choqueEnergia?:number}} options
 */
export function calcularSelix(inputs, { selicAtual = null, mix = {}, choqueEnergia = 0 } = {}) {
  validateInputs(inputs);
  if (selicAtual !== null) finiteNumber("selicAtual", selicAtual);
  finiteNumber("choqueEnergia", choqueEnergia);
  const normalizedMix = {
    etanolGasolina: mix.etanolGasolina ?? 32,
    biodieselDiesel: mix.biodieselDiesel ?? 15,
    pesoGasolina: mix.pesoGasolina ?? 0.42,
    pesoDiesel: mix.pesoDiesel ?? 0.58,
  };
  const tau = calcularTau(normalizedMix);
  const juroReal = calcularJuroRealNecessario(inputs, { tau, choqueEnergia });
  const selicIdeal = quantizarCopom(juroReal);
  return {
    inflacao_esperada: inputs.inflacaoEsperada,
    premio_risco: inputs.premioRisco,
    credibilidade: inputs.credibilidade,
    gap_produto: inputs.gapProduto,
    etanol_pct: normalizedMix.etanolGasolina,
    biodiesel_pct: normalizedMix.biodieselDiesel,
    tau,
    choque_energia_pp: choqueEnergia,
    inflacao_efetiva: Math.round((inputs.inflacaoEsperada + tau * choqueEnergia) * 1000) / 1000,
    juro_real_necessario: Math.round(juroReal * 100) / 100,
    selic_ideal_continua: Math.round(juroReal * 100) / 100,
    selic_ideal_quantizada: selicIdeal,
    selic_atual: selicAtual,
    diferencial_pp: selicAtual === null ? null : Math.round((selicAtual - selicIdeal) * 100) / 100,
  };
}

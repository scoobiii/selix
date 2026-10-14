import test from "node:test";
import assert from "node:assert/strict";
import { calcularSelix } from "../src/index.js";

/**
 * Golden vectors derived from src/selix/core.py (main), using explicit inputs
 * and EnergyMix defaults. Keep these vectors in sync with the Python core.
 * This is a deterministic regression check; it does not execute Python in CI.
 */
const vectors = [
  {
    name: "baseline, no energy shock, no current market observation",
    inputs: {
      inflacaoEsperada: 4.48,
      premioRisco: 1.25,
      credibilidade: 0.5,
      gapProduto: 0.5,
    },
    options: { choqueEnergia: 0 },
    expected: {
      tau: 0.7786,
      inflacao_efetiva: 4.48,
      juro_real_necessario: 7.23,
      selic_ideal_continua: 7.23,
      selic_ideal_quantizada: 7,
      selic_atual: null,
      diferencial_pp: null,
    },
  },
  {
    name: "baseline with one percentage-point energy shock",
    inputs: {
      inflacaoEsperada: 4.48,
      premioRisco: 1.25,
      credibilidade: 0.5,
      gapProduto: 0.5,
    },
    options: { choqueEnergia: 1 },
    expected: {
      tau: 0.7786,
      inflacao_efetiva: 5.259,
      juro_real_necessario: 8.01,
      selic_ideal_continua: 8.01,
      selic_ideal_quantizada: 8,
      selic_atual: null,
      diferencial_pp: null,
    },
  },
  {
    name: "explicitly supplied current rate remains distinct from model output",
    inputs: {
      inflacaoEsperada: 4.48,
      premioRisco: 1.25,
      credibilidade: 0.5,
      gapProduto: 0.5,
    },
    options: { selicAtual: 13.75 },
    expected: {
      tau: 0.7786,
      inflacao_efetiva: 4.48,
      juro_real_necessario: 7.23,
      selic_ideal_continua: 7.23,
      selic_ideal_quantizada: 7,
      selic_atual: 13.75,
      diferencial_pp: 6.75,
    },
  },
];

for (const vector of vectors) {
  test(`Python golden vector: ${vector.name}`, () => {
    const actual = calcularSelix(vector.inputs, vector.options);
    for (const [key, value] of Object.entries(vector.expected)) {
      assert.equal(actual[key], value, `${vector.name}: ${key}`);
    }
  });
}

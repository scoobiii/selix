import test from "node:test";
import assert from "node:assert/strict";
import {
  calcularJuroRealNecessario,
  calcularSelix,
  calcularTau,
  quantizarCopom,
} from "../src/index.js";

const baseline = {
  inflacaoEsperada: 4.48,
  premioRisco: 1.25,
  credibilidade: 0.5,
  gapProduto: 0.5,
};

test("default energy transmission factor matches SELIX Python defaults", () => {
  assert.equal(calcularTau(), 0.7786);
});

test("COPOM quantization floors to the 0.25 percentage-point grid", () => {
  assert.equal(quantizarCopom(8.49), 8.25);
  assert.equal(quantizarCopom(8.5), 8.5);
});

test("model does not fabricate current Selic or differential", () => {
  const result = calcularSelix(baseline);
  assert.equal(result.selic_atual, null);
  assert.equal(result.diferencial_pp, null);
  assert.equal(result.selic_ideal_quantizada, 6.75);
});

test("differential is calculated only when current Selic is supplied", () => {
  const result = calcularSelix(baseline, { selicAtual: 14.25 });
  assert.equal(result.selic_atual, 14.25);
  assert.equal(result.diferencial_pp, 7.5);
});

test("energy shock uses tau in effective inflation", () => {
  const result = calcularSelix(baseline, { choqueEnergia: 1 });
  assert.equal(result.inflacao_efetiva, 5.259);
});

test("invalid credibility is rejected", () => {
  assert.throws(() => calcularJuroRealNecessario({ ...baseline, credibilidade: 0 }), /credibilidade/);
});

test("non-finite inputs are rejected", () => {
  assert.throws(() => calcularSelix({ ...baseline, inflacaoEsperada: Number.NaN }), /finite number/);
});

test("energy percentages outside range are rejected", () => {
  assert.throws(() => calcularTau({ etanolGasolina: 150 }), /between 0 and 100/);
});

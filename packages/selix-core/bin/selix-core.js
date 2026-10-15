#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { calcularSelix } from "../src/index.js";

const args = process.argv.slice(2);
if (args.includes("--help") || args.includes("-h")) {
  console.log("Usage: selix-core [--help] < input.json");
  console.log("Reads JSON { inputs: { inflacaoEsperada, premioRisco, credibilidade, gapProduto }, options?: { mix?, choqueEnergia?, selicAtual? } } from stdin.");
  console.log("selicAtual is optional and defaults to null; this CLI does not fetch current market data.");
  process.exit(0);
}
try {
  const raw = readFileSync(0, "utf8");
  if (!raw.trim()) throw new Error("stdin must contain a JSON object");
  const request = JSON.parse(raw);
  if (!request || typeof request !== "object" || !request.inputs) {
    throw new Error("expected { inputs: {...}, options?: {...} }");
  }
  const result = calcularSelix(request.inputs, request.options ?? {});
  process.stdout.write(JSON.stringify({ ok: true, result }, null, 2) + "\n");
} catch (error) {
  process.stderr.write(JSON.stringify({ ok: false, error: error.message }) + "\n");
  process.exitCode = 1;
}

export interface SelixInputs {
  inflacaoEsperada: number;
  premioRisco: number;
  credibilidade: number;
  gapProduto: number;
}

export interface EnergyMix {
  etanolGasolina?: number;
  biodieselDiesel?: number;
  pesoGasolina?: number;
  pesoDiesel?: number;
}

export interface SelixOptions {
  /** Only set this when independently obtained and provenance-validated. Defaults to null. */
  selicAtual?: number | null;
  mix?: EnergyMix;
  choqueEnergia?: number;
}

export declare const COPOM_GRID: 0.25;
export declare function calcularTau(mix?: EnergyMix): number;
export declare function quantizarCopom(valor: number, grid?: number): number;
export declare function calcularJuroRealNecessario(
  inputs: SelixInputs,
  options?: { tau?: number; choqueEnergia?: number }
): number;
export declare function calcularSelix(inputs: SelixInputs, options?: SelixOptions): {
  inflacao_esperada: number;
  premio_risco: number;
  credibilidade: number;
  gap_produto: number;
  etanol_pct: number;
  biodiesel_pct: number;
  tau: number;
  choque_energia_pp: number;
  inflacao_efetiva: number;
  juro_real_necessario: number;
  selic_ideal_continua: number;
  selic_ideal_quantizada: number;
  selic_atual: number | null;
  diferencial_pp: number | null;
};

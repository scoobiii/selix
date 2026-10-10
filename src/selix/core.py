from src.selix.credibilidade_historica import calcular_credibilidade_continua

#!/usr/bin/env python3
"""
SELIX — core.py (v7.2 — com transmissão energética τ + compatibilidade)

Regra de dados: o core calcula o modelo; não é fonte de mercado.
`selic_atual` nunca tem default numérico. A camada SPI/provider é a única
responsável por obter o valor CURRENT do BCB.
"""

from dataclasses import dataclass
from math import floor
from typing import Optional

COPOM_GRID = 0.25

@dataclass(frozen=True)
class SelixInputs:
    inflacao_esperada: float
    premio_risco: float
    credibilidade: float
    gap_produto: float

@dataclass(frozen=True)
class EnergyMix:
    etanol_gasolina: float = 32.0
    biodiesel_diesel: float = 15.0
    peso_gasolina: float = 0.42
    peso_diesel: float = 0.58


def calcular_tau(mix: EnergyMix) -> float:
    renovavel_gasolina = mix.etanol_gasolina / 100.0
    renovavel_diesel = mix.biodiesel_diesel / 100.0
    peso_renovavel = (
        mix.peso_gasolina * renovavel_gasolina
        + mix.peso_diesel * renovavel_diesel
    )
    return round(max(0.0, min(1.0, 1.0 - peso_renovavel)), 4)


def quantizar_copom(valor: float, grid: float = COPOM_GRID) -> float:
    return round(floor(valor / grid) * grid, 2)


def calcular_juro_real_necessario(
    inputs: SelixInputs,
    tau: float = 0.67,
    choque_energia: float = 0.0,
) -> float:
    if inputs.credibilidade <= 0:
        raise ValueError(f"credibilidade deve ser > 0, recebido: {inputs.credibilidade}")
    inflacao_efetiva = inputs.inflacao_esperada + tau * choque_energia
    return (
        inflacao_efetiva
        + (inputs.premio_risco / inputs.credibilidade)
        + 0.5 * inputs.gap_produto
    )


def calcular_selix(
    inputs: SelixInputs,
    selic_atual: Optional[float] = None,
    mix: Optional[EnergyMix] = None,
    choque_energia: float = 0.0,
) -> dict:
    """Calcula o modelo sem buscar mercado e sem inventar SELIC atual.

    Se `selic_atual` for None, o resultado não fabrica um valor: retorna
    `selic_atual=None` e `diferencial_pp=None`. Para uma operação CURRENT,
    o caller deve obter o valor via `src.selix.spi`.
    """
    if mix is None:
        mix = EnergyMix()

    tau = calcular_tau(mix)
    juro_real = calcular_juro_real_necessario(inputs, tau=tau, choque_energia=choque_energia)
    selic_ideal = quantizar_copom(juro_real)
    diferencial = None if selic_atual is None else round(float(selic_atual) - selic_ideal, 2)

    return {
        "inflacao_esperada": inputs.inflacao_esperada,
        "premio_risco": inputs.premio_risco,
        "credibilidade": inputs.credibilidade,
        "gap_produto": inputs.gap_produto,
        "etanol_pct": mix.etanol_gasolina,
        "biodiesel_pct": mix.biodiesel_diesel,
        "tau": tau,
        "choque_energia_pp": choque_energia,
        "inflacao_efetiva": round(inputs.inflacao_esperada + tau * choque_energia, 3),
        "juro_real_necessario": round(juro_real, 2),
        "selic_ideal_continua": round(juro_real, 2),
        "selic_ideal_quantizada": selic_ideal,
        "selic_atual": selic_atual,
        "diferencial_pp": diferencial,
    }


BASELINE_ATUAL = SelixInputs(
    inflacao_esperada=4.48,
    premio_risco=1.25,
    credibilidade=calcular_credibilidade_continua(),
    gap_produto=0.50,
)

MIX_ATUAL = EnergyMix(
    etanol_gasolina=32.0,
    biodiesel_diesel=15.0,
)


class SELIX:
    """Wrapper legado; mercado é resolvido em runtime quando necessário."""
    TETO_1_DIGITO = 9.99
    JURO_REAL_MAXIMO = 5.0
    FOLGA_ROE = 0.95
    RELACAO_GLOBAL = 1.0
    PREMIO_RISCO_BRASIL = 1.25

    def __init__(self, inflacao=None, roe=None, selic_bacen=None):
        self.inflacao = inflacao or 4.48
        self.roe = roe or 31.23
        self.selic_bacen = selic_bacen

    def _selic_current(self) -> float:
        if self.selic_bacen is not None:
            return float(self.selic_bacen)
        from src.selix.spi import build_current_snapshot
        return float(build_current_snapshot()["selic_atual"])

    def calcular_selix(self):
        inputs = SelixInputs(
            inflacao_esperada=self.inflacao,
            premio_risco=self.PREMIO_RISCO_BRASIL,
            credibilidade=calcular_credibilidade_continua(),
            gap_produto=0.50,
        )
        resultado = calcular_selix(inputs, selic_atual=self._selic_current())
        return resultado["selic_ideal_quantizada"]

    def diagnosticar(self):
        selic_atual = self._selic_current()
        resultado = calcular_selix(BASELINE_ATUAL, selic_atual=selic_atual)
        return {
            "selix_ideal": resultado["selic_ideal_quantizada"],
            "selic_atual": resultado["selic_atual"],
            "diferencial": resultado["diferencial_pp"],
            "juro_real_atual": round(selic_atual - self.inflacao, 2),
            "juro_real_selix": round(resultado["juro_real_necessario"] - self.inflacao, 2),
            "investment_grade": resultado["selic_ideal_quantizada"] <= self.TETO_1_DIGITO,
            "convergencia_meses": abs(resultado["diferencial_pp"]) / 0.5,
        }


if __name__ == "__main__":
    print("=== SELIX v7.2 — modelo + SPI CURRENT ===")
    r0 = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.0)
    for k, v in r0.items():
        print(f"{k:30s}: {v}")

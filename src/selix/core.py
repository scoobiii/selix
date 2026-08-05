from src.selix.credibilidade_historica import calcular_credibilidade_continua
# (cole o código do core.py acima)

#!/usr/bin/env python3
"""
SELIX — core.py (v7.2 — com transmissão energética τ + compatibilidade)

Fórmula base (v7.1):
    juro_real_necessario = inflação + (prêmio_risco / credibilidade) + 0.5 * gap_produto

Extensão v7.2:
    inflação_efetiva = inflação_esperada + τ * choque_energia
    onde τ = 1 - peso_renovável no consumo final de combustíveis rodoviários

Todos os inputs em pontos percentuais (4.48 = 4,48%).
"""

from dataclasses import dataclass
from math import floor
from typing import Optional

# ============================================================
# CONSTANTES
# ============================================================

COPOM_GRID = 0.25  # p.p. — passo de quantização do Copom

# ============================================================
# DATACLASSES
# ============================================================

@dataclass(frozen=True)
class SelixInputs:
    """
    Inputs macro do modelo. Todos em pontos percentuais (4.48 = 4,48%).
    """
    inflacao_esperada: float          # Focus / IPCA 12m
    premio_risco: float               # CDS 5Y em % (ex: 1.25)
    credibilidade: float              # (0, 1]
    gap_produto: float                # hiato do produto (%)


@dataclass(frozen=True)
class EnergyMix:
    """
    Mistura vigente de biocombustíveis (em %).
    Fonte: ANP / CNPE.
    """
    etanol_gasolina: float = 32.0     # E32 atual (ago/2026)
    biodiesel_diesel: float = 15.0    # B15 atual
    # Pesos aproximados no consumo rodoviário brasileiro (ANP 2025/26)
    peso_gasolina: float = 0.42       # ~42% do volume energ. rodoviário
    peso_diesel: float = 0.58         # ~58%


# ============================================================
# FUNÇÕES DO MODELO
# ============================================================

def calcular_tau(mix: EnergyMix) -> float:
    """
    τ = fração do consumo final ainda exposta a combustível fóssil.
    Quanto menor τ, menor a transmissão de choque de Brent/TTF.
    """
    renovavel_gasolina = mix.etanol_gasolina / 100.0
    renovavel_diesel = mix.biodiesel_diesel / 100.0

    peso_renovavel = (
        mix.peso_gasolina * renovavel_gasolina
        + mix.peso_diesel * renovavel_diesel
    )
    tau = 1.0 - peso_renovavel
    return round(max(0.0, min(1.0, tau)), 4)


def quantizar_copom(valor: float, grid: float = COPOM_GRID) -> float:
    """Arredonda para baixo ao múltiplo de `grid` mais próximo."""
    return round(floor(valor / grid) * grid, 2)


def calcular_juro_real_necessario(
    inputs: SelixInputs,
    tau: float = 0.67,
    choque_energia: float = 0.0,
) -> float:
    """
    juro_real = inflação_efetiva + (prêmio_risco / credibilidade) + 0.5 * gap

    choque_energia: variação esperada de IPCA vinda de Brent/TTF (em p.p.)
                    Ex: +0.50 significa +0,50 p.p. de IPCA por choque externo.
    """
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
    selic_atual: float = 14.25,
    mix: Optional[EnergyMix] = None,
    choque_energia: float = 0.0,
) -> dict:
    """
    Retorna o payload completo com τ, impacto energético e demais métricas.
    """
    if mix is None:
        mix = EnergyMix()  # defaults = E32 / B15

    tau = calcular_tau(mix)
    juro_real = calcular_juro_real_necessario(inputs, tau=tau, choque_energia=choque_energia)
    selic_ideal = quantizar_copom(juro_real)
    diferencial = round(selic_atual - selic_ideal, 2)

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


# ============================================================
# BASELINE ATUAL (04/ago/2026)
# ============================================================

BASELINE_ATUAL = SelixInputs(
    inflacao_esperada=4.48,
    premio_risco=1.25,
    credibilidade=calcular_credibilidade_continua(),   # ⚠️ ainda não rastreável — prioridade v7.3
    gap_produto=0.50,
)

MIX_ATUAL = EnergyMix(
    etanol_gasolina=32.0,
    biodiesel_diesel=15.0,
)


# ============================================================
# CLASSE DE COMPATIBILIDADE — mantém testes antigos
# ============================================================

class SELIX:
    """
    Classe wrapper para compatibilidade com os testes antigos.
    Encapsula a nova lógica funcional.
    """
    TETO_1_DIGITO = 9.99
    JURO_REAL_MAXIMO = 5.0
    FOLGA_ROE = 0.95
    RELACAO_GLOBAL = 1.0
    PREMIO_RISCO_BRASIL = 1.25

    def __init__(self, inflacao=None, roe=None, selic_bacen=14.25):
        self.inflacao = inflacao or 4.48
        self.roe = roe or 31.23
        self.selic_bacen = selic_bacen

    def calcular_selix(self):
        """Usa a nova fórmula funcional com o baseline atual."""
        inputs = SelixInputs(
            inflacao_esperada=self.inflacao,
            premio_risco=self.PREMIO_RISCO_BRASIL,
            credibilidade=calcular_credibilidade_continua(),
            gap_produto=0.50,
        )
        resultado = calcular_selix(inputs, selic_atual=self.selic_bacen)
        return resultado["selic_ideal_quantizada"]

    def diagnosticar(self):
        """Retorna dicionário compatível com os testes antigos."""
        resultado = calcular_selix(BASELINE_ATUAL, selic_atual=self.selic_bacen)
        return {
            "selix_ideal": resultado["selic_ideal_quantizada"],
            "selic_atual": resultado["selic_atual"],
            "diferencial": resultado["diferencial_pp"],
            "juro_real_atual": round(self.selic_bacen - self.inflacao, 2),
            "juro_real_selix": round(resultado["juro_real_necessario"] - self.inflacao, 2),
            "investment_grade": resultado["selic_ideal_quantizada"] <= self.TETO_1_DIGITO,
            "convergencia_meses": abs(resultado["diferencial_pp"]) / 0.5,
        }


# ============================================================
# EXECUÇÃO DE DEMONSTRAÇÃO
# ============================================================

if __name__ == "__main__":
    print("=== SELIX v7.2 — com transmissão energética τ ===")
    print()

    # Cenário base (sem choque)
    r0 = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.0)
    print("--- Sem choque energético ---")
    for k, v in r0.items():
        print(f"{k:30s}: {v}")

    print("\n--- Choque +0,50 p.p. (Brent/TTF) ---")
    r1 = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.50)
    for k, v in r1.items():
        print(f"{k:30s}: {v}")

    print("\n--- Projeção E35 + B20 com choque +0,50 ---")
    mix_futuro = EnergyMix(etanol_gasolina=35.0, biodiesel_diesel=20.0)
    r2 = calcular_selix(BASELINE_ATUAL, mix=mix_futuro, choque_energia=0.50)
    for k, v in r2.items():
        print(f"{k:30s}: {v}")

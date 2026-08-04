#!/usr/bin/env python3
"""
SELIX — core.py (baseline mínimo, v6.2-clean)

Escopo deliberadamente restrito: SÓ os 4 inputs macro que têm fonte
verificável. Nada de ROIC, RJ, "choque", "multiplicador" — esses
ficam em módulos separados (ver roic.py) até terem fonte de dado real
e auditável, não hardcode disfarçado de API.

Fórmula (reconciliada em conversa — bate com a tabela comparativa
Brasil/EUA/Europa publicada no README v6.1, que a forma multiplicativa
documentada originalmente NÃO reproduzia):

    juro_real_necessario = inflacao + (premio_risco / credibilidade) + 0.5 * gap_produto

Todos os parâmetros de entrada são PERCENTUAIS EM PONTOS (ex: 4.48
significa 4,48%, não 0.0448). Isso evita o bug recorrente do "×100"
que apareceu em versões anteriores (embi_api retornando já em % e o
motor multiplicando de novo).
"""

from dataclasses import dataclass
from math import floor


COPOM_GRID = 0.25  # p.p. — step de quantização das decisões do Copom


@dataclass(frozen=True)
class SelixInputs:
    """
    Inputs macro do modelo. Todos em pontos percentuais (4.48 = 4,48%).

    Fontes e status na data de fechamento desta versão (04/ago/2026):
      inflacao_esperada : IPCA esperado 12m, Focus/BCB           -> 4.48
      premio_risco      : CDS Brasil 5Y (NÃO usar EMBI+,
                           descontinuado pelo JPMorgan/Ipeadata
                           em jul/2024). Fechamento 01/jul/2026
                           = 125.56 bps = 1.2556%.               -> 1.25
      credibilidade     : histórico de cumprimento da meta de
                           inflação, 0.0-1.0. Valor 0.50 é o
                           baseline documentado nas versões
                           anteriores; NÃO CONFIRMADO contra
                           fonte oficial. O v7.0 usou 0.30 sem
                           explicar a origem — não usar até
                           rastrear a fonte.                      -> 0.50 (⚠️ revisar)
      gap_produto       : hiato do produto, BCB RPM. 2º tri/2026
                           = +0.4% a +0.5% (positivo, não negativo
                           — só fica negativo a partir do
                           4º tri/2027, projeção).                -> 0.50
    """
    inflacao_esperada: float
    premio_risco: float
    credibilidade: float
    gap_produto: float


def quantizar_copom(valor: float, grid: float = COPOM_GRID) -> float:
    """Arredonda para baixo ao múltiplo de `grid` mais próximo (grid do Copom)."""
    return round(floor(valor / grid) * grid, 2)


def calcular_juro_real_necessario(inputs: SelixInputs) -> float:
    """
    juro_real_necessario = inflacao + (premio_risco / credibilidade) + 0.5 * gap_produto

    Levanta ValueError se credibilidade <= 0 (divisão por zero / não-sentido
    econômico — credibilidade é definida em (0, 1]).
    """
    if inputs.credibilidade <= 0:
        raise ValueError(
            f"credibilidade deve ser > 0, recebido: {inputs.credibilidade}"
        )
    return (
        inputs.inflacao_esperada
        + (inputs.premio_risco / inputs.credibilidade)
        + 0.5 * inputs.gap_produto
    )


def calcular_selix(inputs: SelixInputs, selic_atual: float = 14.25) -> dict:
    """
    Retorna o payload completo do cálculo, com o valor bruto (contínuo)
    e o quantizado ao grid do Copom, além do diferencial vs Selic atual.
    """
    juro_real = calcular_juro_real_necessario(inputs)
    selic_ideal_bruta = juro_real  # ver nota de nomenclatura abaixo
    selic_ideal = quantizar_copom(selic_ideal_bruta)
    diferencial = round(selic_atual - selic_ideal, 2)

    return {
        "inflacao_esperada": inputs.inflacao_esperada,
        "premio_risco": inputs.premio_risco,
        "credibilidade": inputs.credibilidade,
        "gap_produto": inputs.gap_produto,
        "juro_real_necessario": round(juro_real, 2),
        "selic_ideal_continua": round(selic_ideal_bruta, 2),
        "selic_ideal_quantizada": selic_ideal,
        "selic_atual": selic_atual,
        "diferencial_pp": diferencial,
    }


# Nota de nomenclatura: o README v6.1 chamava o resultado da fórmula de
# "juro_real_necessario" e depois o usava diretamente como "Selic ideal"
# (quantizada). Isso é uma imprecisão técnica — juro real e Selic nominal
# não são a mesma coisa sem passar por uma equação de Fisher. Mantido aqui
# por compatibilidade com a tabela histórica já publicada, mas sinalizado:
# se for pra virar peça de comunicação técnica séria (Copom, academia),
# isso precisa ser corrigido para incorporar a meta/expectativa de inflação
# explicitamente na conversão real -> nominal.


# Baseline atual (04/ago/2026), a ser usado enquanto não houver
# integração de API viva para os 4 inputs:
BASELINE_ATUAL = SelixInputs(
    inflacao_esperada=4.48,
    premio_risco=1.25,
    credibilidade=0.50,   # ⚠️ não confirmado — ver docstring de SelixInputs
    gap_produto=0.50,
)


if __name__ == "__main__":
    resultado = calcular_selix(BASELINE_ATUAL)
    print("=" * 60)
    print("SELIX — core.py (baseline macro, 4 inputs)")
    print("=" * 60)
    for k, v in resultado.items():
        print(f"{k:30s}: {v}")
    print("=" * 60)
    if BASELINE_ATUAL.credibilidade == 0.50:
        print("⚠️  credibilidade=0.50 é baseline não confirmado. Ver docstring.")

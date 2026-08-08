#!/usr/bin/env python3
"""
SELIX Credit — Análise de crédito PJ
Compara ROIC da empresa com a Selic atual e com a Selix ideal (8.25%)
"""

from typing import Dict, Optional
from src.selix.config import SELIC_IDEAL
from src.selix.roic import get_empresas_que_batem_selic, get_empresas_rj
from src.selix.roic_cvm import get_roic_por_codigo

SELIC_ATUAL = 14.25

def analisar_credito_pj(codigo: str) -> Dict:
    """
    Retorna análise de crédito para uma empresa (PJ).
    Compara ROIC com Selic atual e com Selix ideal.
    """
    roic = get_roic_por_codigo(codigo)
    if roic is None:
        from src.selix.roic import EMPRESAS
        for e in EMPRESAS:
            if e.codigo == codigo:
                roic = e.roic
                break

    if roic is None:
        return {"erro": f"Empresa {codigo} não encontrada", "codigo": codigo}

    spread_selic = roic - SELIC_ATUAL
    spread_selix = roic - SELIC_IDEAL

    if spread_selix > 0:
        classificacao = "baixo risco (cria valor sob Selix)"
    elif spread_selix > -2:
        classificacao = "risco moderado (próximo do break-even)"
    else:
        classificacao = "alto risco (destrói valor mesmo sob Selix)"

    em_rj = codigo in [e.codigo for e in get_empresas_rj()]

    return {
        "codigo": codigo,
        "roic": round(roic, 2),
        "selic_atual": SELIC_ATUAL,
        "selix_ideal": SELIC_IDEAL,
        "spread_selic": round(spread_selic, 2),
        "spread_selix": round(spread_selix, 2),
        "classificacao": classificacao,
        "em_recuperacao_judicial": em_rj,
        "recomendacao": (
            "Aprovar crédito" if spread_selix > 0 else
            "Analisar com cautela" if spread_selix > -2 else
            "Negar crédito ou exigir garantias adicionais"
        )
    }

def analisar_portfolio(empresas: list) -> list:
    return [analisar_credito_pj(codigo) for codigo in empresas]

def get_empresas_que_batem_selix() -> list:
    from src.selix.roic import EMPRESAS
    return [e.codigo for e in EMPRESAS if e.roic > SELIC_IDEAL]

if __name__ == "__main__":
    print(analisar_credito_pj("PETR4"))

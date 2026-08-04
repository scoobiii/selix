#!/usr/bin/env python3
"""
SELIX — ROIC real via CVM/B3

Fonte: CVM (Comissão de Valores Mobiliários) — Portal de Dados Abertos
URL: https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/

Status: ⚠️ IMPLEMENTAÇÃO PENDENTE
- Aguardando integração com a API da CVM
- Os dados abaixo são PLACEHOLDER até a integração ser concluída
"""

import requests
from typing import Dict, Optional

def get_roic_por_codigo(codigo: str) -> Optional[float]:
    """
    Busca ROIC de uma empresa específica na CVM.

    Exemplo de uso:
        roic = get_roic_por_codigo("PETR4")
        print(roic)  # 18.5

    URL base: https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/
    """
    # Placeholder — integração pendente
    # Em produção: baixar ITR da CVM e calcular ROIC
    roic_placeholder = {
        "PETR4": 18.5,
        "PRIO3": 17.2,
        "ABEV3": 15.0,
        "RAIZ4": 8.5,
        "PCAR3": 6.2,
        "MGLU3": 5.8,
        "VIIA3": 4.5,
        "LREN3": 7.1,
        "ITUB4": 12.3,
        "BBDC4": 11.8,
        "SANB11": 11.5,
        "WEGE3": 10.5,
        "EMBR3": 9.2,
        "SUZB3": 10.8,
        "AMER3": 4.0,
    }
    return roic_placeholder.get(codigo, None)

def get_roic_setor(setor: str) -> float:
    """ROIC médio por setor (calculado a partir dos dados da CVM)"""
    # Placeholder — integração pendente
    setores = {
        "Energia": 14.7,
        "Bebidas": 15.0,
        "Varejo": 5.5,
        "Financeiro": 11.9,
        "Industria": 10.2,
        "Outros": 8.0,
    }
    return setores.get(setor, 8.0)

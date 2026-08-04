#!/usr/bin/env python3
"""
SELIX — Credibilidade (fonte: BCB/Focus)

Credibilidade é estimada com base no histórico de cumprimento da meta
de inflação, conforme dados do BCB disponíveis no Relatório Focus e
no Boletim Focus.

Fonte oficial: https://www.bcb.gov.br/controleinflacao/relatoriofocus

Valor atual (ago/2026): 0.50 (baseline)
Status: NÃO CONFIRMADO — aguardando dados oficiais do BCB para
calibração precisa.
"""

from typing import Optional

def get_credibilidade() -> float:
    """
    Retorna a credibilidade do Banco Central.

    Baseline: 0.50 (50%)
    Fonte: BCB/Focus (https://www.bcb.gov.br/controleinflacao/relatoriofocus)
    Status: ⚠️ NÃO CONFIRMADO — valor preliminar.
    """
    # Em produção: consultar API do BCB ou relatório Focus
    return 0.50

def get_fonte_credibilidade() -> str:
    return "BCB/Focus — https://www.bcb.gov.br/controleinflacao/relatoriofocus (pendente de confirmação)"

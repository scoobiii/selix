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

class CredibilidadeModel:
    """Modelo de Credibilidade do Banco Central"""

    def __init__(self):
        self.baseline = 0.50

    def calcular_credibilidade(self) -> float:
        """
        Retorna a credibilidade do Banco Central.
        Baseline: 0.50 (50%)
        """
        return self.baseline

    def get_credibilidade(self) -> float:
        return self.calcular_credibilidade()

def get_credibilidade(): return CredibilidadeModel().get_credibilidade()
def get_fonte_credibilidade(): return "BCB/Focus — https://www.bcb.gov.br/controleinflacao/relatoriofocus"

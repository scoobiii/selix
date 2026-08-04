#!/usr/bin/env python3
"""
SELIX v7.0 - Motor com Derivação Endógena
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.selix.focus_api import FocusAPI
from src.selix.embi_api import EMBIApi
from src.selix.credibilidade import CredibilidadeModel
from src.selix.commodities import CommoditiesAPI
from src.selix.core import SELIX


class SelixV7(SELIX):
    """
    SELIX v7.0 - Modelo com parâmetros derivados endogenamente
    """

    def __init__(self):
        super().__init__()
        self.focus = FocusAPI()
        self.embi = EMBIApi()
        self.cred = CredibilidadeModel()
        self.commodities = CommoditiesAPI()

    def calcular_selic_ideal(self):
        """Calcula Selic ideal com parâmetros dinâmicos"""
        # Parâmetros derivados
        inflacao = self.focus.get_ipca_esperado()
        premio_risco = self.embi.get_spread_percent()
        credibilidade = self.cred.calcular_credibilidade()
        gap = self.focus.get_gap_produto()
        choque = self.commodities.ajuste_choque()

        # Multiplicador de credibilidade
        multiplicador = 1 + premio_risco + (1 - credibilidade) * 0.5

        # Juro real necessário
        juro_real = inflacao * multiplicador + choque + 0.5 * gap

        # Selic ideal = juro_real + meta de inflação
        meta_inflacao = 3.00
        selic_ideal = juro_real + meta_inflacao

        # Quantização ao grid do Copom (0.25pp)
        selic_quantizado = int(selic_ideal / 0.25) * 0.25

        return {
            "selic_ideal": round(selic_quantizado, 2),
            "juro_real_necessario": round(juro_real, 2),
            "inflacao_esperada": round(inflacao, 2),
            "premio_risco": round(premio_risco * 100, 2),
            "credibilidade": round(credibilidade, 2),
            "gap_produto": round(gap, 2),
            "choque": choque,
            "multiplicador": round(multiplicador, 3),
        }


if __name__ == "__main__":
    selix = SelixV7()
    resultado = selix.calcular_selic_ideal()
    print("=" * 60)
    print("📊 SELIX v7.0 - Derivação Endógena")
    print("=" * 60)
    for k, v in resultado.items():
        print(f"   {k}: {v}")

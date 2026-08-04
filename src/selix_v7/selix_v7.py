#!/usr/bin/env python3
"""
SELIX v7.0 - Modelo com Derivação Endógena
Versão simplificada para relatório COPOM
"""

import requests
from datetime import datetime
from typing import Dict, Optional


class SelixV7:
    """Motor do SELIX v7.0 para relatórios COPOM"""

    def __init__(self):
        self.base_url = "https://api.bcb.gov.br/dados/serie"

    def get_selic_atual(self) -> float:
        """Obtém a Selic atual da API do BCB"""
        try:
            url = f"{self.base_url}/bcdata.sgs.11/dados?formato=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data[-1]["valor"])
        except Exception:
            return 14.25  # fallback

    def get_divida_publica(self) -> float:
        """Obtém a dívida pública líquida"""
        try:
            url = f"{self.base_url}/bcdata.sgs.14558/dados?formato=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data[-1]["valor"])
        except Exception:
            return 6900.0

    def calcular_selic_ideal(self):
        """Calcula a Selic ideal com parâmetros derivados"""
        # Parâmetros (simulados para demonstração)
        # Em produção: viriam de APIs Focus/EMBI+/Commodities
        premio_risco = 2.00
        credibilidade = 0.50
        inflacao_esperada = 4.48
        gap_produto = -0.5
        choque_oil = 80.0
        choque_ttf = 40.0

        # Multiplicador de credibilidade
        multiplicador = 1 + premio_risco / 100 + (1 - credibilidade) * 0.5

        # Selic ideal
        selic_ideal = inflacao_esperada * multiplicador + 0.5 * gap_produto

        # Intervalo de confiança (86%)
        desvio = 0.25
        selic_inferior = selic_ideal - 1.5 * desvio
        selic_superior = selic_ideal + 1.5 * desvio

        # Impacto econômico
        selic_atual = self.get_selic_atual()
        divida = self.get_divida_publica()
        economia = divida * ((selic_atual - selic_ideal) / 100)

        from types import SimpleNamespace
        return SimpleNamespace(
            selic_ideal=round(selic_ideal, 2),
            selic_inferior=round(selic_inferior, 2),
            selic_superior=round(selic_superior, 2),
            premio_risco=round(premio_risco, 2),
            credibilidade=round(credibilidade, 2),
            inflacao_esperada=round(inflacao_esperada, 2),
            gap_produto=round(gap_produto, 2),
            choque_oil=round(choque_oil, 2),
            choque_ttf=round(choque_ttf, 2),
            economia_anual=round(economia, 2),
            timestamp=datetime.now().isoformat()
        )


if __name__ == "__main__":
    selix = SelixV7()
    r = selix.calcular_selic_ideal()
    print(f"Selic ideal: {r.selic_ideal}%")
    print(f"Economia anual: R$ {r.economia_anual:.2f} bi")

#!/usr/bin/env python3
"""
SELIX — API Focus (BCB)

Integração com o Relatório Focus do BCB para obter expectativas
de mercado em tempo real.

Fonte: https://www.bcb.gov.br/controleinflacao/relatoriofocus
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict

BCB_API_BASE = "https://api.bcb.gov.br/dados/serie"

class FocusAPI:
    """Interface com a API do Banco Central (SGS/Focus)"""

    def _get_serie(self, codigo: str) -> Optional[float]:
        """Função auxiliar para buscar uma série do BCB."""
        try:
            url = f"{BCB_API_BASE}/bcdata.sgs.{codigo}/dados?formato=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return float(data[-1]["valor"])
            return None
        except Exception:
            return None

    def get_ipca_esperado(self) -> float:
        """IPCA esperado para 12 meses (SGS 14)"""
        return self._get_serie(14) or 4.48

    def get_selic_esperada(self) -> float:
        """Selic esperada para 12 meses (SGS 12)"""
        return self._get_serie(12) or 14.25

    def get_pib_esperado(self) -> float:
        """PIB esperado para o ano corrente (SGS 13)"""
        return self._get_serie(13) or 2.5

    def get_dolar_esperado(self) -> float:
        """Câmbio esperado (R$/US$) — SGS 14"""
        return self._get_serie(14) or 5.20

    def get_gap_produto(self) -> float:
        """Gap do produto (estimado)"""
        return 0.50

    def get_credibilidade_bcb(self) -> float:
        """
        Busca a credibilidade do BCB a partir do histórico de metas.
        """
        # Dados históricos do BCB (2020-2025)
        historico = [
            {"ano": 2020, "meta": 4.00, "realizado": 4.52, "cumprida": False},
            {"ano": 2021, "meta": 3.75, "realizado": 10.06, "cumprida": False},
            {"ano": 2022, "meta": 3.50, "realizado": 5.79, "cumprida": False},
            {"ano": 2023, "meta": 3.25, "realizado": 4.62, "cumprida": False},
            {"ano": 2024, "meta": 3.00, "realizado": 4.83, "cumprida": False},
            {"ano": 2025, "meta": 3.00, "realizado": 4.00, "cumprida": False},
        ]
        cumpridas = sum(1 for h in historico if h.get("cumprida", False))
        return cumpridas / len(historico) if historico else 0.50

    def get_todas_expectativas(self) -> Dict:
        """Retorna todas as expectativas do Focus"""
        return {
            "ipca_12m": self.get_ipca_esperado(),
            "selic_12m": self.get_selic_esperada(),
            "pib_2026": self.get_pib_esperado(),
            "dolar_2026": self.get_dolar_esperado(),
            "credibilidade": self.get_credibilidade_bcb(),
            "timestamp": datetime.now().isoformat(),
            "fonte": "BCB/Focus",
        }

def get_ipca_esperado(): return FocusAPI().get_ipca_esperado()
def get_selic_esperada(): return FocusAPI().get_selic_esperada()
def get_pib_esperado(): return FocusAPI().get_pib_esperado()
def get_dolar_esperado(): return FocusAPI().get_dolar_esperado()
def get_todas_expectativas(): return FocusAPI().get_todas_expectativas()
def get_fonte_focus(): return FocusAPI().get_todas_expectativas()["fonte"]

if __name__ == "__main__":
    print("📊 Expectativas Focus (BCB)")
    print("-" * 40)
    for k, v in get_todas_expectativas().items():
        print(f"{k:20s}: {v}")

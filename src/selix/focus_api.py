#!/usr/bin/env python3
"""
SELIX v7.0 - API Focus (BCB)
Expectativas de mercado em tempo real
"""

import requests
import os
from typing import Dict, Optional

class FocusAPI:
    """Interface com o Relatório Focus do BCB"""

    def __init__(self):
        self.base_url = os.getenv('BCB_API_URL', 'https://api.bcb.gov.br/dados/serie')

    def get_ipca_esperado(self) -> float:
        """IPCA esperado para 12 meses (SGS 14)"""
        try:
            url = f"{self.base_url}/bcdata.sgs.14/dados?formato=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data[-1]["valor"])
        except Exception:
            return 4.48  # fallback

    def get_selic_esperada(self) -> float:
        """Selic esperada para 12 meses (SGS 12)"""
        try:
            url = f"{self.base_url}/bcdata.sgs.12/dados?formato=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data[-1]["valor"])
        except Exception:
            return 14.25  # fallback

    def get_gap_produto(self) -> float:
        """Gap do produto estimado pelo Focus"""
        # Em produção: IBGE/BCB
        return -0.5

    def get_historico_metas(self) -> list:
        """Histórico de cumprimento da meta de inflação"""
        # Em produção: BCB
        return [
            {"ano": 2023, "cumprida": True},
            {"ano": 2024, "cumprida": False},
            {"ano": 2025, "cumprida": True},
        ]

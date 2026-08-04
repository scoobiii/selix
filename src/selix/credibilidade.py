#!/usr/bin/env python3
"""
SELIX v7.0 - Credibilidade Endógena
Baseada no histórico de cumprimento de metas
"""

from typing import Dict, List

class CredibilidadeModel:
    """Modelo de credibilidade baseado em dados históricos"""

    def __init__(self):
        self.historico = self._carregar_historico()

    def _carregar_historico(self) -> List[Dict]:
        """Carrega histórico de cumprimento de metas"""
        # Em produção: API do BCB
        return [
            {"ano": 2020, "meta": 4.00, "realizado": 4.52, "cumprida": False},
            {"ano": 2021, "meta": 3.75, "realizado": 10.06, "cumprida": False},
            {"ano": 2022, "meta": 3.50, "realizado": 5.79, "cumprida": False},
            {"ano": 2023, "meta": 3.25, "realizado": 4.62, "cumprida": False},
            {"ano": 2024, "meta": 3.00, "realizado": 4.83, "cumprida": False},
            {"ano": 2025, "meta": 3.00, "realizado": 4.00, "cumprida": False},
        ]

    def calcular_credibilidade(self) -> float:
        """Calcula credibilidade (0-1) baseado no histórico"""
        if not self.historico:
            return 0.50

        # Quanto mais metas cumpridas, maior a credibilidade
        cumpridas = sum(1 for h in self.historico if h.get("cumprida", False))
        total = len(self.historico)

        # Fator de credibilidade: mínimo 0.3, máximo 0.9
        cred = 0.3 + (cumpridas / total) * 0.6
        return round(cred, 2)

    def get_tendencia(self) -> str:
        """Tendência da credibilidade (melhorando/piorando/estável)"""
        if len(self.historico) < 2:
            return "estável"

        ultimo = self.historico[-1].get("cumprida", False)
        penultimo = self.historico[-2].get("cumprida", False)

        if ultimo and penultimo:
            return "melhorando"
        elif not ultimo and not penultimo:
            return "piorando"
        else:
            return "estável"

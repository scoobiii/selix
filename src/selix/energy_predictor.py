#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# energy_predictor.py
# Versão: 2.0.0-GOS3

from typing import Dict, Any, List


class EnergyPredictor:
    """Preditor energético para misturas de biocombustíveis baseado no Brent."""

    GATILHOS_E: List[Dict[str, Any]] = [
        {"limite": 200, "mistura": "E42", "tempo": "12h", "status": "EMERGÊNCIA MÁXIMA", "cor": "🔴"},
        {"limite": 150, "mistura": "E40", "tempo": "24h", "status": "EMERGÊNCIA", "cor": "🔴"},
        {"limite": 120, "mistura": "E35", "tempo": "48h", "status": "CRISE", "cor": "🟠"},
        {"limite": 90, "mistura": "E30", "tempo": "72h", "status": "ALERTA", "cor": "🟡"},
        {"limite": 0, "mistura": "E27", "tempo": "normal", "status": "NORMAL", "cor": "🟢"},
    ]

    GATILHOS_B: List[Dict[str, Any]] = [
        {"limite": 200, "mistura": "B25", "tempo": "12h", "status": "EMERGÊNCIA MÁXIMA", "cor": "🔴"},
        {"limite": 150, "mistura": "B22", "tempo": "24h", "status": "EMERGÊNCIA", "cor": "🔴"},
        {"limite": 120, "mistura": "B20", "tempo": "48h", "status": "CRÍTICO", "cor": "🟠"},
        {"limite": 90, "mistura": "B15", "tempo": "72h", "status": "ALERTA", "cor": "🟡"},
        {"limite": 0, "mistura": "B14", "tempo": "normal", "status": "NORMAL", "cor": "🟢"},
    ]

    TERMELETRICAS: Dict[str, Dict[str, Any]] = {
        "etanol": {"capacidade_mw": 1200, "usinas": 12},
        "gnv": {"capacidade_mw": 15000, "usinas": 35},
        "biodiesel": {"capacidade_mw": 800, "usinas": 8},
        "biogas": {"capacidade_mw": 300, "usinas": 5},
    }

    @classmethod
    def get_mistura_e(cls, brent_preco: float) -> Dict[str, Any]:
        """Retorna a mistura recomendada de etanol na gasolina (E%)."""
        for gatilho in cls.GATILHOS_E:
            if brent_preco >= gatilho["limite"]:
                return {k: v for k, v in gatilho.items() if k != "limite"}
        return {k: v for k, v in cls.GATILHOS_E[-1].items() if k != "limite"}

    @classmethod
    def get_mistura_b(cls, brent_preco: float) -> Dict[str, Any]:
        """Retorna a mistura recomendada de biodiesel no diesel (B%)."""
        for gatilho in cls.GATILHOS_B:
            if brent_preco >= gatilho["limite"]:
                return {k: v for k, v in gatilho.items() if k != "limite"}
        return {k: v for k, v in cls.GATILHOS_B[-1].items() if k != "limite"}

    @classmethod
    def get_geracao_termica(cls, brent_preco: float) -> Dict[str, Any]:
        """Retorna recomendação de acionamento de termelétricas flex."""
        if brent_preco > 150:
            return {"status": "ACIONAMENTO TOTAL", "capacidade_utilizada": "100%"}
        elif brent_preco > 120:
            return {"status": "ACIONAMENTO PARCIAL", "capacidade_utilizada": "70%"}
        elif brent_preco > 90:
            return {"status": "ACIONAMENTO MÍNIMO", "capacidade_utilizada": "40%"}
        else:
            return {"status": "DESLIGADAS", "capacidade_utilizada": "0%"}


if __name__ == "__main__":
    print("Energy Predictor v2.0.0-GOS3 - Carregado com sucesso")

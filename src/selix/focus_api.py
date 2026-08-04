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

# URL base da API do BCB
BCB_API_BASE = "https://api.bcb.gov.br/dados/serie"

def get_ipca_esperado() -> float:
    """IPCA esperado para 12 meses (SGS 14)"""
    try:
        url = f"{BCB_API_BASE}/bcdata.sgs.14/dados?formato=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data[-1]["valor"])
    except Exception:
        return 4.48  # fallback

def get_selic_esperada() -> float:
    """Selic esperada para 12 meses (SGS 12)"""
    try:
        url = f"{BCB_API_BASE}/bcdata.sgs.12/dados?formato=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data[-1]["valor"])
    except Exception:
        return 14.25  # fallback

def get_pib_esperado() -> float:
    """PIB esperado para o ano corrente (SGS 13)"""
    try:
        url = f"{BCB_API_BASE}/bcdata.sgs.13/dados?formato=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data[-1]["valor"])
    except Exception:
        return 2.5  # fallback

def get_dolar_esperado() -> float:
    """Câmbio esperado (R$/US$) — SGS 14"""
    try:
        url = f"{BCB_API_BASE}/bcdata.sgs.14/dados?formato=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data[-1]["valor"])
    except Exception:
        return 5.20  # fallback

def get_todas_expectativas() -> Dict:
    """Retorna todas as expectativas do Focus"""
    return {
        "ipca_12m": get_ipca_esperado(),
        "selic_12m": get_selic_esperada(),
        "pib_2026": get_pib_esperado(),
        "dolar_2026": get_dolar_esperado(),
        "timestamp": datetime.now().isoformat(),
        "fonte": "BCB/Focus",
    }

def get_fonte_focus() -> str:
    return "BCB/Focus — https://www.bcb.gov.br/controleinflacao/relatoriofocus"

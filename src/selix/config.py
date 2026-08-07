#!/usr/bin/env python3
"""
SELIX v7.2 — Fonte única de verdade

Todos os números oficiais do SELIX devem vir daqui.
"""

from src.selix.core import BASELINE_ATUAL, calcular_selix, MIX_ATUAL

def get_selic_ideal() -> float:
    """Retorna a Selic ideal quantizada (8.25%)."""
    resultado = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.0)
    return resultado["selic_ideal_quantizada"]

def get_tau() -> float:
    """Retorna o fator de blindagem energética (τ)."""
    resultado = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.0)
    return resultado["tau"]

def get_credibilidade() -> float:
    """Retorna a credibilidade calculada (0.35)."""
    from src.selix.credibilidade_historica import calcular_credibilidade_continua
    return calcular_credibilidade_continua()

# Números oficiais
SELIC_IDEAL = get_selic_ideal()          # 8.25
TAU = get_tau()                          # 0.7786
CREDIBILIDADE = get_credibilidade()      # 0.35
DIFERENCIAL = 14.25 - SELIC_IDEAL        # 6.0

if __name__ == "__main__":
    print(f"SELIC IDEAL: {SELIC_IDEAL}%")
    print(f"τ: {TAU}")
    print(f"CREDIBILIDADE: {CREDIBILIDADE}")
    print(f"DIFERENCIAL: {DIFERENCIAL} p.p.")

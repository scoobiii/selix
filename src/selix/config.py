#!/usr/bin/env python3
"""
SELIX v7.2 — fonte única de parâmetros do modelo.
A Selic observada é sempre consultada no BCB em runtime; nunca é constante local.
"""
from src.selix.core import BASELINE_ATUAL, calcular_selix, MIX_ATUAL

def get_selic_ideal() -> float:
    resultado = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.0)
    return float(resultado["selic_ideal_quantizada"])

def get_tau() -> float:
    resultado = calcular_selix(BASELINE_ATUAL, mix=MIX_ATUAL, choque_energia=0.0)
    return float(resultado["tau"])

def get_credibilidade() -> float:
    from src.selix.credibilidade_historica import calcular_credibilidade_continua
    return float(calcular_credibilidade_continua())

SELIC_IDEAL = get_selic_ideal()
TAU = get_tau()
CREDIBILIDADE = get_credibilidade()
DIFERENCIAL = None  # Compatibilidade: derivar via get_diferencial().

def get_selic_atual_from_bcb() -> dict:
    """Compatibilidade legada sobre a consulta canônica validada do SPI."""
    from src.selix.spi import fetch_current_selic, CurrentDataError

    try:
        return fetch_current_selic()
    except CurrentDataError as exc:
        return {
            "success": False,
            "source": "BCB SGS 432",
            "serie": 432,
            "error": str(exc),
        }

def get_diferencial(selic_atual: float | None = None) -> float | None:
    if selic_atual is None:
        result = get_selic_atual_from_bcb()
        if not result.get("success"):
            return None
        selic_atual = float(result["rate"])
    return round(float(selic_atual) - float(SELIC_IDEAL), 2)

if __name__ == "__main__":
    print(f"SELIC IDEAL: {SELIC_IDEAL}%")
    print(f"TAU: {TAU}")
    print(f"CREDIBILIDADE: {CREDIBILIDADE}")
    result = get_selic_atual_from_bcb()
    print(f"BCB: {result}")
    if result.get("success"):
        print(f"DIFERENCIAL: {get_diferencial(result['rate'])} p.p.")

#!/usr/bin/env python3
"""
SELIX v7.2 — Fonte única de verdade

selic_ideal  → modelo (calcular_selix)
selic_atual  → BCB via provider/DB (NUNCA constante neste arquivo)
diferencial  → selic_atual - selic_ideal (só em runtime)
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

# Compat: quem ainda importa DIFERENCIAL precisa buscar selic_atual no BCB.
# Não há mais constante de mercado aqui.
DIFERENCIAL = None  # derivado em runtime — ver get_diferencial()


def get_selic_atual_from_bcb() -> dict:
    """Busca Selic de mercado no BCB. Não inventa número."""
    from src.providers.bcb_provider import BCBProvider
    return BCBProvider().get_selic()


def get_diferencial(selic_atual: float | None = None) -> float | None:
    if selic_atual is None:
        r = get_selic_atual_from_bcb()
        if not r.get("success"):
            return None
        selic_atual = float(r["rate"])
    return round(float(selic_atual) - float(SELIC_IDEAL), 2)


if __name__ == "__main__":
    print(f"SELIC IDEAL: {SELIC_IDEAL}%")
    print(f"τ: {TAU}")
    print(f"CREDIBILIDADE: {CREDIBILIDADE}")
    r = get_selic_atual_from_bcb()
    print(f"BCB: {r}")
    if r.get("success"):
        print(f"DIFERENCIAL: {get_diferencial(r['rate'])} p.p.")

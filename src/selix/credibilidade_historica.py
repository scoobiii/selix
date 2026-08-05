#!/usr/bin/env python3
"""
SELIX — Credibilidade histórica (BCB/Focus)

Calcula a credibilidade do Banco Central com base no histórico
de cumprimento da meta de inflação (2020-2025).

Fonte: BCB — Relatório de Inflação / Focus
"""

from typing import List, Tuple

# Histórico: (ano, meta, realizado)
HISTORICO: List[Tuple[int, float, float]] = [
    (2020, 4.00, 4.52),
    (2021, 3.75, 10.06),
    (2022, 3.50, 5.79),
    (2023, 3.25, 4.62),
    (2024, 3.00, 4.83),
    (2025, 3.00, 4.00),
]

def calcular_credibilidade_continua() -> float:
    """
    Calcula a credibilidade como 1 - (desvio médio / meta média).

    Retorna um valor entre 0 e 1.
    Quanto menor o desvio médio, maior a credibilidade.
    """
    if not HISTORICO:
        return 0.50  # fallback

    desvios = [abs(realizado - meta) for _, meta, realizado in HISTORICO]
    metas = [meta for _, meta, _ in HISTORICO]

    desvio_medio = sum(desvios) / len(desvios)
    meta_media = sum(metas) / len(metas)

    if meta_media == 0:
        return 0.50

    cred = 1 - (desvio_medio / meta_media)
    # Garantir que fique entre 0.10 e 0.90
    return round(max(0.10, min(0.90, cred)), 2)

def calcular_credibilidade_binaria(tolerancia: float = 1.5) -> float:
    """
    Calcula a credibilidade como proporção de metas cumpridas
    dentro de uma tolerância (em p.p.).
    """
    if not HISTORICO:
        return 0.50

    cumpridas = sum(1 for _, meta, realizado in HISTORICO
                    if realizado <= meta + tolerancia)
    return round(cumpridas / len(HISTORICO), 2)

def get_fonte_credibilidade() -> str:
    return "BCB/Focus — Histórico de cumprimento da meta de inflação (2020-2025)"

if __name__ == "__main__":
    print("=== Credibilidade Histórica (BCB) ===")
    print(f"Contínua (desvio médio): {calcular_credibilidade_continua()}")
    print(f"Binária (tolerância 1.5 p.p.): {calcular_credibilidade_binaria()}")
    print(f"Fonte: {get_fonte_credibilidade()}")

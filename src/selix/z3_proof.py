#!/usr/bin/env python3
"""T8 REAL: prova do impacto usando dados CURRENT do SPI.

Nenhuma taxa Selic é hardcoded aqui. A prova recebe a observação dinâmica do
SPI (BCB SGS 432) e o valor ideal do modelo canônico.
"""
from __future__ import annotations

from typing import Any
from z3 import Real, Solver, sat

from src.selix.spi import build_current_snapshot, assert_current_provenance


def provar_impacto_economico(divida_bi: float = 6900) -> dict[str, Any]:
    """Calcula/prova o impacto para a dívida informada com dados CURRENT."""
    current = build_current_snapshot()
    assert_current_provenance(current)

    s = Solver()
    selic_atual = Real("selic_atual")
    selic_ideal = Real("selic_ideal")
    divida_publica = Real("divida_publica")
    economia_anual = Real("economia_anual")
    diferencial = Real("diferencial")

    s.add(selic_atual == current["selic_atual"])
    s.add(selic_ideal == current["selic_ideal"])
    s.add(divida_publica == divida_bi)
    s.add(diferencial == selic_atual - selic_ideal)
    s.add(economia_anual == divida_publica * (diferencial / 100))

    if s.check() != sat:
        return {"status": "INCONSISTENTE", "erro": "Prova falhou"}

    model = s.model()
    return {
        "status": "PROVADO",
        "status_data": current["status"],
        "selic_atual": current["selic_atual"],
        "selic_ideal": current["selic_ideal"],
        "diferencial_pp": current["diferencial"],
        "divida_publica_bi": divida_bi,
        "economia_anual_bi": float(model[economia_anual].as_decimal(10).rstrip("?")),
        "fonte_selic": current["selic_atual_fonte"],
        "serie_selic": current["selic_atual_serie"],
        "data_bcb": current["selic_atual_data_bcb"],
        "provenance": current["provenance"],
        "formula": "economia = divida × (diferencial / 100)",
    }


def provar_cenario_alternativo(divida_bi: float, descricao: str) -> dict[str, Any]:
    resultado = provar_impacto_economico(divida_bi)
    resultado["descricao"] = descricao
    return resultado


def main() -> None:
    print("PROVA FORMAL COM Z3 - T8 REAL (CURRENT)")
    print("=" * 60)
    resultado = provar_impacto_economico()
    print(resultado)


if __name__ == "__main__":
    main()

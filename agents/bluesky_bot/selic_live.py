"""Fonte de Selic atual sem fallback: falha explicitamente se BCB indisponível."""
from __future__ import annotations

def get_selic_atual() -> float:
    from src.selix.config import get_selic_atual_from_bcb
    result = get_selic_atual_from_bcb()
    if not result.get("success"):
        raise RuntimeError("BCB SGS 432 indisponível; não existe valor atual confiável")
    if result.get("serie") != 432 or result.get("rate") is None:
        raise RuntimeError("Resposta BCB inválida para a meta Selic")
    return float(result["rate"])

#!/usr/bin/env python3
"""SELIX SPI — autoridade operacional para dados atuais.

Regra: dados CURRENT nunca são aceitos de fixtures, arte, prompt ou constante.
A taxa de mercado vem exclusivamente do BCB SGS 432 em runtime. O valor ideal
vem do modelo canônico do SELIX (config/core), não de um número legado.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.providers.bcb_provider import BCBProvider, SGS_META
from src.selix.config import SELIC_IDEAL

CANONICAL_SOURCE = f"BCB SGS {SGS_META}"


class CurrentDataError(RuntimeError):
    """Dados atuais ausentes, stale ou provenientes de fonte não autorizada."""


def fetch_current_selic() -> dict[str, Any]:
    """Busca a SELIC CURRENT exclusivamente pela série BCB SGS 432."""
    result = BCBProvider().get_selic_meta()
    if not result.get("success"):
        raise CurrentDataError(f"BCB SGS 432 indisponível: {result}")
    if result.get("serie") != SGS_META:
        raise CurrentDataError(
            f"Fonte não canônica para SELIC atual: {result.get('source')}"
        )
    return result


def build_current_snapshot() -> dict[str, Any]:
    """Produz somente o estado CURRENT autorizado pelo SPI."""
    bcb = fetch_current_selic()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    atual = round(float(bcb["rate"]), 2)
    ideal = round(float(SELIC_IDEAL), 2)
    return {
        "status": "current",
        "selic_atual": atual,
        "selic_ideal": ideal,
        "diferencial": round(atual - ideal, 2),
        "selic_atual_fonte": CANONICAL_SOURCE,
        "selic_atual_serie": SGS_META,
        "selic_atual_data_bcb": bcb.get("data_bcb"),
        "fetched_at": now,
        "provenance": "runtime:BCB SGS 432",
    }


def reject_caller_owned_market_data(payload: dict[str, Any]) -> None:
    """Impede que caller injete valores que pertencem ao SPI."""
    forbidden = {"selic_atual", "selic_ideal", "diferencial"}
    supplied = sorted(forbidden.intersection(payload))
    if supplied:
        raise CurrentDataError(
            "SPI-owned fields cannot be supplied by caller: " + ", ".join(supplied)
        )


def assert_current_provenance(data: dict[str, Any]) -> None:
    """Gate duro: somente BCB SGS 432 pode representar SELIC CURRENT."""
    if data.get("status") != "current":
        raise CurrentDataError("data is not CURRENT")
    if data.get("selic_atual_serie") != SGS_META:
        raise CurrentDataError("current SELIC must use BCB SGS 432")
    if data.get("selic_atual_fonte") != CANONICAL_SOURCE:
        raise CurrentDataError("current SELIC source is not canonical")
    if data.get("provenance") != "runtime:BCB SGS 432":
        raise CurrentDataError("current SELIC provenance is not runtime BCB")
    if not data.get("selic_atual_data_bcb"):
        raise CurrentDataError("current SELIC is missing BCB observation date")

#!/usr/bin/env python3
"""SELIX SPI — autoridade operacional para dados atuais.

Regra: dados CURRENT nunca são aceitos de fixtures, arte, prompt ou constante.
A taxa de mercado vem exclusivamente do BCB SGS 432 em runtime. O valor ideal
vem do modelo canônico do SELIX (config/core), não de um número legado.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timezone
from typing import Any

from src.providers.bcb_provider import BCBProvider, SGS_META
from src.selix.config import SELIC_IDEAL

CANONICAL_SOURCE = f"BCB SGS {SGS_META}"


class CurrentDataError(RuntimeError):
    """Dados atuais ausentes, stale ou provenientes de fonte não autorizada."""


def fetch_current_selic() -> dict[str, Any]:
    """Busca e valida a SELIC CURRENT exclusivamente pela série BCB SGS 432."""
    result = BCBProvider().get_selic_meta()
    if not isinstance(result, dict) or not result.get("success"):
        raise CurrentDataError("BCB SGS 432 indisponível")
    if result.get("serie") != SGS_META or result.get("source") != CANONICAL_SOURCE:
        raise CurrentDataError("Fonte não canônica para Selic atual")

    try:
        rate = float(result["rate"])
        observed = datetime.strptime(result["data_bcb"], "%d/%m/%Y").date()
    except (KeyError, TypeError, ValueError) as exc:
        raise CurrentDataError("Observação BCB SGS 432 inválida ou incompleta") from exc

    if not math.isfinite(rate) or not 0.0 < rate < 100.0:
        raise CurrentDataError("BCB SGS 432 retornou taxa inválida")
    if observed > date.today():
        raise CurrentDataError("BCB SGS 432 retornou observação futura")

    # Normaliza os campos depois da validação; não confia no formato do adapter.
    return {
        **result,
        "rate": rate,
        "serie": SGS_META,
        "source": CANONICAL_SOURCE,
        "data_bcb": observed.strftime("%d/%m/%Y"),
    }


def build_current_snapshot() -> dict[str, Any]:
    """Produz somente o estado CURRENT autorizado pelo SPI."""
    bcb = fetch_current_selic()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    atual = round(bcb["rate"], 2)
    ideal = round(float(SELIC_IDEAL), 2)
    return {
        "status": "current",
        "selic_atual": atual,
        "selic_ideal": ideal,
        "diferencial": round(atual - ideal, 2),
        "selic_atual_fonte": CANONICAL_SOURCE,
        "selic_atual_serie": SGS_META,
        "selic_atual_data_bcb": bcb["data_bcb"],
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
    """Gate duro: somente BCB SGS 432 com observação identificável."""
    if data.get("status") != "current":
        raise CurrentDataError("data is not CURRENT")
    if data.get("selic_atual_serie") != SGS_META:
        raise CurrentDataError("current SELIC must use BCB SGS 432")
    if data.get("selic_atual_fonte") != CANONICAL_SOURCE:
        raise CurrentDataError("current SELIC source is not canonical")
    if not data.get("selic_atual_data_bcb"):
        raise CurrentDataError("current SELIC is missing BCB observation date")
    if data.get("provenance") != "runtime:BCB SGS 432":
        raise CurrentDataError("current SELIC provenance is not runtime BCB")

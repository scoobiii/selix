#!/usr/bin/env python3
"""Runtime IPCA fetchers for the SELIX snapshot producer.

The two fields are deliberately different:

* ``ipca_realizado_12m``: BCB SGS 13522, the published 12-month IPCA rate.
* ``ipca_esperado_12m``: BCB Olinda/Focus 12-month market expectation.

No economic value is embedded in this module.  Every source failure is
fail-closed: ``IPCAFetchError`` propagates and the caller must not publish a
partial snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests


SGS_IPCA_12M_URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1"
)
FOCUS_IPCA_12M_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/"
    "odata/ExpectativasMercadoInflacao12Meses"
)


class IPCAFetchError(RuntimeError):
    """A required IPCA source failed or returned invalid data."""


@dataclass(frozen=True)
class IPCAResultado:
    valor_pct: float
    fonte: str
    data_referencia: str
    data_consulta: str


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_json(url: str, *, params: dict[str, str], timeout_seconds: int):
    try:
        response = requests.get(url, params=params, timeout=timeout_seconds)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError, TypeError) as exc:
        raise IPCAFetchError(f"Falha ao consultar fonte IPCA {url}: {exc}") from exc


def fetch_ipca_realizado_12m(timeout_seconds: int = 10) -> IPCAResultado:
    """Fetch the latest published 12-month IPCA rate from BCB SGS 13522."""
    payload = _get_json(
        SGS_IPCA_12M_URL,
        params={"formato": "json"},
        timeout_seconds=timeout_seconds,
    )

    if not isinstance(payload, list) or not payload:
        raise IPCAFetchError(f"SGS 13522 retornou formato vazio/inválido: {payload!r}")

    item = payload[-1]
    if not isinstance(item, dict):
        raise IPCAFetchError(f"SGS 13522 retornou item inválido: {item!r}")

    try:
        valor = float(item["valor"])
        data = datetime.strptime(item["data"], "%d/%m/%Y")
    except (KeyError, TypeError, ValueError) as exc:
        raise IPCAFetchError(
            f"SGS 13522 retornou valor/data inválidos: {item!r}"
        ) from exc

    return IPCAResultado(
        valor_pct=valor,
        fonte="BCB SGS 13522 (IPCA acumulado 12 meses, IBGE)",
        data_referencia=data.strftime("%Y-%m"),
        data_consulta=_now_utc(),
    )


def fetch_ipca_esperado_12m(timeout_seconds: int = 10) -> IPCAResultado:
    """Fetch the latest 12-month IPCA market expectation from Focus."""
    payload = _get_json(
        FOCUS_IPCA_12M_URL,
        params={
            "$filter": "Indicador eq 'IPCA'",
            "$orderby": "Data desc",
            "$top": "1",
            "$format": "json",
        },
        timeout_seconds=timeout_seconds,
    )

    if not isinstance(payload, dict):
        raise IPCAFetchError(f"Focus retornou formato inválido: {payload!r}")

    values = payload.get("value")
    if not isinstance(values, list) or not values:
        raise IPCAFetchError(f"Focus retornou lista vazia: {payload!r}")

    item = values[0]
    if not isinstance(item, dict):
        raise IPCAFetchError(f"Focus retornou item inválido: {item!r}")

    try:
        valor = float(item["Mediana"])
        data = datetime.strptime(item["Data"], "%Y-%m-%d")
    except (KeyError, TypeError, ValueError) as exc:
        raise IPCAFetchError(
            f"Focus retornou Mediana/Data inválidos: {item!r}"
        ) from exc

    return IPCAResultado(
        valor_pct=valor,
        fonte="BCB Olinda — Expectativas de Mercado (Focus), IPCA 12 meses",
        data_referencia=data.strftime("%Y-%m"),
        data_consulta=_now_utc(),
    )


def build_snapshot_fields(timeout_seconds: int = 10) -> dict[str, object]:
    """Build all IPCA snapshot fields; never return a partial snapshot."""
    realizado = fetch_ipca_realizado_12m(timeout_seconds=timeout_seconds)
    esperado = fetch_ipca_esperado_12m(timeout_seconds=timeout_seconds)

    return {
        "ipca_realizado_12m": realizado.valor_pct,
        "ipca_realizado_12m_fonte": realizado.fonte,
        "ipca_realizado_12m_data_referencia": realizado.data_referencia,
        "ipca_realizado_12m_data_consulta": realizado.data_consulta,
        "ipca_esperado_12m": esperado.valor_pct,
        "ipca_esperado_12m_fonte": esperado.fonte,
        "ipca_esperado_12m_data_referencia": esperado.data_referencia,
        "ipca_esperado_12m_data_consulta": esperado.data_consulta,
    }


if __name__ == "__main__":
    try:
        for key, value in build_snapshot_fields().items():
            print(f"{key:40s}: {value}")
    except IPCAFetchError as exc:
        print(f"FAIL-CLOSED — snapshot NÃO seria gerado: {exc}")
        raise SystemExit(1)

#!/usr/bin/env python3
"""Publica thread SELIX usando somente dados CURRENT verificados pelo SPI.

Este script não contém taxas Selic em texto. Antes de publicar, consulta o
SPI, valida provenance BCB SGS 432 e monta os números a partir do snapshot.
"""

import os
import time
from src.selix.spi import build_current_snapshot, assert_current_provenance

from atproto import Client

HANDLE = os.getenv("BLUESKY_HANDLE") or os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD") or os.getenv("BLUESKY_APP_PASSWORD")


def build_posts() -> list[str]:
    current = build_current_snapshot()
    assert_current_provenance(current)

    atual = current["selic_atual"]
    ideal = current["selic_ideal"]
    diferencial = current["diferencial"]
    fonte = current["selic_atual_fonte"]
    data_bcb = current["selic_atual_data_bcb"]

    return [
        "🧵 Atualização SELIX — dados CURRENT verificados pelo SPI.",
        (
            f"📊 Selic CURRENT: {atual:.2f}% a.a.\n"
            f"Selic ideal do modelo: {ideal:.2f}%\n"
            f"Diferencial: {diferencial:.2f} p.p."
        ),
        (
            "🔐 Proveniência: "
            f"{fonte}; observação BCB: {data_bcb}; "
            "snapshot obtido em runtime."
        ),
        (
            "⚠️ Regra SELIX: número de mercado não é lido de arte, prompt, "
            "few-shot ou prova histórica. Se o SPI não validar a fonte, a "
            "publicação deve ser bloqueada."
        ),
        "📖 Modelo, código e evidências: https://github.com/scoobiii/selix",
    ]


def main() -> None:
    if not HANDLE or not PASSWORD:
        raise RuntimeError("Credenciais Bluesky não configuradas")

    client = Client()
    client.login(HANDLE, PASSWORD)

    posts = build_posts()
    parent_uri = None
    parent_cid = None

    for text in posts:
        if parent_uri is None:
            response = client.send_post(text)
        else:
            response = client.send_post(
                text,
                reply_to={
                    "root": {"uri": root_uri, "cid": root_cid},
                    "parent": {"uri": parent_uri, "cid": parent_cid},
                },
            )
        if parent_uri is None:
            root_uri, root_cid = response.uri, response.cid
        parent_uri, parent_cid = response.uri, response.cid
        time.sleep(2)

    print("✅ Thread CURRENT publicada com provenance BCB SGS 432")


if __name__ == "__main__":
    main()

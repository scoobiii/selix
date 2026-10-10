#!/usr/bin/env python3
"""Publicador simples: números CURRENT vêm do SPI, nunca de texto fixo."""

import os
import sys
import time
from src.selix.spi import build_current_snapshot, assert_current_provenance

try:
    from atproto import Client
except ImportError:
    print("atproto não instalado. Execute: pip install atproto")
    sys.exit(1)

HANDLE = os.getenv("BLUESKY_HANDLE") or os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD") or os.getenv("BLUESKY_APP_PASSWORD")


def gerar_thread() -> list[str]:
    current = build_current_snapshot()
    assert_current_provenance(current)
    atual = current["selic_atual"]
    ideal = current["selic_ideal"]
    diferencial = current["diferencial"]
    data_bcb = current["selic_atual_data_bcb"]

    return [
        "SELIX — modelo regime-dependente com multiplicador de credibilidade.\n\n"
        "Dados CURRENT são obtidos pelo SPI antes da publicação. 🧵↓",
        (
            f"Selic CURRENT: {atual:.2f}% a.a.\n"
            f"Selic ideal (modelo): {ideal:.2f}%\n"
            f"Diferencial: {diferencial:.2f} p.p.\n"
            f"Observação BCB: {data_bcb}"
        ),
        (
            "🔐 Fonte operacional: BCB SGS 432 via SPI SELIX.\n"
            "Arte, prompt, README e histórico não são fontes CURRENT."
        ),
        (
            "O SELIX é ferramenta de apoio à decisão, auditoria aritmética e "
            "código aberto. Não substitui o COPOM."
        ),
    ]


def main() -> None:
    if not HANDLE or not PASSWORD:
        raise RuntimeError("Credenciais Bluesky não configuradas")

    client = Client()
    client.login(HANDLE, PASSWORD)
    posts = gerar_thread()
    parent_uri = None
    parent_cid = None
    root_uri = None
    root_cid = None

    for text in posts:
        if parent_uri is None:
            response = client.send_post(text)
            root_uri, root_cid = response.uri, response.cid
        else:
            response = client.send_post(
                text,
                reply_to={
                    "root": {"uri": root_uri, "cid": root_cid},
                    "parent": {"uri": parent_uri, "cid": parent_cid},
                },
            )
        parent_uri, parent_cid = response.uri, response.cid
        time.sleep(2)

    print("Thread CURRENT publicada com provenance BCB SGS 432")


if __name__ == "__main__":
    main()

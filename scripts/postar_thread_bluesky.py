#!/usr/bin/env python3
"""Publica thread SELIX com dados CURRENT obtidos e validados em runtime."""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.selix.spi import build_current_snapshot, assert_current_provenance

try:
    from atproto import Client
except ImportError:
    print("atproto não instalado. Execute: pip install atproto")
    sys.exit(1)


class BlueskyPoster:
    def __init__(self):
        self.client = Client()
        self.handle = os.getenv("BLUESKY_HANDLE", "zeh-sobrinho.bsky.social")
        self.password = os.getenv("BLUESKY_PASSWORD")
        if not self.password:
            raise RuntimeError("BLUESKY_PASSWORD não configurado no .env")

    def login(self):
        self.client.login(self.handle, self.password)

    def post_thread(self, posts):
        parent_ref = None
        parent_uri = None
        root_ref = None
        root_uri = None

        for text in posts:
            if parent_ref is None:
                response = self.client.send_post(text)
                root_uri, root_ref = response.uri, response.cid
            else:
                response = self.client.send_post(
                    text,
                    reply_to={
                        "root": {"uri": root_uri, "cid": root_ref},
                        "parent": {"uri": parent_uri, "cid": parent_ref},
                    },
                )
            parent_uri, parent_ref = response.uri, response.cid
            time.sleep(1)


def gerar_thread() -> list[str]:
    current = build_current_snapshot()
    assert_current_provenance(current)
    atual = current["selic_atual"]
    ideal = current["selic_ideal"]
    diferencial = current["diferencial"]
    data_bcb = current["selic_atual_data_bcb"]

    return [
        (
            "SELIX — dados CURRENT verificados em runtime.\n\n"
            "O modelo calcula a taxa ideal; o mercado vem do SPI. 🧵↓"
        ),
        (
            f"Selic CURRENT: {atual:.2f}% a.a.\n"
            f"Selic ideal (modelo): {ideal:.2f}%\n"
            f"Diferencial: {diferencial:.2f} p.p.\n"
            f"Observação BCB: {data_bcb}"
        ),
        (
            "🔐 Provenance: runtime:BCB SGS 432.\n"
            "Não usamos número de arte, few-shot, prompt, README ou prova histórica como CURRENT."
        ),
        (
            "O SELIX é ferramenta de apoio à decisão, auditoria aritmética e "
            "código aberto; não substitui o COPOM."
        ),
        "Repositório: https://github.com/scoobiii/selix",
    ]


def main():
    posts = gerar_thread()
    print("\n".join(posts))
    if input("\nPublicar? (s/N): ").strip().lower() != "s":
        return
    poster = BlueskyPoster()
    poster.login()
    poster.post_thread(posts)
    print("Thread CURRENT publicada com provenance BCB SGS 432")


if __name__ == "__main__":
    main()

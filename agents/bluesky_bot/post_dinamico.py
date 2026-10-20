#!/usr/bin/env python3
"""Publica somente um resumo SELIX com dados atuais validados pelo SPI."""
import os
import sys
import requests
from atproto import Client
from dotenv import load_dotenv

load_dotenv()


def obter_snapshot() -> dict:
    url = os.getenv("SELIX_API_URL", "http://localhost:5000").rstrip("/")
    response = requests.get(f"{url}/v1/selic/snapshot", timeout=15, headers={"Accept": "application/json"})
    response.raise_for_status()
    data = response.json()
    if (
        data.get("status") != "current"
        or data.get("selic_atual_serie") != 432
        or data.get("selic_atual_fonte") != "BCB SGS 432"
        or data.get("provenance") != "runtime:BCB SGS 432"
        or not data.get("selic_atual_data_bcb")
    ):
        raise RuntimeError("API não retornou observação CURRENT validada pelo BCB SGS 432")
    return data


def main() -> int:
    username = os.getenv("BLUESKY_USERNAME")
    password = os.getenv("BLUESKY_APP_PASSWORD")
    if not username or not password:
        print("Credenciais Bluesky ausentes; nenhum post enviado.", file=sys.stderr)
        return 2

    try:
        data = obter_snapshot()
    except Exception as exc:
        print(f"Selic oficial indisponível; post bloqueado sem fallback: {exc}", file=sys.stderr)
        return 1

    post = (
        f"SELIX | Meta Selic oficial: {data['selic_atual']:.2f}% a.a. "
        f"(BCB SGS 432; observação {data['selic_atual_data_bcb']}). "
        f"Selic ideal SELIX: {data['selic_ideal']:.2f}% a.a. (saída do modelo, não decisão do COPOM). "
        "Fonte e proveniência no endpoint oficial do projeto. #SELIX #Economia"
    )
    if len(post) > 300:
        post = post[:297] + "..."

    client = Client()
    client.login(username, password)
    result = client.send_post(post)
    print(f"Post enviado: {result.uri}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

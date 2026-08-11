#!/usr/bin/env python3
"""
Publicador CI: importa a constante oficial do SELIX (src.selix.config)
e posta o snapshot no Bluesky. Roda 100% no runner do GitHub Actions,
sem depender de servidor HTTP local.

Falha visivel: se o import do core quebrar, o script para com sys.exit(1)
e NAO posta nada. Nunca publica numero de fallback como se fosse oficial.
"""
import os
import sys
import requests
from datetime import datetime

sys.path.insert(0, os.getcwd())

try:
    from src.selix.config import SELIC_IDEAL, DIFERENCIAL
except Exception as e:
    print(f"ERRO FATAL: nao foi possivel importar src.selix.config: {e}")
    print("Post cancelado — nunca publicamos numero de fallback como oficial.")
    sys.exit(1)

print(f"Core carregado: SELIC_IDEAL={SELIC_IDEAL}, DIFERENCIAL={DIFERENCIAL}")

SELIC_ATUAL = round(SELIC_IDEAL + DIFERENCIAL, 2)

BSKY_HANDLE = os.getenv("BLUESKY_USERNAME")
BSKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")
API_BASE = "https://bsky.social/xrpc"


def get_bsky_session():
    resp = requests.post(
        f"{API_BASE}/com.atproto.server.createSession",
        json={"identifier": BSKY_HANDLE, "password": BSKY_APP_PASSWORD},
    )
    resp.raise_for_status()
    return resp.json()


def post_to_bluesky(session, text):
    post_resp = requests.post(
        f"{API_BASE}/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {session['accessJwt']}"},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text,
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
        },
    )
    post_resp.raise_for_status()
    return post_resp.json()


def main():
    if not BSKY_HANDLE or not BSKY_APP_PASSWORD:
        print("ERRO: credenciais do Bluesky nao configuradas.")
        sys.exit(1)

    post_content = (
        f"SELIX — snapshot automatico\n\n"
        f"Selic atual: {SELIC_ATUAL}%\n"
        f"Selic ideal (quantizada): {SELIC_IDEAL}%\n"
        f"Diferencial: {DIFERENCIAL} p.p.\n\n"
        f"Fonte: src.selix.config (mesma constante usada pela API e pela landing)\n"
        f"Ferramenta de apoio a decisao — nao substitui o COPOM."
    )

    try:
        print("Autenticando no Bluesky...")
        session = get_bsky_session()
        print("Publicando post...")
        post_to_bluesky(session, post_content)
        print("Post publicado com sucesso.")
    except Exception as e:
        print(f"ERRO ao postar: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# agents/bluesky_bot/agentes.py
# Script auxiliar — roda uma vez para validar handles

from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv('/root/selix/.env')

CANDIDATOS = {
    "economia_critica": [
        "laraResende.bsky.social",
        "monicadebolle.bsky.social",
        "lauracarvalho.bsky.social",
        "ricardoamorim.bsky.social",
    ],
    "jornalismo": [
        "valoreconomico.bsky.social",
        "folha.bsky.social",
    ],
    "energia": [
        "ipam.bsky.social",
        "wwfbrasil.bsky.social",
    ],
    "trabalhadores": [
        "nathfinancas.bsky.social",
        "mepoupenath.bsky.social",
    ],
}

def validar_handles(client, candidatos):
    validos = {}
    for ecossistema, handles in candidatos.items():
        validos[ecossistema] = []
        for handle in handles:
            try:
                perfil = client.get_profile(actor=handle)
                validos[ecossistema].append({
                    "handle": handle,
                    "display_name": perfil.display_name,
                    "followers": perfil.followers_count,
                })
                print(f"✅ {handle} — {perfil.followers_count} seguidores")
            except Exception:
                print(f"❌ {handle} — não encontrado")
    return validos

if __name__ == "__main__":
    client = Client()
    client.login(
        os.getenv('BLUESKY_USERNAME'),
        os.getenv('BLUESKY_APP_PASSWORD')
    )
    resultado = validar_handles(client, CANDIDATOS)
    import json
    with open('/root/selix/agents/bluesky_bot/handles_validos.json', 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print("\n✅ Salvo em handles_validos.json")

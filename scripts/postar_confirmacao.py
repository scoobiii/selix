#!/usr/bin/env python3
import os, sys, time
from pathlib import Path
from atproto import Client

env_path = Path("/root/selix/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

HANDLE = os.getenv("BLUESKY_HANDLE") or os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD") or os.getenv("BLUESKY_APP_PASSWORD")

client = Client()
client.login(HANDLE, PASSWORD)

posts = [
    "📌 CORREÇÃO: O valor operacional do SELIX é 9,25% (não 6,25%).\n\nO código foi alinhado com a thread pública.\n\n✅ Selic ideal: 9,25%\n✅ Economia anual: R$ 345 bi (dívida bruta BCB)\n✅ Código e documentação agora batem.",
    
    "🔬 O que mudou:\n\n- Revertidos commits que mudaram para 6,25%\n- Removidos etanol 42% e biodiesel 35% (sem fonte confirmada)\n- README atualizado\n\nRepositório: https://github.com/scoobiii/selix\nVersão: v6.1.0"
]

parent_ref = None
parent_uri = None

for i, text in enumerate(posts, 1):
    print(f"Post {i}/{len(posts)}...")
    if parent_ref is None:
        response = client.send_post(text)
    else:
        response = client.send_post(text, reply_to={
            "root": {"uri": parent_uri, "cid": parent_ref},
            "parent": {"uri": parent_uri, "cid": parent_ref},
        })
    parent_uri = response.uri
    parent_ref = response.cid
    time.sleep(2)

print("✅ Correção publicada!")

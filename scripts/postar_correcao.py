#!/usr/bin/env python3
"""
SELIX - Thread de correção sobre os impactos da Selic
"""

import os
import sys
import time
from pathlib import Path

# Carregar .env
env_path = Path("/root/selix/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

from atproto import Client

HANDLE = os.getenv("BLUESKY_HANDLE") or os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD") or os.getenv("BLUESKY_APP_PASSWORD")

posts = [
    "🧵 Follow-up sobre os números do SELIX:\n\nOs R$ 345 bi/ano não são um número único — dependem da base da dívida considerada. Vamos aos fatos:",
    
    "📊 TRÊS CENÁRIOS, MESMA FÓRMULA:\n\n1️⃣ R$ 270 bi: dívida líquida (R$ 5,4 tri) × 5,0 p.p.\n2️⃣ R$ 345 bi: dívida bruta (R$ 6,9 tri) × 5,0 p.p.\n3️⃣ R$ 430 bi: Selic 2D→1D (14,25→6,25) × parcela pós-fixada\n\nTodos são válidos, com contextos diferentes.",
    
    "🔬 O QUE O SELIX PROVA:\n\n✅ A aritmética fecha: economia = dívida × diferencial/100\n✅ A Selic ideal é ~9,25% (quantizado)\n✅ O custo de oportunidade da Selic atual é mensurável\n\n❌ O SELIX NÃO PROVA qual base de dívida é 'a certa' — isso é escolha do analista.",
    
    "📖 FONTES:\n\n- Dívida líquida: STN (R$ 5,4 tri)\n- Dívida bruta: BCB (R$ 6,9 tri)\n- Selic: BCB SGS 11\n- Modelo: Lean/Z3 com provas formais\n\nCada número tem sua fonte e contexto.",
    
    "🎯 RECOMENDAÇÃO:\n\nO valor operacional do SELIX é R$ 345 bi (usando dívida bruta do BCB).\n\nMas o importante não é o número exato — é a direção: a Selic atual custa centenas de bilhões por ano ao Brasil.",
    
    "Repositório: https://github.com/scoobiii/selix\nBluesky: @zeh-sobrinho.bsky.social\nVersão: v6.1.0\n\nDados abertos. Código aberto. Provas formais."
]

client = Client()
client.login(HANDLE, PASSWORD)

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

print("✅ Thread de correção publicada!")

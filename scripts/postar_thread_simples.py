#!/usr/bin/env python3
"""
SELIX - Postar Thread no Bluesky (versão simplificada)
"""

import os
import sys
import time
from pathlib import Path

# Carregar .env manualmente
env_path = Path("/root/selix/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

try:
    from atproto import Client
except ImportError:
    print("❌ atproto não instalado. Execute: pip install atproto")
    sys.exit(1)

# Credenciais
HANDLE = os.getenv("BLUESKY_HANDLE") or os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_PASSWORD") or os.getenv("BLUESKY_APP_PASSWORD")

if not HANDLE or not PASSWORD:
    print("❌ Credenciais não encontradas")
    sys.exit(1)

print(f"✅ Conectando como: {HANDLE}")

# Posts com menos de 300 caracteres
posts = [
    "SELIX v6.1: modelo regime-dependente com multiplicador de credibilidade.\n\njuro_real = inflação × (1 + prêmio_risco) × (1 + (1 - credibilidade) × 0.5) + 0.5 × gap_produto\n\nProva formal no Lean/Z3. 🧵↓",
    
    "Selic atual: 14,25% | Selic ideal (SELIX): 9,25%\nDiferencial: 5,00 p.p.\nEconomia anual: R$ 345 bi (dívida R$ 6,9 tri × 5,00 p.p.)\n\nO custo da Selic em 2 dígitos: R$ 345 bi/ano.",
    
    "O SELIX é:\n✅ Auditoria aritmética com prova formal\n✅ Código aberto, dados públicos\n✅ Roda 24/7 no Termux/Android\n\nNÃO é:\n❌ Modelo DSGE (não substitui o COPOM)\n❌ Substituto do BACEN",
    
    "Provas formais no Lean:\nT7: r* e risk_premium derivados de dados históricos (BCB/CDS)\nT8: R$ 345 bi provado formalmente\nT9: 9.48% ↔ 9.25% reconciliado\nT11: Brasil ~2× EUA (credibilidade)\n\n93/93 testes. 100% cobertura.",
    
    "Roadmap v7.0:\n🔜 API Focus (expectativas de mercado)\n🔜 EMBI+ em tempo real\n🔜 Credibilidade endógena\n🔜 Choques oil/TTF\n🔜 Intervalos de confiança (86%)\n\nAccountability total em breve.",
    
    "O SELIX não é o COPOM. É uma ferramenta de apoio.\n\nRode o código: https://github.com/scoobiii/selix\nBluesky: @zeh-sobrinho.bsky.social\nVersão: v6.1.0\n\nO custo de não saber é R$ 345 bi/ano."
]

try:
    client = Client()
    client.login(HANDLE, PASSWORD)
    print(f"✅ Login realizado: {HANDLE}")
    
    parent_ref = None
    parent_uri = None
    
    for i, text in enumerate(posts, 1):
        print(f"📝 Publicando post {i}/{len(posts)}...")
        if parent_ref is None:
            response = client.send_post(text)
        else:
            response = client.send_post(
                text,
                reply_to={
                    "root": {"uri": parent_uri, "cid": parent_ref},
                    "parent": {"uri": parent_uri, "cid": parent_ref},
                }
            )
        parent_uri = response.uri
        parent_ref = response.cid
        print(f"   ✅ Post {i} publicado!")
        time.sleep(2)
    
    print("\n✅ Thread publicada com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")

#!/usr/bin/env python3
"""post_seguro.py — SELIX v6.1 - Corrigido 29/05/2026"""

import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carregar .env ANTES do atproto
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(ENV_PATH)

HANDLE = os.getenv('BLUESKY_HANDLE', '')
PASSWORD = os.getenv('BLUESKY_PASSWORD', '')

if not HANDLE or not PASSWORD:
    print(f"❌ .env sem credenciais em: {ENV_PATH}")
    print("   Crie com:")
    print("     BLUESKY_HANDLE=selixbr.bsky.social")
    print("     BLUESKY_PASSWORD=xxxx-xxxx-xxxx-xxxx")
    sys.exit(1)

from atproto import Client

def postar_seguro(texto: str) -> dict:
    if len(texto) > 300:
        print(f"⚠️ {len(texto)} chars → truncando para 300")
        texto = texto[:297] + "..."
    
    print(f"📏 {len(texto)} caracteres")
    
    try:
        client = Client()
        client.login(HANDLE, PASSWORD)
        print(f"🔐 Autenticado: {HANDLE}")
        post = client.send_post(text=texto)
        url = f"https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}"
        print(f"✅ Postado: {url}")
        return {"sucesso": True, "url": url}
    except Exception as e:
        print(f"❌ FALHOU: {e}")
        return {"sucesso": False, "erro": str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python post_seguro.py 'texto do post'")
        sys.exit(1)
    resultado = postar_seguro(sys.argv[1])
    sys.exit(0 if resultado.get('sucesso') else 1)

#!/usr/bin/env python3
"""
Script SEGURO de postagem - Usa o formatter central
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.formatter import BlueskyFormatter
from atproto import Client
from dotenv import load_dotenv

load_dotenv()

def postar_seguro(texto_bruto: str) -> dict:
    """Publica post com validação automática"""
    
    # 1. Validar
    valido, msg, tamanho = BlueskyFormatter.validar_post(texto_bruto)
    
    if not valido:
        print(f"⚠️ Post original tem {tamanho} caracteres. {msg}")
        texto = BlueskyFormatter.formatar_post(texto_bruto)
        print(f"✅ Formatado para {len(texto)} caracteres")
    else:
        texto = texto_bruto
        print(f"✅ Post ok: {tamanho} caracteres")
    
    # 2. Publicar
    client = Client()
    client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))
    
    try:
        post = client.send_post(texto)
        return {
            "sucesso": True,
            "uri": post.uri,
            "url": f"https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}",
            "tamanho": len(texto)
        }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "tamanho": len(texto)
        }

if __name__ == "__main__":
    # Teste com o post que deu erro
    texto_teste = """@b3.bsky.social 

📊 DADOS REAIS DO MERCADO (Yahoo Finance):

GPA (PCAR3):
📍 REAL: R$ 1,96 (MÍNIMA 52 SEM: R$1,89)
📍 SELIX: R$ 6,61 (+237%)

RAIZEN (RAIZ4):
📍 REAL: R$ 0,34 (QUEDA -19% NO DIA!)
📍 SELIX: R$ 11,15 (+3.179%)

✅ SELIX + TrampoForte

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #RAIZ4"""
    
    resultado = postar_seguro(texto_teste)
    print(resultado)

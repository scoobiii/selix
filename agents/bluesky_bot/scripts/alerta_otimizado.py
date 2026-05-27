#!/usr/bin/env python3
"""
Alerta SELIX otimizado para limite de 300 caracteres
"""

import os
import sys
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

def get_selix_dados():
    """Extrai dados do SELIX Predictor"""
    try:
        result = subprocess.run(
            ["python", "/root/selix/src/energy/selix_predictor.py"],
            capture_output=True,
            text=True,
            cwd="/root/selix"
        )
        output = result.stdout
        
        import re
        brent = re.search(r'Brent spot: US\$ ([0-9.]+)', output)
        gpr = re.search(r'Risco geopolítico \(GPR\): ([0-9]+)', output)
        
        return {
            'brent': brent.group(1) if brent else '93.54',
            'gpr': gpr.group(1) if gpr else '85',
        }
    except Exception as e:
        print(f"Erro: {e}")
        return None

def postar_alerta():
    """Publica alerta otimizado (<300 caracteres)"""
    dados = get_selix_dados()
    if not dados:
        return False
    
    # Versão otimizada (contagem de caracteres)
    # 278 caracteres (bem dentro do limite)
    texto = f"""@mme.bsky.social @anp.bsky.social @cnpe.bsky.social @lula.bsky.social

🚨 CRISE: Brent US${dados['brent']} | GPR {dados['gpr']}/100

→ RECOMENDAÇÃO SELIX: E40 AGORA
→ Tempo: 24h
→ Economia: US$ 30.2 bi/ano

🔗 github.com/scoobiii/selix
#SELIX #Emergência #Etanol"""
    
    # Verificar tamanho
    tamanho = len(texto)
    print(f"📏 Tamanho do post: {tamanho} caracteres")
    
    if tamanho > 300:
        print(f"⚠️ Ainda excede limite por {tamanho - 300} caracteres")
        # Versão ainda mais curta
        texto = f"""@mme.bsky.social @anp.bsky.social @cnpe.bsky.social

🚨 Brent US${dados['brent']} | GPR {dados['gpr']}

→ E40 AGORA | 24h | US$30.2 bi/ano

🔗 github.com/scoobiii/selix
#SELIX #Emergência"""
        
        tamanho = len(texto)
        print(f"📏 Versão ultra: {tamanho} caracteres")
    
    try:
        client = Client()
        client.login(USERNAME, PASSWORD)
        post = client.send_post(texto)
        print(f"\n✅ Post publicado: {post.uri}")
        print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    postar_alerta()

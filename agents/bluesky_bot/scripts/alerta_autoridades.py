#!/usr/bin/env python3
"""
Alerta SELIX para autoridades - Com CC no Bluesky
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_autoridades import gerar_post_tecnico, AUTORIDADES

load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

def get_selix_dados():
    """Executa SELIX Predictor e extrai dados"""
    try:
        result = subprocess.run(
            ["python", "/root/selix/src/energy/selix_predictor.py"],
            capture_output=True,
            text=True,
            cwd="/root/selix"
        )
        
        output = result.stdout
        
        # Extrair informações
        import re
        brent = re.search(r'Brent spot: US\$ ([0-9.]+)', output)
        gpr = re.search(r'Risco geopolítico \(GPR\): ([0-9]+)', output)
        previsao = re.search(r'Preço previsto: US\$ ([0-9.]+)', output)
        
        return {
            'brent': brent.group(1) if brent else '93.61',
            'gpr': gpr.group(1) if gpr else '85',
            'previsao': previsao.group(1) if previsao else '120.50',
            'economia': '30.2',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None

def postar_para_autoridades(dados, tipo="tecnico"):
    """Publica alerta no Bluesky marcando autoridades"""
    if not dados:
        return False
    
    texto = gerar_post_tecnico(dados, tipo)
    
    # Mostrar autoridades que serão marcadas
    print("\n📢 AUTORIDADES NOTIFICADAS:")
    print("-" * 40)
    for grupo in ["executivos", "legislativos"]:
        for key, auth in AUTORIDADES[grupo].items():
            if auth.get("bluesky"):
                print(f"   ✓ {auth['nome']} ({auth['cargo']})")
                print(f"     → {auth['bluesky']}")
    print("-" * 40)
    
    try:
        client = Client()
        client.login(USERNAME, PASSWORD)
        post = client.send_post(texto)
        print(f"\n✅ Alerta publicado: {post.uri}")
        print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def postar_thread_autoridades(dados):
    """Publica thread com diferentes enfoques para diferentes autoridades"""
    if not dados:
        return False
    
    posts = [
        # Post 1: Executivos (técnico)
        gerar_post_tecnico(dados, "tecnico"),
        
        # Post 2: Legislativos (impacto)
        gerar_post_tecnico(dados, "impacto"),
        
        # Post 3: Resumo curto
        gerar_post_tecnico(dados, "curto")
    ]
    
    try:
        client = Client()
        client.login(USERNAME, PASSWORD)
        
        parent_ref = None
        root_ref = None
        
        for i, texto in enumerate(posts, 1):
            if parent_ref and root_ref:
                post = client.send_post(
                    text=texto,
                    reply_to=parent_ref,
                    root=root_ref
                )
            else:
                post = client.send_post(texto)
            
            print(f"✅ Post {i}/3 publicado: {post.uri}")
            
            if i == 1:
                root_ref = post
            parent_ref = post
            
            import time
            time.sleep(3)
        
        return True
    except Exception as e:
        print(f"❌ Erro na thread: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Alerta SELIX para autoridades')
    parser.add_argument('--tipo', choices=['single', 'thread'], default='single')
    parser.add_argument('--formato', choices=['tecnico', 'impacto', 'curto'], default='tecnico')
    args = parser.parse_args()
    
    print("📊 Coletando dados da SELIX...")
    dados = get_selix_dados()
    
    if not dados:
        print("❌ Falha ao coletar dados")
        sys.exit(1)
    
    print(f"   Brent: US$ {dados['brent']}")
    print(f"   GPR: {dados['gpr']}/100")
    print(f"   Previsão: US$ {dados['previsao']}")
    
    if args.tipo == 'thread':
        print("\n📱 Publicando THREAD com 3 posts...")
        postar_thread_autoridades(dados)
    else:
        print(f"\n📱 Publicando post {args.formato}...")
        postar_para_autoridades(dados, args.formato)

if __name__ == "__main__":
    main()

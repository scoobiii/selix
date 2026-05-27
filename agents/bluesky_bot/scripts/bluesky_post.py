#!/usr/bin/env python3
"""
SELIX Bluesky Poster - Publica automaticamente usando a conta @selixbr.bsky.social
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

# Carregar credenciais
load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

if not USERNAME or not PASSWORD:
    print("❌ Configure BLUESKY_USERNAME e BLUESKY_APP_PASSWORD no .env")
    sys.exit(1)

# Conectar
client = Client()
client.login(USERNAME, PASSWORD)
print(f"✅ Conectado: @{client.me.handle}")

# ============================================================
# POSTS PRONTOS (com limite de 300 caracteres)
# ============================================================

# Versão 1 - Tom geral (diretão) - 296 caracteres
POST_GERAL = """GPA: trabalhadores sem PLR de R$2 mil. Empresa renegocia R$4,5bi com bancos.

Causa: Selic 14,5% (juro real 10%) > ROI do negócio.

Solução: SELIX (Selic 1 dígito, 9,48%) + TrampoForte.

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #PLR"""

# Versão 2 - Curta e direta - 152 caracteres
POST_CURTO = """GPA: juros evaporam caixa. Selic 14,5% > ROI.

Funcionários sem PLR. Rentismo vence.

Solução: SELIX (9,48%) + TrampoForte.

🔗 github.com/scoobiii/selix
#SELIX #GPA"""

# Versão 3 - Propositiva - 284 caracteres
POST_PROPOSITIVO = """✅ Solução para o GPA:

1️⃣ SELIX: Selic 1 dígito (9,48%, juro real 4,77%)
2️⃣ TrampoForte: prioridade para salários e PLR

Empresa respira, trabalhador recebe PLR, rentismo para.

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #PLR"""

# Versão 4 - Com menções - 293 caracteres
POST_MENCOES = """@secsp.bsky.social @cut.bsky.social

Apoiamos a luta dos trabalhadores do GPA pela PLR.

Causa: Selic 14,5% > ROI.

Solução: SELIX (9,48%) + TrampoForte.

🔗 github.com/scoobiii/selix
#SELIX #GPA #PLR"""

# Thread (3 posts)
THREAD_POST1 = "🧵 GPA: trabalhadores sem PLR de R$2 mil. Empresa renegocia R$4,5bi com bancos. Causa: Selic 14,5% > ROI."  # 115 chars
THREAD_POST2 = "Empresa é viável no operacional, mas rentismo (juros) come resultado antes do trabalhador receber."  # 91 chars
THREAD_POST3 = "Solução: SELIX (9,48%) + TrampoForte. 🔗 github.com/scoobiii/selix #SELIX #TrampoForte #GPA"  # 97 chars

# ============================================================
# FUNÇÕES DE PUBLICAÇÃO
# ============================================================

def postar_texto(texto):
    """Publica um post simples no Bluesky"""
    try:
        # Verificar tamanho
        tamanho = len(texto)
        if tamanho > 300:
            print(f"❌ Texto com {tamanho} caracteres (limite 300). Não publicado.")
            return None
        
        post = client.send_post(texto)
        print(f"✅ Post publicado ({tamanho} caracteres): {post.uri}")
        return post
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")
        return None

def postar_thread(posts, intervalo=3):
    """Publica uma thread (posts em sequência, um respondendo ao outro)"""
    parent_ref = None
    root_ref = None
    
    for i, texto in enumerate(posts, 1):
        try:
            # Verificar tamanho
            if len(texto) > 300:
                print(f"❌ Post {i} com {len(texto)} caracteres (limite 300). Pulando.")
                continue
                
            if parent_ref and root_ref:
                post = client.send_post(
                    text=texto,
                    reply_to=parent_ref,
                    root=root_ref
                )
            else:
                post = client.send_post(texto)
            
            print(f"✅ Post {i}/{len(posts)} publicado ({len(texto)} chars): {post.uri}")
            
            # Atualiza referências
            if i == 1:
                root_ref = post
            parent_ref = post
            
            time.sleep(intervalo)
        except Exception as e:
            print(f"❌ Erro no post {i}: {e}")
    
    print(f"🎉 Thread concluída!")

def listar_opcoes():
    print("\n" + "="*50)
    print("SELIX Bluesky Poster")
    print("="*50)
    print("1 - Post geral (diretão) - 296 chars")
    print("2 - Post curto - 152 chars")
    print("3 - Post propositivo - 284 chars")
    print("4 - Post com menções - 293 chars")
    print("5 - Thread (3 posts)")
    print("0 - Sair")
    print("="*50)

# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) > 1:
        # Modo automático
        opcao = sys.argv[1]
        if opcao == "1":
            postar_texto(POST_GERAL)
        elif opcao == "2":
            postar_texto(POST_CURTO)
        elif opcao == "3":
            postar_texto(POST_PROPOSITIVO)
        elif opcao == "4":
            postar_texto(POST_MENCOES)
        elif opcao == "5":
            postar_thread([THREAD_POST1, THREAD_POST2, THREAD_POST3])
        else:
            print("Opções: 1,2,3,4,5")
    else:
        # Modo interativo
        while True:
            listar_opcoes()
            escolha = input("\nEscolha uma opção: ").strip()
            
            if escolha == "1":
                postar_texto(POST_GERAL)
            elif escolha == "2":
                postar_texto(POST_CURTO)
            elif escolha == "3":
                postar_texto(POST_PROPOSITIVO)
            elif escolha == "4":
                postar_texto(POST_MENCOES)
            elif escolha == "5":
                postar_thread([THREAD_POST1, THREAD_POST2, THREAD_POST3])
            elif escolha == "0":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida")

if __name__ == "__main__":
    main()

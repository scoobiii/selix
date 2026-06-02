#!/usr/bin/env python3
"""
🤖 SELIX Agent for Bluesky (AT Protocol)
Monitora menções a @selixbr.bsky.social e responde automaticamente
"""

import time
from atproto import Client, client_utils

# Credenciais da conta
USERNAME = "selixbr.bsky.social"
PASSWORD = "SUA_SENHA_AQUI"  # ⚠️ Use variável de ambiente na prática

# Inicializa cliente
client = Client()
client.login(USERNAME, PASSWORD)

# Mensagem padrão de resposta
TEXTO_RESPOSTA = (
    "📊 SELIX | Selic Energy Real Time\n"
    "🔬 Provada com Z3 + Lean 4\n"
    "💰 9,48% | Economia de R$ 270 bi/ano\n"
    "✅ Investment Grade BBB+\n"
    "🔗 github.com/scoobiii/selix"
)

def processar_mencoes():
    # Busca as últimas menções (feed pessoal)
    # Nota: para monitoramento em tempo real seria necessário usar WebSub ou polling
    feed = client.get_author_feed(actor=USERNAME, limit=10)
    for post in feed.feed:
        # Verifica se o post é uma menção
        if post.post.record.reply and post.post.author.handle != USERNAME:
            # Verifica se já respondeu
            # (Aqui seria necessário um banco de ids para não repetir)
            try:
                resposta = client.send_post(
                    text=TEXTO_RESPOSTA,
                    reply_to=post.post
                )
                print(f"Respondido a @{post.post.author.handle}")
                time.sleep(10)
            except Exception as e:
                print(f"Erro: {e}")

if __name__ == "__main__":
    print("🤖 SELIX Bot rodando no Bluesky...")
    while True:
        processar_mencoes()
        time.sleep(60)  # Espera 1 minuto para nova rodada

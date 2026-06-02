#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv
from atproto import Client

load_dotenv('/root/selix/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

API_BASE = "http://localhost:5000"

def responder_mencoes():
    timeline = client.app.bsky.feed.get_author_feed(
        actor=os.getenv('BLUESKY_USERNAME'), 
        limit=10
    )
    
    for feed_view in timeline.feed:
        post = feed_view.post
        if os.getenv('BLUESKY_USERNAME') in post.text and not post.viewer.reply:
            pergunta = post.text.split(os.getenv('BLUESKY_USERNAME'))[-1].strip()
            
            # Chama o endpoint da API
            try:
                resp = requests.post(
                    f"{API_BASE}/v1/perguntar",
                    json={"pergunta": pergunta},
                    timeout=30
                )
                if resp.status_code == 200:
                    resposta = resp.json().get('resposta', 'Não consegui processar sua pergunta.')
                else:
                    resposta = "Desculpe, tive um problema interno. Tente novamente mais tarde."
            except Exception as e:
                resposta = f"Erro ao consultar o agente: {str(e)}"
            
            # Responde no Bluesky
            client.send_post(f"@{post.author.handle} {resposta}", reply_to=post.uri)
            print(f"Respondido a @{post.author.handle}: {pergunta[:50]}...")

if __name__ == "__main__":
    responder_mencoes()

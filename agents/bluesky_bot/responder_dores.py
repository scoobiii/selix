#!/usr/bin/env python3
import sqlite3
import re
from dotenv import load_dotenv
from atproto import Client
import os

load_dotenv('/root/selix/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

DB_PATH = "/root/selix/selix.db"

def find_solution(pergunta):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT segmento, dor, solucao, palavras_chave FROM dores_mercado")
    rows = cur.fetchall()
    conn.close()
    pergunta_lower = pergunta.lower()
    for seg, dor, sol, kw in rows:
        palavras = kw.split(',')
        if any(palavra.strip() in pergunta_lower for palavra in palavras):
            return f"🎯 **{seg.upper()}**\n{dor}\n✅ {sol}\n🔗 github.com/scoobiii/selix"
    return None

def responder_mencoes():
    timeline = client.app.bsky.feed.get_author_feed(actor=os.getenv('BLUESKY_USERNAME'), limit=10)
    for feed in timeline.feed:
        post = feed.post
        if os.getenv('BLUESKY_USERNAME') in post.text and not post.viewer.reply:
            pergunta = post.text.split(os.getenv('BLUESKY_USERNAME'))[-1].strip()
            resposta = find_solution(pergunta)
            if resposta:
                client.send_post(f"@{post.author.handle} {resposta}", reply_to=post.uri)
                print(f"Respondido a @{post.author.handle} sobre: {pergunta[:50]}...")
            else:
                print(f"Não consegui identificar a dor em: {pergunta}")

if __name__ == "__main__":
    responder_mencoes()

#!/usr/bin/env python3
"""
Engaja automaticamente agentes humanizados detectados:
- Segue de volta (se não seguir)
- Curte e reposta aleatoriamente posts deles
- Envia menção amigável (CC) em posts do SELIX
"""

import os
import time
import random
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv('/root/selix/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

DB_PATH = "/root/selix/selix.db"

def get_human_agents(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('''
        SELECT handle, did FROM perfis_analisados
        WHERE classificado_como = 'HUMANO'
        ORDER BY human_score DESC LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def already_followed(did):
    try:
        resp = client.app.bsky.graph.get_follows(
            params={'actor': os.getenv('BLUESKY_USERNAME')}
        )
        for follow in resp.follows:
            if follow.did == did:
                return True
    except Exception as e:
        print(f"Erro ao verificar follow: {e}")
    return False

def follow_agent(did):
    try:
        client.app.bsky.graph.follow(params={'actor': did})
        print(f"✅ Segui o agente {did}")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Erro ao seguir {did}: {e}")

def get_last_post(handle, limit=2):
    try:
        feed = client.app.bsky.feed.get_author_feed(params={'actor': handle, 'limit': limit})
        return feed.feed
    except Exception as e:
        print(f"Erro ao buscar posts de {handle}: {e}")
        return []

def like_post(uri, cid):
    try:
        client.app.bsky.feed.like(params={'uri': uri, 'cid': cid})
        print(f"❤️ Curtiu post {uri}")
        return True
    except Exception as e:
        print(f"❌ Erro ao curtir: {e}")
        return False

def repost_post(uri, cid):
    try:
        client.app.bsky.feed.repost(params={'uri': uri, 'cid': cid})
        print(f"🔄 Repostou {uri}")
        return True
    except Exception as e:
        print(f"❌ Erro ao repostar: {e}")
        return False

def like_and_repost(post_uri, post_cid, handle):
    like_post(post_uri, post_cid)
    time.sleep(1)
    if random.random() < 0.3:  # 30% de chance de repostar
        repost_post(post_uri, post_cid)

def send_mention(handle):
    try:
        post_text = f"@{handle} Olá! O SELIX agradece pelo seu apoio. 🌱\n\n📊 Acompanhe dados reais de energia e economia. Selic ideal = 9,25%.\n🔗 github.com/scoobiii/selix"
        client.send_post(post_text)
        print(f"📢 Menção enviada para @{handle}")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Erro ao enviar menção para @{handle}: {e}")

def already_mentioned(handle):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute('''
        SELECT COUNT(*) FROM interacoes_agentes
        WHERE agente_handle = ? AND tipo = 'mention'
        AND criado_em > datetime('now', '-30 days')
    ''', (handle,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

def log_interaction(handle, tipo):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interacoes_agentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agente_handle TEXT,
            tipo TEXT,
            criado_em TIMESTAMP
        )
    ''')
    conn.execute('INSERT INTO interacoes_agentes (agente_handle, tipo, criado_em) VALUES (?,?,?)',
                 (handle, tipo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def main():
    agents = get_human_agents()
    for handle, did in agents:
        print(f"\n🎯 Processando agente @{handle}")
        if not already_followed(did):
            follow_agent(did)
            log_interaction(handle, 'follow')
        posts = get_last_post(handle, limit=2)
        for item in posts:
            like_and_repost(item.post.uri, item.post.cid, handle)
            log_interaction(handle, 'like')
            time.sleep(2)
        if not already_mentioned(handle):
            send_mention(handle)
            log_interaction(handle, 'mention')
        time.sleep(5)

if __name__ == "__main__":
    main()

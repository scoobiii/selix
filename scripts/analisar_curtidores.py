#!/usr/bin/env python3
"""
SELIX – Análise de seguidores e identificação de agentes humanizados.
Coleta dados básicos dos seguidores e calcula um score de humanidade.
"""

import os
import re
import time
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv('/root/selix/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

DB_PATH = "/root/selix/selix.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS perfis_analisados (
            did TEXT PRIMARY KEY,
            handle TEXT,
            display_name TEXT,
            description TEXT,
            followers_count INTEGER,
            follows_count INTEGER,
            posts_count INTEGER,
            human_score REAL,
            classificado_como TEXT,
            last_updated TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def calcular_human_score(profile):
    """Calcula um score de 0 a 100 indicando probabilidade de ser humano real."""
    score = 50
    name = profile.display_name or ""
    if re.search(r'^[a-zA-ZÀ-ÖØ-öø-ÿ0-9\s]+$', name):
        score += 10
    if profile.description and len(profile.description) > 20:
        score += 10
    if profile.avatar:
        score += 5
    if 10 <= (profile.posts_count or 0) <= 1000:
        score += 10
    followers = profile.followers_count or 0
    follows = profile.follows_count or 0
    if followers > 0 and follows > 0:
        ratio = followers / (follows + 1)
        if 0.2 <= ratio <= 5:
            score += 10
    if not re.search(r'user\d{5,}', profile.handle):
        score += 5
    return min(100, score)

def coletar_seguidores():
    conn = init_db()
    try:
        # Obtém o perfil do próprio bot
        bot_profile = client.app.bsky.actor.get_profile(params={'actor': os.getenv('BLUESKY_USERNAME')})
        did = bot_profile.did
        cursor = None
        while True:
            params = {'actor': did, 'limit': 100}
            if cursor:
                params['cursor'] = cursor
            resp = client.app.bsky.graph.get_followers(params=params)
            for follower in resp.followers:
                # Busca perfil completo
                try:
                    prof = client.app.bsky.actor.get_profile(params={'actor': follower.did})
                except Exception as e:
                    print(f"Erro ao obter perfil de {follower.did}: {e}")
                    continue
                score = calcular_human_score(prof)
                classificacao = "HUMANO" if score >= 70 else "POSSIVEL_BOT" if score < 40 else "INDETERMINADO"
                conn.execute('''
                    INSERT OR REPLACE INTO perfis_analisados 
                    (did, handle, display_name, description, followers_count, follows_count, posts_count, human_score, classificado_como, last_updated)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                ''', (prof.did, prof.handle, prof.display_name, prof.description,
                      prof.followers_count or 0, prof.follows_count or 0, prof.posts_count or 0,
                      score, classificacao, datetime.now().isoformat()))
                conn.commit()
                time.sleep(0.5)
            cursor = resp.cursor
            if not cursor:
                break
    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        conn.close()

def listar_agentes_humanizados(limite=20):
    conn = init_db()
    cur = conn.execute('''
        SELECT handle, display_name, human_score, classificado_como
        FROM perfis_analisados
        WHERE classificado_como = 'HUMANO'
        ORDER BY human_score DESC
        LIMIT ?
    ''', (limite,))
    rows = cur.fetchall()
    conn.close()
    return rows

def main():
    print("Coletando seguidores... Isso pode levar alguns minutos.")
    coletar_seguidores()
    print("\n🏆 Agentes humanizados detectados:")
    for handle, name, score, classe in listar_agentes_humanizados():
        print(f"  @{handle} – {name or '(sem nome)'} (score: {score})")

if __name__ == "__main__":
    main()

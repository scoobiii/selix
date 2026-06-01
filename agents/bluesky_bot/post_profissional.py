#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX - Bot Profissional com Provenance
Versão: v4.0
Data: 2026-06-01

Publica threads separando fatos (observações) de cenários (projeções)
com índice de confiança calculado.
"""

import sqlite3
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client, models

# Adicionar path para importar calculadora
sys.path.insert(0, '/root/selix')
from confidence.calculator import SelixConfidenceCalculator

load_dotenv('/root/selix/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

DB_PATH = "/root/selix/selix.db"
REPO_LINK = "github.com/scoobiii/selix"

def get_fato(indicador):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT o.valor, o.unidade, f.nome as fonte, o.timestamp
        FROM observacoes o
        JOIN fontes f ON o.fonte_id = f.id
        WHERE o.indicador = ?
        ORDER BY o.timestamp DESC LIMIT 1
    """, (indicador,))
    row = cur.fetchone()
    conn.close()
    return row if row else None

def get_projecao(indicador):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT p.valor, p.unidade, c.nome as cenario, p.confianca
        FROM projecoes p
        JOIN cenarios c ON p.cenario_id = c.id
        WHERE p.indicador = ? AND c.nome = 'Selix_925'
        ORDER BY p.timestamp DESC LIMIT 1
    """, (indicador,))
    row = cur.fetchone()
    conn.close()
    return row if row else None

def post_fatos():
    brent = get_fato('brent')
    selic = get_fato('selic')
    
    post = f"📊 **Dados observados**\n\n"
    if brent:
        post += f"🛢️ Brent: US${brent[0]} (fonte: {brent[2]})\n"
    if selic:
        post += f"🏦 Selic: {selic[0]}% (fonte: {selic[2]})\n"
    post += f"\n🔗 {REPO_LINK}\n✅ Dados reais de fontes oficiais"
    return post[:300]

def post_cenario():
    pib = get_projecao('pib_per_capita')
    b3 = get_projecao('b3_market_cap')
    selic_proj = get_projecao('selic_aa')
    economia = get_projecao('economia_anual')
    
    # Calcular confiança
    calc = SelixConfidenceCalculator()
    conf, fatores = calc.calculate()
    calc.close()
    
    post = f"🎯 **Cenário Selix_925** (Selic 9,25%)\n\n"
    if selic_proj:
        post += f"📉 Selic projetada: {selic_proj[0]}% a.a.\n"
    if pib:
        post += f"🇧🇷 PIB per capita: US$ {pib[0]:,.0f}\n"
    if b3:
        post += f"🏦 B3 Market Cap: US$ {b3[0]:,.0f}\n"
    if economia:
        post += f"💰 Economia anual: R$ {economia[0]:,.0f} bi\n"
    post += f"\n⚠️ Projeção | Modelo: selix_v4.0 | Confiança: {conf:.0f}%"
    post += f"\n🔗 {REPO_LINK}"
    return post[:300]

def post_thread():
    # Post 1: Fatos (root)
    fato = post_fatos()
    root = client.send_post(fato)
    print(f"✅ Post 1 (fatos) enviado. URI: {root.uri}")
    
    # Post 2: Cenário (reply)
    cenario = post_cenario()
    reply_ref = models.AppBskyFeedPost.ReplyRef(
        parent=models.ComAtprotoRepoStrongRef.Main(uri=root.uri, cid=root.cid),
        root=models.ComAtprotoRepoStrongRef.Main(uri=root.uri, cid=root.cid)
    )
    reply = client.send_post(cenario, reply_to=reply_ref)
    print(f"✅ Post 2 (cenário) enviado. URI: {reply.uri}")
    print(f"✅ Thread profissional publicada!")

if __name__ == "__main__":
    post_thread()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# post_thread_completo.py — Versão 2.0.0-PRO
# Fix: usa .cid direto do response de send_post() — zero roundtrips extras
# Compatível com atproto >= 0.0.40

import os, sys, time, sqlite3, requests
from dotenv import load_dotenv
from atproto import Client, models

load_dotenv('/root/selix/.env')

USERNAME = os.getenv('BLUESKY_USERNAME')
PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')
API_KEY  = os.getenv('SELIX_API_KEY') or os.getenv('MASTER_API_KEY')

if not USERNAME or not PASSWORD:
    sys.exit("❌ Credenciais Bluesky não encontradas no .env")
if not API_KEY:
    sys.exit("❌ SELIX_API_KEY não encontrada no .env")

API_BASE  = "http://localhost:5000"
REPO_LINK = "https://github.com/scoobiii/selix"
DB_PATH   = "/root/selix/selix.db"
HEADERS   = {"X-API-Key": API_KEY}
MAX_CHARS = 295


# ── DADOS ─────────────────────────────────────────────────────────────────

def fetch_from_api(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"⚠️  {endpoint}: {e}")
    return None

def get_last_from_db(table):
    try:
        conn = sqlite3.connect(DB_PATH)
        sql  = {
            "brent": "SELECT price FROM brent WHERE success=1 ORDER BY timestamp DESC LIMIT 1",
            "selic": "SELECT rate  FROM selic WHERE success=1 ORDER BY timestamp DESC LIMIT 1",
        }.get(table)
        if not sql: return None
        row = conn.execute(sql).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"⚠️  DB/{table}: {e}")
        return None

def fetch_dados():
    energia    = fetch_from_api("/v1/energia/mistura")
    selic_data = fetch_from_api("/v1/selic")
    if energia and selic_data:
        brent = energia['brent_usd']
        print("✅ Dados via API")
        return dict(brent=brent, e_mix=energia['etanol']['mistura'],
                    b_mix=energia['biodiesel']['mistura'],
                    selic_val=selic_data[0]['valor'],
                    sent="negativo" if brent > 90 else ("positivo" if brent < 70 else "neutro"))
    brent     = get_last_from_db("brent")
    selic_val = get_last_from_db("selic")
    if brent and selic_val:
        print("✅ Dados via banco")
        return dict(brent=brent, e_mix=27, b_mix=14, selic_val=selic_val,
                    sent="negativo" if brent > 90 else "neutro")
    print("⚠️  Mock")
    return dict(brent=97.36, e_mix=27, b_mix=14, selic_val=14.25, sent="negativo")


# ── POSTS ─────────────────────────────────────────────────────────────────

def trunc(text, limit=MAX_CHARS):
    return text if len(text) <= limit else text[:limit-1] + "…"

def gerar_posts(d):
    brent, e_mix, b_mix = d['brent'], d['e_mix'], d['b_mix']
    sv, sent, rl = d['selic_val'], d['sent'], REPO_LINK
    raw = [
        f"🧵 SELIX — Economia que prioriza quem trabalha\n\n🌍 Brent: US${brent}\n📉 Selic efetiva: {sv}%\n📰 Sentimento: {sent}\n💰 Selic ideal: 9,25% (1 dígito)\n🔗 {rl}\n\nAcompanhe o fio 👇",
        f"👷 Para trabalhadores\n\nSelic {sv}% corrói seu poder de compra e trava PLR em GPA e Raízen.\n✅ Exija #Selix 9,25% e #TrampoForte — receba antes dos bancos.\n🔗 {rl}",
        f"🏦 Para bancos\n\nCom Selic 9,25%, custo de capital cai, bolsa sobe e o país ganha investment grade A-. Spread bancário continua lucrativo.\n🔗 {rl}",
        f"🏛️ Para governo\n\nSelix 9,25%: R$270 bi/ano economizados, dívida/PIB cai, investment grade A-.\n🔗 {rl}",
        f"🗳️ Para políticos\n\nApoie o PL #TrampoForte e Selic 1 dígito (9,25%). Bom para o trabalhador, bom para os votos.\n🔗 {rl}",
        f"🌱 Para ambientalistas\n\nCom Brent US${brent}, mix ideal: E{e_mix}/B{b_mix}.\nCrise (Brent >150): E42/B25 — máximo histórico de biocombustíveis.\n🔗 {rl}",
        f"📈 Para investidores\n\nGPA (+68%), Raízen (+76%) em RJ. Com Selic 9,25%, upside → +150%. B3 pode chegar a US$10 tri em 10 anos.\n🔗 {rl}",
        f"📰 Para jornalistas\n\nProva formal (Z3 + Lean 4): Selic deveria ser 9,25%. Entreviste os criadores do Selix.\n🔗 {rl}",
        f"⚖️ Para sindicatos\n\nSelic {sv}% bloqueia PLR. Mobilize pela Selix 9,25% agora! #TrampoForte\n🔗 {rl}",
        f"☀️ Solar e Biocombustíveis\n\nCom Selic 1 dígito: 100 GW solar em 10 anos, etanol E42, biogás em escala nacional.\n🔗 {rl}",
        f"📊 Cenário Selix 9,25% em 10 anos\n\n🇧🇷 PIB per capita: US$130k (+118%)\n🏦 B3: US$10 tri (6× atual)\n⭐ Investment Grade A-\n💰 Economia: R$270 bi/ano\n🔗 {rl}",
        f"🔁 Compartilhe\n\n✅ Selic: 9,25%\n✅ Economia: R$270 bi/ano\n✅ PIB per capita: US$130k\n✅ B3: US$10 tri\n✅ Solar + biocombustíveis\n\n🔗 {rl}\n\n#Selix #TrampoForte #PLR #Economia #EnergiaSolar",
    ]
    return [trunc(p) for p in raw]


# ── THREAD ────────────────────────────────────────────────────────────────

def post_thread(client, textos):
    """
    SOLUÇÃO PROFISSIONAL:
    send_post() já devolve .uri E .cid no mesmo response.
    Não precisa de get_record() nem get_post() — ambos são
    roundtrips desnecessários e fontes de incompatibilidade entre
    versões da SDK atproto.
    """
    if not textos:
        return

    root = client.send_post(textos[0])          # post raiz
    print(f"✅  1/{len(textos)}: {root.uri}")

    prev = root

    for i, texto in enumerate(textos[1:], start=2):
        reply_ref = models.AppBskyFeedPost.ReplyRef(
            root   = models.ComAtprotoRepoStrongRef.Main(uri=root.uri, cid=root.cid),
            parent = models.ComAtprotoRepoStrongRef.Main(uri=prev.uri, cid=prev.cid),
        )
        prev = client.send_post(text=texto, reply_to=reply_ref)
        print(f"✅  {i}/{len(textos)}: {prev.uri}")
        time.sleep(0.5)


# ── MAIN ──────────────────────────────────────────────────────────────────

def main():
    print("📡 Obtendo dados...")
    dados = fetch_dados()
    print("📝 Gerando posts...")
    posts = gerar_posts(dados)
    print(f"🔐 Autenticando como {USERNAME}...")
    client = Client()
    client.login(USERNAME, PASSWORD)
    print(f"🧵 Publicando thread ({len(posts)} posts)...")
    post_thread(client, posts)
    print("🎉 Thread completa!")

if __name__ == "__main__":
    main()

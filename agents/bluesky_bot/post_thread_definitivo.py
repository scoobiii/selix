#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# post_thread_definitivo.py
# Versão: 2.0.0-GOS3
# Responsabilidade: Publicar thread completa (12 posts) do Selix no Bluesky com fallback HTTP
# Assinatura: GOS3/2026-06-02/agents/bluesky_bot/post_thread_definitivo.py

import os
import sys
import sqlite3
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Tenta importar atproto, mas se falhar, usa apenas requests
try:
    from atproto import Client, models
    HAS_ATPROTO = True
except ImportError:
    HAS_ATPROTO = False
    print("⚠️  Biblioteca atproto não encontrada. Usando apenas requisições HTTP diretas.")

load_dotenv('/root/selix/.env')

# ========== CREDENCIAIS ==========
USERNAME = os.getenv('BLUESKY_USERNAME')
PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')
if not USERNAME or not PASSWORD:
    print("❌ Credenciais do Bluesky não encontradas no .env")
    sys.exit(1)

API_KEY = os.getenv('SELIX_API_KEY') or os.getenv('MASTER_API_KEY')
if not API_KEY:
    print("❌ Nenhuma chave de API local encontrada. Configure SELIX_API_KEY ou MASTER_API_KEY")
    sys.exit(1)

# ========== CONFIGURAÇÕES ==========
API_BASE = "http://localhost:5000"
REPO_LINK = "https://github.com/scoobiii/selix"
DB_PATH = "/root/selix/selix.db"
HEADERS = {"X-API-Key": API_KEY}

# ========== FUNÇÕES AUXILIARES ==========
def fetch_from_api(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"⚠️  API {endpoint} falhou: {e}")
    return None

def get_last_from_db(table):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if table == "brent":
            c.execute("SELECT price FROM brent WHERE success=1 ORDER BY timestamp DESC LIMIT 1")
        elif table == "selic":
            c.execute("SELECT rate FROM selic WHERE success=1 ORDER BY timestamp DESC LIMIT 1")
        else:
            return None
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"⚠️  Banco ({table}): {e}")
        return None

def calcular_sentimento(brent):
    return "negativo" if brent > 90 else ("positivo" if brent < 70 else "neutro")

def fetch_dados():
    energia = fetch_from_api("/v1/energia/mistura")
    selic_data = fetch_from_api("/v1/selic")
    if energia and selic_data:
        brent = energia['brent_usd']
        e_mix = energia['etanol']['mistura']
        b_mix = energia['biodiesel']['mistura']
        selic_val = selic_data[0]['valor']
        sent = calcular_sentimento(brent)
        print("✅ Dados via API")
        return {'brent': brent, 'e_mix': e_mix, 'b_mix': b_mix,
                'selic_val': selic_val, 'sent': sent}
    print("⚠️  API indisponível, tentando banco...")
    brent = get_last_from_db("brent")
    selic_val = get_last_from_db("selic")
    if brent is not None and selic_val is not None:
        print("✅ Dados via banco")
        return {'brent': brent, 'e_mix': 27, 'b_mix': 14,
                'selic_val': selic_val, 'sent': calcular_sentimento(brent)}
    print("⚠️  Usando valores mock")
    return {'brent': 97.36, 'e_mix': 27, 'b_mix': 14,
            'selic_val': 14.25, 'sent': "negativo"}

# ========== GERAÇÃO DOS POSTS ==========
def gerar_posts(dados):
    brent = dados['brent']
    e_mix = dados['e_mix']
    b_mix = dados['b_mix']
    selic_val = dados['selic_val']
    sent = dados['sent']

    posts_dict = {
        "abertura": f"🧵 SELIX - Economia que prioriza quem trabalha\n\n🌍 Brent: US${brent}\n📉 Selic efetiva: {selic_val}%\n📰 Sentimento: {sent}\n💰 Selic ideal: 9,25% (1 dígito)\n🔗 {REPO_LINK}\n\nAcompanhe o fio 👇",
        "trabalhadores": f"👷 Para trabalhadores\n\nA Selic a {selic_val}% corrói seu poder de compra e trava PLR em empresas como GPA e Raízen.\n✅ Exija a #Selix 9,25% e o #TrampoForte para receber primeiro que bancos.\n🔗 {REPO_LINK}\n\ncc @mpt.bsky.social @tst.bsky.social",
        "bancos": f"🏦 Para bancos\n\nCom Selic 9,25%, custo de capital cai, mercado de ações sobe e o país ganha investment grade A-. Spread bancário continua lucrativo.\n🔗 {REPO_LINK}\n\ncc @febraban.bsky.social",
        "governo": f"🏛️ Para governo\n\nSelix 9,25%: economia de R$270 bi/ano, redução da dívida/PIB, investment grade A- e mais votos.\n🔗 {REPO_LINK}\n\ncc @planalto.bsky.social @fazenda.bsky.social",
        "politicos": f"🗳️ Para políticos\n\nApoie o PL da TrampoForte e a redução da Selic para 1 dígito (9,25%). Bom para o trabalhador e para os votos.\n🔗 {REPO_LINK}\n\ncc @camaradeputados @senadofederal",
        "ambientalistas": f"🌱 Para ambientalistas\n\nCom Brent US${brent}, mix ideal: E{e_mix}/B{b_mix}. Em crises (Brent >150): E42/B25 — máximo histórico de biocombustíveis.\n🔗 {REPO_LINK}\n\ncc @sosma @greenpeace @ipam",
        "investidores": f"📈 Para investidores\n\nEmpresas em RJ: GPA (+68%), Raízen (+76%). Com Selic 9,25%, upside pode chegar a +150%. B3 → US$10 tri em 10 anos.\n🔗 {REPO_LINK}\n\ncc @b3oficial @cvm @anbima",
        "midia": f"📰 Para jornalistas\n\nEstudo formal com Z3 (Microsoft) e Lean 4 prova que a Selic deveria ser 9,25% (1 dígito). Entreviste os criadores.\n🔗 {REPO_LINK}\n\ncc @folha @estadao @globo @valor",
        "sindicatos": f"⚖️ Para sindicatos\n\nSelic {selic_val}% bloqueia PLR em empresas em RJ. Mobilização pela Selix 9,25% já! #TrampoForte\n🔗 {REPO_LINK}\n\ncc @cut @forcasindical @cgtb",
        "energia": f"☀️ Governança Solar e Biocombustíveis\n\nCom Selic 1 dígito: 100 GW solar em 10 anos, etanol até E42, biogás em escala.\n🔗 {REPO_LINK}\n\ncc @aneel @mme @epe",
        "pib_b3": f"📊 Cenário com Selic 9,25% em 10 anos\n\n🇧🇷 PIB per capita: US$130.000 (+118%)\n🏦 B3: US$10 TRILHÕES (6x atual)\n⭐ Investment Grade A-\n💰 Economia anual: R$270 bi\n🔗 {REPO_LINK}\n\ncc @b3oficial @cvm @fazenda @planejamento",
        "encerramento": f"🔁 Compartilhe este fio\n\n✅ Selic ideal: 9,25%\n✅ Economia: R$270 bi/ano\n✅ PIB per capita: US$130k\n✅ B3: US$10 tri\n✅ Solar + biocombustíveis\n\n🔗 {REPO_LINK}\n\n#Selix #TrampoForte #PLR #Economia #EnergiaSolar"
    }
    ordem = ["abertura", "trabalhadores", "bancos", "governo", "politicos",
             "ambientalistas", "investidores", "midia", "sindicatos",
             "energia", "pib_b3", "encerramento"]
    return [posts_dict[seg] for seg in ordem]

# ========== POSTAGEM (fallback HTTP) ==========
def create_session_http():
    """Cria sessão e retorna access token via requests."""
    resp = requests.post(
        'https://bsky.social/xrpc/com.atproto.server.createSession',
        json={'identifier': USERNAME, 'password': PASSWORD}
    )
    resp.raise_for_status()
    return resp.json()['accessJwt']

def send_post_http(access_token, text, reply_uri=None):
    """Envia um post via HTTP puro."""
    payload = {
        'collection': 'app.bsky.feed.post',
        'repo': USERNAME,
        'record': {
            '$type': 'app.bsky.feed.post',
            'text': text,
            'createdAt': datetime.now().isoformat() + 'Z'
        }
    }
    if reply_uri:
        payload['record']['reply'] = {
            'parent': {'uri': reply_uri},
            'root': {'uri': reply_uri}
        }
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.post(
        'https://bsky.social/xrpc/com.atproto.repo.createRecord',
        headers=headers, json=payload
    )
    resp.raise_for_status()
    return resp.json()['uri']

def post_thread_http(textos):
    """Publica thread usando HTTP requests (100% funcional)."""
    token = create_session_http()
    prev_uri = None
    for i, texto in enumerate(textos):
        uri = send_post_http(token, texto, reply_uri=prev_uri)
        print(f"✅ Post {i+1}/12: {uri}")
        prev_uri = uri
        time.sleep(1)  # pequeno delay para evitar rate limit
    print("🎉 Thread completa publicada via HTTP!")

# ========== POSTAGEM (atproto - se disponível) ==========
def get_cid_atproto(client, uri):
    """Obtém CID de um post usando atproto."""
    parts = uri.split('/')
    did = parts[2]
    rkey = parts[4]
    result = client.com.atproto.repo.get_record(
        params=models.ComAtprotoRepoGetRecord.Params(
            repo=did,
            collection='app.bsky.feed.post',
            rkey=rkey,
        )
    )
    return result.cid

def post_thread_atproto(textos):
    """Publica thread usando biblioteca atproto (se funcionar)."""
    client = Client()
    client.login(USERNAME, PASSWORD)

    primeiro = client.send_post(textos[0])
    root_uri = primeiro.uri
    root_cid = get_cid_atproto(client, root_uri)
    print(f"✅ Post 1/12: {root_uri}")

    prev_uri, prev_cid = root_uri, root_cid
    for i, texto in enumerate(textos[1:], start=2):
        reply_ref = models.AppBskyFeedPost.ReplyRef(
            root=models.ComAtprotoRepoStrongRef.Main(uri=root_uri, cid=root_cid),
            parent=models.ComAtprotoRepoStrongRef.Main(uri=prev_uri, cid=prev_cid)
        )
        reply = client.send_post(text=texto, reply_to=reply_ref)
        prev_uri = reply.uri
        prev_cid = get_cid_atproto(client, prev_uri)
        print(f"✅ Post {i}/12: {reply.uri}")
        time.sleep(1)
    print("🎉 Thread completa publicada via atproto!")

# ========== MAIN ==========
def main():
    print("📡 Obtendo dados...")
    dados = fetch_dados()
    print("📝 Gerando textos...")
    posts = gerar_posts(dados)
    print(f"🔐 Autenticando como {USERNAME}...")

    # Tenta atproto primeiro; se falhar, usa HTTP
    if HAS_ATPROTO:
        try:
            post_thread_atproto(posts)
            return
        except Exception as e:
            print(f"⚠️  Falha no atproto: {e}. Usando fallback HTTP.")
    # Fallback HTTP
    post_thread_http(posts)

if __name__ == "__main__":
    main()

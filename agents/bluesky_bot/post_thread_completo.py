#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# post_thread_completo.py
# Versão: 1.0.0-GOS3
# Responsabilidade: Publicar thread completa (12 posts) do Selix no Bluesky
# Assinatura: GOS3/2026-06-02/agents/bluesky_bot/post_thread_completo.py
#
# Requisitos: atproto, requests, python-dotenv
# Uso: python post_thread_completo.py
# A chave da API deve estar definida em /root/selix/.env como SELIX_API_KEY ou MASTER_API_KEY

import os
import sys
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client, models

# Carrega variáveis do .env (fora do repositório)
load_dotenv('/root/selix/.env')

# ========== CREDENCIAIS ==========
USERNAME = os.getenv('BLUESKY_USERNAME')
PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')
if not USERNAME or not PASSWORD:
    print("❌ Credenciais do Bluesky não encontradas no .env")
    sys.exit(1)

API_KEY = os.getenv('SELIX_API_KEY') or os.getenv('MASTER_API_KEY')
if not API_KEY:
    print("❌ Nenhuma chave de API encontrada. Configure SELIX_API_KEY ou MASTER_API_KEY no .env")
    sys.exit(1)

# ========== CONFIGURAÇÕES ==========
API_BASE = "http://localhost:5000"
REPO_LINK = "github.com/scoobiii/selix"
DB_PATH = "/root/selix/selix.db"
HEADERS = {"X-API-Key": API_KEY}

# ========== FUNÇÕES AUXILIARES ==========
def fetch_from_api(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"⚠️ API {endpoint} retornou {r.status_code}")
    except Exception as e:
        print(f"⚠️ API {endpoint} falhou: {e}")
    return None

def get_last_from_db(table, field):
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
        print(f"⚠️ Erro no banco ({table}): {e}")
        return None

def calcular_sentimento(brent):
    if brent > 90:
        return "negativo"
    elif brent < 70:
        return "positivo"
    else:
        return "neutro"

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
        return {
            'brent': brent,
            'e_mix': e_mix,
            'b_mix': b_mix,
            'selic_val': selic_val,
            'sent': sent
        }
    print("⚠️ API indisponível, tentando banco...")
    brent = get_last_from_db("brent", "price")
    selic_val = get_last_from_db("selic", "rate")
    if brent is not None and selic_val is not None:
        e_mix = 27
        b_mix = 14
        sent = calcular_sentimento(brent)
        print("✅ Dados via banco")
        return {
            'brent': brent,
            'e_mix': e_mix,
            'b_mix': b_mix,
            'selic_val': selic_val,
            'sent': sent
        }
    print("⚠️ Usando valores mock")
    brent = 97.36
    selic_val = 14.25
    e_mix = 27
    b_mix = 14
    sent = calcular_sentimento(brent)
    return {
        'brent': brent,
        'e_mix': e_mix,
        'b_mix': b_mix,
        'selic_val': selic_val,
        'sent': sent
    }

def gerar_posts(dados):
    brent = dados['brent']
    e_mix = dados['e_mix']
    b_mix = dados['b_mix']
    selic_val = dados['selic_val']
    sent = dados['sent']

    posts_dict = {
        "abertura": f"🧵 **SELIX - Economia que prioriza quem trabalha**\n\n🌍 Brent: US${brent}\n📉 Selic efetiva: {selic_val}%\n📰 Sentimento: {sent}\n💰 Selic ideal: 9,25% (1 dígito)\n🔗 {REPO_LINK}\n\nAcompanhe o fio 👇",
        "trabalhadores": f"👷 **Para trabalhadores**\n\nA Selic a {selic_val}% corrói seu poder de compra e trava o pagamento de PLR em empresas como GPA e Raízen.\n✅ Exija a #Selix 9,25% e o #TrampoForte para receber primeiro que bancos.\n🔗 {REPO_LINK}\n\ncc @mpt.bsky.social @tst.bsky.social",
        "bancos": f"🏦 **Para bancos**\n\nCom Selic 9,25% (1 dígito), o custo de capital cai, o mercado de ações sobe e o país ganha investment grade A-. Spread bancário continua lucrativo.\n🔗 {REPO_LINK}\n\ncc @febraban.bsky.social",
        "governo": f"🏛️ **Para governo**\n\nSelix 9,25%: economia de R$270 bi/ano, redução da dívida/PIB, investment grade A- e mais votos.\n🔗 {REPO_LINK}\n\ncc @planalto.bsky.social @fazenda.bsky.social",
        "politicos": f"🏛️ **Para políticos**\n\nApoie o PL da TrampoForte e a redução da Selic para 1 dígito (9,25%). É bom para o trabalhador e para os votos.\n🔗 {REPO_LINK}\n\ncc @camaradeputados @senadofederal",
        "ambientalistas": f"🌱 **Para ambientalistas**\n\nCom Brent US${brent}, o mix ideal é {e_mix}/{b_mix}. Em crises (Brent >150): E42/B25 (máximo histórico de biocombustíveis).\n🔗 {REPO_LINK}\n\ncc @sosma @greenpeace @ipam",
        "investidores": f"📈 **Para investidores**\n\nEmpresas em RJ: GPA (+68%), Raízen (+76%). Com Selic 9,25%, o upside pode chegar a +150%. B3 pode atingir US$ 10 trilhões em 10 anos.\n🔗 {REPO_LINK}\n\ncc @b3oficial @cvm @anbima",
        "midia": f"📰 **Para jornalistas**\n\nEstudo formal com Z3 (Microsoft) e Lean 4 prova que a Selic deveria ser 9,25% (1 dígito). Entreviste os criadores.\n🔗 {REPO_LINK}\n\ncc @folha @estadao @globo @valor",
        "sindicatos": f"⚖️ **Para sindicatos**\n\nSelic {selic_val}% > ROI bloqueia PLR em empresas em RJ. Mobilização pela Selix 9,25% já! #TrampoForte\n🔗 {REPO_LINK}\n\ncc @cut @forcasindical @cgtb",
        "energia": f"☀️ **Governança Solar e Biocombustíveis**\n\nCom Selic 1 dígito, o Brasil pode acelerar: 100 GW solar em 10 anos, etanol até E42, biogás.\n🔗 {REPO_LINK}\n\ncc @aneel @mme @epe",
        "pib_b3": f"📊 **Cenário com Selic 9,25% em 10 anos**\n\n🇧🇷 PIB per capita: US$ 130.000 (+118%)\n🏦 B3 Market Cap: US$ 10 TRILHÕES (6x atual)\n⭐ Investment Grade: A-\n💰 Economia anual: R$ 270 bi\n🔗 {REPO_LINK}\n\ncc @b3oficial @cvm @fazenda @planejamento",
        "encerramento": f"🔁 **Compartilhe este fio**\n\n✅ Selic ideal: 9,25% (1 dígito)\n✅ Economia: R$270 bi/ano\n✅ PIB per capita: US$130k\n✅ B3: US$10 tri\n✅ Energia solar + biocombustíveis\n\nAcesse o estudo completo:\n🔗 {REPO_LINK}\n\n#Selix #TrampoForte #PLR #Economia #EnergiaSolar"
    }
    ordem = ["abertura", "trabalhadores", "bancos", "governo", "politicos",
             "ambientalistas", "investidores", "midia", "sindicatos",
             "energia", "pib_b3", "encerramento"]
    return [posts_dict[seg] for seg in ordem]

def post_thread(client, textos):
    """Publica thread corretamente (primeiro + replies)."""
    if not textos:
        return
    # Primeiro post
    primeiro = client.send_post(textos[0])
    print(f"✅ Post principal: {primeiro.uri}")
    prev_uri = primeiro.uri

    # Função auxiliar para extrair did e rkey da URI
    def extract_did_rkey(uri):
        parts = uri.split('/')
        # uri = at://did:plc:xxx/app.bsky.feed.post/rkey
        return parts[2], parts[4]   # did, rkey

    for texto in textos[1:]:
        did, rkey = extract_did_rkey(prev_uri)
        # Obtém o CID do post anterior
        post_info = client.com.atproto.repo.get_record(
            repo=did,
            collection='app.bsky.feed.post',
            rkey=rkey
        )
        cid = post_info.cid
        reply_ref = models.AppBskyFeedPost.ReplyRef(
            parent=models.ComAtprotoRepoStrongRef.Main(uri=prev_uri, cid=cid),
            root=models.ComAtprotoRepoStrongRef.Main(uri=prev_uri, cid=cid)
        )
        reply = client.send_post(text=texto, reply_to=reply_ref)
        print(f"✅ Reply enviado: {reply.uri}")
        prev_uri = reply.uri


def main():
    print("📡 Obtendo dados...")
    dados = fetch_dados()
    print("📝 Gerando textos...")
    posts = gerar_posts(dados)
    print(f"🔐 Autenticando como {USERNAME}...")
    client = Client()
    client.login(USERNAME, PASSWORD)
    print("🧵 Publicando thread...")
    post_thread(client, posts)
    print("🎉 Thread completa publicada!")

if __name__ == "__main__":
    main()

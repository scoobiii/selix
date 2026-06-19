#!/usr/bin/env python3
"""
SELIX – Thread do Roubo Diário (USANDO API LOCAL)
Conta: @selixbr.bsky.social (ou @zeh-sobrinho.bsky.social)
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from getpass import getpass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURAÇÃO – API LOCAL
# ============================================================
API_BASE = "http://localhost:5000"
ENDPOINT_SELIC = f"{API_BASE}/v1/selic"
ENDPOINT_HEALTH = f"{API_BASE}/v1/health"

# Conta principal (mude se quiser usar zeh-sobrinho)
BLUESKY_HANDLE = os.environ.get("BLUESKY_USERNAME", "selixbr.bsky.social")

STAKEHOLDERS = ["@josephkalim", "@andreadamico", "@robertosecemski", "@bankofamerica", "@serasaexperian", "@galipolo"]

# ============================================================
# VERIFICA SE A API LOCAL ESTÁ RODANDO
# ============================================================
def check_api():
    try:
        resp = requests.get(ENDPOINT_HEALTH, timeout=3)
        return resp.status_code == 200
    except:
        return False

# ============================================================
# OBTÉM DADOS DA API LOCAL
# ============================================================
def get_selic_data():
    try:
        resp = requests.get(ENDPOINT_SELIC, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            selic_real = data.get('rate', 14.25)
            timestamp = data.get('timestamp', datetime.now().isoformat())
            return selic_real, timestamp
    except Exception as e:
        logger.error(f"❌ Erro na API: {e}")
    return 14.25, datetime.now().isoformat()

def get_selic_ideal():
    return 9.48  # Valor fixo do SELIX

# ============================================================
# CONSTRÓI THREAD
# ============================================================
def build_thread(selic_real, selic_ideal):
    desvio = selic_real - selic_ideal
    custo_bilhoes = desvio * 0.01 * 10_000

    mencoes = " ".join(STAKEHOLDERS)

    return [
        f"1/10 🧵 A COPA É A CORTINA, A SELIC É O ROUBO\n\nEnquanto o Brasil vê futebol, o BC (Galípolo) esconde a maior transferência de renda da história. Selic a {selic_real}% enquanto a inflação está CONTROLADA.\n\n{mencoes}",
        f"2/10 💰 O CÁLCULO É SIMPLES\nSelic real: {selic_real}%\nSelic ideal (SELIX): {selic_ideal}%\nDesvio: {desvio:.2f} p.p.\nCusto extra: R$ {custo_bilhoes:,.0f} bi/ano\n\nIsso é o que o rentista tira do seu bolso.",
        "3/10 🏦 GALÍPOLO E A COPA\nEnquanto a Fifa fatura, o BC finge que não vê. A Selic não baixa porque o rentista é o patrocinador oficial do 'tigrinho'.",
        "4/10 📉 O RESULTADO?\n- Raízen em RJ (R$75 bi em dívida)\n- Braskem com PL negativo\n- 80% das famílias em recuperação judicial\n- PLR congelada",
        "5/10 🔥 A PROVA ESTÁ AQUI\n🔗 https://selix-555922434592.us-west2.run.app/\n\nNão é opinião. É matemática com Z3 e Lean 4.",
        "6/10 🛠️ O QUE O SELIX FAZ?\n- Prova formal da Selic ideal\n- API pública\n- Bot no Bluesky posta o roubo diário",
        "7/10 🎯 O QUE VOCÊ PODE FAZER?\n- Compartilhe a prova\n- Cobre os deputados\n- Use o SELIX no seu sindicato",
        "8/10 💀 O RENTISTA NÃO QUER QUE VOCÊ SAIBA\nPor isso a mídia não fala. Por isso o BC não baixa.",
        f"9/10 🚨 A SOLUÇÃO É TÉCNICA E POLÍTICA\nSelic ideal = {selic_ideal}%\nPLR atrelada à Selic real\nFundo Soberano Indígena",
        "10/10 🔗 LINKS\nDashboard: https://selix-555922434592.us-west2.run.app/\nCódigo: github.com/scoobiii/selix\nAgente Moltbook: moltbook.com/u/selixbr\n\n#SelicIdeal #ForaRentismo #Galipolo"
    ]

# ============================================================
# PUBLICA NO BLUESKY
# ============================================================
def post_bluesky(thread):
    try:
        from atproto import Client, models
    except ImportError:
        logger.error("❌ atproto não instalado. Instale: pip install atproto")
        return False

    handle = BLUESKY_HANDLE
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not password:
        password = getpass(f"🔑 Senha para {handle}: ")

    logger.info(f"🔐 Conectando a {handle}...")
    client = Client()
    client.login(handle, password)
    logger.info("✅ Conectado!")

    parent = None
    root = None

    for i, text in enumerate(thread, 1):
        try:
            if parent:
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    parent=models.ComAtprotoRepoStrongRef.Main(uri=parent["uri"], cid=parent["cid"]),
                    root=models.ComAtprotoRepoStrongRef.Main(uri=root["uri"], cid=root["cid"])
                )
                post = client.send_post(text=text, reply_to=reply_ref)
            else:
                post = client.send_post(text=text)
                root = {"uri": post.uri, "cid": post.cid}

            logger.info(f"✅ Post {i}/10")
            parent = {"uri": post.uri, "cid": post.cid}
            time.sleep(8)
        except Exception as e:
            logger.error(f"❌ Falha no post {i}: {e}")
            return False

    logger.info("🎉 Thread publicada com sucesso!")
    return True

# ============================================================
# ÚLTIMAS POSTAGENS
# ============================================================
def get_last_posts():
    try:
        from atproto import Client
    except ImportError:
        logger.error("❌ atproto não instalado")
        return

    handle = BLUESKY_HANDLE
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not password:
        password = getpass(f"🔑 Senha para {handle}: ")

    client = Client()
    client.login(handle, password)

    profile = client.get_profile(handle)
    feed = client.get_author_feed(profile.did, limit=5)

    print(f"\n📰 ÚLTIMAS POSTAGENS DE {handle}\n")
    for i, post in enumerate(feed.feed, 1):
        text = post.post.record.text.replace('\n', ' ')[:80]
        print(f"{i}. {text}...")
        print(f"   🔗 https://bsky.app/profile/{handle}/post/{post.post.uri.split('/')[-1]}\n")

# ============================================================
# MAIN
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="SELIX Thread do Roubo Diário")
    parser.add_argument("--check", action="store_true", help="Verifica últimas postagens")
    parser.add_argument("--post", action="store_true", help="Publica thread")
    args = parser.parse_args()

    print("\n🔥 SELIX – Thread do Roubo Diário\n")

    if args.check:
        get_last_posts()
        return

    if not check_api():
        logger.error("❌ API SELIX local não está rodando!")
        logger.info("   Inicie: cd /root/selix && python src/api/main_v4_fixed.py &")
        return

    selic_real, timestamp = get_selic_data()
    selic_ideal = get_selic_ideal()
    thread = build_thread(selic_real, selic_ideal)

    logger.info(f"📊 Selic real: {selic_real}% | Ideal: {selic_ideal}%")
    logger.info(f"📅 Dados de: {timestamp}")

    if args.post or not args.check:
        post_bluesky(thread)

if __name__ == "__main__":
    main()

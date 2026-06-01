#!/usr/bin/env python3
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv()
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

API_BASE = "http://localhost:5000"

def get_energia():
    r = requests.get(f"{API_BASE}/v1/energia/mistura")
    return r.json()

def get_empresas():
    r = requests.get(f"{API_BASE}/v1/empresas/rj")
    return r.json() if r.status_code == 200 else []

def post_thread():
    energia = get_energia()
    brent = energia['brent_usd']
    e_mix = energia['etanol']['mistura']
    b_mix = energia['biodiesel']['mistura']
    empresas = get_empresas()

    # Post principal
    main = client.send_post(f"🧵 #Selix - Impacto da Selic 9,25% (vs 14,5%)\n🌍 Brent ${brent} → {e_mix}/{b_mix}\nEconomia: R$270 bi/ano\nAcompanhe:")
    time.sleep(2)

    # Posts para cada empresa
    for emp in empresas:
        plr = emp.get('plr_devido', '?')
        msg = f"🏢 {emp['nome']} ({emp['codigo_b3']})\n👥 {emp['funcionarios']} trabalhadores\n⚠️ PLR bloqueado: R$ {plr}\n📈 Upside com Selix: {emp['potencial_percentual']}%\n#TrampoForte"
        client.send_post(msg, reply_to=main.uri)
        time.sleep(3)

def responder_mencoes():
    # Busca as últimas menções (feed do usuário)
    timeline = client.app.bsky.feed.get_author_feed(actor=os.getenv('BLUESKY_USERNAME'))
    for feed_view in timeline.feed:
        post = feed_view.post
        # Verifica se o post menciona o bot
        if 'zeh-sobrinho.bsky.social' in post.text and not post.viewer.reply:
            resposta = f"Olá! Com Selix 9,25%, a economia seria de R$270 bi/ano. Mais dados: {API_BASE}/v1/energia/mistura"
            client.send_post(resposta, reply_to=post.uri)
            time.sleep(5)
            break

if __name__ == "__main__":
    agora = datetime.now()
    if agora.hour == 9:
        post_thread()
    # Loop para responder menções a cada 10 minutos
    while True:
        responder_mencoes()
        time.sleep(600)

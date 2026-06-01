#!/usr/bin/env python3
"""
SELIX v3.5.0 – Publicação rotativa (1 post por hora, alternando segmentos)
"""
import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv('/root/selix/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

API_BASE = "http://localhost:5000"
REPO_LINK = "github.com/scoobiii/selix"

# Perfis para CC (menções)
MENTIONS = {
    "trabalhadores": "@mpt.bsky.social @tst.bsky.social",
    "bancos": "@febraban.bsky.social",
    "governo": "@planalto.bsky.social @fazenda.bsky.social",
    "politicos": "@camaradeputados @senadofederal",
    "ambientalistas": "@sosma @greenpeace",
    "investidores": "@b3oficial @cvm",
    "midia": "@folha @estadao @globo",
    "sindicatos": "@cut @forcasindical"
}

def get_energia():
    r = requests.get(f"{API_BASE}/v1/energia/mistura")
    return r.json()

def get_selic():
    r = requests.get(f"{API_BASE}/v1/selic")
    if r.status_code == 200:
        data = r.json()
        for item in data:
            if item['tipo'] == 'efetiva':
                return item['valor'], item.get('is_stale', 0)
    return 14.40, 1

def get_sentimento():
    r = requests.get(f"{API_BASE}/v1/sentimento")
    if r.status_code == 200:
        data = r.json()
        return data['sentimento'], data['score']
    return "NEUTRO", 0

def get_segmento_atual():
    hora = datetime.now().hour
    segmentos = list(MENTIONS.keys())
    segmentos_full = segmentos + ["encerramento"] * (24 - len(segmentos))
    return segmentos_full[hora % 24]

def montar_post_por_segmento(segmento, energia, selic_val, selic_stale, sentimento):
    brent = energia['brent_usd']
    e_mix = energia['etanol']['mistura']
    b_mix = energia['biodiesel']['mistura']
    stale_mark = " (dado aproximado)" if selic_stale else ""

    posts = {
        "trabalhadores": f"👷 **Para trabalhadores**\n\nA Selic a 14,5% corrói seu poder de compra e trava o pagamento de PLR em empresas como GPA e Raízen.\n✅ Exija a #Selix 9,25% e o #TrampoForte para receber primeiro que bancos.\n🔗 {REPO_LINK}\n\ncc {MENTIONS['trabalhadores']}",
        
        "bancos": f"🏦 **Para bancos**\n\nCom Selic 9,25%, o custo de capital cai, o mercado de ações sobe e o país ganha investment grade (BBB+).\n🔗 {REPO_LINK}\n\ncc {MENTIONS['bancos']}",
        
        "governo": f"🏛️ **Para governo**\n\nSelix 9,25%: economia de R$270 bi/ano, redução da dívida/PIB, investment grade e mais votos.\n🔗 {REPO_LINK}\n\ncc {MENTIONS['governo']}",
        
        "politicos": f"🏛️ **Para políticos**\n\nApoie o PL da TrampoForte e a redução da Selic. É bom para o trabalhador e para a economia.\n🔗 {REPO_LINK}\n\ncc {MENTIONS['politicos']}",
        
        "ambientalistas": f"🌱 **Para ambientalistas**\n\nBrent US${brent} → mix ideal {e_mix}/{b_mix}. O modelo prioriza renováveis e reduz emissões.\n🔗 {REPO_LINK}\n\ncc {MENTIONS['ambientalistas']}",
        
        "investidores": f"📈 **Para investidores**\n\nEmpresas em RJ: GPA (+68%), Raízen (+76%). Selic 9,25% desbloqueia valor.\n🔗 {REPO_LINK}\n\ncc {MENTIONS['investidores']}",
        
        "midia": f"📰 **Para jornalistas**\n\nEstudo formal com Z3 (Microsoft) e Lean 4 prova que a Selic deveria ser 9,25%.\n🔗 {REPO_LINK}\n\ncc {MENTIONS['midia']}",
        
        "sindicatos": f"⚖️ **Para sindicatos**\n\nSelic > ROI bloqueia PLR em RJ. Mobilização pela Selix 9,25% já! #TrampoForte\n🔗 {REPO_LINK}\n\ncc {MENTIONS['sindicatos']}",
        
        "encerramento": f"🔁 **Compartilhe**\n\nSelic ideal é 9,25% (prova Z3+Lean4). Acesse o estudo completo:\n🔗 {REPO_LINK}\n\n🌍 Brent: US${brent}\n📉 Selic efetiva: {selic_val}%{stale_mark}\n📰 Sentimento: {sentimento}\n\n#Selix #TrampoForte #PLR #Economia"
    }
    return posts.get(segmento, posts["encerramento"])[:300]

def post_rotativo():
    energia = get_energia()
    selic_val, selic_stale = get_selic()
    sentimento, _ = get_sentimento()
    stale_mark = " (dado aproximado)" if selic_stale else ""
    
    segmento = get_segmento_atual()
    post_content = montar_post_por_segmento(segmento, energia, selic_val, selic_stale, sentimento)
    
    # Post de abertura (apenas na hora 0)
    if datetime.now().hour == 0:
        abertura = f"🧵 **SELIX - Economia que prioriza quem trabalha**\n\n🌍 Brent: {energia['brent_usd']}\n📉 Selic efetiva: {selic_val}%{stale_mark}\n📰 Sentimento: {sentimento}\n🔗 {REPO_LINK}\n\nAcompanhe os posts diários com dados em tempo real! 👇"
        client.send_post(abertura[:300])
        print(f"📌 Post de abertura enviado às {datetime.now()}")
        time.sleep(3)
    
    # Envia o post segmentado
    client.send_post(post_content)
    print(f"✅ Post enviado para segmento '{segmento}' às {datetime.now()}")

if __name__ == "__main__":
    try:
        post_rotativo()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

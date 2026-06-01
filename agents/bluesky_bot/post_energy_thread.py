6#!/usr/bin/env python3
import os
import time
import requests
from dotenv import load_dotenv
from atproto import Client, models

# Carrega credenciais
load_dotenv()
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

API_BASE = "http://localhost:5000"

def get_energia():
    r = requests.get(f"{API_BASE}/v1/energia/mistura")
    return r.json()

def get_empresas():
    try:
        r = requests.get(f"{API_BASE}/v1/empresas/rj")
        if r.status_code == 200:
            return r.json()
        else:
            return []
    except:
        return []

def post_energy_thread():
    print("🚀 Publicando thread do Energy Predictor...")
    energia = get_energia()
    brent = energia.get('brent_usd', 'N/A')
    e_mix = energia.get('etanol', {}).get('mistura', 'N/A')
    b_mix = energia.get('biodiesel', {}).get('mistura', 'N/A')

    # Conteúdo da thread (cada string é um post)
    posts = [
        f"🧵 #EnergyPredictor: como o SELIX calcula a mistura ideal de etanol (E%) e biodiesel (B%) com base no preço do Brent (hoje US${brent})? Um fio para governo, empresas, ambientalistas e trabalhadores. 👇",
        "🏛️ Governo/ANEEL/MME: Gatilhos do Energy Predictor:\n- Brent < US$70 → E27/B14\n- >US$90 → E30/B15\n- >US$120 → E35/B20\n- >US$150 → E42/B25\nRegras abertas: github.com/scoobiii/selix",
        "⚡ Termelétricas flexíveis (17,3 GW mapeados):\n• Gás natural (15 GW)\n• Etanol (1,2 GW)\n• Biodiesel (0,8 GW)\n• Biogás (0,3 GW)\nCom Brent alto, acionamos biocombustíveis e reduzimos emissões.",
        "🌍 Ambientalistas: Quanto maior o Brent, maior a mistura de biocombustíveis (até E42/B25). O modelo prioriza renováveis, reduzindo termelétricas fósseis. Código aberto para auditoria. #TransiçãoEnergética",
        "📈 Investidores: O Energy Predictor expõe: preço do Brent → mistura E/B → oferta de etanol/biodiesel. Termelétricas flex aumentam segurança energética. Modelo preditivo pode precificar risco e créditos de carbono.",
        "⛽ Trabalhadores do setor: Usinas de etanol, biodiesel e termelétricas são valorizadas em crises (Brent alto). Selic 9,25% reduz custo do capital e incentiva investimentos no setor. #TrampoForte",
        f"🔗 API v3.3 em tempo real: /v1/energia/mistura (recomendação atual: E{e_mix}/B{b_mix}), /v1/energia/gatilhos, /v1/energia/termicas. Desenvolvedores, integrem! Código aberto. #Selix"
    ]

    # Envia o primeiro post (root)
    root = client.send_post(posts[0])
    print("Post principal enviado. Aguardando 3 segundos...")
    time.sleep(3)

    # Para cada post seguinte, cria um reply ao root
    for content in posts[1:]:
        # Monta a referência do reply corretamente
        reply_ref = models.AppBskyFeedPost.ReplyRef(
            parent=models.ComAtprotoRepoStrongRef.Main(uri=root.uri, cid=root.cid),
            root=models.ComAtprotoRepoStrongRef.Main(uri=root.uri, cid=root.cid)
        )
        client.send_post(content, reply_to=reply_ref)
        print("Reply enviado. Aguardando 5 segundos...")
        time.sleep(5)

    print("✅ Thread do Energy Predictor publicada com sucesso!")

if __name__ == "__main__":
    post_energy_thread()

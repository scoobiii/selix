#!/usr/bin/env python3
import os, sys, time, requests
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv('/app/.env')
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

API_BASE = "http://api:5000"   # nome do serviço no docker, ou localhost
REPO_LINK = "github.com/scoobiii/selix"

def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def get_segmento_atual():
    hora = datetime.now().hour
    segmentos = ["abertura","trabalhadores","bancos","governo","politicos",
                 "ambientalistas","investidores","midia","sindicatos",
                 "energia","pib_b3","encerramento"]
    return segmentos[hora % len(segmentos)]

def montar_post(segmento):
    energia = api_get("/v1/energia/mistura")
    selic_data = api_get("/v1/selic")
    sentimento = api_get("/v1/sentimento")
    if not energia or not selic_data or not sentimento:
        return f"⚠️ Dados de mercado temporariamente indisponíveis. Acesse {REPO_LINK} para saber sobre a #Selix 9,25%."
    brent = energia['brent_usd']
    e_mix = energia['etanol']['mistura']
    b_mix = energia['biodiesel']['mistura']
    selic_val = selic_data[0]['valor']
    sent = sentimento['sentimento']
    posts = {
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
    return posts.get(segmento, posts["encerramento"])[:300]

def post_rotativo():
    segmento = get_segmento_atual()
    post_content = montar_post(segmento)
    client.send_post(post_content)
    print(f"✅ Post enviado para segmento '{segmento}' às {datetime.now()}")

if __name__ == "__main__":
    try:
        post_rotativo()
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

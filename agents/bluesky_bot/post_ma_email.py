#!/usr/bin/env python3
"""
SELIX – Publica o e-mail da M&A Community como thread no Bluesky
Conteúdo: Proálcool preditivo, Energy Crash, Selic 9,48%
Assinatura: Designed & Powered by Galaxy A23
"""

import os
import sys
import time
import logging
from getpass import getpass
from atproto import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# THREAD – E-mail refinado (dividido em posts)
# ============================================================
THREAD = [
    "1/10\n📧 PROÁLCOOL PREDITIVO, ENERGY CRASH E O CUSTO DA SELIC ERRADA\n\nO que o M&A não está contando.\n\nA análise da quinzena está cirúrgica — Raízen, Braskem, Grupo João Santos, Mercuria, juro alto e balanço apertado.\n\nMas há uma camada que os números não capturam.\n\n@selixbr.bsky.social",

    "2/10\n🧠 O QUE O SELIX JÁ PROVOU MATEMATICAMENTE\n\nEnquanto o Bacen sustenta Selic 14% para compensar Brent/TTF, o SELIX (Z3+Lean4) prova que a Selic ideal é 9,48%.\n\n• Economia anual: R$ 270 bi\n• Blindagem ecológica Ex/Bx\n• Investment Grade BBB+\n\n🔗 github.com/scoobiii/selix",

    "3/10\n⚡ A GEOPOLÍTICA QUE O M&A ESTÁ PRECIFICANDO (MAS NÃO NOMEANDO)\n\nO crash energético de 2026 — POTUS + Netanyahu + TTF — é o mesmo padrão do choque do petróleo nos anos 70.\n\nO Proálcool original foi criado para combater isso. A mistura preditiva Ex/Bx poderia ter nos isolado.",

    "4/10\n🌍 O PLANO QUE FLOPOU\n\nNord Stream (€20/MWh) → GNL do Qatar → flopou.\nUcrânia → Marrocos (FIFA 2030) → flopou.\n\nEnquanto isso, o Brasil ficou assistindo. MME falhou na mistura preditiva. Bacen mantém a Selic como o 'tigrinho oficial'.",

    "5/10\n📉 O QUE ISSO SIGNIFICA PARA O M&A\n\nCom Selic em 14%:\n• Raízen (R$ 75,3 bi em dívida) sendo canibalizada\n• Braskem (PL negativo R$ 16,5 bi) na corda bamba\n• Ativos estratégicos vendidos a preço de banana para traders como Mercuria",

    "6/10\n💸 NÚMEROS QUE ASSUSTAM\n\n• 2.466 CNPJs em RJ (recorde Serasa 2025)\n• Mercuria comprou downstream da Raízen por US$ 1,42 bi\n• Grupo João Santos vendeu última jazida de calcário de SP por R$ 250 mi\n\nQuando se vende a opcionalidade, é porque não há mais margem.",

    "7/10\n🔐 A SAÍDA EXISTE (E É MATEMÁTICA)\n\nO SELIX não é teoria — é prova formal com Z3 e Lean 4.\n\nSe o Brasil adotasse a mistura preditiva e a Selic de 9,48%:\n• Empresas não precisariam vender ativos\n• PIB per capita não seria medíocre\n• Investment Grade seria realidade",

    "8/10\n🏆 O FUTURO QUE PODERÍAMOS TER\n\nEmpatar com Maricá/RJ (GDP per capita US$ 130k).\n\nRating soberano A+.\nInvestment Grade certification.\nCapital de verdade fluindo.\n\nEconomia que prioriza quem trabalha.",

    "9/10\n🔗 LINKS\n\n• Whitepaper: github.com/scoobiii/selix\n• Dashboard: selix-555922434592.us-west2.run.app\n• Agente Moltbook: moltbook.com/u/selixbr\n\nEstamos à disposição para apresentação técnica.",

    "10/10\n📱 DESIGNED & POWERED BY GALAXY A23\n\nSELIX rodando em hardware restrito — prova de que eficiência não depende de nuvem.\n\n#EnergyCrash #SelicIdeal #Proalcool #M&A #InvestmentGrade\n\n@selixbr.bsky.social"
]

# ============================================================
# FUNÇÃO DE POSTAGEM
# ============================================================
def post_thread(client, posts, delay=8):
    """Publica thread completa com replies"""
    parent_ref = None
    for i, text in enumerate(posts, 1):
        try:
            if parent_ref:
                post = client.send_post(text=text, reply_to=parent_ref)
            else:
                post = client.send_post(text=text)
            logger.info(f"✅ Post {i}/{len(posts)} publicado")
            parent_ref = {"uri": post.uri, "cid": post.cid}
            if i < len(posts):
                time.sleep(delay)
        except Exception as e:
            logger.error(f"❌ Falha no post {i}: {e}")
            return False
    return True

# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "="*50)
    print("📧 SELIX – Publicando e-mail M&A Community")
    print("="*50 + "\n")

    handle = os.environ.get("BLUESKY_USERNAME", "selixbr.bsky.social")
    password = os.environ.get("BLUESKY_APP_PASSWORD")

    if not password:
        password = getpass(f"🔐 App Password para {handle}: ")

    logger.info(f"Conectando a {handle}...")
    client = Client()
    client.login(handle, password)
    logger.info("✅ Conectado!")

    logger.info(f"📢 Publicando thread de {len(THREAD)} posts...")
    success = post_thread(client, THREAD, delay=8)

    if success:
        logger.info("🎉 THREAD COMPLETA PUBLICADA!")
        print("\n🔗 Ver em: https://bsky.app/profile/" + handle)
    else:
        logger.info("⚠️ Publicação interrompida.")

if __name__ == "__main__":
    main()

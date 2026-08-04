#!/usr/bin/env python3
"""
SELIX – Publica thread com proteção contra rate limit
- Delay maior entre posts (12 segundos)
- Verifica se já foi publicado (evita duplicação)
- Para se bater no limite
"""

import os
import sys
import time
import json
import logging
from getpass import getpass
from datetime import datetime
from pathlib import Path
from atproto import Client, models

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Estado para evitar duplicação
STATE_FILE = Path("/root/selix/logs/ma_email_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================================
# THREAD (10 posts)
# ============================================================
THREAD = [
    "1/10\n📧 PROÁLCOOL PREDITIVO, ENERGY CRASH E O CUSTO DA SELIC ERRADA\n\nO que o M&A não está contando.\n\nA análise da quinzena está cirúrgica — Raízen, Braskem, Grupo João Santos, Mercuria, juro alto e balanço apertado.\n\nMas há uma camada que os números não capturam.\n\n@zeh-sobrinho.bsky.social",
    "2/10\n🧠 O QUE O SELIX JÁ PROVOU MATEMATICAMENTE\n\nEnquanto o Bacen sustenta Selic 14% para compensar Brent/TTF, o SELIX (Z3+Lean4) prova que a Selic ideal é 9,48%.\n\n• Economia anual: R$ 270 bi\n• Blindagem ecológica Ex/Bx\n• Investment Grade BBB+\n\n🔗 github.com/scoobiii/selix",
    "3/10\n⚡ A GEOPOLÍTICA QUE O M&A ESTÁ PRECIFICANDO (MAS NÃO NOMEANDO)\n\nO crash energético de 2026 — POTUS + Netanyahu + TTF — é o mesmo padrão do choque do petróleo nos anos 70.\n\nO Proálcool original foi criado para combater isso. A mistura preditiva Ex/Bx poderia ter nos isolado.",
    "4/10\n🌍 O PLANO QUE FLOPOU\n\nNord Stream (€20/MWh) → GNL do Qatar → flopou.\nUcrânia → Marrocos (FIFA 2030) → flopou.\n\nEnquanto isso, o Brasil ficou assistindo. MME falhou na mistura preditiva. Bacen mantém a Selic como o 'tigrinho oficial'.",
    "5/10\n📉 O QUE ISSO SIGNIFICA PARA O M&A\n\nCom Selic em 14%:\n• Raízen (R$ 75,3 bi em dívida) sendo canibalizada\n• Braskem (PL negativo R$ 16,5 bi) na corda bamba\n• Ativos estratégicos vendidos a preço de banana para traders como Mercuria",
    "6/10\n💸 NÚMEROS QUE ASSUSTAM\n\n• 2.466 CNPJs em RJ (recorde Serasa 2025)\n• Mercuria comprou downstream da Raízen por US$ 1,42 bi\n• Grupo João Santos vendeu última jazida de calcário de SP por R$ 250 mi\n\nQuando se vende a opcionalidade, é porque não há mais margem.",
    "7/10\n🔐 A SAÍDA EXISTE (E É MATEMÁTICA)\n\nO SELIX não é teoria — é prova formal com Z3 e Lean 4.\n\nSe o Brasil adotasse a mistura preditiva e a Selic de 9,48%:\n• Empresas não precisariam vender ativos\n• PIB per capita não seria medíocre\n• Investment Grade seria realidade",
    "8/10\n🏆 O FUTURO QUE PODERÍAMOS TER\n\nEmpatar com Maricá/RJ (GDP per capita US$ 130k).\n\nRating soberano A+.\nInvestment Grade certification.\nCapital de verdade fluindo.\n\nEconomia que prioriza quem trabalha.",
    "9/10\n🔗 LINKS\n\n• Whitepaper: github.com/scoobiii/selix\n• Dashboard: selix-555922434592.us-west2.run.app\n• Agente Moltbook: moltbook.com/u/selixbr\n\nEstamos à disposição para apresentação técnica.",
    "10/10\n📱 DESIGNED & POWERED BY GALAXY A23\n\nSELIX rodando em hardware restrito — prova de que eficiência não depende de nuvem.\n\n#EnergyCrash #SelicIdeal #Proalcool #M&A #InvestmentGrade\n\n@zeh-sobrinho.bsky.social"
]

# ============================================================
# FUNÇÃO PARA CARREGAR/SALVAR ESTADO
# ============================================================
def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            return {"published": []}
    return {"published": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ============================================================
# FUNÇÃO DE POSTAGEM COM RATE LIMIT PROTECTION
# ============================================================
def post_thread(client, posts, delay=12, max_posts_per_day=8):
    """Publica thread com proteção contra rate limit"""
    state = load_state()
    published = state.get("published", [])
    
    # Identificador único da thread
    thread_id = "ma_email_2026_06_16"
    
    # Verifica se já foi publicada
    if thread_id in published:
        logger.info(f"⏭️ Thread '{thread_id}' já foi publicada. Pulando.")
        return True
    
    # Verifica quantos posts já foram feitos hoje
    today = datetime.now().strftime("%Y-%m-%d")
    today_posts = [p for p in published if p.startswith(today)]
    
    if len(today_posts) >= max_posts_per_day:
        logger.warning(f"⚠️ Limite de {max_posts_per_day} posts/dia atingido.")
        logger.info(f"   Posts de hoje: {len(today_posts)}")
        logger.info(f"   Aguarde até amanhã para continuar.")
        return False
    
    logger.info(f"📢 Publicando thread de {len(posts)} posts...")
    logger.info(f"   Delay entre posts: {delay}s")
    logger.info(f"   Limite diário: {max_posts_per_day} posts")
    
    parent_ref = None
    root_ref = None
    
    for i, text in enumerate(posts, 1):
        # Verifica limite diário antes de cada post
        if len([p for p in state.get("published", []) if p.startswith(today)]) >= max_posts_per_day:
            logger.warning(f"⚠️ Limite diário atingido no post {i}.")
            logger.info(f"   Posts publicados hoje: {len([p for p in state.get('published', []) if p.startswith(today)])}")
            logger.info(f"   Thread incompleta. Continue amanhã.")
            save_state(state)
            return False
        
        try:
            if parent_ref:
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    parent=models.ComAtprotoRepoStrongRef.Main(
                        uri=parent_ref["uri"],
                        cid=parent_ref["cid"]
                    ),
                    root=models.ComAtprotoRepoStrongRef.Main(
                        uri=root_ref["uri"],
                        cid=root_ref["cid"]
                    )
                )
                post = client.send_post(text=text, reply_to=reply_ref)
            else:
                post = client.send_post(text=text)
                root_ref = {"uri": post.uri, "cid": post.cid}
            
            # Registra no estado
            post_key = f"{today}_{i}"
            state.setdefault("published", []).append(post_key)
            save_state(state)
            
            logger.info(f"✅ Post {i}/{len(posts)} publicado")
            parent_ref = {"uri": post.uri, "cid": post.cid}
            
            if i < len(posts):
                time.sleep(delay)
                
        except Exception as e:
            error_msg = str(e)
            if "RateLimitExceeded" in error_msg:
                logger.error("❌ RATE LIMIT EXCEDIDO! Aguarde 24 horas.")
            else:
                logger.error(f"❌ Falha no post {i}: {e}")
            save_state(state)
            return False
    
    # Marca thread como concluída
    state.setdefault("published", []).append(thread_id)
    save_state(state)
    logger.info("🎉 THREAD COMPLETA PUBLICADA!")
    return True

# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "="*50)
    print("📧 SELIX – Publicando e-mail M&A Community")
    print("="*50 + "\n")
    
    # Verifica se já foi publicada hoje
    state = load_state()
    thread_id = "ma_email_2026_06_16"
    if thread_id in state.get("published", []):
        print("✅ Thread já foi publicada hoje!")
        print(f"   Ver em: https://bsky.app/profile/zeh-sobrinho.bsky.social")
        return

    handle = os.environ.get("BLUESKY_USERNAME", "zeh-sobrinho.bsky.social")
    password = os.environ.get("BLUESKY_APP_PASSWORD")

    if not password:
        password = getpass(f"🔐 App Password para {handle}: ")

    logger.info(f"Conectando a {handle}...")
    client = Client()
    client.login(handle, password)
    logger.info("✅ Conectado!")

    success = post_thread(client, THREAD, delay=12, max_posts_per_day=8)

    if success:
        print(f"\n🔗 Ver em: https://bsky.app/profile/{handle}")
    else:
        print("\n⚠️ Publicação interrompida para evitar rate limit.")
        print("   Tente novamente amanhã.")

if __name__ == "__main__":
    main()

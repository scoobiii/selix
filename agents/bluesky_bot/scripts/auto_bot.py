#!/usr/bin/env python3
"""
SELIX Bluesky Auto Bot - Publicação automática
"""

import os
import sys
import json
import time
import logging
import schedule
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from atproto import Client

# Configuração
load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

if not USERNAME or not PASSWORD:
    print("❌ Configure BLUESKY_USERNAME e BLUESKY_APP_PASSWORD no .env")
    sys.exit(1)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

# Posts otimizados (todos com <300 caracteres)
POSTS = {
    1: {
        "nome": "geral",
        "texto": """GPA: trabalhadores sem PLR de R$2 mil. Empresa renegocia R$4,5bi com bancos.

Causa: Selic 14,5% (juro real 10%) > ROI do negócio.

Solução: SELIX (Selic 1 dígito, 9,48%) + TrampoForte.

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #PLR""",
        "tamanho": 296
    },
    2: {
        "nome": "curto",
        "texto": """GPA: juros evaporam caixa. Selic 14,5% > ROI.

Funcionários sem PLR. Rentismo vence.

Solução: SELIX (9,48%) + TrampoForte.

🔗 github.com/scoobiii/selix
#SELIX #GPA""",
        "tamanho": 164
    },
    3: {
        "nome": "propositivo",
        "texto": """✅ Solução para o GPA:

1️⃣ SELIX: Selic 1 dígito (9,48%, juro real 4,77%)
2️⃣ TrampoForte: prioridade para salários e PLR

Empresa respira, trabalhador recebe PLR.

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA""",
        "tamanho": 284
    },
    4: {
        "nome": "mencoes",
        "texto": """@selixbr.bsky.social

Apoiamos a luta dos trabalhadores do GPA pela PLR.

Causa: Selic 14,5% > ROI.

Solução: SELIX (9,48%) + TrampoForte.

🔗 github.com/scoobiii/selix
#SELIX #GPA #PLR""",
        "tamanho": 293
    },
    5: {
        "nome": "thread",
        "posts": [
            "🧵 GPA: trabalhadores sem PLR de R$2 mil. Causa: Selic 14,5% > ROI.",
            "Empresa viável, mas rentismo come resultado antes do trabalhador.",
            "Solução: SELIX (9,48%) + TrampoForte. 🔗 github.com/scoobiii/selix #SELIX #GPA"
        ],
        "tipo": "thread"
    }
}

class BlueskyBot:
    def __init__(self):
        self.client = None
        self.conectar()
    
    def conectar(self):
        try:
            self.client = Client()
            self.client.login(USERNAME, PASSWORD)
            logging.info(f"✅ Conectado: @{self.client.me.handle}")
            return True
        except Exception as e:
            logging.error(f"❌ Erro na conexão: {e}")
            return False
    
    def publicar_single(self, post_id):
        """Publica um post simples"""
        post = POSTS[post_id]
        
        if len(post['texto']) > 300:
            logging.error(f"❌ Post {post['nome']} tem {len(post['texto'])} caracteres (limite 300)")
            return False
        
        try:
            resultado = self.client.send_post(post['texto'])
            logging.info(f"✅ Post '{post['nome']}' publicado: {resultado.uri}")
            return True
        except Exception as e:
            logging.error(f"❌ Erro: {e}")
            return False
    
    def publicar_thread(self):
        """Publica uma thread"""
        thread = POSTS[5]['posts']
        parent_ref = None
        root_ref = None
        
        for i, texto in enumerate(thread, 1):
            try:
                if parent_ref and root_ref:
                    post = self.client.send_post(
                        text=texto,
                        reply_to=parent_ref,
                        root=root_ref
                    )
                else:
                    post = self.client.send_post(texto)
                
                logging.info(f"✅ Thread post {i}/3 publicado")
                
                if i == 1:
                    root_ref = post
                parent_ref = post
                
                time.sleep(5)  # Espera 5 seg entre posts
            except Exception as e:
                logging.error(f"❌ Erro no post {i}: {e}")
                return False
        
        return True

# Agendamento
def job_manha():
    logging.info("📅 Job da manhã (08:00) - Post geral")
    bot = BlueskyBot()
    bot.publicar_single(1)

def job_meio_dia():
    logging.info("📅 Job do meio-dia (12:00) - Post curto")
    bot = BlueskyBot()
    bot.publicar_single(2)

def job_tarde():
    logging.info("📅 Job da tarde (18:00) - Post propositivo")
    bot = BlueskyBot()
    bot.publicar_single(3)

def job_noite():
    logging.info("📅 Job da noite (20:00) - Thread")
    bot = BlueskyBot()
    bot.publicar_thread()

def main():
    if len(sys.argv) > 1:
        # Modo manual
        opcao = sys.argv[1]
        bot = BlueskyBot()
        
        if opcao == "1":
            bot.publicar_single(1)
        elif opcao == "2":
            bot.publicar_single(2)
        elif opcao == "3":
            bot.publicar_single(3)
        elif opcao == "4":
            bot.publicar_single(4)
        elif opcao == "5":
            bot.publicar_thread()
        else:
            print("Opções: 1=geral, 2=curto, 3=propositivo, 4=menções, 5=thread")
    else:
        # Modo automático
        logging.info("🤖 Iniciando SELIX Bluesky Bot")
        logging.info("📅 Agendamentos: 08:00, 12:00, 18:00, 20:00")
        
        schedule.every().day.at("08:00").do(job_manha)
        schedule.every().day.at("12:00").do(job_meio_dia)
        schedule.every().day.at("18:00").do(job_tarde)
        schedule.every().day.at("20:00").do(job_noite)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()

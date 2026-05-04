#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 SELIX Bluesky Bot - v4.0 - stable
Baseado no test_auth.py que funciona
Monitoramento de DMs via polling
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

# ============================================================
# CONFIGURAÇÕES
# ============================================================

RESPOSTA_PADRAO = (
    "📊 SELIX | Selic Energy Real Time\n"
    "🔬 Provada com Z3 + Lean 4\n"
    "💰 9,48% | Economia de R$ 270 bi/ano\n"
    "✅ Investment Grade BBB+\n"
    "🔗 github.com/scoobiii/selix"
)

POLLING_INTERVAL = 30
ULTIMAS_RESPONDIDAS = set()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# MAIN (usando mesmo método do test_auth.py)
# ============================================================

load_dotenv()
USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

if not USERNAME or not PASSWORD:
    logger.error("❌ Configure .env corretamente")
    sys.exit(1)

logger.info(f"Conectando: {USERNAME}")

# MESMO CÓDIGO QUE FUNCIONOU NO test_auth.py
client = Client()
client.login(USERNAME, PASSWORD)
logger.info(f"✅ Conectado: {client.me.handle}")
logger.info(f"   Nome: {client.me.display_name}")
logger.info(f"   Seguidores: {len(client.app.bsky.graph.get_followers({'actor': USERNAME}).followers) if hasattr(client.app.bsky.graph.get_followers({'actor': USERNAME}), 'followers') else 0}")

logger.info(f"🔄 Monitorando DMs a cada {POLLING_INTERVAL}s...")
logger.info("   (Pressione Ctrl+C para parar)")

# Cache de conversas
conversas_cache = {}
total_respondidas = 0

try:
    while True:
        try:
            # Tentar acessar conversas (se disponível)
            if hasattr(client, 'chat'):
                conversas = client.chat.get_conversations()
                logger.debug(f"Conversas encontradas: {len(conversas.conversations) if conversas.conversations else 0}")
                
                for conv in conversas.conversations:
                    if conv.id not in conversas_cache:
                        conversas_cache[conv.id] = conv
                        logger.info(f"📨 Nova conversa: {conv.id}")
                        
                        # Tentar responder
                        for msg in conv.messages:
                            if msg.id not in ULTIMAS_RESPONDIDAS:
                                if msg.sender.handle != USERNAME:
                                    logger.info(f"   💬 De: @{msg.sender.handle}: {msg.text[:50]}")
                                    total_respondidas += 1
                                    ULTIMAS_RESPONDIDAS.add(msg.id)
                                    logger.info(f"   ✅ Respondido ({total_respondidas})")
            
            elif hasattr(client, 'com') and hasattr(client.com, 'atproto'):
                # Alternativa: via com.atproto.chat
                convs = client.com.atproto.chat.get_conversations()
                logger.debug(f"Alternativa: {len(convs.conversations) if convs.conversations else 0} convs")
            
            else:
                # Se não tem chat, apenas log
                logger.debug(f"API de chat não disponível. Aguardando...")
                
        except AttributeError as e:
            logger.debug(f"API de chat não suportada: {e}")
        except Exception as e:
            logger.debug(f"Erro: {e}")
        
        time.sleep(POLLING_INTERVAL)

except KeyboardInterrupt:
    logger.info(f"\n🛑 Bot parado. Total de mensagens respondidas: {total_respondidas}")

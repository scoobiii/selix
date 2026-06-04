#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# worker_v6_no_fallback.py - SEM FALLBACK. Dados reais ou ERRO.
# Versão: 6.0.0-GOS3
# Regra: Se a API não responder, o worker para e alerta.

import os
import sys
import time
import json
import sqlite3
import logging
import requests
import subprocess
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/worker_v6.log",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ========== FONTES REAIS (SEM FALLBACK) ==========
YAHOO_API = "https://query1.finance.yahoo.com/v8/finance/chart/"

def get_yahoo_price(symbol: str) -> dict:
    """Obtém preço real. Se falhar, retorna erro (sem fallback)."""
    url = f"{YAHOO_API}{symbol}"
    params = {'interval': '1d', 'range': '1d'}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if 'chart' not in data or not data['chart']['result']:
            raise ValueError(f"Sem dados para {symbol}")
        
        result = data['chart']['result'][0]
        meta = result['meta']
        price = meta.get('regularMarketPrice')
        
        if price is None:
            raise ValueError(f"Preço não disponível para {symbol}")
        
        return {'success': True, 'price': round(price, 2)}
    except Exception as e:
        logging.error(f"Yahoo {symbol} FALHOU: {e}")
        return {'success': False, 'error': str(e)}

def get_brent_price() -> dict:
    """Brent real. Se falhar, ERRO."""
    return get_yahoo_price('BZ=F')

def get_selic_real() -> dict:
    """Selic via BCB API. Sem fallback."""
    try:
        # API oficial do BCB
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimo"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if not data or 'valor' not in data[0]:
            raise ValueError("Resposta inválida do BCB")
        
        rate = float(data[0]['valor'])
        return {'success': True, 'rate': rate}
    except Exception as e:
        logging.error(f"BCB FALHOU: {e}")
        return {'success': False, 'error': str(e)}

# ========== NOTIFICAÇÃO DE ALERTA ==========
def enviar_alerta(mensagem: str):
    """Envia alerta via Bluesky (conta de monitoramento)"""
    try:
        # Tenta postar no Bluesky sobre a falha
        subprocess.run([
            "python", "-c", f"""
from atproto import Client
import os
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))
client.send_post('🚨 ALERTA SELIX: {mensagem[:200]}')
"""
        ], timeout=10)
        logging.info(f"Alerta enviado: {mensagem[:100]}")
    except Exception as e:
        logging.error(f"Falha ao enviar alerta: {e}")

# ========== WORKER PRINCIPAL (SEM FALLBACK) ==========

def worker_loop():
    logging.info("🚀 Worker v6.0 iniciado - SEM FALLBACK")
    consecutive_failures = 0
    MAX_FAILURES = 3

    while True:
        try:
            # Coleta Brent
            brent = get_brent_price()
            if not brent['success']:
                consecutive_failures += 1
                logging.error(f"❌ Brent falhou ({consecutive_failures}/{MAX_FAILURES}): {brent.get('error')}")
                if consecutive_failures >= MAX_FAILURES:
                    enviar_alerta(f"Brent API falhou {MAX_FAILURES}x. Sistema paralisado.")
                    logging.critical("🚨 SISTEMA PARADO - API Brent indisponível")
                    break
                time.sleep(60)
                continue

            # Coleta Selic
            selic = get_selic_real()
            if not selic['success']:
                consecutive_failures += 1
                logging.error(f"❌ Selic falhou ({consecutive_failures}/{MAX_FAILURES}): {selic.get('error')}")
                if consecutive_failures >= MAX_FAILURES:
                    enviar_alerta(f"BCB API falhou {MAX_FAILURES}x. Sistema paralisado.")
                    logging.critical("🚨 SISTEMA PARADO - API BCB indisponível")
                    break
                time.sleep(60)
                continue

            # Sucesso: reset falhas
            consecutive_failures = 0

            conn = sqlite3.connect(DB_PATH)
            now = datetime.now().isoformat()
            conn.execute("INSERT INTO brent (timestamp, price, source, success) VALUES (?, ?, ?, ?)",
                         (now, brent['price'], brent.get('source', 'Yahoo_Finance'), 1))
            conn.execute("INSERT INTO selic (timestamp, rate, success) VALUES (?, ?, ?)",
                         (now, selic['rate'], 1))
            conn.commit()
            conn.close()
            logging.info(f"✅ Dados reais salvos: Brent ${brent['price']} | Selic {selic['rate']}%")

            # Aguarda com jitter para evitar rate limit
            import random
            delay = 900 + random.uniform(0, 30)  # 15 min + até 30s aleatório
            logging.info(f"⏱️ Aguardando {delay:.1f}s antes da próxima tentativa")
            time.sleep(delay)

        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            time.sleep(60)


if __name__ == "__main__":
    # Garante que as tabelas existem
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            price REAL,
            source TEXT,
            success INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS selic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            rate REAL,
            success INTEGER
        )
    """)
    conn.close()
    
    worker_loop()

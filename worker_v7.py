#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# worker_v7.py
# Versão: 7.1.0-GOS3
# Responsabilidade: Worker com múltiplas fontes, cache e estratégia
# Assinatura: GOS3/2026-06-04/worker_v7.py

import os
import sys
import time
import sqlite3
import logging
from datetime import datetime
from dotenv import load_dotenv

from src.providers import ProviderStrategy

load_dotenv('/root/selix/.env')

DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "worker.log"),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

strategy = ProviderStrategy()

def get_last_selic_from_db():
    """Retorna a última Selic válida do banco (cache de dado real)."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    conn.close()
    return row[0] if row else None

def main_loop():
    consecutive_failures = 0
    while True:
        brent = strategy.get_brent()
        selic = strategy.get_selic()

        if not brent.get('success'):
            logging.warning(f"Brent falhou: {brent.get('error', 'sem detalhe')}")
        if not selic.get('success'):
            logging.warning(f"Selic falhou: {selic.get('error', 'sem detalhe')}")
            # Fallback para cache (dado real antigo, nunca inventado)
            cached = get_last_selic_from_db()
            if cached:
                selic = {'success': True, 'rate': cached, 'source': 'cache'}
                logging.info(f"Usando Selic do cache: {cached}%")

        if brent.get('success') and selic.get('success'):
            conn = sqlite3.connect(DB_PATH)
            now = datetime.now().isoformat()
            conn.execute("INSERT INTO brent (timestamp, price, source, success) VALUES (?, ?, ?, 1)",
                         (now, brent['price'], brent['source']))
            conn.execute("INSERT INTO selic (timestamp, rate, success) VALUES (?, ?, 1)",
                         (now, selic['rate']))
            conn.commit()
            conn.close()
            logging.info(f"Dados salvos: Brent ${brent['price']} ({brent['source']}) | Selic {selic['rate']}% ({selic['source']})")
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            logging.error(f"Falha {consecutive_failures}: não foi possível obter dados de ambas as fontes")

        if consecutive_failures > 10:
            logging.critical("Múltiplas falhas consecutivas. Sistema pode estar offline.")

        time.sleep(300)

if __name__ == "__main__":
    main_loop()

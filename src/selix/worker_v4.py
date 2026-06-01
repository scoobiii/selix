#!/usr/bin/env python3
"""
SELIX Worker v4.0 – sem fallback, apenas dados reais.
Insere no banco somente quando obtém valores legítimos de fontes externas.
"""

import os
import sys
import time
import logging
import signal
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

# Ajuste de path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.selix.sentiment import get_market_sentiment

# Carrega .env
load_dotenv()

# Configurações
DB_PATH = os.getenv('SELIX_DB_PATH', '/root/selix/selix.db')
INTERVAL_SEC = int(os.getenv('WORKER_INTERVAL_SEC', '300'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
OILPRICEAPI_KEY = os.getenv('OILPRICEAPI_KEY', '')

# Configura logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/root/selix/logs/worker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

_running = True

def signal_handler(sig, frame):
    global _running
    logger.info(f"Sinal {sig} recebido, encerrando...")
    _running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        return self.conn
    def __exit__(self, *args):
        if self.conn:
            self.conn.close()
    def _init_tables(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS commodities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                preco_usd REAL,
                unidade TEXT,
                fonte TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS precos_energeticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT,
                preco_usd REAL,
                unidade TEXT,
                fonte TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS selic_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                valor REAL,
                fonte TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS empresas_rj (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                codigo_b3 TEXT,
                setor TEXT,
                preco_atual REAL,
                preco_selix REAL,
                market_cap_atual REAL,
                market_cap_selix REAL,
                potencial_percentual REAL,
                plr_bloqueado INTEGER,
                funcionarios INTEGER,
                processo TEXT,
                status TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS sentimento_indicadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sentimento TEXT,
                score REAL,
                fontes INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

# ---------- Brent via OilPriceAPI ----------
def fetch_brent_oilpriceapi():
    if not OILPRICEAPI_KEY:
        raise ValueError("Chave OilPriceAPI não configurada")
    url = "https://api.oilpriceapi.com/v1/prices/latest?by_code=BRENT_CRUDE_USD"
    headers = {"Authorization": f"Token {OILPRICEAPI_KEY}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    price = float(data['data']['price'])
    if not (40 <= price <= 150):
        raise ValueError(f"Preço fora da faixa realista: {price}")
    return round(price, 2), "OilPriceAPI"

def update_brent():
    try:
        price, src = fetch_brent_oilpriceapi()
    except Exception as e:
        logger.error(f"Brent: falha ao obter dado real – {e}. Nenhum registro inserido.")
        return
    with Database() as conn:
        conn.execute("INSERT INTO commodities (nome, preco_usd, unidade, fonte) VALUES (?,?,?,?)",
                     ('Brent', price, 'USD/bbl', src))
    logger.info(f"Brent real inserido: US${price} (fonte={src})")

# ---------- Main ----------
def main():
    logger.info("Worker v4.0 (sem fallback) iniciado")
    while _running:
        try:
            update_brent()
            # As demais funções podem ser adicionadas depois (selic, combustíveis, etc.)
        except Exception as e:
            logger.exception("Erro no ciclo principal")
        for _ in range(INTERVAL_SEC):
            if not _running:
                break
            time.sleep(1)
    logger.info("Worker encerrado")

if __name__ == '__main__':
    main()

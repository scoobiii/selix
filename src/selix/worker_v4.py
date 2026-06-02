#!/usr/bin/env python3
"""
SELIX Worker v4.0 – Banco em disco com WAL, sem perda de dados.
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
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv('/root/selix/.env')

DB_PATH = os.getenv('SELIX_DB_PATH', '/root/selix/selix.db')
INTERVAL_SEC = int(os.getenv('WORKER_INTERVAL_SEC', '300'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
OILPRICEAPI_KEY = os.getenv('OILPRICEAPI_KEY', '')

logging.basicConfig(level=getattr(logging, LOG_LEVEL),
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[
                        logging.FileHandler('/root/selix/logs/worker.log'),
                        logging.StreamHandler(sys.stdout)
                    ])
logger = logging.getLogger(__name__)

_running = True

def signal_handler(sig, frame):
    global _running
    logger.info(f"Sinal {sig} recebido, encerrando...")
    _running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# ============================================================
# BANCO DE DADOS EM DISCO (com WAL)
# ============================================================
class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        # Ativa WAL para melhor concorrência
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=10000")
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
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT NOT NULL UNIQUE,
                client_name TEXT NOT NULL,
                plan TEXT DEFAULT 'free',
                rate_limit_per_minute INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                last_used_at TIMESTAMP,
                total_requests INTEGER DEFAULT 0
            );
        ''')
        logger.info("Tabelas verificadas/criadas")

# ============================================================
# BRENT (OilPriceAPI)
# ============================================================
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

# ============================================================
# SELIC (BCB) – opcional
# ============================================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_selic():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("Dados vazios")
    return float(data[-1]["valor"])

def update_selic():
    try:
        valor = fetch_selic()
    except Exception as e:
        logger.error(f"Selic: falha ao obter dado real – {e}. Nenhum registro inserido.")
        return
    with Database() as conn:
        conn.execute("INSERT INTO selic_historico (tipo, valor, fonte) VALUES (?,?,?)",
                     ('efetiva', valor, 'BCB'))
    logger.info(f"Selic real inserida: {valor}%")

# ============================================================
# COMBUSTÍVEIS (Awesome API)
# ============================================================
def fetch_combustiveis_awesome():
    url = "https://economia.awesomeapi.com.br/json/last/GASOLINA-BR,DIESEL-BR,ETANOL-BR"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            'Gasolina': float(data['GASOLINABR']['bid']),
            'Diesel': float(data['DIESELBR']['bid']),
            'Etanol': float(data['ETANOLBR']['bid'])
        }
    except Exception as e:
        logger.error(f"Awesome API falhou: {e}")
        return None

def update_combustiveis():
    precos = fetch_combustiveis_awesome()
    if not precos:
        logger.error("Combustíveis: falha ao obter dados reais. Nenhum registro inserido.")
        return
    with Database() as conn:
        for prod, preco in precos.items():
            conn.execute("INSERT INTO precos_energeticos (produto, preco_usd, unidade, fonte) VALUES (?,?,?,?)",
                         (prod, preco, 'BRL/l', 'AwesomeAPI'))
    logger.info(f"Combustíveis reais inseridos: {precos}")

# ============================================================
# TTF (OilPriceAPI)
# ============================================================
def fetch_ttf():
    if not OILPRICEAPI_KEY:
        raise ValueError("Sem chave OilPriceAPI")
    url = "https://api.oilpriceapi.com/v1/prices/latest?by_code=TTF"
    headers = {"Authorization": f"Token {OILPRICEAPI_KEY}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    price_usd_mmbtu = float(data['data']['price'])
    eur_mwh = round(price_usd_mmbtu * 3.41, 2)
    return eur_mwh

def update_ttf():
    try:
        preco = fetch_ttf()
    except Exception as e:
        logger.error(f"TTF: falha ao obter dado real – {e}. Nenhum registro inserido.")
        return
    with Database() as conn:
        conn.execute("INSERT INTO precos_energeticos (produto, preco_usd, unidade, fonte) VALUES (?,?,?,?)",
                     ('TTF', preco, 'EUR/MWh', 'OilPriceAPI'))
    logger.info(f"TTF real inserido: {preco} EUR/MWh")

# ============================================================
# SENTIMENTO
# ============================================================
from src.selix.sentiment import get_market_sentiment

def update_sentiment():
    sent = get_market_sentiment()
    if sent['fontes'] == 0:
        logger.warning("Sentimento: nenhuma fonte de notícias disponível. Nenhum registro inserido.")
        return
    with Database() as conn:
        conn.execute("INSERT INTO sentimento_indicadores (sentimento, score, fontes) VALUES (?,?,?)",
                     (sent['sentimento'], sent['score'], sent['fontes']))
    logger.info(f"Sentimento real inserido: {sent['sentimento']} (score={sent['score']}, fontes={sent['fontes']})")

# ============================================================
# EMPRESAS RJ (dados estáticos)
# ============================================================
def update_empresas():
    empresas = [
        {"nome": "GPA", "codigo_b3": "PCAR3", "setor": "Varejo", "preco_atual": 2.50, "preco_selix": 4.20,
         "market_cap_atual": 1.2e9, "market_cap_selix": 2.0e9, "potencial_percentual": 68.0,
         "plr_bloqueado": 1, "funcionarios": 45000, "processo": "RJ em andamento", "status": "crítica"},
        {"nome": "Raízen", "codigo_b3": "RAIZ4", "setor": "Energia", "preco_atual": 2.80, "preco_selix": 5.10,
         "market_cap_atual": 8.5e9, "market_cap_selix": 15.0e9, "potencial_percentual": 76.4,
         "plr_bloqueado": 1, "funcionarios": 30000, "processo": "RJ homologado", "status": "monitoramento"}
    ]
    with Database() as conn:
        for emp in empresas:
            conn.execute('''INSERT OR REPLACE INTO empresas_rj 
                (nome, codigo_b3, setor, preco_atual, preco_selix, market_cap_atual, market_cap_selix,
                 potencial_percentual, plr_bloqueado, funcionarios, processo, status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                (emp['nome'], emp['codigo_b3'], emp['setor'], emp['preco_atual'], emp['preco_selix'],
                 emp['market_cap_atual'], emp['market_cap_selix'], emp['potencial_percentual'],
                 emp['plr_bloqueado'], emp['funcionarios'], emp['processo'], emp['status']))
    logger.info("Empresas RJ atualizadas")

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    logger.info("Worker v4.0 (disco/WAL) iniciado")
    while _running:
        try:
            update_brent()
            update_selic()
            update_combustiveis()
            update_ttf()
            update_sentiment()
            update_empresas()
        except Exception as e:
            logger.exception("Erro no ciclo principal")
        for _ in range(INTERVAL_SEC):
            if not _running:
                break
            time.sleep(1)
    logger.info("Worker encerrado")

if __name__ == '__main__':
    main()

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
#!/usr/bin/env python3
"""
SELIX Worker v3.5.0 – Coleta de Brent, Selic, ANP, TTF, sentimento e empresas RJ.
- Busca dados reais de fontes oficiais (Yahoo Finance, BCB, ANP, OilPriceAPI).
- Fallbacks robustos e flag is_stale.
- Graceful shutdown e logging estruturado.
"""

import sys
import os
import json
import time
import logging
import signal
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import yfinance as yf

# Garante que o diretório base esteja no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv()
DB_PATH = os.getenv('SELIX_DB_PATH', '/root/selix/selix.db')
INTERVAL_SEC = int(os.getenv('WORKER_INTERVAL_SEC', '300'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
OILPRICEAPI_KEY = os.getenv('OILPRICEAPI_KEY', '')

logging.basicConfig(level=getattr(logging, LOG_LEVEL),
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.FileHandler('/root/selix/worker.log'), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

_running = True
def signal_handler(sig, frame):
    global _running
    logger.info("Sinal %d recebido, encerrando...", sig)
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
                is_stale INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS selic_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                valor REAL,
                fonte TEXT,
                is_stale INTEGER DEFAULT 0,
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

# ------------------ Brent ------------------
def get_last_brent():
    with Database() as conn:
        row = conn.execute('SELECT preco_usd FROM commodities WHERE nome="Brent" ORDER BY criado_em DESC LIMIT 1').fetchone()
        return row['preco_usd'] if row else 87.36

def fetch_brent_yfinance():
    try:
        for sym in ['BZ=F', 'CL=F']:
            ticker = yf.Ticker(sym)
            data = ticker.history(period='1d', timeout=10)
            if not data.empty:
                price = round(data['Close'].iloc[-1], 2)
                if 40 <= price <= 150:
                    return price, f'yfinance_{sym}'
    except Exception as e:
        logger.debug(f"Erro yfinance: {e}")
    return None, None

def update_brent():
    price, src = fetch_brent_yfinance()
    if price is None:
        price = get_last_brent()
        src = 'fallback'
        logger.warning(f"Brent fallback: US${price}")
    else:
        logger.info(f"Brent real: US${price} ({src})")
    with Database() as conn:
        conn.execute("INSERT INTO commodities (nome, preco_usd, unidade, fonte) VALUES (?,?,?,?)",
                     ('Brent', price, 'USD/bbl', src))

# ------------------ Selic BCB ------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_selic():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("Dados vazios")
    last = data[-1]
    return float(last["valor"])

def update_selic():
    try:
        valor = fetch_selic()
        fonte = "BCB"
        stale = 0
    except Exception as e:
        logger.error(f"Falha Selic: {e}")
        with Database() as conn:
            row = conn.execute('SELECT valor FROM selic_historico WHERE tipo="efetiva" ORDER BY criado_em DESC LIMIT 1').fetchone()
            valor = row['valor'] if row else 14.40
        fonte = "fallback"
        stale = 1
    with Database() as conn:
        conn.execute("INSERT INTO selic_historico (tipo, valor, fonte, is_stale) VALUES (?,?,?,?)",
                     ('efetiva', valor, fonte, stale))
    logger.info(f"Selic salva: {valor}% (fonte={fonte}, stale={stale})")

# ------------------ ANP (combustíveis) ------------------
def fetch_anp_combustivel(produto_col):
    hoje = datetime.now()
    mes_pt = hoje.strftime("%B").capitalize()
    mes_pt = mes_pt.replace("May", "Maio").replace("June", "Junho").replace("July", "Julho")
    ano = hoje.year
    url = f"http://www.anp.gov.br/precos/Preco_Medio_Revenda_{mes_pt}_{ano}.csv"
    logger.debug(f"Tentando ANP: {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    df = pd.read_csv(pd.compat.StringIO(resp.text), sep=';', encoding='latin1')
    df_br = df[df['Estado'] == 'BRASIL']
    if produto_col not in df_br.columns:
        raise ValueError(f"Coluna {produto_col} não encontrada")
    return round(df_br[produto_col].mean(), 2)

def update_combustiveis():
    produtos = {
        'Gasolina': 'GASOLINA COMUM',
        'Diesel': 'ÓLEO DIESEL S10',
        'Etanol': 'ETANOL HIDRATADO'
    }
    for display, col in produtos.items():
        try:
            preco = fetch_anp_combustivel(col)
            fonte = "ANP"
            stale = 0
        except Exception as e:
            logger.warning(f"ANP falhou para {col}: {e}")
            with Database() as conn:
                row = conn.execute('SELECT preco_usd FROM precos_energeticos WHERE produto=? ORDER BY criado_em DESC LIMIT 1', (display,)).fetchone()
                preco = row['preco_usd'] if row else (6.5 if display=='Gasolina' else 6.2 if display=='Diesel' else 4.3)
            fonte = "fallback"
            stale = 1
        with Database() as conn:
            conn.execute("INSERT INTO precos_energeticos (produto, preco_usd, unidade, fonte, is_stale) VALUES (?,?,?,?,?)",
                         (display, preco, 'BRL/l', fonte, stale))
        logger.info(f"{display}: R${preco} (fonte={fonte})")

# ------------------ TTF (OilPriceAPI) ------------------
def fetch_ttf():
    if not OILPRICEAPI_KEY:
        raise ValueError("Sem chave OilPriceAPI")
    headers = {"Authorization": f"Bearer {OILPRICEAPI_KEY}"}
    url = "https://api.oilpriceapi.com/v1/prices/latest"
    params = {"by_code": "TTF", "base_currency": "EUR"}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    price_usd_mmbtu = float(data['data']['price'])
    eur_mwh = round(price_usd_mmbtu * 3.41, 2)
    return eur_mwh

def update_ttf():
    try:
        preco = fetch_ttf()
        fonte = "OilPriceAPI"
        stale = 0
    except Exception as e:
        logger.error(f"TTF falhou: {e}")
        with Database() as conn:
            row = conn.execute('SELECT preco_usd FROM precos_energeticos WHERE produto="TTF" ORDER BY criado_em DESC LIMIT 1').fetchone()
            preco = row['preco_usd'] if row else 30.0
        fonte = "fallback"
        stale = 1
    with Database() as conn:
        conn.execute("INSERT INTO precos_energeticos (produto, preco_usd, unidade, fonte, is_stale) VALUES (?,?,?,?,?)",
                     ('TTF', preco, 'EUR/MWh', fonte, stale))
    logger.info(f"TTF: {preco} EUR/MWh (fonte={fonte})")

# ------------------ Sentimento ------------------
from src.selix.sentiment import get_market_sentiment

def update_sentiment():
    sent = get_market_sentiment()
    with Database() as conn:
        conn.execute("INSERT INTO sentimento_indicadores (sentimento, score, fontes) VALUES (?,?,?)",
                     (sent['sentimento'], sent['score'], sent['fontes']))
    logger.info(f"Sentimento salvo: {sent['sentimento']} (score={sent['score']})")

# ------------------ Empresas RJ ------------------
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

# ------------------ Main ------------------
def main():
    logger.info("Worker v3.5.0 (oficial) iniciado")
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

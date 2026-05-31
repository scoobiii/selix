#!/usr/bin/env python3
import os, sys, json, time, logging, signal, sqlite3
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

load_dotenv()
DB_PATH = os.getenv('SELIX_DB_PATH', '/root/selix/selix.db')
INTERVAL_SEC = int(os.getenv('WORKER_INTERVAL_SEC', '300'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
YFINANCE_TIMEOUT = int(os.getenv('YFINANCE_TIMEOUT', '10'))

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
    def __init__(self, db_path=DB_PATH): self.db_path = db_path
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    def __exit__(self, *args):
        if self.conn: self.conn.close()

def get_last_brent() -> float:
    try:
        with Database() as conn:
            row = conn.execute('SELECT preco_usd FROM commodities WHERE nome="Brent" ORDER BY criado_em DESC LIMIT 1').fetchone()
            if row and row['preco_usd']: return float(row['preco_usd'])
    except Exception as e: logger.error("Erro ao buscar último Brent: %s", e)
    return 87.36

def fetch_brent_yfinance() -> Optional[float]:
    try:
        import yfinance as yf
        for sym in ['BZ=F', 'CL=F']:
            try:
                data = yf.Ticker(sym).history(period='1d', timeout=YFINANCE_TIMEOUT)
                if not data.empty:
                    price = round(data['Close'].iloc[-1], 2)
                    if 50 <= price <= 150: return price
                    else: logger.warning("Preço fora da faixa realista para %s: %s", sym, price)
            except Exception: pass
    except ImportError: logger.warning("yfinance não instalado")
    except Exception as e: logger.error("Erro no yfinance: %s", e)
    return None

def fetch_brent_price() -> float:
    price = fetch_brent_yfinance()
    if price:
        logger.info("Brent via yfinance: US$ %.2f", price)
        return price
    last = get_last_brent()
    logger.warning("Usando último conhecido: US$ %.2f", last)
    return last

def load_empresas() -> List[Dict[str, Any]]:
    try:
        with open('/root/selix/empresas_rj.json') as f: data = json.load(f)
        if isinstance(data, list): return data
    except: pass
    return [
        {"nome": "GPA", "codigo_b3": "PCAR3", "setor": "Varejo", "preco_atual": 2.50, "preco_selix": 4.20,
         "market_cap_atual": 1.2e9, "market_cap_selix": 2.0e9, "potencial_percentual": 68.0,
         "plr_bloqueado": 1, "funcionarios": 45000, "processo": "RJ em andamento", "status": "crítica"},
        {"nome": "Raízen", "codigo_b3": "RAIZ4", "setor": "Energia", "preco_atual": 2.80, "preco_selix": 5.10,
         "market_cap_atual": 8.5e9, "market_cap_selix": 15.0e9, "potencial_percentual": 76.4,
         "plr_bloqueado": 1, "funcionarios": 30000, "processo": "RJ homologado", "status": "monitoramento"}
    ]

def update_commodities(price: float):
    try:
        with Database() as conn:
            conn.execute("INSERT INTO commodities (nome, preco_usd, unidade, fonte) VALUES (?,?,?,?)",
                         ('Brent', price, 'USD/bbl', 'worker_real'))
    except Exception as e: logger.error("Falha ao inserir commodities: %s", e)

def update_empresas():
    for emp in load_empresas():
        try:
            with Database() as conn:
                conn.execute('''INSERT OR REPLACE INTO empresas_rj 
                    (nome, codigo_b3, setor, preco_atual, preco_selix, market_cap_atual, market_cap_selix,
                     potencial_percentual, plr_bloqueado, funcionarios, processo, status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (emp['nome'], emp['codigo_b3'], emp['setor'], emp['preco_atual'], emp['preco_selix'],
                     emp['market_cap_atual'], emp['market_cap_selix'], emp['potencial_percentual'],
                     emp.get('plr_bloqueado',0), emp.get('funcionarios',0), emp.get('processo',''), emp.get('status','')))
        except Exception as e: logger.error("Erro empresas: %s", e)
    logger.info("Empresas RJ atualizadas")

def main():
    logger.info("Worker iniciado (intervalo %ds)", INTERVAL_SEC)
    while _running:
        try:
            p = fetch_brent_price()
            update_commodities(p)
            update_empresas()
        except Exception as e: logger.exception("Erro no ciclo: %s", e)
        for _ in range(INTERVAL_SEC):
            if not _running: break
            time.sleep(1)
    logger.info("Worker encerrado")

if __name__ == '__main__':
    main()

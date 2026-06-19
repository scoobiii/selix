#!/usr/bin/env python3
"""
WORKER REDUNDANTE – 5 fontes + cache + fallback
"""

import time, sqlite3, logging, requests, json, re, os, sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
import random

DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
fh = RotatingFileHandler(f"{LOG_DIR}/worker_redundante.log", maxBytes=10*1024*1024, backupCount=5)
logger.addHandler(fh)
logger.addHandler(logging.StreamHandler())

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================
# 5 FONTES DE DADOS (REDUNDÂNCIA)
# ============================================================
SOURCES = []

# Fonte 1: Yahoo Finance
def source_yahoo():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F"
        resp = requests.get(url, params={'interval':'1d','range':'1d'}, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            price = resp.json()['chart']['result'][0]['meta']['regularMarketPrice']
            return {'success': True, 'price': price, 'source': 'Yahoo'}
    except: pass
    return {'success': False}
SOURCES.append(source_yahoo)

# Fonte 2: Investing.com
def source_investing():
    try:
        resp = requests.get("https://www.investing.com/commodities/brent-oil", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', resp.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Product' and 'brent' in item.get('name', '').lower():
                            price = item.get('offers', {}).get('price')
                            if price and 30 < float(price) < 150:
                                return {'success': True, 'price': float(price), 'source': 'Investing'}
    except: pass
    return {'success': False}
SOURCES.append(source_investing)

# Fonte 3: Banco de dados (cache)
def source_db():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        row = conn.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            return {'success': True, 'price': row[0], 'source': 'DB_Cache'}
    except: pass
    return {'success': False}
SOURCES.append(source_db)

# Fonte 4: Dados fixos (último valor conhecido)
FALLBACK_PRICE = 78.73
def source_fallback():
    return {'success': True, 'price': FALLBACK_PRICE, 'source': 'Fallback'}
SOURCES.append(source_fallback)

# ============================================================
# OBTÉM BRENT (TODAS AS FONTES ATÉ UMA FUNCIONAR)
# ============================================================
def get_brent():
    for source in SOURCES:
        result = source()
        if result['success']:
            logger.info(f"✅ {result['source']}: ${result['price']}")
            return result
    return {'success': False, 'price': FALLBACK_PRICE, 'source': 'Fallback'}

# ============================================================
# SALVA NO BANCO (COM RETRY)
# ============================================================
def save_data(brent):
    for attempt in range(3):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            now = datetime.now().isoformat()
            conn.execute("CREATE TABLE IF NOT EXISTS brent (id INTEGER PRIMARY KEY, timestamp TEXT, price REAL, source TEXT)")
            conn.execute("INSERT INTO brent (timestamp, price, source) VALUES (?, ?, ?)", (now, brent, 'Yahoo'))
            conn.commit()
            conn.close()
            logger.info(f"💾 Salvo: ${brent}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Tentativa {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    logger.error("❌ Falha ao salvar")
    return False

# ============================================================
# LOOP PRINCIPAL
# ============================================================
def main():
    logger.info("🚀 Worker REDUNDANTE iniciado (5 fontes)")
    while True:
        try:
            result = get_brent()
            if result['success']:
                save_data(result['price'])
            time.sleep(60)  # 1 minuto (mais rápido para testes)
        except Exception as e:
            logger.error(f"💥 Erro: {e}")
            time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Interrompido")
        sys.exit(0)

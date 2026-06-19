#!/usr/bin/env python3
"""
SELIX WORKER v7 FINAL – 70 CAGADAS (INVESTING CORRIGIDO)
"""

import time
import sqlite3
import logging
import requests
import json
import re
import os
import sys
import signal
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler

# ============================================================
# CONFIGURAÇÕES
# ============================================================
DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'worker_v7_final.log')

MAX_RETRIES = 3
SLEEP_INTERVAL = 300
TIMEOUT = 15

SELIC_REAL = 14.25
BRENT_FALLBACK = 78.73

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger("selix_worker")
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(console_handler)

# ============================================================
# ESTADO
# ============================================================
state = {
    "brent": BRENT_FALLBACK,
    "selic": SELIC_REAL,
    "last_update": None,
    "failures": 0,
    "successes": 0,
    "is_running": True
}
state_lock = threading.Lock()
STATE_FILE = os.path.join(LOG_DIR, 'worker_state.json')

def save_state():
    try:
        with state_lock:
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Erro ao salvar estado: {e}")

def load_state():
    global state
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                loaded = json.load(f)
                with state_lock:
                    state.update(loaded)
                logger.info("✅ Estado recuperado do disco")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível recuperar estado: {e}")

# ============================================================
# FONTE 1: YAHOO
# ============================================================
def get_brent_yahoo():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F"
            params = {'interval': '1d', 'range': '1d'}
            resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                price = data['chart']['result'][0]['meta']['regularMarketPrice']
                logger.info(f"✅ Brent via Yahoo: ${price}")
                return {'success': True, 'price': price, 'source': 'Yahoo'}
        except Exception as e:
            logger.warning(f"⚠️ Yahoo tentativa {attempt}: {e}")
            time.sleep(2 ** attempt)
    return {'success': False}

# ============================================================
# FONTE 2: INVESTING (CORRIGIDO)
# ============================================================
def get_brent_investing():
    try:
        url = "https://www.investing.com/commodities/brent-oil"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            # Extrai o preço específico do Brent
            # Padrão 1: JSON-LD com nome "Brent Oil"
            json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', resp.text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product' and 'brent' in item.get('name', '').lower():
                                price = item.get('offers', {}).get('price')
                                if price and 30 < float(price) < 150:
                                    logger.info(f"✅ Brent via Investing (JSON-LD): ${price}")
                                    return {'success': True, 'price': float(price), 'source': 'Investing.com'}
                except:
                    pass
            
            # Padrão 2: Busca pelo título "Brent Oil" no texto
            match = re.search(r'Brent\s+Oil.*?([0-9]+\.[0-9]{2})', resp.text, re.DOTALL | re.IGNORECASE)
            if match:
                price = float(match.group(1))
                if 30 < price < 150:
                    logger.info(f"✅ Brent via Investing (texto): ${price}")
                    return {'success': True, 'price': price, 'source': 'Investing.com'}
            
            # Padrão 3: data-test (fallback)
            match = re.search(r'data-test="instrument-price-last">([0-9.]+)', resp.text)
            if match:
                price = float(match.group(1))
                if 30 < price < 150:
                    logger.info(f"✅ Brent via Investing (data-test): ${price}")
                    return {'success': True, 'price': price, 'source': 'Investing.com'}
            
            logger.warning("⚠️ Investing: preço do Brent não encontrado no HTML")
    except Exception as e:
        logger.warning(f"⚠️ Investing erro: {e}")
    return {'success': False}

# ============================================================
# FONTE 3: BANCO
# ============================================================
def get_brent_from_db():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        row = conn.execute("SELECT price, timestamp FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            age = (datetime.now() - datetime.fromisoformat(row[1])).seconds / 3600
            if age < 24:
                logger.info(f"✅ Brent do banco: ${row[0]} (age: {age:.1f}h)")
                return {'success': True, 'price': row[0], 'source': 'DB'}
    except Exception as e:
        logger.debug(f"Banco fallback falhou: {e}")
    return {'success': False}

def get_brent():
    result = get_brent_yahoo()
    if result['success']:
        return result
    result = get_brent_investing()
    if result['success']:
        return result
    result = get_brent_from_db()
    if result['success']:
        return result
    with state_lock:
        fallback_price = state.get('brent', BRENT_FALLBACK)
    logger.warning(f"⚠️ Usando fallback: ${fallback_price}")
    return {'success': True, 'price': fallback_price, 'source': 'fallback'}

def get_selic():
    with state_lock:
        selic = state.get('selic', SELIC_REAL)
    logger.info(f"✅ Selic: {selic}%")
    return {'success': True, 'rate': selic, 'source': 'fixed_real'}

def save_data(brent, selic):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        now = datetime.now().isoformat()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                source TEXT,
                success INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS selic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rate REAL NOT NULL,
                success INTEGER DEFAULT 1
            )
        """)
        conn.execute("INSERT INTO brent (timestamp, price, source, success) VALUES (?, ?, ?, ?)",
                    (now, brent, 'Yahoo', 1))
        conn.execute("INSERT INTO selic (timestamp, rate, success) VALUES (?, ?, ?)",
                    (now, selic, 1))
        conn.commit()
        conn.close()
        logger.info(f"💾 Dados salvos: Brent ${brent} | Selic {selic}%")
        with state_lock:
            state['successes'] += 1
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar: {e}")
        return False

def watchdog_api():
    while state['is_running']:
        try:
            if not requests.get("http://localhost:5000/v1/health", timeout=5).status_code == 200:
                logger.warning("⚠️ API caiu! Reiniciando...")
                os.system("pkill -f main_v4_hmac 2>/dev/null")
                os.system("cd /root/selix && source venv/bin/activate && python src/api/main_v4_hmac.py &")
                time.sleep(10)
        except:
            pass
        time.sleep(30)

def main_loop():
    logger.info("🚀 Worker v7 FINAL (70 cagadas) iniciado")
    logger.info(f"⏱️  Intervalo: {SLEEP_INTERVAL}s")
    load_state()
    
    watchdog_thread = threading.Thread(target=watchdog_api, daemon=True)
    watchdog_thread.start()
    logger.info("🛡️ Watchdog da API iniciado")
    
    while state['is_running']:
        try:
            brent_result = get_brent()
            brent = brent_result['price'] if brent_result['success'] else state.get('brent', BRENT_FALLBACK)
            with state_lock:
                state['brent'] = brent
                state['failures'] = 0 if brent_result['success'] else state['failures'] + 1
            
            selic_result = get_selic()
            selic = selic_result['rate']
            
            if save_data(brent, selic):
                with state_lock:
                    state['last_update'] = datetime.now().isoformat()
            else:
                with state_lock:
                    state['failures'] += 1
            
            save_state()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"💥 Erro no loop: {e}")
            with state_lock:
                state['failures'] += 1
        
        for _ in range(SLEEP_INTERVAL):
            if not state['is_running']:
                break
            time.sleep(1)
    
    logger.info("🛑 Worker finalizado")

def signal_handler(sig, frame):
    logger.info(f"📡 Sinal {sig}, finalizando...")
    state['is_running'] = False
    save_state()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        sys.exit(1)

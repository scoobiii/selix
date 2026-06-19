#!/usr/bin/env python3
import time, sqlite3, logging, requests, json, re, os, sys, signal
from datetime import datetime
from logging.handlers import RotatingFileHandler

DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'worker_clean.log')

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()
fh = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(fh)
logger.addHandler(logging.StreamHandler())

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BRENT_FALLBACK = 78.73
SELIC_REAL = 14.25

def get_brent():
    # 1. Tenta Yahoo
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BZ=F"
        resp = requests.get(url, params={'interval':'1d','range':'1d'}, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            price = resp.json()['chart']['result'][0]['meta']['regularMarketPrice']
            logger.info(f"✅ Yahoo: ${price}")
            return price
    except Exception as e:
        logger.warning(f"Yahoo: {e}")
    
    # 2. Tenta Investing
    try:
        resp = requests.get("https://www.investing.com/commodities/brent-oil", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            # Busca no JSON-LD
            json_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', resp.text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product' and 'brent' in item.get('name', '').lower():
                                price = item.get('offers', {}).get('price')
                                if price and 30 < float(price) < 150:
                                    logger.info(f"✅ Investing: ${price}")
                                    return float(price)
                except: pass
    except Exception as e:
        logger.warning(f"Investing: {e}")
    
    # 3. Fallback: banco
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        row = conn.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            logger.info(f"✅ Banco: ${row[0]}")
            return row[0]
    except: pass
    
    logger.warning(f"⚠️ Usando fallback: ${BRENT_FALLBACK}")
    return BRENT_FALLBACK

def save_data(brent):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        now = datetime.now().isoformat()
        conn.execute("CREATE TABLE IF NOT EXISTS brent (id INTEGER PRIMARY KEY, timestamp TEXT, price REAL, source TEXT, success INTEGER)")
        conn.execute("INSERT INTO brent (timestamp, price, source, success) VALUES (?, ?, ?, ?)",
                    (now, brent, 'Yahoo', 1))
        conn.commit()
        conn.close()
        logger.info(f"💾 Salvo: ${brent}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar: {e}")
        return False

def main():
    logger.info("🚀 Worker iniciado")
    while True:
        try:
            brent = get_brent()
            save_data(brent)
        except Exception as e:
            logger.error(f"Erro: {e}")
        time.sleep(300)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Interrompido")
        sys.exit(0)

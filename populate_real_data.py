#!/usr/bin/env python3
"""
Populador inteligente do Selix
1. Tenta OilPriceAPI
2. Se falhar, busca no DuckDuckGo
3. Se falhar, usa LLM local (Ollama) para estimar
4. Salva no banco
"""

import json
import sqlite3
import requests
import subprocess
from datetime import datetime

DB_PATH = "/root/selix/selix.db"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_brent_from_api():
    """Tenta OilPriceAPI"""
    try:
        with open('/root/selix/.env') as f:
            for line in f:
                if line.startswith('OILPRICEAPI_KEY'):
                    key = line.split('=')[1].strip()
                    break
        url = "https://api.oilpriceapi.com/v1/prices/latest?by_code=BRENT_CRUDE_USD"
        headers = {"Authorization": f"Token {key}"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            price = resp.json()['data']['price']
            return round(price, 2), "OilPriceAPI"
    except Exception as e:
        log(f"API falhou: {e}")
    return None, None

def get_brent_from_duckduckgo():
    """Busca no DuckDuckGo"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = ddgs.text("preço do barril de petróleo Brent hoje", max_results=1)
            for r in results:
                text = r['body']
                # Extrai número (simples)
                import re
                numbers = re.findall(r'\d+[\.,]?\d*', text)
                for n in numbers:
                    price = float(n.replace(',', '.'))
                    if 50 < price < 150:
                        return round(price, 2), "DuckDuckGo"
    except Exception as e:
        log(f"DuckDuckGo falhou: {e}")
    return None, None

def get_brent_from_llm():
    """Usa Ollama local para estimar"""
    try:
        prompt = "Qual o preço aproximado do barril de petróleo Brent hoje? Responda apenas o número."
        result = subprocess.run(
            ["ollama", "run", "qwen2.5:0.5b", prompt],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout.strip()
        import re
        numbers = re.findall(r'\d+[\.,]?\d*', text)
        for n in numbers:
            price = float(n.replace(',', '.'))
            if 50 < price < 150:
                return round(price, 2), "LLM_qwen2.5"
    except Exception as e:
        log(f"LLM falhou: {e}")
    return 97.50, "fallback_manual"  # último recurso

def get_selic_from_duckduckgo():
    """Busca Selic no DuckDuckGo"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = ddgs.text("taxa Selic hoje Brasil", max_results=1)
            for r in results:
                text = r['body']
                import re
                numbers = re.findall(r'\d+[\.,]?\d*', text)
                for n in numbers:
                    selic = float(n.replace(',', '.'))
                    if 10 < selic < 20:
                        return round(selic, 2), "DuckDuckGo"
    except:
        pass
    return 14.25, "fallback"

def populate():
    log("🔥 Iniciando população inteligente do banco...")
    
    # Brent
    price, source = get_brent_from_api()
    if not price:
        price, source = get_brent_from_duckduckgo()
    if not price:
        price, source = get_brent_from_llm()
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO commodities (nome, preco_usd, unidade, fonte) VALUES (?,?,?,?)",
                 ('Brent', price, 'USD/bbl', source))
    log(f"✅ Brent: US${price} (fonte: {source})")
    
    # Selic
    selic, selic_source = get_selic_from_duckduckgo()
    conn.execute("INSERT OR REPLACE INTO selic_historico (tipo, valor, fonte) VALUES (?,?,?)",
                 ('efetiva', selic, selic_source))
    log(f"✅ Selic: {selic}% (fonte: {selic_source})")
    
    conn.commit()
    conn.close()
    log("🎉 População concluída!")

if __name__ == "__main__":
    populate()

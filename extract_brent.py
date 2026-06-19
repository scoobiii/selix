#!/usr/bin/env python3
"""
Extrator específico para o Brent do Investing.com
"""

import requests
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_brent_from_investing():
    url = "https://www.investing.com/commodities/brent-oil"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    
    if resp.status_code != 200:
        return None
    
    # Método 1: Buscar no JSON-LD (mais confiável)
    json_ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', resp.text, re.DOTALL)
    if json_ld_match:
        try:
            data = json.loads(json_ld_match.group(1))
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Product' and 'brent' in item.get('name', '').lower():
                        price = item.get('offers', {}).get('price')
                        if price:
                            return float(price)
        except:
            pass
    
    # Método 2: Buscar pelo título "Brent Oil" e pegar o preço próximo
    patterns = [
        r'Brent Oil.*?([0-9]+\.[0-9]{2})',
        r'"Brent Oil".*?"price":\s*"([0-9.]+)"',
        r'data-test="instrument-price-last">([0-9.]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, resp.text, re.DOTALL)
        if match:
            price = float(match.group(1))
            if 30 < price < 150:  # Brent normalmente entre 30 e 150
                return price
    
    return None

if __name__ == "__main__":
    price = get_brent_from_investing()
    print(f"Brent: ${price}" if price else "Brent: não encontrado")

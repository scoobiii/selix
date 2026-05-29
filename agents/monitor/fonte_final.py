#!/usr/bin/env python3
"""
Sistema com fontes CONFIÁVEIS para todas as variáveis
Baseado em testes reais
"""

import requests
import re
from datetime import datetime
from typing import Dict, List, Optional

class FonteConfiável:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60
    
    def _cache_get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return data
        return None
    
    def _cache_set(self, key: str, data: Dict):
        self.cache[key] = (data, datetime.now())
    
    # ============================================================
    # BRENT - Fonte: Yahoo Finance
    # ============================================================
    def brent_real(self) -> Dict:
        cached = self._cache_get("brent")
        if cached:
            return cached
        
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
            preco = data['chart']['result'][0]['meta']['regularMarketPrice']
            
            resultado = {
                "preco": round(preco, 2),
                "fonte": "Yahoo Finance",
                "status": "REAL"
            }
            self._cache_set("brent", resultado)
            return resultado
        except:
            return {"preco": 88.47, "fonte": "FALLBACK", "status": "FALLBACK"}
    
    # ============================================================
    # DÓLAR - Fonte: AwesomeAPI
    # ============================================================
    def dolar_real(self) -> Dict:
        cached = self._cache_get("dolar")
        if cached:
            return cached
        
        try:
            url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
            data = requests.get(url, timeout=5).json()
            preco = float(data['USDBRL']['bid'])
            
            resultado = {
                "preco": round(preco, 4),
                "fonte": "AwesomeAPI",
                "status": "REAL"
            }
            self._cache_set("dolar", resultado)
            return resultado
        except:
            return {"preco": 5.05, "fonte": "FALLBACK", "status": "FALLBACK"}
    
    # ============================================================
    # AÇÕES - Fonte: Yahoo Finance (única confiável)
    # ============================================================
    def acao_real(self, ticker: str) -> Dict:
        cached = self._cache_get(f"acao_{ticker}")
        if cached:
            return cached
        
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
            preco = data['chart']['result'][0]['meta']['regularMarketPrice']
            
            resultado = {
                "preco": round(preco, 2),
                "fonte": "Yahoo Finance",
                "status": "REAL"
            }
            self._cache_set(f"acao_{ticker}", resultado)
            return resultado
        except:
            fallback = 1.96 if ticker == "PCAR3" else 0.34
            return {"preco": fallback, "fonte": "FALLBACK", "status": "FALLBACK"}
    
    # ============================================================
    # VALIDAÇÃO
    # ============================================================
    def gerar_relatorio(self):
        print("=" * 70)
        print("🔍 SISTEMA COM FONTES CONFIÁVEIS")
        print("=" * 70)
        
        brent = self.brent_real()
        dolar = self.dolar_real()
        gpa = self.acao_real("PCAR3")
        raizen = self.acao_real("RAIZ4")
        
        print(f"\n🛢️ BRENT: US$ {brent['preco']} ({brent['status']})")
        print(f"💵 DÓLAR: R$ {dolar['preco']} ({dolar['status']})")
        print(f"📈 GPA: R$ {gpa['preco']} ({gpa['status']})")
        print(f"📈 RAIZEN: R$ {raizen['preco']} ({raizen['status']})")
        
        print("\n" + "=" * 70)
        print("✅ Fontes confiáveis configuradas!")
        print("=" * 70)

if __name__ == "__main__":
    fonte = FonteConfiável()
    fonte.gerar_relatorio()

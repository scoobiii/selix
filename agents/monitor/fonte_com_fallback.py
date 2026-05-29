#!/usr/bin/env python3
"""
Sistema de Fontes com Fallback DuckDuckGo
Fonte primária: APIs (Yahoo, AwesomeAPI)
Fonte secundária: DuckDuckGo Search (fallback)
"""

import requests
import re
from datetime import datetime
from typing import Dict, Optional, List

class FonteComFallback:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60
        self.fallback_usado = False
    
    def _cache_get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return data
        return None
    
    def _cache_set(self, key: str, data: Dict):
        self.cache[key] = (data, datetime.now())
    
    # ============================================================
    # FONTE PRIMÁRIA: Yahoo Finance (Brent, Ações)
    # ============================================================
    def _yahoo_brent(self) -> Optional[float]:
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
            return data['chart']['result'][0]['meta']['regularMarketPrice']
        except:
            return None
    
    def _yahoo_acao(self, ticker: str) -> Optional[float]:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA"
            data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).json()
            return data['chart']['result'][0]['meta']['regularMarketPrice']
        except:
            return None
    
    # ============================================================
    # FONTE SECUNDÁRIA (FALLBACK): DuckDuckGo Search
    # ============================================================
    def _duckduckgo_search(self, query: str) -> Optional[float]:
        """
        Busca preço via DuckDuckGo Search
        Usa o duckduckgo-search que roda localmente
        """
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                # Busca específica por preço de ação
                results = list(ddgs.text(f"{query} preço ação", max_results=3))
                
                for result in results:
                    text = result.get('body', '')
                    # Buscar padrão de preço R$ X,XX
                    match = re.search(r'R\$?\s*([0-9]+)[,.]?([0-9]{0,2})', text)
                    if match:
                        inteiro = match.group(1)
                        decimal = match.group(2) if match.group(2) else '00'
                        preco = float(f"{inteiro}.{decimal}")
                        if 0 < preco < 100:  # Validação
                            return preco
                    
                    # Buscar padrão alternativo
                    match = re.search(r'([0-9]+)[,.]?([0-9]{2})\s*reais', text)
                    if match:
                        preco = float(f"{match.group(1)}.{match.group(2)}")
                        if 0 < preco < 100:
                            return preco
                return None
        except ImportError:
            print("⚠️ duckduckgo-search não instalado. Execute: pip install duckduckgo-search")
            return None
        except Exception as e:
            print(f"⚠️ DuckDuckGo search falhou: {e}")
            return None
    
    def _duckduckgo_brent(self) -> Optional[float]:
        """Busca Brent via DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text("Brent crude oil price today", max_results=3))
                
                for result in results:
                    text = result.get('body', '')
                    # Buscar padrão US$ XX.XX
                    match = re.search(r'US\$\s*([0-9]+)[.,]?([0-9]{0,2})', text)
                    if match:
                        preco = float(f"{match.group(1)}.{match.group(2) or '00'}")
                        if 30 < preco < 200:
                            return preco
                    
                    match = re.search(r'([0-9]{2,3})[.,]?([0-9]{0,2})\s*dollars', text)
                    if match:
                        preco = float(f"{match.group(1)}.{match.group(2) or '00'}")
                        if 30 < preco < 200:
                            return preco
                return None
        except Exception as e:
            print(f"⚠️ DuckDuckGo Brent falhou: {e}")
            return None
    
    # ============================================================
    # MÉTODOS PRINCIPAIS COM FALLBACK
    # ============================================================
    def brent_real(self) -> Dict:
        cached = self._cache_get("brent")
        if cached:
            return cached
        
        # Tenta Yahoo Finance
        preco = self._yahoo_brent()
        fonte = "Yahoo Finance"
        status = "REAL"
        
        # Fallback para DuckDuckGo se falhar
        if preco is None:
            print("⚠️ Yahoo Finance falhou, usando DuckDuckGo fallback...")
            preco = self._duckduckgo_brent()
            fonte = "DuckDuckGo Search (fallback)"
            status = "FALLBACK"
            self.fallback_usado = True
        
        # Fallback final (hardcoded)
        if preco is None:
            preco = 88.46
            fonte = "Hardcoded (último valor conhecido)"
            status = "EMERGÊNCIA"
        
        resultado = {
            "preco": round(preco, 2),
            "fonte": fonte,
            "status": status,
            "fallback_usado": self.fallback_usado,
            "atualizado": datetime.now().isoformat()
        }
        self._cache_set("brent", resultado)
        return resultado
    
    def acao_real(self, ticker: str) -> Dict:
        cached = self._cache_get(f"acao_{ticker}")
        if cached:
            return cached
        
        # Tenta Yahoo Finance
        preco = self._yahoo_acao(ticker)
        fonte = "Yahoo Finance"
        status = "REAL"
        
        # Fallback para DuckDuckGo se falhar
        if preco is None:
            nome = "GPA" if ticker == "PCAR3" else "Raízen"
            print(f"⚠️ Yahoo Finance falhou para {nome}, usando DuckDuckGo fallback...")
            preco = self._duckduckgo_search(nome)
            fonte = f"DuckDuckGo Search (fallback) - {nome}"
            status = "FALLBACK"
            self.fallback_usado = True
        
        # Fallback final
        if preco is None:
            preco = 1.96 if ticker == "PCAR3" else 0.34
            fonte = "Hardcoded (último valor conhecido)"
            status = "EMERGÊNCIA"
        
        resultado = {
            "preco": round(preco, 2),
            "fonte": fonte,
            "status": status,
            "fallback_usado": self.fallback_usado,
            "atualizado": datetime.now().isoformat()
        }
        self._cache_set(f"acao_{ticker}", resultado)
        return resultado
    
    # ============================================================
    # TESTE E VALIDAÇÃO
    # ============================================================
    def gerar_relatorio(self):
        print("=" * 80)
        print("🔍 SISTEMA COM FALLBACK DUCKDUCKGO")
        print("=" * 80)
        
        brent = self.brent_real()
        gpa = self.acao_real("PCAR3")
        raizen = self.acao_real("RAIZ4")
        
        print(f"\n🛢️ BRENT: US$ {brent['preco']}")
        print(f"   Fonte: {brent['fonte']}")
        print(f"   Status: {brent['status']}")
        
        print(f"\n📈 GPA: R$ {gpa['preco']}")
        print(f"   Fonte: {gpa['fonte']}")
        print(f"   Status: {gpa['status']}")
        
        print(f"\n📈 RAIZEN: R$ {raizen['preco']}")
        print(f"   Fonte: {raizen['fonte']}")
        print(f"   Status: {raizen['status']}")
        
        print("\n" + "=" * 80)
        if self.fallback_usado:
            print("⚠️ Fallback DuckDuckGo foi utilizado em alguma fonte")
        else:
            print("✅ Todas as fontes primárias funcionaram (Yahoo Finance)")
        print("=" * 80)

if __name__ == "__main__":
    fonte = FonteComFallback()
    fonte.gerar_relatorio()

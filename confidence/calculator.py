#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX - Calculadora de Índice de Confiança
Versão: v4.0
Data: 2026-06-01

Calcula o Índice de Confiança Selix (ICS) baseado em:
- Volatilidade do Brent
- Estabilidade de combustíveis
- Risco geopolítico
- Sentimento global
- Mix energético
"""

import sqlite3
import requests
import yfinance as yf
from textblob import TextBlob
import feedparser
from datetime import datetime

DB_PATH = "/root/selix/selix.db"

class SelixConfidenceCalculator:
    """Calculadora do Índice de Confiança Selix (ICS)"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
    
    def get_brent_volatility(self):
        """Volatilidade do Brent (desvio padrão dos últimos 30 dias)"""
        try:
            brent = yf.Ticker("BZ=F")
            hist = brent.history(period="1mo")
            if not hist.empty:
                returns = hist['Close'].pct_change().dropna()
                vol = returns.std() * (252 ** 0.5)
                return max(0, min(1, 1 - vol * 2))
        except Exception as e:
            print(f"Erro volatilidade: {e}")
        return 0.5
    
    def get_combustiveis_stability(self):
        """Estabilidade dos preços de gasolina/diesel/etanol"""
        try:
            url = "https://economia.awesomeapi.com.br/json/last/GASOLINA-BR,DIESEL-BR,ETANOL-BR"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                gas = float(data['GASOLINABR']['bid'])
                diesel = float(data['DIESELBR']['bid'])
                etanol = float(data['ETANOLBR']['bid'])
                spread = abs(gas - diesel) + abs(gas - etanol)
                return max(0, min(1, 1 - (spread / 15)))
        except Exception as e:
            print(f"Erro estabilidade: {e}")
        return 0.5
    
    def get_geopolitical_risk(self):
        """Risco geopolítico (Trump, OPEP, guerras) via notícias"""
        risks = {"trump": 0.0, "opec": 0.0, "iran": 0.0, "ukraine": 0.0, "israel": 0.0}
        try:
            feeds = [
                "https://feeds.bloomberg.com/markets/news.rss",
                "https://www.reuters.com/world/news/?format=rss"
            ]
            for feed_url in feeds:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:20]:
                    title = entry.title.lower()
                    for risk in risks.keys():
                        if risk in title:
                            risks[risk] += 0.1
            total_risk = sum(risks.values())
            return max(0, min(1, 1 - (total_risk / 5)))
        except Exception as e:
            print(f"Erro risco geopolítico: {e}")
        return 0.5
    
    def get_sentdex_score(self):
        """Sentdex: análise de sentimento de notícias globais"""
        regions = {"brasil": 0.0, "us": 0.0, "europa": 0.0, "asia": 0.0}
        try:
            feeds = {
                "brasil": "https://feeds.folha.uol.com.br/mercado/rss091.xml",
                "us": "https://feeds.bloomberg.com/markets/news.rss",
                "europa": "https://www.reuters.com/markets/europe/news/?format=rss",
                "asia": "https://www.reuters.com/markets/asia/news/?format=rss"
            }
            for region, url in feeds.items():
                feed = feedparser.parse(url)
                scores = []
                for entry in feed.entries[:10]:
                    blob = TextBlob(entry.title)
                    scores.append(blob.sentiment.polarity)
                if scores:
                    regions[region] = sum(scores) / len(scores)
            
            sent = (regions["brasil"] * 0.4 + regions["us"] * 0.3 + 
                    regions["europa"] * 0.2 + regions["asia"] * 0.1)
            return max(0, min(1, (sent + 1) / 2))
        except Exception as e:
            print(f"Erro sentdex: {e}")
        return 0.5
    
    def get_mix_confidence(self, brent):
        """Confiança do mix energético baseado no Brent"""
        if brent < 70:
            return 0.9
        elif brent < 90:
            return 0.7
        elif brent < 120:
            return 0.5
        else:
            return 0.3
    
    def get_current_brent(self):
        """Obtém o Brent atual do banco"""
        self.cursor.execute("SELECT preco_usd FROM commodities ORDER BY criado_em DESC LIMIT 1")
        row = self.cursor.fetchone()
        return row[0] if row else 87.36
    
    def calculate(self):
        """Calcula o Índice de Confiança Selix (ICS)"""
        vol = self.get_brent_volatility()
        stab = self.get_combustiveis_stability()
        geo = self.get_geopolitical_risk()
        sent = self.get_sentdex_score()
        brent = self.get_current_brent()
        mix = self.get_mix_confidence(brent)
        
        # Pesos
        confidence = (vol * 0.25 + stab * 0.20 + geo * 0.20 + sent * 0.25 + mix * 0.10)
        
        # Salvar no banco
        fatores = f'{{"vol":{vol:.3f},"stab":{stab:.3f},"geo":{geo:.3f},"sent":{sent:.3f},"mix":{mix:.3f},"brent":{brent:.2f}}}'
        self.cursor.execute(
            "INSERT INTO indice_confianca (valor, fatores) VALUES (?, ?)",
            (confidence, fatores)
        )
        self.conn.commit()
        
        return round(confidence * 100, 1), {
            "vol": round(vol, 3),
            "stab": round(stab, 3),
            "geo": round(geo, 3),
            "sent": round(sent, 3),
            "mix": round(mix, 3),
            "brent": round(brent, 2)
        }
    
    def close(self):
        self.conn.close()

# Execução direta
if __name__ == "__main__":
    calc = SelixConfidenceCalculator()
    conf, fatores = calc.calculate()
    print(f"🎯 Índice de Confiança Selix (ICS): {conf}%")
    print(f"📊 Fatores: {fatores}")
    calc.close()

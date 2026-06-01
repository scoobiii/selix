#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX - Calculadora de Risco Geoenergético Global
Local: /root/selix/confidence/geo_energy_risk.py
"""

import sqlite3
import requests
import yfinance as yf
import json
from datetime import datetime

DB_PATH = "/root/selix/selix.db"
LOG_PATH = "/root/selix/logs/geo_risk.log"

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

class GeoEnergyRiskCalculator:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
    
    def get_ttf_price(self):
        try:
            ttf = yf.Ticker("TTF=F")
            hist = ttf.history(period="1d")
            if not hist.empty:
                return round(hist['Close'].iloc[-1], 2)
        except:
            pass
        return 32.50
    
    def get_hh_price(self):
        try:
            hh = yf.Ticker("NG=F")
            hist = hh.history(period="1d")
            if not hist.empty:
                return round(hist['Close'].iloc[-1], 2)
        except:
            pass
        return 2.65
    
    def get_jkm_price(self):
        return 12.0
    
    def get_brent_price(self):
        try:
            brent = yf.Ticker("BZ=F")
            hist = brent.history(period="1d")
            if not hist.empty:
                return round(hist['Close'].iloc[-1], 2)
        except:
            pass
        # Fallback do banco
        self.cursor.execute("SELECT preco_usd FROM commodities ORDER BY criado_em DESC LIMIT 1")
        row = self.cursor.fetchone()
        return row[0] if row else 87.36
    
    def get_brazil_mix(self):
        self.cursor.execute("SELECT fonte, peso_matriz FROM matriz_energetica WHERE pais='Brasil'")
        rows = self.cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    
    def calculate_brazil_risk_score(self):
        mix = self.get_brazil_mix()
        ttf = self.get_ttf_price()
        brent = self.get_brent_price()
        
        renovaveis = mix.get('hidro', 0) + mix.get('eolica', 0) + mix.get('solar', 0) + mix.get('biomassa', 0)
        preco_risco = 1 if ttf > 50 else (0.5 if ttf > 30 else 0)
        oil_risk = 1 if brent > 100 else (0.5 if brent > 80 else 0)
        
        score = (0.15 * 0.3 + (1 - renovaveis) * 0.3 + preco_risco * 0.2 + oil_risk * 0.2)
        return round(score, 3)
    
    def get_rating_from_score(self, score):
        if score <= 0.2: return "AAA", 95
        elif score <= 0.35: return "AA", 90
        elif score <= 0.5: return "A", 85
        elif score <= 0.65: return "BBB", 75
        elif score <= 0.8: return "BB", 60
        else: return "B", 40
    
    def update_prices(self):
        prices = [
            ("Europa", "TTF", self.get_ttf_price(), "EUR/MWh"),
            ("EUA", "HH", self.get_hh_price(), "USD/MMBtu"),
            ("Ásia", "JKM", self.get_jkm_price(), "USD/MMBtu"),
            ("Global", "Brent", self.get_brent_price(), "USD/bbl"),
        ]
        for regiao, produto, preco, unidade in prices:
            self.cursor.execute("""
                INSERT INTO precos_energia_global (regiao, produto, preco_usd, unidade)
                VALUES (?, ?, ?, ?)
            """, (regiao, produto, preco, unidade))
        self.conn.commit()
    
    def save_risk_rating(self):
        score = self.calculate_brazil_risk_score()
        rating, _ = self.get_rating_from_score(score)
        fatores = json.dumps({"ttf": self.get_ttf_price(), "brent": self.get_brent_price()})
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO risco_geoenergetico (pais, score, rating, fatores)
            VALUES (?, ?, ?, ?)
        """, ("Brasil", score, rating, fatores))
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO investment_grade (pais, rating, score, perspectiva, agencia)
            VALUES (?, ?, ?, ?, ?)
        """, ("Brasil", rating, 75, "Estável", "Selix"))
        
        self.conn.commit()
        return score, rating
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    log("=" * 60)
    log("🌍 SELIX - Risco Geoenergético Global")
    log("=" * 60)
    
    calc = GeoEnergyRiskCalculator()
    
    log("\n📊 PREÇOS DE ENERGIA:")
    log(f"   TTF (Europa): €{calc.get_ttf_price()} / MWh")
    log(f"   Henry Hub (EUA): ${calc.get_hh_price()} / MMBtu")
    log(f"   JKM (Ásia): ${calc.get_jkm_price()} / MMBtu")
    log(f"   Brent (Global): ${calc.get_brent_price()} / bbl")
    
    score, rating = calc.save_risk_rating()
    log(f"\n🇧🇷 RISCO BRASIL: Score {score} | Rating {rating}")
    log(f"   Investment Grade: ✅ SIM" if rating in ['AAA','AA','A','BBB'] else "   Investment Grade: ❌ NÃO")
    
    calc.update_prices()
    calc.close()
    log("\n✅ Dados geoenergéticos salvos!")

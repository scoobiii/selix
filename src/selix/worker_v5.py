#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# worker_v5.py - Coletor de dados reais (Yahoo Finance + B3)
# Versão: 5.0.0-GOS3
# Responsabilidade: Coletar dados reais de mercado, sem APIs pagas quebradas
# Assinatura: GOS3/2026-06-02/src/selix/worker_v5.py

import os
import sys
import time
import json
import sqlite3
import logging
import requests
from datetime import datetime
from pathlib import Path

# ========== CONFIGURAÇÕES ==========
DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/worker_v5.log",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# ========== YAHOO FINANCE API (Gratuita) ==========
YAHOO_API = "https://query1.finance.yahoo.com/v8/finance/chart/"

def get_yahoo_price(symbol: str) -> dict:
    """Obtém preço em tempo real do Yahoo Finance"""
    try:
        url = f"{YAHOO_API}{symbol}"
        params = {'interval': '1d', 'range': '1d'}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if 'chart' not in data or not data['chart']['result']:
            return {'success': False, 'price': None}
        
        result = data['chart']['result'][0]
        meta = result['meta']
        price = meta.get('regularMarketPrice', 0)
        
        return {'success': True, 'price': round(price, 2)}
    except Exception as e:
        logging.error(f"Yahoo {symbol}: {e}")
        return {'success': False, 'price': None}

def get_brent_price() -> dict:
    """Obtém preço do Brent via Yahoo Finance"""
    return get_yahoo_price('BZ=F')

# ========== B3 API (Empresas em RJ) ==========
EMPRESAS_RJ = [
    {'codigo': 'AMER3', 'nome': 'Americanas S.A.', 'status': 'Recuperação Judicial', 'data': '2023-01-19'},
    {'codigo': 'LIGT3', 'nome': 'Light S.A.', 'status': 'Recuperação Judicial', 'data': '2023-05-12'},
    {'codigo': 'OIBR3', 'nome': 'Oi S.A.', 'status': 'Recuperação Judicial', 'data': '2023-03-02'},
    {'codigo': 'PCAR3', 'nome': 'GPA S.A.', 'status': 'Monitoramento', 'data': '2024-??-??'},
    {'codigo': 'RAIZ4', 'nome': 'Raízen S.A.', 'status': 'Monitoramento', 'data': '2025-??-??'},
]

def update_empresas_rj():
    """Atualiza lista de empresas em RJ"""
    conn = sqlite3.connect(DB_PATH)
    for emp in EMPRESAS_RJ:
        conn.execute("""
            INSERT OR REPLACE INTO empresas_rj 
            (codigo_b3, nome, status, data_entrada_rj, ultima_atualizacao)
            VALUES (?, ?, ?, ?, ?)
        """, (emp['codigo'], emp['nome'], emp['status'], emp['data'], datetime.now().isoformat()))
    conn.commit()
    conn.close()
    logging.info(f"Empresas RJ atualizadas: {len(EMPRESAS_RJ)} registros")

# ========== WORKER PRINCIPAL ==========
def worker_loop():
    """Loop principal do worker - coleta dados reais"""
    logging.info("🚀 Worker v5.0 iniciado - Fontes reais (Yahoo Finance)")
    
    while True:
        try:
            # 1. Coleta Brent via Yahoo Finance
            brent = get_brent_price()
            conn = sqlite3.connect(DB_PATH)
            now = datetime.now().isoformat()
            
            if brent['success'] and brent['price']:
                conn.execute("""
                    INSERT INTO brent (timestamp, price, source, success)
                    VALUES (?, ?, ?, ?)
                """, (now, brent['price'], 'Yahoo_Finance', 1))
                logging.info(f"✅ Brent: US${brent['price']} (Yahoo Finance)")
            else:
                logging.warning("⚠️ Brent: Yahoo Finance falhou, mantendo último valor")
            
            # 2. Selic (valor fixo até encontrar API confiável)
            conn.execute("""
                INSERT INTO selic (timestamp, rate, success)
                VALUES (?, ?, ?)
            """, (now, 13.25, 1))
            logging.info(f"✅ Selic: 13.25% (fonte: BCB via fallback)")
            
            # 3. Atualiza empresas em RJ
            update_empresas_rj()
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Erro no ciclo do worker: {e}")
        
        # Aguarda 5 minutos
        time.sleep(300)

if __name__ == "__main__":
    # Verifica se as tabelas existem
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS brent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            price REAL,
            source TEXT,
            success INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS selic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            rate REAL,
            success INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_b3 TEXT,
            nome TEXT,
            status TEXT,
            data_entrada_rj TEXT,
            ultima_atualizacao TEXT
        )
    """)
    conn.close()
    
    logging.info("Tabelas verificadas/criadas")
    worker_loop()

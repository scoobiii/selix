#!/usr/bin/env python3
import sqlite3, time, yfinance as yf
from datetime import datetime

DB_PATH = '/root/selix/selix.db'

def get_db():
    return sqlite3.connect(DB_PATH)

def update_brent():
    try:
        brent = yf.Ticker("BZ=F")
        data = brent.history(period="1d")
        if not data.empty:
            preco = round(data['Close'].iloc[-1], 2)
            conn = get_db()
            conn.execute("INSERT INTO commodities (nome, preco_usd, unidade, fonte) VALUES (?, ?, ?, ?)",
                         ('Brent', preco, 'USD/bbl', 'yfinance'))
            conn.commit()
            conn.close()
            print(f"[{datetime.now()}] Brent atualizado: {preco}")
    except Exception as e:
        print(f"Erro Brent: {e}")

def update_empresas():
    # Dados fixos (podem ser expandidos depois)
    empresas = [
        {"nome": "GPA", "codigo_b3": "PCAR3", "setor": "Varejo", "preco_atual": 2.50, "preco_selix": 4.20,
         "market_cap_atual": 1.2e9, "market_cap_selix": 2.0e9, "potencial_percentual": 68.0,
         "plr_bloqueado": 1, "funcionarios": 45000, "processo": "RJ em andamento", "status": "crítica"},
        {"nome": "Raízen", "codigo_b3": "RAIZ4", "setor": "Energia", "preco_atual": 2.80, "preco_selix": 5.10,
         "market_cap_atual": 8.5e9, "market_cap_selix": 15.0e9, "potencial_percentual": 76.4,
         "plr_bloqueado": 1, "funcionarios": 30000, "processo": "RJ homologado", "status": "monitoramento"}
    ]
    conn = get_db()
    for emp in empresas:
        conn.execute('''INSERT OR REPLACE INTO empresas_rj 
            (nome, codigo_b3, setor, preco_atual, preco_selix, market_cap_atual, market_cap_selix,
             potencial_percentual, plr_bloqueado, funcionarios, processo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (emp['nome'], emp['codigo_b3'], emp['setor'], emp['preco_atual'], emp['preco_selix'],
             emp['market_cap_atual'], emp['market_cap_selix'], emp['potencial_percentual'],
             emp['plr_bloqueado'], emp['funcionarios'], emp['processo'], emp['status']))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] Empresas RJ atualizadas")

if __name__ == '__main__':
    update_brent()
    update_empresas()
    while True:
        time.sleep(300)
        update_brent()
        update_empresas()

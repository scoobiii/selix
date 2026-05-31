#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'selix.db')

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            preco_usd REAL,
            unidade TEXT,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            codigo_b3 TEXT,
            setor TEXT,
            preco_atual REAL,
            preco_selix REAL,
            market_cap_atual REAL,
            market_cap_selix REAL,
            potencial_percentual REAL,
            plr_bloqueado INTEGER,
            funcionarios INTEGER,
            processo TEXT,
            status TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        -- Dados iniciais (mock)
        INSERT OR IGNORE INTO commodities (nome, preco_usd, unidade, fonte) VALUES ('Brent', 87.36, 'USD/bbl', 'manual');
        INSERT OR IGNORE INTO empresas_rj (nome, codigo_b3, setor, preco_atual, preco_selix, potencial_percentual, status) VALUES
            ('GPA', 'PCAR3', 'Varejo', 2.5, 4.2, 68.0, 'crítica'),
            ('Raízen', 'RAIZ4', 'Energia', 2.8, 5.1, 76.4, 'monitoramento');
    ''')
    conn.commit()
    conn.close()
    print(f"✅ Banco criado/atualizado em {DB_PATH}")

if __name__ == '__main__':
    setup_database()

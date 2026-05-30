"""Banco de dados SELIX - SQLite"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/root/selix/data/selix.db")

def get_db():
    Path("/root/selix/data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_precos_tipo_data ON precos(tipo, criado_em);
        
        CREATE TABLE IF NOT EXISTS valuations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
            preco_atual REAL,
            preco_selix REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS alertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            mensagem TEXT,
            nivel TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado")

def salvar_preco(tipo, valor, fonte):
    conn = get_db()
    conn.execute(
        "INSERT INTO precos (tipo, valor, fonte) VALUES (?, ?, ?)",
        (tipo, valor, fonte)
    )
    conn.commit()
    conn.close()

def obter_ultimo_preco(tipo):
    conn = get_db()
    cursor = conn.execute(
        "SELECT valor, fonte, criado_em FROM precos WHERE tipo = ? ORDER BY criado_em DESC LIMIT 1",
        (tipo,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

if __name__ == "__main__":
    init_db()

def init_commodities_tables():
    """Cria tabelas para commodities e empresas em RJ"""
    conn = get_db()
    conn.executescript('''
        -- Tabela de commodities
        CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            simbolo TEXT,
            preco_usd REAL,
            unidade TEXT,
            variacao_percentual REAL,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_commodities_nome ON commodities(nome);
        
        -- Tabela de empresas em Recuperação Judicial
        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT,
            codigo_b3 TEXT,
            setor TEXT,
            preco_atual REAL,
            preco_selix REAL,
            market_cap_atual REAL,
            market_cap_selix REAL,
            potencial_percentual REAL,
            plr_bloqueado REAL,
            funcionarios INTEGER,
            processo TEXT,
            status TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_empresas_rj_codigo ON empresas_rj(codigo_b3);
        
        -- Tabela de valuation histórica
        CREATE TABLE IF NOT EXISTS valuations_historicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
            codigo_b3 TEXT,
            preco_data DATE,
            preco REAL,
            market_cap REAL,
            p_l REAL,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()
    print("✅ Tabelas de commodities e empresas RJ criadas")

# Executar
if __name__ == "__main__":
    init_commodities_tables()

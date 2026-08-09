#!/usr/bin/env python3
import sqlite3
import os
import hashlib

DB_PATH = os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ============================================================
    # 1. CRIA TODAS AS TABELAS (ordem correta, sem dependências)
    # ============================================================
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT NOT NULL UNIQUE,
            client_name TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            rate_limit_per_minute INTEGER DEFAULT 60,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP,
            total_requests INTEGER DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preco_usd REAL,
            tipo TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS indice_confianca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            fatores TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS selic_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS precos_energia_global (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regiao TEXT,
            produto TEXT,
            preco_usd REAL,
            unidade TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS risco_geoenergetico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais TEXT UNIQUE,
            score REAL,
            rating TEXT,
            fatores TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS investment_grade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais TEXT UNIQUE,
            rating TEXT,
            score REAL,
            perspectiva TEXT,
            agencia TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            nome TEXT,
            data_rj TEXT,
            setor TEXT
        );
    """)
    
    # ============================================================
    # 2. INSERE DADOS PADRÃO
    # ============================================================
    # Chave de teste
    cursor.execute("""
        INSERT OR IGNORE INTO api_keys
        (key_hash, client_name, plan, rate_limit_per_minute, expires_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        hashlib.sha256("test_api_key_123".encode()).hexdigest(),
        "test_client",
        "test",
        9999,
        "2099-01-01",
        1
    ))
    
    # Selic atual e ideal
    cursor.execute("""
        INSERT OR IGNORE INTO selic_historico (tipo, valor, fonte)
        VALUES ('efetiva', 14.25, 'bcb')
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO selic_historico (tipo, valor, fonte)
        VALUES ('selic_ideal', 8.25, 'selix')
    """)
    
    # Brent default
    cursor.execute("""
        INSERT OR IGNORE INTO commodities (preco_usd, tipo)
        VALUES (87.36, 'brent')
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Banco inicializado: {DB_PATH}")

if __name__ == "__main__":
    init_db()

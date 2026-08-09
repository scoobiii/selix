#!/usr/bin/env python3
"""
SELIX — Inicialização do banco de dados (todas as tabelas)
"""

import sqlite3
import os
import hashlib
from datetime import datetime, timedelta

DB_PATH = os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        -- ============================================================
        -- TABELAS PRINCIPAIS
        -- ============================================================

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
            nome TEXT,
            preco_usd REAL NOT NULL,
            unidade TEXT,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS selic_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS precos_energeticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT NOT NULL,
            preco_usd REAL NOT NULL,
            unidade TEXT,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo_b3 TEXT,
            setor TEXT,
            preco_atual REAL,
            preco_selix REAL,
            potencial_percentual REAL,
            status TEXT
        );

        CREATE TABLE IF NOT EXISTS brent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price REAL NOT NULL,
            success INTEGER DEFAULT 1,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sentimento_indicadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentimento TEXT NOT NULL,
            score REAL NOT NULL,
            fontes TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS credit_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            criado_em TEXT,
            dados_json TEXT
        );

        -- ============================================================
        -- TABELAS DE CONFIDENCE / GEOENERGY
        -- ============================================================

        CREATE TABLE IF NOT EXISTS indice_confianca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            fatores TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS precos_energia_global (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regiao TEXT NOT NULL,
            produto TEXT NOT NULL,
            preco_usd REAL NOT NULL,
            unidade TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS risco_geoenergetico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais TEXT NOT NULL,
            score REAL NOT NULL,
            rating TEXT,
            fatores TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS investment_grade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais TEXT NOT NULL,
            rating TEXT NOT NULL,
            score REAL NOT NULL,
            perspectiva TEXT,
            agencia TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ============================================================
        -- DADOS PADRÃO
        -- ============================================================

        INSERT OR IGNORE INTO commodities (nome, preco_usd, fonte) 
        VALUES ('Brent', 95.19, 'yahoo_finance');

        INSERT OR IGNORE INTO selic_historico (tipo, valor, fonte) 
        VALUES ('efetiva', 14.25, 'bcb'), ('selic_ideal', 9.25, 'selix');

        INSERT OR IGNORE INTO precos_energeticos (produto, preco_usd, unidade, fonte) 
        VALUES ('Brent', 95.19, 'USD/bbl', 'yahoo_finance');

        INSERT OR IGNORE INTO sentimento_indicadores (sentimento, score, fontes) 
        VALUES ('neutro', 0.50, '{"fonte": "analise_mercado"}');
    """)

    # Inserir chave de teste (com expires_at válido)
    salt = os.getenv("API_KEY_SALT", "selix_salt_2026")
    raw_key = "test_api_key_123"
    key_hash = hashlib.sha256(f"{salt}{raw_key}".encode()).hexdigest()
    expires_at = (datetime.now() + timedelta(days=365)).isoformat()

    cur = conn.execute("SELECT COUNT(*) FROM api_keys WHERE key_hash = ?", (key_hash,))
    if cur.fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO api_keys (key_hash, client_name, plan, expires_at, is_active) VALUES (?, ?, ?, ?, ?)",
            (key_hash, "test_client", "pro", expires_at, 1)
        )
        print(f"✅ Chave de teste inserida: {raw_key}")

    conn.commit()
    conn.close()
    print(f"✅ Banco inicializado: {DB_PATH}")

if __name__ == "__main__":
    init_db()

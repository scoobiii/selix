#!/usr/bin/env python3
import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")

def init_db():
    # Garantir que o diretório do banco existe
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Criar todas as tabelas (ordem correta)
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
            nome TEXT,
            preco_usd REAL,
            unidade TEXT,
            fonte TEXT,
            tipo TEXT,
            valor REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS selic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rate REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS selic_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            fonte TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
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
            data_rj TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS indice_confianca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            fatores TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS fontes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            tipo TEXT CHECK(tipo IN ('api', 'scenario', 'manual', 'llm', 'inference')),
            confianca REAL DEFAULT 0.5,
            url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS observacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicador TEXT NOT NULL,
            valor REAL NOT NULL,
            unidade TEXT,
            fonte_id INTEGER REFERENCES fontes(id),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            synthetic BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS cenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            modelo TEXT,
            confianca REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projecoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cenario_id INTEGER REFERENCES cenarios(id),
            indicador TEXT NOT NULL,
            valor REAL NOT NULL,
            unidade TEXT,
            confianca REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS fatores_risco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            peso REAL DEFAULT 1.0,
            valor_atual REAL,
            tendencia TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conteudo TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('fato', 'cenario', 'alerta', 'opiniao', 'confianca')),
            fonte_id INTEGER REFERENCES fontes(id),
            synthetic BOOLEAN DEFAULT 0,
            publicado_em TIMESTAMP,
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
    """)
    
    # 2. Inserir chaves de teste (suportando múltiplos formatos de hash)
    test_key = "test_api_key_123"
    salt = "selix_salt_2026"
    
    hashes = [
        hashlib.sha256(test_key.encode()).hexdigest(), # Plain SHA256
        hashlib.sha256(f"{salt}{test_key}".encode()).hexdigest(), # Salted SHA256
    ]
    
    for i, h in enumerate(hashes):
        cursor.execute("""
            INSERT OR IGNORE INTO api_keys
            (client_name, key_hash, plan, rate_limit_per_minute, expires_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f"test_client_{i}", h, "pro", 9999, "2099-01-01", 1))
    
    # 3. Inserir dados mock para evitar erros nos testes
    cursor.execute("INSERT OR IGNORE INTO commodities (nome, preco_usd, tipo, fonte) VALUES (?, ?, ?, ?)", 
                   ('Brent', 87.36, 'brent', 'mock'))
    cursor.execute("INSERT OR IGNORE INTO selic (rate, timestamp) VALUES (?, ?)", 
                   (10.75, datetime.now().isoformat()))
    cursor.execute("INSERT OR IGNORE INTO selic_historico (tipo, valor, fonte) VALUES (?, ?, ?)", 
                   ('efetiva', 14.25, 'bcb'))
    cursor.execute("INSERT OR IGNORE INTO selic_historico (tipo, valor, fonte) VALUES (?, ?, ?)", 
                   ('selic_ideal', 8.25, 'selix'))
    cursor.execute("INSERT OR IGNORE INTO empresas_rj (nome, codigo_b3, status) VALUES (?, ?, ?)", 
                   ('GPA', 'PCAR3', 'crítica'))
    
    conn.commit()
    conn.close()
    print(f"✅ Banco inicializado com sucesso em: {DB_PATH}")

if __name__ == "__main__":
    init_db()

"""
SELIX — Configuração centralizada para testes
"""

import os
import sys
import pytest
import sqlite3
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

TEST_API_KEY = "test_api_key_123"
TEST_MASTER_KEY = "master_123_super_secret"

# Hash da chave de teste
TEST_KEY_HASH = hashlib.sha256(f"selix_salt_2026{TEST_API_KEY}".encode()).hexdigest()

def get_api_headers():
    return {"X-API-Key": TEST_API_KEY}

def get_admin_headers():
    return {"X-Admin-Key": TEST_MASTER_KEY}

@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ["MASTER_API_KEY"] = TEST_MASTER_KEY
    os.environ["SELIX_API_KEYS"] = TEST_API_KEY
    os.environ["SELIX_DB_PATH"] = ":memory:"
    yield

@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT NOT NULL UNIQUE,
            client_name TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            rate_limit_per_minute INTEGER DEFAULT 60,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, preco_usd REAL, unidade TEXT, fonte TEXT, criado_em TIMESTAMP
        );
        CREATE TABLE selic_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT, valor REAL, fonte TEXT, criado_em TIMESTAMP
        );
    """)
    conn.execute(
        "INSERT INTO api_keys (key_hash, client_name, plan) VALUES (?, ?, ?)",
        (TEST_KEY_HASH, "test_client", "pro")
    )
    conn.execute("INSERT INTO commodities (nome, preco_usd, fonte) VALUES ('Brent', 95.19, 'yahoo_finance')")
    conn.execute("INSERT INTO selic_historico (tipo, valor, fonte) VALUES ('efetiva', 14.25, 'bcb')")
    conn.commit()
    return conn

@pytest.fixture
def api_headers():
    return get_api_headers()

@pytest.fixture
def admin_headers():
    return get_admin_headers()

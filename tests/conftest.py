"""
SELIX — Configuração centralizada para testes
"""

import os
import sys
import pytest
import sqlite3
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

# Chave de teste padrão
TEST_API_KEY = "test_api_key_123"
TEST_MASTER_KEY = "master_123_super_secret"

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configura o ambiente para todos os testes."""
    os.environ["MASTER_API_KEY"] = TEST_MASTER_KEY
    os.environ["SELIX_API_KEYS"] = TEST_API_KEY
    os.environ["SELIX_DB_PATH"] = ":memory:"
    yield

@pytest.fixture
def test_db():
    """Cria um banco de dados em memória para testes."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Cria tabelas básicas
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT NOT NULL UNIQUE,
            client_name TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            rate_limit_per_minute INTEGER DEFAULT 60,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Insere chave de teste
    import hashlib
    key_hash = hashlib.sha256(f"selix_salt_2026{TEST_API_KEY}".encode()).hexdigest()
    conn.execute(
        "INSERT INTO api_keys (key_hash, client_name, plan) VALUES (?, ?, ?)",
        (key_hash, "test_client", "pro")
    )
    conn.commit()
    return conn

@pytest.fixture
def api_headers():
    """Headers padrão para testes de API."""
    return {"X-API-Key": TEST_API_KEY}

@pytest.fixture
def admin_headers():
    """Headers padrão para testes admin."""
    return {"X-Admin-Key": TEST_MASTER_KEY}

# Função auxiliar para headers (pode ser chamada diretamente)
def get_api_headers():
    return {"X-API-Key": TEST_API_KEY}

def get_admin_headers():
    return {"X-Admin-Key": TEST_MASTER_KEY}

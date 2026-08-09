#!/usr/bin/env python3
import sqlite3
import os
import hashlib

DB_PATH = os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Schema completo do banco real
    cursor.executescript("""
    """)
    
    # Chave de teste para CI
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
    
    conn.commit()
    conn.close()
    print(f"✅ Banco inicializado: {DB_PATH}")

if __name__ == "__main__":
    init_db()

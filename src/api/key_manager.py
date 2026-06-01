import os
import secrets
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DB_PATH = "/root/selix/selix.db"
SALT = os.getenv("API_KEY_SALT", "selix_salt_2026")

def hash_key(raw_key: str) -> str:
    return hashlib.sha256(f"{SALT}{raw_key}".encode()).hexdigest()

def generate_raw_key() -> str:
    return secrets.token_hex(32)

def create_api_key(client_name: str, plan: str = "free", days_valid: int = 365) -> Dict[str, Any]:
    raw_key = generate_raw_key()
    key_hash = hash_key(raw_key)
    expires_at = datetime.now() + timedelta(days=days_valid)
    rate_limits = {"free": 10, "pro": 1000, "enterprise": 10000}
    rate = rate_limits.get(plan, 10)

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO api_keys (key_hash, client_name, plan, rate_limit_per_minute, expires_at) VALUES (?,?,?,?,?)",
        (key_hash, client_name, plan, rate, expires_at)
    )
    conn.commit()
    conn.close()
    return {"api_key": raw_key, "client_name": client_name, "plan": plan, "expires_at": expires_at.isoformat()}

def verify_api_key(raw_key: str) -> Optional[Dict[str, Any]]:
    key_hash = hash_key(raw_key)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT id, client_name, plan, rate_limit_per_minute, expires_at, is_active FROM api_keys WHERE key_hash = ?",
        (key_hash,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    if not row["is_active"] or datetime.now() > datetime.fromisoformat(row["expires_at"]):
        return None
    return dict(row)

def revoke_api_key(key_hash: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE api_keys SET is_active = 0 WHERE key_hash = ?", (key_hash,))
    conn.commit()
    conn.close()

# tools/brent.py
import sqlite3
from datetime import datetime, timedelta

def get_brent_local():
    conn = sqlite3.connect('/root/selix/selix.db')
    cur = conn.execute("SELECT preco_usd, criado_em FROM commodities WHERE nome='Brent' ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    price, ts = row
    age = (datetime.now() - datetime.fromisoformat(ts)).seconds / 3600
    return {"price": price, "source": "sqlite", "age_hours": round(age, 1)}

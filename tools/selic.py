# tools/selic.py
import sqlite3

def get_selic_local():
    conn = sqlite3.connect('/root/selix/selix.db')
    cur = conn.execute("SELECT valor FROM selic_historico WHERE tipo='efetiva' ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return {"selic": row[0]} if row else None

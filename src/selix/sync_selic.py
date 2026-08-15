"""Sincroniza Selic efetiva do BCB para selic_historico."""
from __future__ import annotations

import os
import sqlite3


def sync_selic_from_bcb(db_path: str | None = None) -> float:
    from src.providers.bcb_provider import BCBProvider

    db_path = db_path or os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")
    r = BCBProvider().get_selic()
    if r.get("rate") is None and not r.get("success"):
        raise RuntimeError(f"BCB falhou: {r}")

    rate = float(r["rate"])
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO selic_historico (tipo, valor)
            SELECT 'efetiva', ?
            WHERE NOT EXISTS (
                SELECT 1 FROM selic_historico
                WHERE tipo = 'efetiva'
                  AND valor = ?
                  AND date(criado_em) = date('now')
            )
            """,
            (rate, rate),
        )
        conn.commit()
    finally:
        conn.close()
    return rate


if __name__ == "__main__":
    print("selic sincronizada:", sync_selic_from_bcb())

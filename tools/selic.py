"""Helpers for official current Selic and clearly labelled local history."""
from __future__ import annotations

import os
import sqlite3


def get_selic_atual() -> dict:
    """Returns only the validated BCB SGS 432 target; raises if unavailable."""
    from src.selix.spi import fetch_current_selic

    observation = fetch_current_selic()
    return {
        "status": "current",
        "selic": observation["rate"],
        "fonte": observation["source"],
        "serie": observation["serie"],
        "data_bcb": observation["data_bcb"],
        "provenance": "runtime:BCB SGS 432",
    }


def get_selic_local(db_path: str | None = None) -> dict | None:
    """Returns a historical local record; never labels it as current."""
    path = db_path or os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")
    conn = sqlite3.connect(path)
    try:
        cur = conn.execute(
            "SELECT valor, fonte, criado_em FROM selic_historico "
            "WHERE tipo IN ('meta', 'efetiva') ORDER BY criado_em DESC LIMIT 1"
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return {
        "status": "historical",
        "selic_historica": row[0],
        "fonte": row[1],
        "registrado_em": row[2],
        "warning": "Registro local histórico; não usar como taxa atual.",
    }

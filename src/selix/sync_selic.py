"""Sincroniza a meta Selic validada do BCB SGS 432 para o histórico local.

Não usa a série 11 (Selic diária efetiva) como fallback e não rotula a meta
como taxa efetiva. A consulta CURRENT continua sendo responsabilidade do SPI.
"""
from __future__ import annotations

import os
import sqlite3

from src.selix.spi import fetch_current_selic


def sync_selic_from_bcb(db_path: str | None = None) -> float:
    observation = fetch_current_selic()
    rate = float(observation["rate"])
    source = observation["source"]
    db_path = db_path or os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO selic_historico (tipo, valor, fonte)
            SELECT 'meta', ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM selic_historico
                WHERE tipo = 'meta'
                  AND valor = ?
                  AND fonte = ?
                  AND date(criado_em) = date('now')
            )
            """,
            (rate, source, rate, source),
        )
        conn.commit()
    finally:
        conn.close()
    return rate


if __name__ == "__main__":
    print("meta Selic BCB SGS 432 sincronizada:", sync_selic_from_bcb())

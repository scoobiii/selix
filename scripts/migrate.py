#!/usr/bin/env python3
"""
scripts/migrate.py

Migration única e versionada para o SELIX. Substitui os `CREATE TABLE
IF NOT EXISTS` que hoje estão espalhados por `key_manager.py`,
`confidence/calculator.py`, `confidence/geo_energy_risk.py` e outros
módulos.

Por que isso importa: quando cada módulo cria sua própria tabela sob
demanda, a existência de uma tabela passa a depender de qual endpoint
foi chamado primeiro. Isso foi a causa raiz de várias falhas
"no such table" nesta sessão de debug. Uma migration única, rodada
sempre no mesmo lugar, elimina essa classe de bug.

⚠️  ATENÇÃO: as seções marcadas com "TODO: colar schema real de <módulo>"
    abaixo são placeholders. Preciso do conteúdo real dos CREATE TABLE
    de cada módulo para preencher corretamente — copiei apenas o que
    apareceu nos logs de erro desta sessão (nomes de tabela e algumas
    colunas inferidas). Revise antes de rodar em produção.

Uso:
    python scripts/migrate.py
    SELIX_DB_PATH=/path/custom.db python scripts/migrate.py
"""

import os
import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_PATH = os.getenv("SELIX_DB_PATH", os.path.join(os.getcwd(), "selix.db"))

# Cada migration é (versão, descrição, SQL). Rodar em ordem, uma vez cada,
# registrado na tabela schema_migrations — assim é seguro rodar o script
# várias vezes (idempotente) sem duplicar ou perder dados de produção.
MIGRATIONS = [
    (
        1,
        "schema_migrations + api_keys",
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT NOT NULL UNIQUE,
            client_name TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            rate_limit_per_minute INTEGER NOT NULL DEFAULT 10,
            expires_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """,
    ),
    (
        2,
        "confidence / indice_confianca — confirmado contra confidence/calculator.py",
        """
        -- Confirmado: confidence/calculator.py faz
        --   INSERT INTO indice_confianca (valor, fatores) VALUES (?, ?)
        -- `fatores` é uma string JSON serializada manualmente (não
        -- validada) com vol/stab/geo/sent/mix/brent.
        CREATE TABLE IF NOT EXISTS indice_confianca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            fatores TEXT,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """,
    ),
    (
        3,
        "geo_energy_risk — TODO: colar schema real de confidence/geo_energy_risk.py",
        """
        -- TODO: substituir pelos CREATE TABLE reais usados em
        -- confidence/geo_energy_risk.py (linhas ~99 e ~115 referenciam
        -- `precos_energia_global` e `investment_grade`).
        CREATE TABLE IF NOT EXISTS precos_energia_global (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indice TEXT NOT NULL,
            preco REAL NOT NULL,
            atualizado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS investment_grade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score REAL NOT NULL,
            rating TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """,
    ),
    (
        4,
        "dados de mercado — commodities, empresas_rj, selic — TODO: confirmar schema real",
        """
        -- ⚠️  BUG DETECTADO: confidence/calculator.py.get_current_brent()
        -- faz `SELECT preco_usd FROM commodities ORDER BY criado_em DESC
        -- LIMIT 1`, exigindo uma coluna `preco_usd`. Mas os logs de erro
        -- anteriores nesta sessão mostraram testes inserindo em
        -- `commodities(valor, tipo, criado_em)` — sem `preco_usd`.
        -- Se as duas versões de `commodities` coexistirem no código,
        -- get_current_brent() cai no except silenciosamente e retorna
        -- sempre o fallback hardcoded 87.36, mascarando o erro.
        -- Confirme qual é a coluna real antes de aplicar esta migration:
        --   sqlite3 selix.db ".schema commodities"  (num banco já populado)
        --   grep -rn "commodities" src/ confidence/ scripts/
        -- Schema abaixo inclui as duas colunas até confirmar; ajuste
        -- depois de checar.
        CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL,
            preco_usd REAL,
            tipo TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS empresas_rj (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nome TEXT,
            em_recuperacao_judicial INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS selic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fonte TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """,
    ),
]

# Dados de seed apenas para ambiente de teste/dev — nunca em produção real.
SEED_TEST_API_KEY = os.getenv("SELIX_SEED_TEST_KEY", "true").lower() == "true"


def already_applied(conn, version: int) -> bool:
    try:
        cur = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
        )
        return cur.fetchone() is not None
    except sqlite3.OperationalError:
        # schema_migrations ainda não existe (primeira execução)
        return False


def apply_migration(conn, version: int, description: str, sql: str):
    conn.executescript(sql)
    conn.execute(
        "INSERT OR IGNORE INTO schema_migrations (version, description, applied_at) VALUES (?, ?, ?)",
        (version, description, datetime.now().isoformat()),
    )
    conn.commit()
    print(f"  ✅ v{version}: {description}")


def seed_test_key(conn):
    """Insere a API key de teste padrão, com expires_at válido (não NULL)."""
    raw_key = "test_api_key_123"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    expires_at = (datetime.now() + timedelta(days=365)).isoformat()

    conn.execute(
        """
        INSERT OR IGNORE INTO api_keys
            (key_hash, client_name, plan, rate_limit_per_minute, expires_at, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
        """,
        (key_hash, "test-client", "pro", 1000, expires_at),
    )
    conn.commit()
    print(f"  ✅ Chave de teste inserida: {raw_key} (expira em {expires_at})")


def main():
    print(f"Migrando banco em: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    for version, description, sql in MIGRATIONS:
        if already_applied(conn, version):
            print(f"  ⏭  v{version} já aplicada, pulando")
            continue
        apply_migration(conn, version, description, sql)

    if SEED_TEST_API_KEY:
        seed_test_key(conn)

    conn.close()
    print(f"✅ Banco inicializado: {DB_PATH}")


if __name__ == "__main__":
    main()

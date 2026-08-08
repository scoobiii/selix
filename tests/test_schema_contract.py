"""tests/test_schema_contract.py

Testes escritos ANTES da correção do código (TDD) — definem o contrato
que confidence/calculator.py precisa cumprir.
"""

import os
import re
import sqlite3
import sys
import logging
import pytest

# Ajuste o import conforme a localização real do módulo no seu projeto.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Banco de teste isolado, populado com o schema que a migration
    consolidada declara como fonte de verdade."""
    db_path = tmp_path / "test_selix.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE indice_confianca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            fatores TEXT,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL,
            preco_usd REAL,
            tipo TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()
    conn.close()
    return str(db_path)


# ---------------------------------------------------------------------------
# CONTRATO 1 — DB_PATH deve ser configurável, não hardcoded
# ---------------------------------------------------------------------------

class TestDbPathConfiguravel:
    def test_calculator_respeita_env_var_selix_db_path(self, tmp_db, monkeypatch):
        import importlib
        import sys
        monkeypatch.setenv("SELIX_DB_PATH", tmp_db)
        # Força recarga do módulo para pegar a env var
        if 'confidence.calculator' in sys.modules:
            importlib.reload(sys.modules['confidence.calculator'])
        from confidence.calculator import SelixConfidenceCalculator
        calc = SelixConfidenceCalculator()
        try:
            actual_path = calc.conn.execute("PRAGMA database_list").fetchone()[2]
            assert actual_path == tmp_db, (
                f"Esperado conectar em {tmp_db}, mas conectou em {actual_path}. "
                "DB_PATH provavelmente ainda está hardcoded no módulo."
            )
        finally:
            calc.close()


# ---------------------------------------------------------------------------
# CONTRATO 2 — toda query SQL no código deve referenciar colunas que
# existem no schema real
# ---------------------------------------------------------------------------

class TestContratoDeSchema:
    def test_get_current_brent_nao_quebra_contra_schema_real(self, tmp_db, monkeypatch):
        import importlib
        import sys
        monkeypatch.setenv("SELIX_DB_PATH", tmp_db)
        # Força recarga do módulo para pegar a env var
        if 'confidence.calculator' in sys.modules:
            importlib.reload(sys.modules['confidence.calculator'])
        conn = sqlite3.connect(tmp_db)
        conn.execute(
            "INSERT INTO commodities (preco_usd, tipo) VALUES (91.2, 'brent')"
        )
        conn.commit()
        conn.close()

        from confidence.calculator import SelixConfidenceCalculator
        calc = SelixConfidenceCalculator()
        try:
            brent = calc.get_current_brent()
            assert brent == 91.2, (
                "get_current_brent() não retornou o valor real inserido — "
                "possível mismatch de coluna (preco_usd vs valor) ou "
                "DB_PATH hardcoded apontando para outro banco."
            )
        finally:
            calc.close()

    def test_todas_colunas_referenciadas_existem_no_schema(self, tmp_db):
        import confidence.calculator as calc_module

        source = open(calc_module.__file__, encoding="utf-8").read()

        select_pattern = re.compile(
            r"SELECT\s+([\w,\s]+?)\s+FROM\s+(\w+)", re.IGNORECASE
        )
        insert_pattern = re.compile(
            r"INSERT\s+INTO\s+(\w+)\s*\(([\w,\s]+)\)", re.IGNORECASE
        )

        conn = sqlite3.connect(tmp_db)
        problems = []

        for cols_raw, table in select_pattern.findall(source):
            cols = [c.strip() for c in cols_raw.split(",") if c.strip() != "*"]
            try:
                schema_cols = {
                    row[1] for row in conn.execute(f"PRAGMA table_info({table})")
                }
            except sqlite3.OperationalError:
                continue
            for col in cols:
                if col not in schema_cols and not col.isdigit():
                    problems.append(f"SELECT {col} FROM {table} — coluna não existe no schema")

        for table, cols_raw in insert_pattern.findall(source):
            cols = [c.strip() for c in cols_raw.split(",")]
            try:
                schema_cols = {
                    row[1] for row in conn.execute(f"PRAGMA table_info({table})")
                }
            except sqlite3.OperationalError:
                continue
            for col in cols:
                if col not in schema_cols:
                    problems.append(f"INSERT INTO {table}({col}) — coluna não existe no schema")

        conn.close()
        assert not problems, "Mismatch de schema encontrado:\n" + "\n".join(problems)


# ---------------------------------------------------------------------------
# CONTRATO 3 — fallbacks silenciosos devem ser observáveis (logados)
# ---------------------------------------------------------------------------

class TestFallbackObservavel:
    @pytest.mark.parametrize(
        "method_name",
        [
            "get_brent_volatility",
            "get_combustiveis_stability",
            "get_geopolitical_risk",
            "get_sentdex_score",
        ],
    )
    def test_fallback_gera_warning_logado(self, tmp_db, monkeypatch, caplog, method_name):
        monkeypatch.setenv("SELIX_DB_PATH", tmp_db)

        from confidence.calculator import SelixConfidenceCalculator
        calc = SelixConfidenceCalculator()
        try:
            monkeypatch.setattr(
                "requests.get", lambda *a, **k: (_ for _ in ()).throw(ConnectionError("sem rede"))
            )
            monkeypatch.setattr(
                "yfinance.Ticker",
                lambda *a, **k: (_ for _ in ()).throw(ConnectionError("sem rede")),
            )
            monkeypatch.setattr(
                "feedparser.parse",
                lambda *a, **k: (_ for _ in ()).throw(ConnectionError("sem rede")),
            )

            with caplog.at_level(logging.WARNING):
                getattr(calc, method_name)()

            assert any(
                record.levelno >= logging.WARNING for record in caplog.records
            ), (
                f"{method_name}() usou fallback silenciosamente (via print, "
                "não logging). Troque print() por logging.warning() para "
                "que falhas de rede sejam observáveis em produção."
            )
        finally:
            calc.close()


# ---------------------------------------------------------------------------
# CONTRATO 4 — calculate() deve persistir e retornar de forma consistente
# ---------------------------------------------------------------------------

class TestCalculateConsistencia:
    def test_calculate_grava_e_retorna_mesmo_valor(self, tmp_db, monkeypatch):
        monkeypatch.setenv("SELIX_DB_PATH", tmp_db)

        from confidence.calculator import SelixConfidenceCalculator
        calc = SelixConfidenceCalculator()
        try:
            conf, fatores = calc.calculate()
            assert 0 <= conf <= 100
            assert set(fatores.keys()) == {"vol", "stab", "geo", "sent", "mix", "brent"}

            row = calc.cursor.execute(
                "SELECT valor FROM indice_confianca ORDER BY id DESC LIMIT 1"
            ).fetchone()
            assert row is not None, "calculate() não persistiu em indice_confianca"
            assert abs(row[0] * 100 - conf) < 0.15
        finally:
            calc.close()

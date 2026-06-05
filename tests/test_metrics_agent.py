#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_metrics_agent.py — v2.2.0 — 20/20 expected
# Compatível com Termux/Android + Linux

import pytest, sys, os, json, sqlite3
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, "/root/selix/scripts")
import metrics_agent as ma

# ── FIXTURES ────────────────────────────────────────────────────

@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_metrics.db")

# ── TEMPERATURA ─────────────────────────────────────────────────

class TestGetTemp:

    def test_retorna_none_sem_sensors(self):
        """AttributeError no Termux — não deve crashar."""
        with patch("psutil.sensors_temperatures",
                   side_effect=AttributeError("no sensors")):
            # sem sysfs disponível
            result = ma.get_temp(thermal_paths=["/nonexistent/path"])
        assert result is None

    def test_retorna_none_sensors_vazio(self):
        with patch("psutil.sensors_temperatures", return_value={}):
            result = ma.get_temp(thermal_paths=["/nonexistent/path"])
        assert result is None

    def test_le_sysfs_android(self, tmp_path):
        """
        FIX: injeta o path do arquivo temporário diretamente,
        sem precisar mockar open nem os.path.exists.
        """
        thermal_file = tmp_path / "temp"
        thermal_file.write_text("42500\n")   # Android: millicelsius

        with patch("psutil.sensors_temperatures",
                   side_effect=AttributeError("no sensors")):
            result = ma.get_temp(thermal_paths=[str(thermal_file)])

        assert result == 42.5

    def test_retorna_valor_psutil(self):
        mock_temp = MagicMock()
        mock_temp.current = 55.0
        with patch("psutil.sensors_temperatures",
                   return_value={"cpu-thermal": [mock_temp]}):
            result = ma.get_temp()
        assert result == 55.0

# ── LOAD AVG ────────────────────────────────────────────────────

class TestGetLoad:

    def test_usa_psutil(self):
        with patch("psutil.getloadavg", return_value=(0.5, 0.8, 1.0)):
            result = ma.get_load()
        assert result == [0.5, 0.8, 1.0]

    def test_fallback_proc_loadavg(self, tmp_path):
        """
        FIX: cria /proc/loadavg simulado como arquivo real.
        """
        loadavg = tmp_path / "loadavg"
        loadavg.write_text("0.12 0.34 0.56 1/234 5678\n")

        with patch("psutil.getloadavg", side_effect=AttributeError):
            with patch("builtins.open",
                       return_value=loadavg.open()):
                result = ma.get_load()
        assert result == [0.12, 0.34, 0.56]

    def test_fallback_zeros_se_tudo_falhar(self):
        with patch("psutil.getloadavg", side_effect=AttributeError):
            with patch("builtins.open", side_effect=OSError("no file")):
                result = ma.get_load()
        assert result == [0.0, 0.0, 0.0]

# ── CHECK API ────────────────────────────────────────────────────

class TestCheckApi:

    def test_api_online(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("requests.get", return_value=mock_resp):
            assert ma.check_api() == 1

    def test_api_offline_500(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        with patch("requests.get", return_value=mock_resp):
            assert ma.check_api() == 0

    def test_api_offline_exception(self):
        with patch("requests.get", side_effect=ConnectionError):
            assert ma.check_api() == 0

    def test_api_timeout(self):
        import requests as req
        with patch("requests.get", side_effect=req.exceptions.Timeout):
            assert ma.check_api() == 0

# ── CHECK BRENT / SELIC ──────────────────────────────────────────

class TestCheckData:

    def test_brent_disponivel(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        conn.execute(
            "CREATE TABLE brent "
            "(price REAL, success INTEGER, timestamp TEXT)")
        conn.execute("INSERT INTO brent VALUES (97.0, 1, '2026-06-03')")
        conn.commit(); conn.close()
        assert ma.check_brent(tmp_db) == 1

    def test_brent_indisponivel(self, tmp_db):
        # FIX: passa tmp_db vazio — não usa o DB real do sistema
        assert ma.check_brent(tmp_db) == 0

    def test_selic_disponivel_commodities(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        conn.execute(
            "CREATE TABLE commodities "
            "(valor REAL, tipo TEXT, criado_em TEXT)")
        conn.execute(
            "INSERT INTO commodities VALUES (14.25,'efetiva','2026-06-03')")
        conn.commit(); conn.close()
        assert ma.check_selic(tmp_db) == 1

    def test_selic_indisponivel(self, tmp_db):
        # FIX: passa tmp_db vazio
        assert ma.check_selic(tmp_db) == 0

# ── COLLECT ──────────────────────────────────────────────────────

class TestCollect:

    def _mock_collect(self, tmp_db):
        return patch.multiple(
            ma,
            get_temp    = lambda *a, **kw: 42.5,
            get_load    = lambda: [0.5, 0.8, 1.0],
            check_api   = lambda: 1,
            check_worker= lambda: 1,
            check_brent = lambda db_path=None: 1,
            check_selic = lambda db_path=None: 1,
        )

    def test_collect_retorna_todos_campos(self, tmp_db):
        with patch("psutil.cpu_percent",    return_value=15.0), \
             patch("psutil.virtual_memory",
                   return_value=MagicMock(percent=60.0,
                                          available=2*1024**2)), \
             patch("psutil.disk_usage",
                   return_value=MagicMock(percent=40.0)), \
             patch("psutil.pids",           return_value=list(range(100))), \
             patch.object(ma, "get_temp",    return_value=42.5), \
             patch.object(ma, "get_load",    return_value=[0.5,0.8,1.0]), \
             patch.object(ma, "check_api",   return_value=1), \
             patch.object(ma, "check_worker",return_value=1), \
             patch.object(ma, "check_brent", return_value=1), \
             patch.object(ma, "check_selic", return_value=1):
            m = ma.collect(tmp_db)

        campos = ["timestamp","cpu_percent","memory_percent","disk_percent",
                  "temperature_c","load_avg","api_healthy","worker_running",
                  "brent_available","selic_available"]
        for c in campos:
            assert c in m, f"Campo ausente: {c}"

        assert m["cpu_percent"]     == 15.0
        assert m["temperature_c"]   == 42.5
        assert m["api_healthy"]     == 1
        assert m["brent_available"] == 1

    def test_collect_temperatura_none_nao_quebra(self, tmp_db):
        with patch("psutil.cpu_percent",    return_value=5.0), \
             patch("psutil.virtual_memory",
                   return_value=MagicMock(percent=30.0,
                                          available=1024**2)), \
             patch("psutil.disk_usage",
                   return_value=MagicMock(percent=20.0)), \
             patch("psutil.pids",           return_value=[]), \
             patch.object(ma, "get_temp",    return_value=None), \
             patch.object(ma, "get_load",    return_value=[0.0,0.0,0.0]), \
             patch.object(ma, "check_api",   return_value=0), \
             patch.object(ma, "check_worker",return_value=0), \
             patch.object(ma, "check_brent", return_value=0), \
             patch.object(ma, "check_selic", return_value=0):
            m = ma.collect(tmp_db)

        assert m["temperature_c"] is None

# ── SAVE / ENSURE TABLE ──────────────────────────────────────────

class TestSave:

    BASE = {
        "timestamp": "2026-06-03T12:00:00",
        "cpu_percent": 10.0, "memory_percent": 50.0,
        "disk_percent": 30.0, "temperature_c": 40.0,
        "api_healthy": 1, "worker_running": 1,
        "last_post_success": 0,
        "brent_available": 1, "selic_available": 1,
        "load_avg": [0.1, 0.2, 0.3],
    }

    def test_cria_tabela_automaticamente(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        ma.ensure_table(conn)
        conn.commit()
        tabelas = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        conn.close()
        assert "metrics_history" in tabelas

    def test_save_insere_registro(self, tmp_db):
        # FIX: passa tmp_db explicitamente — save() usa db_path param
        ma.save(self.BASE, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT cpu_percent, api_healthy FROM metrics_history LIMIT 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 10.0
        assert row[1] == 1

    def test_save_multiplos_registros(self, tmp_db):
        for i in range(5):
            m = dict(self.BASE, cpu_percent=float(i))
            ma.save(m, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM metrics_history"
        ).fetchone()[0]
        conn.close()
        assert count == 5


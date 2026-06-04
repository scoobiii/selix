#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# metrics_agent.py — v2.0.0-GOS3
# Coleta métricas do sistema + saúde dos serviços Selix

import os, sys, time, json, sqlite3, subprocess
import psutil, requests
from datetime import datetime

DB_PATH  = "/root/selix/selix.db"
LOG_DIR  = "/root/selix/logs"
API_URL  = "http://localhost:5000/v1/health"
INTERVAL = 60   # segundos entre coletas

os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def ensure_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metrics_history (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp        TEXT,
            cpu_percent      REAL,
            memory_percent   REAL,
            disk_percent     REAL,
            temperature_c    REAL,
            api_healthy      INTEGER,
            worker_running   INTEGER,
            last_post_success INTEGER,
            brent_available  INTEGER,
            selic_available  INTEGER,
            load_avg         TEXT,
            raw_json         TEXT
        )
    """)
    conn.commit()

def get_temp():
    try:
        temps = psutil.sensors_temperatures()
        for key in ('cpu-thermal', 'cpu_thermal', 'coretemp', 'k10temp'):
            if key in temps and temps[key]:
                return round(temps[key][0].current, 1)
    except Exception:
        pass
    return None

def check_api():
    try:
        r = requests.get(API_URL, timeout=3)
        return 1 if r.status_code == 200 else 0
    except Exception:
        return 0

def check_worker():
    for p in psutil.process_iter(['cmdline']):
        try:
            cmd = " ".join(p.info['cmdline'] or [])
            if "worker" in cmd and "python" in cmd:
                return 1
        except Exception:
            pass
    return 0

def check_brent():
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT price FROM brent WHERE success=1 "
            "ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return 1 if row else 0
    except Exception:
        return 0

def check_selic():
    try:
        conn = sqlite3.connect(DB_PATH)
        # tenta tabela commodities (worker atual)
        for sql in [
            "SELECT valor FROM commodities WHERE tipo='efetiva' ORDER BY criado_em DESC LIMIT 1",
            "SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1",
        ]:
            try:
                row = conn.execute(sql).fetchone()
                if row:
                    conn.close()
                    return 1
            except Exception:
                continue
        conn.close()
        return 0
    except Exception:
        return 0

def collect():
    vm   = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    load = psutil.getloadavg()

    metrics = {
        "timestamp":        datetime.now().isoformat(),
        "cpu_percent":      psutil.cpu_percent(interval=1),
        "cpu_per_core":     psutil.cpu_percent(percpu=True),
        "memory_percent":   round(vm.percent, 1),
        "memory_avail_mb":  vm.available // (1024**2),
        "disk_percent":     round(disk.percent, 1),
        "temperature_c":    get_temp(),
        "load_avg":         list(load),
        "process_count":    len(psutil.pids()),
        "api_healthy":      check_api(),
        "worker_running":   check_worker(),
        "brent_available":  check_brent(),
        "selic_available":  check_selic(),
        "last_post_success": 0,   # atualizado pelo campaign_supervisor
    }
    return metrics

def save(metrics):
    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)
    conn.execute("""
        INSERT INTO metrics_history
            (timestamp, cpu_percent, memory_percent, disk_percent,
             temperature_c, api_healthy, worker_running,
             last_post_success, brent_available, selic_available,
             load_avg, raw_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        metrics["timestamp"],
        metrics["cpu_percent"],
        metrics["memory_percent"],
        metrics["disk_percent"],
        metrics["temperature_c"],
        metrics["api_healthy"],
        metrics["worker_running"],
        metrics["last_post_success"],
        metrics["brent_available"],
        metrics["selic_available"],
        json.dumps(metrics["load_avg"]),
        json.dumps(metrics),
    ))
    conn.commit()
    conn.close()

def main():
    log("metrics_agent v2.0.0 iniciado")
    while True:
        try:
            m = collect()
            save(m)
            status = (
                f"cpu={m['cpu_percent']}% "
                f"mem={m['memory_percent']}% "
                f"api={'✅' if m['api_healthy'] else '❌'} "
                f"worker={'✅' if m['worker_running'] else '❌'} "
                f"brent={'✅' if m['brent_available'] else '❌'} "
                f"selic={'✅' if m['selic_available'] else '❌'}"
            )
            log(status)
        except Exception as e:
            log(f"❌ Erro: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

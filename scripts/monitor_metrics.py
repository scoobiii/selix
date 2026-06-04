#!/usr/bin/env python3
import psutil, json, time, sqlite3
from datetime import datetime

DB_PATH = "/root/selix/selix.db"

def collect_metrics():
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_per_core": psutil.cpu_percent(percpu=True),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_mb": psutil.virtual_memory().available // (1024**2),
        "swap_percent": psutil.swap_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "load_avg": psutil.getloadavg(),
        "temperature_c": None,
        "process_count": len(psutil.pids())
    }
    temps = psutil.sensors_temperatures().get('cpu-thermal', [])
    if temps:
        metrics["temperature_c"] = temps[0].current
    return metrics

def save_metrics():
    metrics = collect_metrics()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            timestamp TEXT,
            cpu_percent REAL,
            memory_percent REAL,
            temperature_c REAL,
            load_avg TEXT,
            disk_percent REAL
        )
    """)
    conn.execute("INSERT INTO system_metrics VALUES (?, ?, ?, ?, ?, ?)",
                 (metrics["timestamp"], metrics["cpu_percent"], metrics["memory_percent"],
                  metrics["temperature_c"], json.dumps(metrics["load_avg"]), metrics["disk_percent"]))
    conn.commit()
    conn.close()
    print(f"Metrics saved at {metrics['timestamp']}")

if __name__ == "__main__":
    save_metrics()

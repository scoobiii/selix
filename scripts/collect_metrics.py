#!/usr/bin/env python3
import sqlite3
import requests
from datetime import date

DB_PATH = "/root/selix/selix.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def collect_investor_metrics():
    conn = get_db()
    cur = conn.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1 AND plan IN ('pro','enterprise')")
    clientes = cur.fetchone()[0]
    cur = conn.execute("SELECT SUM(CASE plan WHEN 'pro' THEN 99 WHEN 'enterprise' THEN 999 ELSE 0 END) FROM api_keys WHERE is_active = 1")
    mrr = cur.fetchone()[0] or 0
    conn.close()
    return clientes, mrr

def collect_environmental_metrics():
    # TODO: calcular CO₂ evitado com base no mix E/B (simulação)
    # Você pode usar a lógica do Energy Predictor para estimar
    return 200_000_000  # placeholder

def collect_worker_metrics():
    # Conta posts no Bluesky com #PLR (precisa da API)
    # Placeholder – integre com a API do Bluesky depois
    return 42

def main():
    today = date.today().isoformat()
    conn = get_db()
    clientes, mrr = collect_investor_metrics()
    conn.execute("INSERT INTO metricas_reais (segmento, indicador, valor, data_coleta) VALUES (?,?,?,?)",
                 ('investidores', 'clientes_pagos', clientes, today))
    conn.execute("INSERT INTO metricas_reais (segmento, indicador, valor, data_coleta) VALUES (?,?,?,?)",
                 ('investidores', 'receita_mensal_mrr', mrr, today))
    co2 = collect_environmental_metrics()
    conn.execute("INSERT INTO metricas_reais (segmento, indicador, valor, data_coleta) VALUES (?,?,?,?)",
                 ('ambientalistas', 'co2_evitado_ton', co2, today))
    posts = collect_worker_metrics()
    conn.execute("INSERT INTO metricas_reais (segmento, indicador, valor, data_coleta) VALUES (?,?,?,?)",
                 ('trabalhadores', 'posts_plr', posts, today))
    conn.commit()
    conn.close()
    print(f"Métricas coletadas para {today}")

if __name__ == "__main__":
    main()

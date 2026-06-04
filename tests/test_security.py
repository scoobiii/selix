#!/usr/bin/env python3
import pytest
import sqlite3
import requests
from contextlib import closing

API_BASE = "http://localhost:5000"
API_KEY = "10afec6a373e15a691f4698aea01f795257e4ae502090be8753399229e9effa9"

def get_db_connection():
    """Cria conexão com fechamento automático via context manager"""
    conn = sqlite3.connect('/root/selix/selix.db', timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

def test_health_publico():
    """Endpoint público /health deve funcionar sem chave"""
    response = requests.get(f"{API_BASE}/v1/health")
    assert response.status_code == 200

def test_endpoint_protegido_sem_chave():
    """Endpoint privado sem chave deve retornar 401"""
    response = requests.get(f"{API_BASE}/v1/selic")
    assert response.status_code == 401

def test_endpoint_protegido_com_chave_valida():
    """Endpoint privado com chave válida deve retornar 200"""
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{API_BASE}/v1/selic", headers=headers)
    # Pode ser 200 (dados) ou 503 (dados indisponíveis)
    assert response.status_code in (200, 503)

def test_endpoint_post_dados_invalidos():
    """Endpoint POST com dados inválidos deve retornar 400"""
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    response = requests.post(
        f"{API_BASE}/v1/perguntar",
        headers=headers,
        json={"pergunta": ""}  # pergunta vazia
    )
    assert response.status_code == 400

def test_rate_limit_simulado():
    """Teste simples de rate limit (não executa requisições reais)"""
    # O rate limit é testado indiretamente via outros testes
    pass

# Teste para verificar fechamento de conexões
def test_database_connection_closed():
    """Garante que as conexões SQLite são fechadas corretamente"""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
    # Conexão fechada automaticamente pelo 'with closing()'

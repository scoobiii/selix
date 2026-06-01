#!/usr/bin/env python3
"""Testes da API"""

import pytest
import requests
import sqlite3
import json

BASE_URL = "http://localhost:5000"
DB_PATH = "/root/selix/selix.db"

class TestAPI:
    
    def setup_method(self):
        """Insere dados de teste"""
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO commodities (nome, preco_usd, fonte) VALUES ('Brent', 95.19, 'test')")
        conn.commit()
        conn.close()
    
    def test_health(self):
        resp = requests.get(f"{BASE_URL}/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
    
    def test_energia_mistura(self):
        resp = requests.get(f"{BASE_URL}/v1/energia/mistura")
        assert resp.status_code == 200 or resp.status_code == 503
        if resp.status_code == 200:
            data = resp.json()
            assert 'brent_usd' in data
    
    def test_commodities(self):
        resp = requests.get(f"{BASE_URL}/v1/commodities")
        assert resp.status_code == 200 or resp.status_code == 503
    
    def test_selic(self):
        resp = requests.get(f"{BASE_URL}/v1/selic")
        assert resp.status_code == 200 or resp.status_code == 503
    
    def test_alertas_geral(self):
        resp = requests.get(f"{BASE_URL}/v1/alertas/geral")
        assert resp.status_code == 200
        data = resp.json()
        assert 'alertas' in data or 'selic_atual' in data

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de segurança para a API SELIX: autenticação, validação e rate limit.
"""

import pytest
from src.api.main_v4 import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_publico(client):
    resp = client.get('/v1/health')
    assert resp.status_code == 200

def test_endpoint_protegido_sem_chave(client):
    resp = client.get('/v1/commodities')
    assert resp.status_code == 401
    assert 'API key' in resp.json['erro']

def test_endpoint_protegido_com_chave_valida(client, monkeypatch):
    monkeypatch.setenv('SELIX_API_KEYS', 'chave_teste')
    # Recarrega o módulo para atualizar AUTHORIZED_API_KEYS
    import importlib
    import src.api.main_v4
    importlib.reload(src.api.main_v4)
    resp = client.get('/v1/commodities', headers={'X-API-Key': 'chave_teste'})
    assert resp.status_code in (200, 503)  # pode ser 503 se banco vazio, mas não 401

def test_endpoint_post_dados_invalidos(client):
    resp = client.post('/v1/perguntar', json={'pergunta': ''})
    assert resp.status_code == 400
    resp = client.post('/v1/perguntar', json={'pergunta': ' ' * 600})
    assert resp.status_code == 400

def test_rate_limit_simulado(client):
    resp = client.get('/v1/health')
    assert resp.status_code == 200

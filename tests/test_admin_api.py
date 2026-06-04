#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_admin_api.py
# Testes para endpoints administrativos da API (gerar/revogar chaves)

import pytest
from unittest.mock import patch, MagicMock
from src.api.main_v4 import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_admin_generate_key_without_master(client):
    resp = client.post('/v1/admin/generate_key', json={'client_name': 'test'})
    assert resp.status_code == 403
    assert 'acesso administrativo' in resp.json['erro'].lower()

def test_admin_generate_key_with_master(client):
    with patch('src.api.main_v4.create_api_key') as mock_create:
        mock_create.return_value = {'api_key': 'selix_test', 'client_name': 'test'}
        headers = {'X-Admin-Key': 'master_123_super_secret'}
        resp = client.post('/v1/admin/generate_key', headers=headers, json={'client_name': 'test', 'plan': 'pro', 'days_valid': 30})
        assert resp.status_code == 201
        assert 'api_key' in resp.json

def test_admin_list_keys_without_master(client):
    resp = client.get('/v1/admin/list_keys')
    assert resp.status_code == 403

def test_admin_list_keys_with_master(client):
    with patch('src.api.main_v4.get_db') as mock_db:
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.execute.return_value
        mock_cursor.fetchall.return_value = [{'id': 1, 'client_name': 'test', 'plan': 'free'}]
        headers = {'X-Admin-Key': 'master_123_super_secret'}
        resp = client.get('/v1/admin/list_keys', headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json, list)

def test_admin_revoke_key(client):
    with patch('src.api.main_v4.get_db') as mock_db:
        mock_conn = mock_db.return_value
        headers = {'X-Admin-Key': 'master_123_super_secret'}
        resp = client.post('/v1/admin/revoke_key', headers=headers, json={'key_hash': 'abc'})
        assert resp.status_code == 200
        assert 'revogada' in resp.json['mensagem']

def test_admin_renew_key(client):
    with patch('src.api.main_v4.get_db') as mock_db:
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.execute.return_value
        mock_cursor.fetchone.return_value = {'expires_at': '2026-01-01T00:00:00'}
        headers = {'X-Admin-Key': 'master_123_super_secret'}
        resp = client.post('/v1/admin/renew_key', headers=headers, json={'key_hash': 'abc', 'extra_days': 30})
        assert resp.status_code == 200
        assert 'validade estendida' in resp.json['mensagem'].lower()

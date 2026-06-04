#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_key_manager.py
# Testes para funções de gerenciamento de chaves

import pytest
from unittest.mock import patch, MagicMock
from src.api.key_manager import hash_key, verify_api_key

def test_hash_key():
    raw = "test-key"
    hashed = hash_key(raw)
    assert isinstance(hashed, str)
    assert len(hashed) == 64
    assert hash_key(raw) == hashed

@patch('src.api.key_manager.sqlite3.connect')
def test_verify_api_key_valid(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        'client_id': 1, 'plan': 'pro', 'rate_limit_per_minute': 60,
        'expires_at': '2099-12-31T23:59:59', 'is_active': 1
    }
    mock_conn.execute.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    result = verify_api_key("any_key")
    assert result is not None
    assert result['plan'] == 'pro'

@patch('src.api.key_manager.sqlite3.connect')
def test_verify_api_key_invalid(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.execute.return_value
    mock_cursor.fetchone.return_value = None
    mock_connect.return_value = mock_conn
    result = verify_api_key("invalid")
    assert result is None

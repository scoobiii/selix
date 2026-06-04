#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_worker.py
# Testes para worker_v7.py (funções auxiliares)

import pytest
from unittest.mock import patch, MagicMock
import worker_v7 as worker

def test_get_last_selic_from_db_with_data():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (14.25,)
    mock_conn.execute.return_value = mock_cursor
    with patch('sqlite3.connect', return_value=mock_conn):
        result = worker.get_last_selic_from_db()
        assert result == 14.25

def test_get_last_selic_from_db_no_data():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.execute.return_value = mock_cursor
    with patch('sqlite3.connect', return_value=mock_conn):
        result = worker.get_last_selic_from_db()
        assert result is None

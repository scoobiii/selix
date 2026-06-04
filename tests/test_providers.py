#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_providers.py
# Testes para provedores (Yahoo, BCB, Circuit Breaker, Strategy)

import pandas as pd
from unittest.mock import patch, MagicMock
import pytest
from src.providers.yahoo_provider import YahooFinanceProvider
from src.providers.bcb_provider import BCBProvider
from src.providers.circuit_breaker import CircuitBreaker
from src.providers.strategy import ProviderStrategy

# ------------------------------------------------------------------
# YahooFinanceProvider
# ------------------------------------------------------------------

import pandas as pd
from unittest.mock import patch, MagicMock
from src.providers.yahoo_provider import YahooFinanceProvider

def test_yahoo_brent_success():
    with patch('src.providers.yahoo_provider.yf.Ticker') as mock_ticker:
        mock_instance = MagicMock()
        # Cria um DataFrame com uma única linha e coluna 'Close'
        df = pd.DataFrame({'Close': [95.09]})
        mock_instance.history.return_value = df
        mock_ticker.return_value = mock_instance
        provider = YahooFinanceProvider()
        result = provider.get_brent()
        assert result['success'] is True
        assert result['price'] == 95.09
        assert result['source'] == 'Yahoo'


def test_yahoo_brent_empty_data():
    with patch('src.providers.yahoo_provider.yf.Ticker') as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.history.return_value = {}
        mock_ticker.return_value = mock_instance
        provider = YahooFinanceProvider()
        result = provider.get_brent()
        assert result['success'] is False

def test_yahoo_brent_exception():
    with patch('src.providers.yahoo_provider.yf.Ticker', side_effect=Exception("Network error")):
        provider = YahooFinanceProvider()
        result = provider.get_brent()
        assert result['success'] is False
        assert "Network error" in result.get('error', '')

# ------------------------------------------------------------------
# BCBProvider
# ------------------------------------------------------------------
def test_bcb_selic_success():
    with patch('src.providers.bcb_provider.requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{'valor': '14.25'}]
        mock_get.return_value = mock_resp
        provider = BCBProvider()
        result = provider.get_selic()
        assert result['success'] is True
        assert result['rate'] == 14.25
        assert result['source'] == 'BCB'

def test_bcb_selic_failure():
    with patch('src.providers.bcb_provider.requests.get', side_effect=Exception("Timeout")):
        provider = BCBProvider()
        result = provider.get_selic()
        assert result['success'] is False
        assert result['source'] == 'BCB'

# ------------------------------------------------------------------
# CircuitBreaker
# ------------------------------------------------------------------
def test_circuit_breaker_closed():
    cb = CircuitBreaker(failure_threshold=2, timeout=10)
    func = MagicMock(return_value={'success': True})
    result = cb.call(func)
    assert result['success'] is True
    assert cb.failure_count == 0

def test_circuit_breaker_open_after_failures():
    cb = CircuitBreaker(failure_threshold=2, timeout=10)
    func = MagicMock(return_value={'success': False})
    result = cb.call(func)
    assert result['success'] is False
    assert cb.failure_count == 1
    result = cb.call(func)
    assert result['success'] is False
    assert cb.failure_count == 2
    result = cb.call(func)
    assert result['success'] is False
    assert result['error'] == 'circuit open'
    assert func.call_count == 2

# ------------------------------------------------------------------
# ProviderStrategy
# ------------------------------------------------------------------
def test_strategy_brent_first_provider_works():
    with patch('src.providers.strategy.YahooFinanceProvider') as MockYahoo:
        mock_yahoo = MockYahoo.return_value
        mock_yahoo.get_brent.return_value = {'success': True, 'price': 95.0, 'source': 'Yahoo'}
        strategy = ProviderStrategy()
        strategy.brent_providers = [mock_yahoo]
        result = strategy.get_brent()
        assert result['success'] is True
        assert result['price'] == 95.0

def test_strategy_brent_all_fail():
    with patch('src.providers.strategy.YahooFinanceProvider') as MockYahoo:
        mock_yahoo = MockYahoo.return_value
        mock_yahoo.get_brent.return_value = {'success': False}
        strategy = ProviderStrategy()
        strategy.brent_providers = [mock_yahoo]
        result = strategy.get_brent()
        assert result['success'] is False
        assert 'Todas as fontes' in result['error']

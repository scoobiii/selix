#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# yahoo_provider.py
# Versão: 2.0.0-GOS3
# Responsabilidade: Coleta preço do Brent via Yahoo Finance (yfinance)
# Assinatura: GOS3/2026-06-04/src/providers/yahoo_provider.py

import yfinance as yf
from .base_provider import DataProvider

class YahooFinanceProvider(DataProvider):
    """Provedor que utiliza a biblioteca yfinance para obter o Brent."""

    def get_brent(self) -> dict:
        try:
            ticker = yf.Ticker("BZ=F")
            data = ticker.history(period="1d")
            if data.empty:
                return {'success': False, 'source': 'Yahoo', 'error': 'Dados vazios'}
            price = float(data['Close'].iloc[-1])
            return {'success': True, 'price': round(price, 2), 'source': 'Yahoo'}
        except Exception as e:
            return {'success': False, 'source': 'Yahoo', 'error': str(e)}

    def get_selic(self) -> dict:
        # Yahoo não fornece Selic
        return {'success': False, 'source': 'Yahoo'}

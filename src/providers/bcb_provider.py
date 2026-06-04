#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# bcb_provider.py
# Versão: 1.0.0-GOS3
# Responsabilidade: Coleta taxa Selic via API do Banco Central do Brasil
# Assinatura: GOS3/2026-06-04/src/providers/bcb_provider.py

import requests
from .base_provider import DataProvider

class BCBProvider(DataProvider):
    """Obtém a Selic oficial do BCB."""

    def get_brent(self) -> dict:
        return {'success': False, 'source': 'BCB'}

    def get_selic(self) -> dict:
        try:
            url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimo"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                rate = float(resp.json()[0]['valor'])
                return {'success': True, 'rate': rate, 'source': 'BCB'}
        except Exception:
            pass
        return {'success': False, 'source': 'BCB'}

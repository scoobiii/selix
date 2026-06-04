#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# strategy.py
# Versão: 1.0.0-GOS3
# Responsabilidade: Orquestra múltiplos provedores (Strategy Pattern)
# Assinatura: GOS3/2026-06-04/src/providers/strategy.py

from .yahoo_provider import YahooFinanceProvider
from .bcb_provider import BCBProvider
from .circuit_breaker import CircuitBreaker

class ProviderStrategy:
    """Gerencia a cadeia de provedores para Brent e Selic."""

    def __init__(self):
        # Provedores para Brent (ordem de prioridade)
        self.brent_providers = [
            YahooFinanceProvider(),   # primário
            # AlphaVantageProvider()  # pode ser adicionado depois
        ]
        # Provedores para Selic
        self.selic_providers = [
            BCBProvider(),
        ]
        # Circuit breakers individuais
        self.circuits = {}

    def get_brent(self) -> dict:
        for provider in self.brent_providers:
            source = provider.__class__.__name__
            if source not in self.circuits:
                self.circuits[source] = CircuitBreaker(failure_threshold=2, timeout=120)
            result = self.circuits[source].call(provider.get_brent)
            if result.get('success'):
                return result
        return {'success': False, 'error': 'Todas as fontes de Brent falharam', 'source': 'none'}

    def get_selic(self) -> dict:
        for provider in self.selic_providers:
            source = provider.__class__.__name__
            if source not in self.circuits:
                self.circuits[source] = CircuitBreaker(failure_threshold=2, timeout=120)
            result = self.circuits[source].call(provider.get_selic)
            if result.get('success'):
                return result
        return {'success': False, 'error': 'Todas as fontes de Selic falharam', 'source': 'none'}

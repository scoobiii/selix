#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# circuit_breaker.py
# Versão: 1.0.0-GOS3
# Responsabilidade: Evita tentativas repetidas em provedores com falha
# Assinatura: GOS3/2026-06-04/src/providers/circuit_breaker.py

import time

class CircuitBreaker:
    """Implementação simples de Circuit Breaker para provedores de dados."""

    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = 0

    def call(self, func, *args, **kwargs) -> dict:
        """
        Executa a função se o circuito estiver fechado.
        Retorna dicionário {'success': bool, ...}
        """
        if self.failure_count >= self.failure_threshold and (time.time() - self.last_failure_time) < self.timeout:
            return {'success': False, 'error': 'circuit open', 'source': 'circuit'}
        result = func(*args, **kwargs)
        if result.get('success'):
            self.failure_count = 0
            return result
        else:
            self.failure_count += 1
            self.last_failure_time = time.time()
            return result

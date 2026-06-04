#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# base_provider.py
# Versão: 1.0.0-GOS3
# Responsabilidade: Interface abstrata para todos os provedores de dados
# Assinatura: GOS3/2026-06-04/src/providers/base_provider.py

from abc import ABC, abstractmethod

class DataProvider(ABC):
    """Contrato que todos os provedores de dados devem seguir."""

    @abstractmethod
    def get_brent(self) -> dict:
        """
        Retorna preço do petróleo Brent.
        Estrutura de retorno: {'success': bool, 'price': float, 'source': str, 'error': str (opcional)}
        """
        pass

    @abstractmethod
    def get_selic(self) -> dict:
        """
        Retorna taxa Selic.
        Estrutura: {'success': bool, 'rate': float, 'source': str}
        """
        pass

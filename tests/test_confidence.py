#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do módulo de confiança"""

import pytest
import sys
sys.path.insert(0, '/root/selix')
from confidence.calculator import SelixConfidenceCalculator

class TestConfidenceCalculator:
    
    def test_confidence_range(self):
        calc = SelixConfidenceCalculator()
        conf, _ = calc.calculate()
        assert 0 <= conf <= 100
        calc.close()
    
    def test_confidence_components(self):
        calc = SelixConfidenceCalculator()
        conf, fatores = calc.calculate()
        assert 'vol' in fatores
        assert 'stab' in fatores
        assert 'geo' in fatores
        assert 'sent' in fatores
        assert 'brent' in fatores
        calc.close()
    
    def test_brent_fallback(self):
        calc = SelixConfidenceCalculator()
        brent = calc.get_current_brent()
        assert 40 <= brent <= 150
        calc.close()

#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/selix')
from src.selix.energy_predictor import EnergyPredictor

def test_get_mistura_e():
    # Faixas de Brent
    assert EnergyPredictor.get_mistura_e(60) == "E27"
    assert EnergyPredictor.get_mistura_e(80) == "E30"
    assert EnergyPredictor.get_mistura_e(100) == "E35"
    assert EnergyPredictor.get_mistura_e(130) == "E40"
    assert EnergyPredictor.get_mistura_e(200) == "E42"

def test_get_mistura_b():
    assert EnergyPredictor.get_mistura_b(60) == "B14"
    assert EnergyPredictor.get_mistura_b(80) == "B15"
    assert EnergyPredictor.get_mistura_b(100) == "B20"
    assert EnergyPredictor.get_mistura_b(130) == "B25"
    assert EnergyPredictor.get_mistura_b(200) == "B25"

def test_get_geracao_termica():
    res = EnergyPredictor.get_geracao_termica(60)
    assert res['status'] == "DESLIGADAS"
    res = EnergyPredictor.get_geracao_termica(95)
    assert res['status'] == "ACIONAMENTO MÍNIMO"
    res = EnergyPredictor.get_geracao_termica(130)
    assert res['status'] == "ACIONAMENTO PARCIAL"
    res = EnergyPredictor.get_geracao_termica(200)
    assert res['status'] == "ACIONAMENTO TOTAL"

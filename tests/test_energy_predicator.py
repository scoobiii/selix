#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/selix')
from src.selix.energy_predictor import EnergyPredictor

def test_get_mistura_e():
    # Valores reais baseados nos gatilhos do Energy Predictor
    assert EnergyPredictor.get_mistura_e(60)["mistura"] == "E27"
    assert EnergyPredictor.get_mistura_e(80)["mistura"] == "E27"
    assert EnergyPredictor.get_mistura_e(90)["mistura"] == "E27"   # ainda E27 até 90
    assert EnergyPredictor.get_mistura_e(91)["mistura"] == "E30"
    assert EnergyPredictor.get_mistura_e(100)["mistura"] == "E35"
    assert EnergyPredictor.get_mistura_e(120)["mistura"] == "E35"
    assert EnergyPredictor.get_mistura_e(150)["mistura"] == "E40"
    assert EnergyPredictor.get_mistura_e(200)["mistura"] == "E42"

def test_get_mistura_b():
    assert EnergyPredictor.get_mistura_b(60)["mistura"] == "B14"
    assert EnergyPredictor.get_mistura_b(80)["mistura"] == "B14"
    assert EnergyPredictor.get_mistura_b(90)["mistura"] == "B14"   # ainda B14 até 90
    assert EnergyPredictor.get_mistura_b(91)["mistura"] == "B15"
    assert EnergyPredictor.get_mistura_b(100)["mistura"] == "B20"
    assert EnergyPredictor.get_mistura_b(120)["mistura"] == "B20"
    assert EnergyPredictor.get_mistura_b(150)["mistura"] == "B25"
    assert EnergyPredictor.get_mistura_b(200)["mistura"] == "B25"

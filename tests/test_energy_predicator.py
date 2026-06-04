#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_energy_predicator.py
# Testes unitários para o Energy Predictor

import pytest
from src.selix.energy_predictor import EnergyPredictor


def test_get_mistura_e():
    """Testa os gatilhos de mistura de etanol"""
    # Casos normais (limites inclusivos)
    assert EnergyPredictor.get_mistura_e(0)["mistura"] == "E27"      # limite 0
    assert EnergyPredictor.get_mistura_e(50)["mistura"] == "E27"
    assert EnergyPredictor.get_mistura_e(89)["mistura"] == "E27"
    
    # Alerta (>=90)
    assert EnergyPredictor.get_mistura_e(90)["mistura"] == "E30"
    assert EnergyPredictor.get_mistura_e(95)["mistura"] == "E30"
    assert EnergyPredictor.get_mistura_e(119)["mistura"] == "E30"
    
    # Crise (>=120)
    assert EnergyPredictor.get_mistura_e(120)["mistura"] == "E35"
    assert EnergyPredictor.get_mistura_e(130)["mistura"] == "E35"
    assert EnergyPredictor.get_mistura_e(149)["mistura"] == "E35"
    
    # Emergência (>=150)
    assert EnergyPredictor.get_mistura_e(150)["mistura"] == "E40"
    assert EnergyPredictor.get_mistura_e(160)["mistura"] == "E40"
    assert EnergyPredictor.get_mistura_e(199)["mistura"] == "E40"
    
    # Emergência máxima (>=200)
    assert EnergyPredictor.get_mistura_e(200)["mistura"] == "E42"
    assert EnergyPredictor.get_mistura_e(250)["mistura"] == "E42"


def test_get_mistura_b():
    """Testa os gatilhos de mistura de biodiesel"""
    assert EnergyPredictor.get_mistura_b(0)["mistura"] == "B14"
    assert EnergyPredictor.get_mistura_b(50)["mistura"] == "B14"
    assert EnergyPredictor.get_mistura_b(89)["mistura"] == "B14"
    
    assert EnergyPredictor.get_mistura_b(90)["mistura"] == "B15"
    assert EnergyPredictor.get_mistura_b(95)["mistura"] == "B15"
    assert EnergyPredictor.get_mistura_b(119)["mistura"] == "B15"
    
    assert EnergyPredictor.get_mistura_b(120)["mistura"] == "B20"
    assert EnergyPredictor.get_mistura_b(130)["mistura"] == "B20"
    assert EnergyPredictor.get_mistura_b(149)["mistura"] == "B20"
    
    assert EnergyPredictor.get_mistura_b(150)["mistura"] == "B22"
    assert EnergyPredictor.get_mistura_b(160)["mistura"] == "B22"
    assert EnergyPredictor.get_mistura_b(199)["mistura"] == "B22"
    
    assert EnergyPredictor.get_mistura_b(200)["mistura"] == "B25"
    assert EnergyPredictor.get_mistura_b(250)["mistura"] == "B25"


def test_get_geracao_termica():
    """Testa o acionamento de termelétricas"""
    assert EnergyPredictor.get_geracao_termica(50)["status"] == "DESLIGADAS"
    assert EnergyPredictor.get_geracao_termica(95)["status"] == "ACIONAMENTO MÍNIMO"
    assert EnergyPredictor.get_geracao_termica(130)["status"] == "ACIONAMENTO PARCIAL"
    assert EnergyPredictor.get_geracao_termica(160)["status"] == "ACIONAMENTO TOTAL"
    assert EnergyPredictor.get_geracao_termica(200)["status"] == "ACIONAMENTO TOTAL"


def test_get_mistura_e_invalido():
    """Testa comportamento com entrada inválida (não numérica)"""
    with pytest.raises(TypeError):
        EnergyPredictor.get_mistura_e("texto")
    with pytest.raises(TypeError):
        EnergyPredictor.get_mistura_b(None)

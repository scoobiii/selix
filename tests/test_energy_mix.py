import pytest
from src.selix.core import (
    EnergyMix,
    calcular_tau,
    calcular_selix,
    SelixInputs,
    BASELINE_ATUAL,
)

def test_tau_atual():
    mix = EnergyMix(32.0, 15.0)
    tau = calcular_tau(mix)
    assert tau == pytest.approx(0.7786, abs=0.0001)

def test_tau_futuro():
    mix = EnergyMix(35.0, 20.0)
    tau = calcular_tau(mix)
    assert tau == pytest.approx(0.737, abs=0.001)

def test_tau_limites():
    mix_100 = EnergyMix(100.0, 100.0)
    assert calcular_tau(mix_100) == 0.0
    mix_0 = EnergyMix(0.0, 0.0)
    assert calcular_tau(mix_0) == 1.0

def test_choque_aumenta_juro_real():
    inputs = SelixInputs(4.48, 1.25, 0.50, 0.50)
    mix = EnergyMix(32.0, 15.0)
    r0 = calcular_selix(inputs, mix=mix, choque_energia=0.0)
    r1 = calcular_selix(inputs, mix=mix, choque_energia=0.50)
    assert r1["juro_real_necessario"] > r0["juro_real_necessario"]

def test_maior_mistura_reduz_impacto_choque():
    inputs = SelixInputs(4.48, 1.25, 0.50, 0.50)
    mix_baixo = EnergyMix(32.0, 15.0)
    mix_alto = EnergyMix(35.0, 20.0)
    r_baixo = calcular_selix(inputs, mix=mix_baixo, choque_energia=0.50)
    r_alto = calcular_selix(inputs, mix=mix_alto, choque_energia=0.50)
    assert r_alto["inflacao_efetiva"] < r_baixo["inflacao_efetiva"]

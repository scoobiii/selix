#!/usr/bin/env python3
"""
Testes adicionais para core.py — SELIX
"""

import pytest
from src.selix.core import (
    SelixInputs,
    calcular_juro_real_necessario,
    calcular_selix,
    quantizar_copom,
    BASELINE_ATUAL,
)


def test_baseline_nao_muda_sem_aviso():
    """Trava: se o baseline mudar, o teste quebra e força revisão."""
    assert BASELINE_ATUAL.inflacao_esperada == 4.48
    assert BASELINE_ATUAL.premio_risco == 1.25
    assert BASELINE_ATUAL.credibilidade == 0.35
    assert BASELINE_ATUAL.gap_produto == 0.50


def test_cenarios_alternativos():
    """Testa diferentes cenários de credibilidade e gap"""
    cenarios = [
        (SelixInputs(4.48, 1.25, 0.30, 0.50), "credibilidade baixa"),
        (SelixInputs(4.48, 1.25, 0.70, 0.50), "credibilidade media"),
        (SelixInputs(4.48, 1.25, 0.95, 0.50), "credibilidade alta"),
    ]
    for inputs, _ in cenarios:
        r = calcular_juro_real_necessario(inputs)
        assert r > 0


def test_selic_quantizada_sempre_multiplo_025():
    for i in range(100):
        valor = 5.0 + i * 0.07
        q = quantizar_copom(valor)
        assert (q * 100) % 25 == 0


def test_diferencial_negativo_quando_selic_abaixo_do_ideal():
    r = calcular_selix(BASELINE_ATUAL, selic_atual=5.0)
    assert r["diferencial_pp"] < 0


def test_gap_produto_afeta_juro_real():
    base = SelixInputs(4.48, 1.25, 0.50, 0.50)
    gap_negativo = SelixInputs(4.48, 1.25, 0.50, -0.50)
    assert calcular_juro_real_necessario(gap_negativo) < calcular_juro_real_necessario(base)

#!/usr/bin/env python3
"""
Testes para core.py — SELIX (baseline macro, 4 inputs).

Rodar: pytest test_core.py -v
"""

import pytest
from src.selix.core import (
    SelixInputs,
    calcular_juro_real_necessario,
    calcular_selix,
    quantizar_copom,
    BASELINE_ATUAL,
)


class TestQuantizacaoCopom:
    def test_quantiza_para_baixo_ao_grid(self):
        # 7.23 -> 28.92 passos de 0.25 -> floor 28 -> 7.00
        assert quantizar_copom(7.23) == 7.00

    def test_valor_ja_no_grid_nao_muda(self):
        assert quantizar_copom(14.25) == 14.25

    def test_grid_customizado(self):
        assert quantizar_copom(7.23, grid=0.5) == 7.00
        assert quantizar_copom(7.60, grid=0.5) == 7.50


class TestFormulaJuroReal:
    def test_formula_baseline_atual(self):
        # inflacao=4.48, premio=1.25, cred=0.50, gap=0.50
        # 4.48 + (1.25/0.50) + 0.5*0.50 = 4.48 + 2.50 + 0.25 = 7.23
        resultado = calcular_juro_real_necessario(BASELINE_ATUAL)
        assert resultado == pytest.approx(8.30, abs=0.01)

    def test_credibilidade_zero_levanta_erro(self):
        inputs = SelixInputs(
            inflacao_esperada=4.48, premio_risco=1.25,
            credibilidade=0.0, gap_produto=0.50,
        )
        with pytest.raises(ValueError):
            calcular_juro_real_necessario(inputs)

    def test_credibilidade_negativa_levanta_erro(self):
        inputs = SelixInputs(
            inflacao_esperada=4.48, premio_risco=1.25,
            credibilidade=-0.1, gap_produto=0.50,
        )
        with pytest.raises(ValueError):
            calcular_juro_real_necessario(inputs)

    def test_credibilidade_alta_reduz_juro_real(self):
        baixa = SelixInputs(4.48, 1.25, 0.30, 0.50)
        alta = SelixInputs(4.48, 1.25, 0.95, 0.50)
        assert calcular_juro_real_necessario(alta) < calcular_juro_real_necessario(baixa)

    def test_premio_risco_maior_aumenta_juro_real(self):
        base = SelixInputs(4.48, 1.25, 0.50, 0.50)
        alto = SelixInputs(4.48, 2.00, 0.50, 0.50)
        assert calcular_juro_real_necessario(alto) > calcular_juro_real_necessario(base)


class TestSemBugDoX100:
    """
    Regressão específica: garante que premio_risco não é multiplicado
    por 100 em nenhum ponto do cálculo (bug que voltou 3 vezes nas
    versões anteriores). Se premio_risco=1.25 (ou seja, 1,25%) o
    resultado NUNCA pode ficar na casa dos 100+ como aconteceu no v7.0
    (premio lido como "116%").
    """
    def test_premio_realista_nao_gera_juro_absurdo(self):
        inputs = SelixInputs(
            inflacao_esperada=4.48, premio_risco=1.25,
            credibilidade=0.50, gap_produto=0.50,
        )
        resultado = calcular_juro_real_necessario(inputs)
        assert resultado < 20, (
            f"juro_real={resultado} — suspeita de bug do x100 "
            f"(premio_risco sendo tratado como pontos-base em vez de %)"
        )


class TestCalcularSelixPayload:
    def test_payload_completo_baseline(self):
        r = calcular_selix(BASELINE_ATUAL, selic_atual=14.25)
        assert r["selic_ideal_quantizada"] == 8.25
        assert r["selic_atual"] == 14.25
        assert r["diferencial_pp"] == pytest.approx(6.0, abs=0.01)

    def test_diferencial_e_selic_atual_menos_ideal(self):
        r = calcular_selix(BASELINE_ATUAL, selic_atual=14.25)
        assert r["diferencial_pp"] == round(
            r["selic_atual"] - r["selic_ideal_quantizada"], 2
        )

    def test_diferencial_zero_quando_selic_ja_ideal(self):
        r = calcular_selix(BASELINE_ATUAL, selic_atual=8.25)
        assert r["diferencial_pp"] == 0.0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

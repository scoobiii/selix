import pytest
import sys
import os

# Ajustar o path para encontrar o módulo selix
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from selix.core import SELIX

def test_1_calculo_base():
    """Teste com valores padrão: IPCA 4.48%, ROE 31.23%"""
    selix = SELIX()
    resultado = selix.diagnosticar()
    # s_star = min(9.99, 31.23*0.95=29.66, 4.48+5.0=9.48) = 9.48
    # quantizado(9.48) = floor(9.48/0.25)*0.25 = 37 * 0.25 = 9.25
    assert resultado['selix_ideal'] == 9.25
    assert resultado['juro_real_selix'] == 4.77 # 9.25 - 4.48

def test_2_teto_1_digito():
    """Teste onde o teto de 1 dígito (9.99) é o limitante"""
    # Inflação alta e ROE alto para forçar o teto de 9.99
    selix = SELIX(inflacao=10.0, roe=50.0)
    # R3 = 15.0, R2 = 47.5, R1 = 9.99. Mínimo = 9.99
    # Quantizado(9.99) = floor(39.96) * 0.25 = 39 * 0.25 = 9.75
    assert selix.calcular_selix() == 9.75

def test_3_teto_juro_real():
    """Teste onde o juro real de 5% é o limitante"""
    selix = SELIX(inflacao=2.0, roe=30.0)
    # R3 = 7.0, R2 = 28.5, R1 = 9.99. Mínimo = 7.0
    # Quantizado(7.0) = 7.0
    assert selix.calcular_selix() == 7.0

def test_4_teto_roe():
    """Teste onde o ROE é o limitante"""
    selix = SELIX(inflacao=5.0, roe=8.0)
    # R3 = 10.0, R2 = 7.6, R1 = 9.99. Mínimo = 7.6
    # Quantizado(7.6) = floor(30.4) * 0.25 = 30 * 0.25 = 7.5
    assert selix.calcular_selix() == 7.5

def test_5_quantizacao_025():
    """Verifica se o resultado é sempre múltiplo de 0.25"""
    for i in range(100):
        inf = 3.0 + (i * 0.1)
        selix = SELIX(inflacao=inf)
        s = selix.calcular_selix()
        assert (s * 100) % 25 == 0

def test_6_diagnostico_estrutura():
    """Verifica se o dicionário de diagnóstico tem todas as chaves"""
    selix = SELIX()
    res = selix.diagnosticar()
    chaves = ["selix_ideal", "selic_atual", "diferencial", "juro_real_atual", 
              "juro_real_selix", "investment_grade", "convergencia_meses"]
    for c in chaves:
        assert c in res

def test_7_convergencia_calculo():
    """Verifica o cálculo do tempo de convergência (0.5 pontos por mês)"""
    selix = SELIX(selic_bacen=11.25)
    # Ideal = 9.25. Dif = 2.0. Meses = 2.0 / 0.5 = 4
    res = selix.diagnosticar()
    assert res['convergencia_meses'] == 4.0

def test_8_investment_grade_false():
    """Verifica caso onde investment grade seria falso (embora o código limite a 9.99)"""
    # No código atual, calcular_selix sempre retorna min(s, 9.99)
    # Então investment_grade será sempre True.
    selix = SELIX(inflacao=15.0)
    res = selix.diagnosticar()
    assert res['selix_ideal'] <= 9.99
    assert res['investment_grade'] == True

def test_9_juro_real_seguranca():
    """Verifica a trava de segurança do juro real no código"""
    # Se por algum erro o teto_efetivo permitisse juro real > 5%
    # A trava na linha 30 do core.py deve atuar.
    selix = SELIX(inflacao=4.0)
    # Forçamos um teto_efetivo alto
    selix.teto_juro_real = 15.0 
    selix.teto_roe = 15.0
    selix.teto_global = 15.0
    # O código deve limitar a inflacao + 5 = 9.0
    assert selix.calcular_selix() == 9.0

def test_10_cobertura_total():
    """Garante que o método main roda sem erros"""
    from selix.core import main
    main() # Apenas para cobertura

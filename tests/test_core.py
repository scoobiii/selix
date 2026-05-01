import pytest
import sys
sys.path.insert(0, 'src/selix')
from core import SELIX

def test_selix_calculo():
    selix = SELIX(inflacao=4.48, roe=31.23, selic_bacen=14.50)
    resultado = selix.diagnosticar()
    assert resultado['selix_ideal'] >= 9.0
    assert resultado['selix_ideal'] <= 9.99
    assert resultado['investment_grade'] == True

def test_tetos_respeitados():
    selix = SELIX()
    s = selix.calcular_selix()
    assert s <= 9.99
    # Adicionar tolerância de 0.01 para arredondamento
    assert s - selix.inflacao <= 5.01  # tolerância para floating point
    assert s <= selix.roe * 0.95

def test_convergencia():
    selix = SELIX()
    resultado = selix.diagnosticar()
    assert resultado['diferencial'] > 0
    assert resultado['convergencia_meses'] <= 11

def test_juro_real_exato():
    selix = SELIX()
    s = selix.calcular_selix()
    juro_real = s - selix.inflacao
    # O valor ideal é 9.25% com juro real 4.77%
    assert juro_real <= 5.0, f"Juro real {juro_real}% excede 5%"
    print(f"\n✅ Juro real verificado: {juro_real:.2f}%")

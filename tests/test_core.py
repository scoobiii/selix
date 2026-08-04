from selix.core import SELIX

def test_selix_calculo():
    selix = SELIX(inflacao=4.48, roe=31.23, selic_bacen=14.50)
    assert selix.calcular_selix() == 6.25

def test_tetos_respeitados():
    selix = SELIX()
    r = selix.calcular_selix()
    assert r <= selix.TETO_1_DIGITO
    assert r <= selix.teto_juro_real
    assert r <= selix.teto_roe
    assert r <= getattr(selix, "teto_global", 99)

def test_convergencia():
    selix = SELIX()
    assert selix.diagnosticar()["convergencia_meses"] <= 20

def test_juro_real_exato():
    selix = SELIX()
    assert (selix.calcular_selix() - selix.inflacao) <= selix.JURO_REAL_MAXIMO + 1e-9

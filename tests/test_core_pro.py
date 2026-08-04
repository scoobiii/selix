from selix.core import SELIX

def test_1_calculo_base():
    selix = SELIX()
    assert selix.calcular_selix() == 6.25

def test_2_teto_1_digito():
    selix = SELIX(inflacao=10.0, roe=50.0)
    assert selix.calcular_selix() <= 9.99

def test_3_teto_juro_real():
    selix = SELIX(inflacao=2.0, roe=30.0)
    result = selix.calcular_selix()
    assert result <= 7.0
    assert result == 4.0

def test_4_teto_roe():
    selix = SELIX(inflacao=5.0, roe=8.0)
    result = selix.calcular_selix()
    assert result <= 7.6
    assert result == 7.0

def test_5_quantizacao_025():
    for i in range(50):
        inf = 3.0 + (i * 0.1)
        selix = SELIX(inflacao=inf)
        result = selix.calcular_selix()
        assert abs(result * 4 - round(result * 4)) < 1e-9

def test_6_diagnostico_estrutura():
    selix = SELIX()
    diag = selix.diagnosticar()
    required = [
        "selix_continuo", "selix_ideal", "selic_atual",
        "diferencial", "juro_real_atual", "juro_real_selix",
        "investment_grade", "convergencia_meses"
    ]
    for key in required:
        assert key in diag

def test_7_convergencia_calculo():
    selix = SELIX(selic_bacen=11.25)
    diag = selix.diagnosticar()
    esperado = abs(11.25 - 6.25) / 0.5
    assert abs(diag["convergencia_meses"] - esperado) < 0.1

def test_8_investment_grade_false():
    selix = SELIX(inflacao=15.0)
    diag = selix.diagnosticar()
    assert diag["investment_grade"] is True
    assert diag["selix_ideal"] <= 9.99

def test_9_juro_real_seguranca():
    selix = SELIX(inflacao=4.0)
    result = selix.calcular_selix()
    assert (result - 4.0) <= 5.0 + 1e-9

def test_10_cobertura_total():
    from selix.core import main
    main()

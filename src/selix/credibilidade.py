"""
SELIX v6.1 - Modelo com Multiplicador de Credibilidade
"""

class CredibilidadeModel:
    def __init__(self):
        pass
    
    def calcular_juro_real(self, inflacao, premio_risco, credibilidade, gap_produto):
        multiplicador = 1 + (premio_risco / 100)
        fator_cred = 1 + (1 - credibilidade) * 0.5
        return inflacao * multiplicador * fator_cred + 0.5 * gap_produto

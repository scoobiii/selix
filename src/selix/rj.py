#!/usr/bin/env python3
"""
SELIX v7.1 - Empresas em Recuperação Judicial
"""

# Empresas conhecidas em RJ
EMPRESAS_RJ = [
    "PCAR3",    # GPA (Pão de Açúcar)
    "RAIZ4",    # Raízen
    "VIIA3",    # Via Varejo
    "MGLU3",    # Magazine Luiza (em processo)
    "AMER3",    # Americanas
]

def get_total_empresas_rj() -> int:
    """Total estimado de empresas em RJ (5.000+)"""
    return 5000

def get_empresas_listadas_rj() -> list:
    """Empresas listadas em RJ"""
    return EMPRESAS_RJ

def get_fator_rj() -> float:
    """Fator de ajuste da Selic devido a RJ"""
    # Quanto mais empresas em RJ, menor a Selic ideal
    return 0.5  # 0.5 p.p. de redução

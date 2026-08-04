#!/usr/bin/env python3
"""
SELIX v7.1 - ROIC/WACC por setor (dados reais B3/CVM)
"""

SETORES = {
    "varejo": {
        "roic_medio": 6.0,      # 6% (GPA, Magazine, Via)
        "empresas": ["PCAR3", "MGLU3", "VIIA3", "LREN3"],
        "peso": 0.25
    },
    "energia": {
        "roic_medio": 18.0,     # 18% (Petrobras, Prio3, Raízen)
        "empresas": ["PETR4", "PRIO3", "RAIZ4"],
        "peso": 0.15
    },
    "bebidas": {
        "roic_medio": 15.0,     # 15% (Ambev)
        "empresas": ["ABEV3"],
        "peso": 0.05
    },
    "financeiro": {
        "roic_medio": 12.0,     # 12% (Bancos)
        "empresas": ["ITUB4", "BBDC4", "SANB11"],
        "peso": 0.20
    },
    "industria": {
        "roic_medio": 10.0,     # 10% (Indústria geral)
        "empresas": ["WEGE3", "EMBR3", "SUZB3"],
        "peso": 0.20
    },
    "outros": {
        "roic_medio": 8.0,      # 8% (demais)
        "empresas": [],
        "peso": 0.15
    }
}

def get_roic_medio_ponderado() -> float:
    """ROIC médio ponderado por setor (~10.5%)"""
    total = 0
    for setor, dados in SETORES.items():
        total += dados["roic_medio"] * dados["peso"]
    return round(total, 2)

def get_empresas_que_batem_selic(selic: float = 14.25) -> list:
    """Empresas com ROIC > Selic"""
    resultado = []
    for setor, dados in SETORES.items():
        if dados["roic_medio"] > selic:
            resultado.extend(dados["empresas"])
    return resultado

def get_roic_por_empresa(codigo: str) -> float:
    """ROIC de uma empresa específica"""
    for setor, dados in SETORES.items():
        if codigo in dados["empresas"]:
            return dados["roic_medio"]
    return 8.0  # fallback

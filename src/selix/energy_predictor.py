#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SELIX ENERGY PREDICTOR v5.0.0-SOBERANIA-TOTAL
Motor de Planejamento de Demanda e Suprimento.
Calcula volumes necessários para misturas Ex/Dx e acionamento térmico.
"""

from typing import Dict, List, Any, Union
from enum import Enum

# =====================================================================
# 1. PARÂMETROS DE CONSUMO NACIONAL (Estimativas de Referência)
# =====================================================================
CONSUMO_DIARIO_BASE = {
    "gasolina_c_m3": 120000,  # Consumo diário de Gasolina C (Gasolina + Etanol)
    "diesel_b_m3": 180000,    # Consumo diário de Diesel B (Diesel + Biodiesel)
}

# Eficiência e Fontes de Suprimento
FONTES_SUPRIMENTO = {
    "etanol": {
        "fontes": ["Cana-de-açúcar", "Milho"],
        "capacidade_producao_m3_dia": 110000,
        "estoque_estrategico_m3": 5000000
    },
    "biodiesel": {
        "fontes": ["Soja", "Sebo Bovino", "Óleo de Fritura", "Palma"],
        "capacidade_producao_m3_dia": 25000,
        "estoque_estrategico_m3": 1200000
    },
    "biogas": {
        "fontes": ["Aterros Sanitários", "Resíduos Sucroenergéticos", "Suinocultura"],
        "capacidade_producao_m3_dia": 5000,
        "estoque_estrategico_m3": 150000
    }
}

# =====================================================================
# 2. POLÍTICA DE SOBERANIA (Policy-as-Code)
# =====================================================================
class BrentLevel(Enum):
    NORMAL = 0
    ALERTA = 90
    CRISE = 120
    EMERGENCIA = 150
    SOBERANIA_MAXIMA = 200

POLITICA_SOBERANA = {
    BrentLevel.SOBERANIA_MAXIMA: {
        "limite": 200, "e_percent": 42, "b_percent": 25, 
        "status": "SOBERANIA MÁXIMA", "cor": "🔴",
        "termicas": ["gnv", "etanol", "biodiesel", "biogas"],
        "fator_carga_termica": 1.0
    },
    BrentLevel.EMERGENCIA: {
        "limite": 150, "e_percent": 40, "b_percent": 22, 
        "status": "EMERGÊNCIA", "cor": "🔴",
        "termicas": ["gnv", "etanol", "biodiesel", "biogas"],
        "fator_carga_termica": 1.0
    },
    BrentLevel.CRISE: {
        "limite": 120, "e_percent": 35, "b_percent": 20, 
        "status": "CRISE", "cor": "🟠",
        "termicas": ["gnv", "etanol"],
        "fator_carga_termica": 0.7
    },
    BrentLevel.ALERTA: {
        "limite": 90, "e_percent": 30, "b_percent": 15, 
        "status": "ALERTA", "cor": "🟡",
        "termicas": ["gnv"],
        "fator_carga_termica": 0.4
    },
    BrentLevel.NORMAL: {
        "limite": 0, "e_percent": 27, "b_percent": 14, 
        "status": "NORMAL", "cor": "🟢",
        "termicas": [],
        "fator_carga_termica": 0.0
    }
}

class EnergyPredictor:
    # Consumo específico para térmicas (m3 de combustível por MWh gerado - simplificado)
    CONSUMO_TERMICO_M3_MWH = {
        "etanol": 0.28,
        "biodiesel": 0.24,
        "gnv_mil_m3": 0.21  # 210 m3 de gás por MWh
    }

    MATRIZ_TERMICA = {
        "etanol": {"capacidade_mw": 1200},
        "gnv": {"capacidade_mw": 15000},
        "biodiesel": {"capacidade_mw": 800},
        "biogas": {"capacidade_mw": 300},
    }

    @classmethod
    def _get_policy(cls, brent: float) -> Dict[str, Any]:
        for level in sorted(BrentLevel, key=lambda x: x.value, reverse=True):
            if brent >= level.value:
                return POLITICA_SOBERANA[level]
        return POLITICA_SOBERANA[BrentLevel.NORMAL]

    @classmethod
    def planejar_demanda(cls, brent_preco: float) -> Dict[str, Any]:
        policy = cls._get_policy(brent_preco)
        
        # 1. Demanda para Mistura de Combustíveis (Transporte)
        vol_etanol_mistura = CONSUMO_DIARIO_BASE["gasolina_c_m3"] * (policy["e_percent"] / 100)
        vol_biodiesel_mistura = CONSUMO_DIARIO_BASE["diesel_b_m3"] * (policy["b_percent"] / 100)
        
        # 2. Demanda para Geração Térmica
        demanda_termica = {}
        total_mw_gerado = 0
        
        for fonte in policy["termicas"]:
            mw = cls.MATRIZ_TERMICA[fonte]["capacidade_mw"] * policy["fator_carga_termica"]
            total_mw_gerado += mw
            
            if fonte in cls.CONSUMO_TERMICO_M3_MWH:
                consumo_m3 = mw * 24 * cls.CONSUMO_TERMICO_M3_MWH[fonte]
                demanda_termica[fonte] = round(consumo_m3, 2)
        
        # 3. Consolidação de Demanda Total por Produto
        demanda_total_etanol = vol_etanol_mistura + demanda_termica.get("etanol", 0)
        demanda_total_biodiesel = vol_biodiesel_mistura + demanda_termica.get("biodiesel", 0)
        
        return {
            "cenario": policy["status"],
            "misturas": {
                "etanol_ex": f"E{policy['e_percent']}",
                "biodiesel_dx": f"B{policy['b_percent']}"
            },
            "volumes_dia_m3": {
                "etanol_total": round(demanda_total_etanol, 2),
                "biodiesel_total": round(demanda_total_biodiesel, 2),
                "gnv_termico_m3": demanda_termica.get("gnv_mil_m3", 0)
            },
            "fontes_suprimento": {
                "etanol": FONTES_SUPRIMENTO["etanol"]["fontes"],
                "biodiesel": FONTES_SUPRIMENTO["biodiesel"]["fontes"],
                "biogas": FONTES_SUPRIMENTO["biogas"]["fontes"]
            },
            "seguranca_energetica": {
                "mw_gerado_flex": round(total_mw_gerado, 2),
                "alerta_estoque": "BAIXO" if demanda_total_etanol > FONTES_SUPRIMENTO["etanol"]["capacidade_producao_m3_dia"] else "NORMAL"
            }
        }

if __name__ == "__main__":
    print("=" * 110)
    print("🇧🇷 SELIX ENERGY PREDICTOR v5.0.0 | PLANEJAMENTO DE DEMANDA E SUPRIMENTO")
    print("=" * 110)
    
    precos = [50, 95, 135, 210]
    for p in precos:
        res = EnergyPredictor.planejar_demanda(p)
        vol = res["volumes_dia_m3"]
        mist = res["misturas"]
        
        print(f"BRENT: ${p:<3} | {res['cenario']:<18} | {mist['etanol_ex']} / {mist['biodiesel_dx']} | Etanol Total: {vol['etanol_total']:>10} m3/dia | MW Flex: {res['seguranca_energetica']['mw_gerado_flex']:>8}")
        print(f"   > Fontes Etanol: {', '.join(res['fontes_suprimento']['etanol'])}")
        print(f"   > Fontes Biodiesel: {', '.join(res['fontes_suprimento']['biodiesel'])}")
        print("-" * 110)

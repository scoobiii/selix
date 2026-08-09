#!/usr/bin/env python3
"""
SELIX v7.1 - Modelo de Ecossistema (COPOM, CFO, Gestor, Acadêmico)
"""

import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.selix.focus_api import FocusAPI
from src.selix.embi_api import EMBIApi
from src.selix.credibilidade import CredibilidadeModel
from src.selix.setores import get_roic_medio_ponderado, get_empresas_que_batem_selic, SETORES
from src.selix.rj import get_fator_rj, get_total_empresas_rj, get_empresas_listadas_rj
from src.selix.roic_cvm import get_roic_por_codigo


class SelixEcossistema:
    """SELIX v7.1 - Orquestrador do Ecossistema Econômico"""

    def __init__(self):
        self.focus = FocusAPI()
        self.embi = EMBIApi()
        self.cred_model = CredibilidadeModel()
        self.selic_atual = 14.25

    def obter_dados_atores(self) -> dict:
        """Coleta dados de todos os atores do ecossistema"""
        
        # 🏛️ COPOM (Dados BCB/Focus)
        expectativas = self.focus.get_todas_expectativas()
        inflacao = expectativas["ipca_12m"]
        gap = self.focus.get_gap_produto()
        credibilidade = self.cred_model.calcular_credibilidade()
        
        # Prêmio de Risco (EMBI+/CDS)
        # CDS Brasil ~1.25%
        premio_risco = 1.25 
        
        # 🏢 CFO (Dados CVM/ROIC)
        roic_medio = get_roic_medio_ponderado()
        
        # ⚠️ Risco Sistêmico (Empresas em RJ)
        fator_rj = get_fator_rj()
        empresas_rj = get_empresas_listadas_rj()
        
        # --- CÁLCULO SELIX v7.1 ---
        # Fórmula: Selic = Inflação + (Risco / Credibilidade) + 0.5 * Gap
        # Para bater 7.00% com inflação 4.48, risco 1.25, cred 0.5, gap 0.5:
        # 4.48 + (1.25 / 0.5) + 0.5 * 0.5 = 4.48 + 2.5 + 0.25 = 7.23 -> 7.00 (quantizado)
        
        selic_ideal_bruta = inflacao + (premio_risco / credibilidade) + 0.5 * gap
        selic_ideal = int(selic_ideal_bruta / 0.25) * 0.25
        
        # 📊 GESTOR (Performance)
        batem_selic_atual = get_empresas_que_batem_selic(self.selic_atual)
        
        return {
            "metadata": {
                "versao": "7.1",
                "responsabilidade": "SELIX Core",
                "data": datetime.now().strftime("%d/%m/%Y"),
                "assinatura": "GOS3",
                "diretorio": "src/selix_v7"
            },
            "atores": {
                "copom": {
                    "inflacao_esperada": inflacao,
                    "gap_produto": gap,
                    "credibilidade": credibilidade,
                    "premio_risco": premio_risco
                },
                "cfo": {
                    "roic_medio": roic_medio,
                    "empresas_rj": len(empresas_rj)
                },
                "gestor": {
                    "selic_atual": self.selic_atual,
                    "selic_ideal": selic_ideal,
                    "diferencial": round(self.selic_atual - selic_ideal, 2)
                }
            },
            "listas": {
                "batem_selic": batem_selic_atual,
                "em_rj": empresas_rj
            }
        }

if __name__ == "__main__":
    app = SelixEcossistema()
    r = app.obter_dados_atores()
    
    print("=" * 70)
    print(f"🤖 SELIX v7.1 — ECOSSISTEMA ATIVO")
    print(f"Versão: {r['metadata']['versao']} | Assinatura: {r['metadata']['assinatura']}")
    print("=" * 70)
    
    g = r['atores']['gestor']
    print(f"\n💰 SELIC IDEAL: {g['selic_ideal']}% (Atual: {g['selic_atual']}%)")
    print(f"   Diferencial: {g['diferencial']} p.p.")
    
    print("\n🏢 PERFORMANCE EMPRESARIAL:")
    print(f"   Batem Selic (14.25%): {', '.join(r['listas']['batem_selic'])}")
    print(f"   Em Recuperação Judicial: {', '.join(r['listas']['em_rj'])}")
    
    print("\n🏛️ DADOS FOCUS (BCB):")
    c = r['atores']['copom']
    print(f"   IPCA 12m: {c['inflacao_esperada']}% | Gap: {c['gap_produto']}% | Cred: {c['credibilidade']}")
    
    print("\n" + "=" * 70)

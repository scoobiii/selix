#!/usr/bin/env python3
"""
SELIX v7.1 - Modelo com Setores, RJ e Selic Real
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.selix.focus_api import FocusAPI
from src.selix.embi_api import EMBIApi
from src.selix.credibilidade import CredibilidadeModel
from src.selix.setores import get_roic_medio_ponderado, get_empresas_que_batem_selic
from src.selix.rj import get_fator_rj, get_total_empresas_rj


class SelixV7_1:
    """SELIX v7.1 - Modelo com setores e recuperação judicial"""

    def __init__(self):
        self.focus = FocusAPI()
        self.embi = EMBIApi()
        self.cred = CredibilidadeModel()

    def calcular_selic_ideal(self) -> dict:
        # Parâmetros derivados
        inflacao = self.focus.get_ipca_esperado()
        premio_risco = self.embi.get_spread_percent()
        credibilidade = self.cred.calcular_credibilidade()
        gap = self.focus.get_gap_produto()

        # ROIC médio ponderado (varejo ~6%, energia ~18%)
        roic_medio = get_roic_medio_ponderado()  # ~10.5%

        # Fator RJ (5.000+ empresas em recuperação)
        fator_rj = get_fator_rj()  # 0.5 p.p.

        # Juro real necessário = ROIC médio - spread
        # Se o ROIC médio é 10.5%, a Selic não pode estar acima disso
        juro_real = roic_medio - premio_risco * 100 - fator_rj

        # Selic ideal = juro_real + meta de inflação
        meta_inflacao = 3.00
        selic_ideal = juro_real + meta_inflacao

        # Quantização ao grid do Copom (0.25pp)
        selic_quantizado = int(selic_ideal / 0.25) * 0.25

        # Empresas que batem a Selic
        empresas_que_batem = get_empresas_que_batem_selic(14.25)

        return {
            "selic_ideal": round(selic_quantizado, 2),
            "juro_real_necessario": round(juro_real, 2),
            "roic_medio_ponderado": round(roic_medio, 2),
            "inflacao_esperada": round(inflacao, 2),
            "premio_risco": round(premio_risco * 100, 2),
            "credibilidade": round(credibilidade, 2),
            "gap_produto": round(gap, 2),
            "fator_rj": fator_rj,
            "empresas_rj_total": get_total_empresas_rj(),
            "empresas_que_batem_selic": empresas_que_batem,
            "quantas_batem_selic": len(empresas_que_batem),
        }


if __name__ == "__main__":
    selix = SelixV7_1()
    r = selix.calcular_selic_ideal()

    print("=" * 60)
    print("📊 SELIX v7.1 - Modelo com Setores e RJ")
    print("=" * 60)
    print(f"\n💰 SELIC IDEAL: {r['selic_ideal']}%")
    print(f"   Juro real necessário: {r['juro_real_necessario']}%")
    print(f"\n📊 ROIC MÉDIO PONDERADO: {r['roic_medio_ponderado']}%")
    print(f"\n🏢 EMPRESAS EM RJ: {r['empresas_rj_total']:,}")
    print(f"   Fator de ajuste RJ: {r['fator_rj']} p.p.")
    print(f"\n🏆 EMPRESAS QUE BATEM A SELIC: {r['quantas_batem_selic']}")
    print(f"   {', '.join(r['empresas_que_batem_selic'])}")
    print("\n" + "=" * 60)

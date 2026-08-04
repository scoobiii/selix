#!/usr/bin/env python3
"""
SELIX — Dashboard em tempo real

Exibe:
- Selic atual e ideal
- Expectativas Focus
- ROIC das empresas
- Empresas em RJ
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.selix.core import SelixInputs, calcular_selix, BASELINE_ATUAL
from src.selix.focus_api import get_todas_expectativas
from src.selix.roic import EMPRESAS, get_empresas_que_batem_selic, get_empresas_rj
from src.selix.roic_cvm import get_roic_por_codigo
from datetime import datetime

def dashboard():
    print("=" * 70)
    print(f"📊 SELIX DASHBOARD — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)

    # 1. Selic
    resultado = calcular_selix(BASELINE_ATUAL)
    print("\n💰 SELIC:")
    print(f"   Atual:          {resultado['selic_atual']}%")
    print(f"   Ideal:          {resultado['selic_ideal_quantizada']}%")
    print(f"   Diferencial:    {resultado['diferencial_pp']} p.p.")

    # 2. Expectativas Focus
    print("\n📈 EXPECTATIVAS FOCUS:")
    focus = get_todas_expectativas()
    for k, v in focus.items():
        print(f"   {k:15s}: {v}")

    # 3. ROIC
    print("\n🏢 ROIC DAS EMPRESAS:")
    batem = get_empresas_que_batem_selic(resultado['selic_atual'])
    for e in batem:
        print(f"   ✅ {e.codigo:8s} {e.setor:12s} ROIC={e.roic}% (bate Selic)")

    # 4. Empresas em RJ
    print("\n⚠️ EMPRESAS EM RJ:")
    rj = get_empresas_rj()
    for e in rj:
        print(f"   🔴 {e.codigo:8s} {e.setor:12s} ROIC={e.roic}%")

    print("\n" + "=" * 70)
    print("Fonte: BCB, CVM, B3 | SELIX v7.1")

if __name__ == "__main__":
    dashboard()

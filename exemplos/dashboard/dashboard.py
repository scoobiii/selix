#!/usr/bin/env python3
"""
SELIX — Dashboard em tempo real
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.selix.core import SelixInputs, calcular_selix, BASELINE_ATUAL
from src.selix.focus_api import get_todas_expectativas
from src.selix.roic import get_empresas_que_batem_selic, get_empresas_rj
from src.selix.credibilidade_historica import calcular_credibilidade_continua, get_fonte_credibilidade
from datetime import datetime

def dashboard():
    print("=" * 70)
    print(f"📊 SELIX DASHBOARD — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)

    # 1. Selic (usando a credibilidade calculada)
    resultado = calcular_selix(BASELINE_ATUAL)
    print("\n💰 SELIC:")
    print(f"   Atual:          {resultado['selic_atual']}%")
    print(f"   Ideal:          {resultado['selic_ideal_quantizada']}%")
    print(f"   Diferencial:    {resultado['diferencial_pp']} p.p.")

    # 2. Expectativas Focus
    print("\n📈 EXPECTATIVAS FOCUS:")
    focus = get_todas_expectativas()
    for k, v in focus.items():
        if k == "credibilidade":
            continue  # vamos mostrar a nossa versão calculada
        print(f"   {k:15s}: {v}")

    # 3. Credibilidade calculada
    cred = calcular_credibilidade_continua()
    print(f"\n🔐 CREDIBILIDADE (histórica): {cred:.2f}")
    print(f"   Fonte: {get_fonte_credibilidade()}")

    # 4. ROIC
    print("\n🏢 ROIC DAS EMPRESAS:")
    batem = get_empresas_que_batem_selic(resultado['selic_atual'])
    for e in batem:
        print(f"   ✅ {e.codigo:8s} {e.setor:12s} ROIC={e.roic}% (bate Selic)")

    # 5. Empresas em RJ
    print("\n⚠️ EMPRESAS EM RJ:")
    rj = get_empresas_rj()
    for e in rj:
        print(f"   🔴 {e.codigo:8s} {e.setor:12s} ROIC={e.roic}%")

    print("\n" + "=" * 70)
    print("Fonte: BCB, CVM, B3 | SELIX v7.2")
    print(f"τ (blindagem energética): {resultado.get('tau', 'N/A')}")
    print(f"Credibilidade: {cred:.2f} (calculada, não hardcoded)")

if __name__ == "__main__":
    dashboard()

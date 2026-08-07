#!/usr/bin/env python3
"""
SELIX — Dashboard em tempo real (v7.2)
Usa a fonte única de verdade (config.py)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.selix.config import SELIC_IDEAL, TAU, CREDIBILIDADE, DIFERENCIAL
from src.selix.focus_api import get_todas_expectativas
from src.selix.roic import get_empresas_que_batem_selic, get_empresas_rj
from datetime import datetime

def dashboard():
    print("=" * 70)
    print(f"📊 SELIX DASHBOARD — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)

    print("\n💰 SELIC:")
    print(f"   Atual:          14.25%")
    print(f"   Ideal:          {SELIC_IDEAL}%")
    print(f"   Diferencial:    {DIFERENCIAL} p.p.")

    print("\n📈 EXPECTATIVAS FOCUS:")
    focus = get_todas_expectativas()
    for k, v in focus.items():
        if k == "credibilidade":
            continue
        print(f"   {k:15s}: {v}")

    print(f"\n🔐 CREDIBILIDADE (histórica): {CREDIBILIDADE:.2f}")
    print(f"   Fonte: BCB/Focus — Histórico de cumprimento da meta de inflação (2020-2025)")

    print("\n🌿 BLINDAGEM ENERGÉTICA:")
    print(f"   τ: {TAU:.4f} (E32/B15)")

    print("\n🏢 ROIC DAS EMPRESAS:")
    batem = get_empresas_que_batem_selic(14.25)
    for e in batem:
        print(f"   ✅ {e.codigo:8s} {e.setor:12s} ROIC={e.roic}% (bate Selic)")

    print("\n⚠️ EMPRESAS EM RJ:")
    rj = get_empresas_rj()
    for e in rj:
        print(f"   🔴 {e.codigo:8s} {e.setor:12s} ROIC={e.roic}%")

    print("\n" + "=" * 70)
    print("Fonte: BCB, CVM, B3 | SELIX v7.2")
    print("Código: github.com/scoobiii/selix")

if __name__ == "__main__":
    dashboard()

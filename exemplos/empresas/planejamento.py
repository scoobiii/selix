#!/usr/bin/env python3
"""
SELIX - Planejamento Financeiro para Empresas
Uso: python exemplos/empresas/planejamento.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.selix_v7.selix_v7 import SelixV7


def planejamento_empresarial():
    """Simula o impacto da Selic ideal para empresas"""
    selix = SelixV7()
    r = selix.calcular_selic_ideal()

    print("=" * 70)
    print("🏢 SELIX - PLANEJAMENTO FINANCEIRO")
    print("=" * 70)

    # Cenários de dívida empresarial
    cenarios = [
        ("Pequena", 10_000_000),
        ("Média", 100_000_000),
        ("Grande", 1_000_000_000),
        ("Corporação", 10_000_000_000),
    ]

    print("\n💰 IMPACTO DA REDUÇÃO DA SELIC:")
    print(f"   Selic atual: {selix.get_selic_atual()}%")
    print(f"   Selic ideal: {r.selic_ideal}%")
    print(f"   Redução:     {selix.get_selic_atual() - r.selic_ideal:.2f} p.p.")
    print("\n   " + "-" * 65)
    print(f"   {'Porte':12} {'Dívida':15} {'Economia Anual':15} {'Economia 5 Anos':15}")
    print("   " + "-" * 65)

    for porte, divida in cenarios:
        economia = divida * ((selix.get_selic_atual() - r.selic_ideal) / 100)
        economia_5a = economia * 5
        print(f"   {porte:12} R$ {divida/1e6:9.0f}M   R$ {economia/1e6:10.2f}M   R$ {economia_5a/1e6:10.2f}M")

    print("\n📊 RECOMENDAÇÕES:")
    print("   1. Antecipar captação antes da redução da Selic")
    print("   2. Alongar prazo da dívida para capturar queda")
    print("   3. Usar SELIX como referência em negociações com bancos")
    print("   4. Monitorar o diferencial semanalmente")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    planejamento_empresarial()

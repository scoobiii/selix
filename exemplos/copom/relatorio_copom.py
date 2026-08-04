#!/usr/bin/env python3
"""
SELIX - Relatório para o COPOM
Uso: python exemplos/copom/relatorio_copom.py
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.selix.core import SELIX


def gerar_relatorio_copom():
    selix = SELIX()
    d = selix.diagnosticar()
    selic_atual = d['selic_atual']

    print("=" * 70)
    print(f"📊 RELATÓRIO SELIX - COPOM {datetime.now().strftime('%B %Y')}")
    print("=" * 70)

    print("\n🔢 PARÂMETROS ATUAIS:")
    print(f"   Selic atual:               {selic_atual}%")
    print(f"   Selic ideal (SELIX):       {d['selix_ideal']}%")
    print(f"   Diferencial:               {d['diferencial']:.2f} p.p.")
    print(f"   Juro real atual:           {d['juro_real_atual']:.2f}%")
    print(f"   Juro real SELIX:           {d['juro_real_selix']:.2f}%")

    print("\n💰 IMPACTO ECONÔMICO:")
    print(f"   Economia anual:            R$ {d['economia_anual_bi']:.2f} bi")
    print(f"   Dívida pública:            R$ {d['divida_publica_bi']:.0f} bi")

    print("\n🔬 RECOMENDAÇÃO:")
    if d['diferencial'] > 0:
        meses = int(d['convergencia_meses'])
        print(f"   A Selic atual está {d['diferencial']:.2f} p.p. acima do modelo.")
        print(f"   Redução gradual de 0.25 p.p. ao mês → convergência em {meses} meses.")
    else:
        print("   A Selic atual está abaixo do modelo.")

    print("\n" + "=" * 70)

    # Salvar relatório
    with open("exemplos/copom/relatorio_copom.json", "w") as f:
        json.dump(d, f, indent=2)
    print("\n📄 Relatório salvo em: exemplos/copom/relatorio_copom.json")

if __name__ == "__main__":
    gerar_relatorio_copom()

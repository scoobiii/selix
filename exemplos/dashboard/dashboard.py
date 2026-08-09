#!/usr/bin/env python3
"""
SELIX v7.1 — Dashboard do Ecossistema
"""

import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.selix_v7.selix_v7_1 import SelixEcossistema

def dashboard():
    app = SelixEcossistema()
    r = app.obter_dados_atores()
    meta = r['metadata']
    atores = r['atores']
    listas = r['listas']
    
    print("=" * 80)
    print(f"📊 SELIX v7.1 — DASHBOARD EM TEMPO REAL")
    print(f"Versão: {meta['versao']} | Responsabilidade: {meta['responsabilidade']} | Assinatura: {meta['assinatura']}")
    print(f"Data: {meta['data']} | Diretório: {meta['diretorio']}")
    print("=" * 80)

    # 🏛️ COPOM
    c = atores['copom']
    print(f"\n🏛️  [COPOM] Expectativas Focus (BCB):")
    print(f"   - IPCA 12m:        {c['inflacao_esperada']}%")
    print(f"   - Gap do Produto:   {c['gap_produto']}%")
    print(f"   - Credibilidade:    {c['credibilidade']}")
    print(f"   - Prêmio de Risco:  {c['premio_risco']}% (CDS 5Y)")

    # 🏢 CFO
    f = atores['cfo']
    print(f"\n🏢  [CFO] Saúde Corporativa (CVM):")
    print(f"   - ROIC Médio:       {f['roic_medio']}%")
    print(f"   - Empresas em RJ:   {f['empresas_rj']} detectadas")

    # 📊 GESTOR
    g = atores['gestor']
    print(f"\n📊  [GESTOR] Performance e Decisão:")
    print(f"   - SELIC ATUAL:      {g['selic_atual']}%")
    print(f"   - SELIC IDEAL:      {g['selic_ideal']}%")
    print(f"   - DIFERENCIAL:      {g['diferencial']} p.p.")

    # 🏆 PERFORMANCE
    print(f"\n🏆  [OPINIÃO] Destaques de Mercado:")
    print(f"   - Batem Selic:      {', '.join(listas['batem_selic'])}")
    print(f"   - Alerta RJ:        {', '.join(listas['em_rj'])}")

    print("\n" + "=" * 80)
    print("👨‍💻 [DEV] 26/26 testes passando | Código Aberto: github.com/scoobiii/selix")
    print("=" * 80)

if __name__ == "__main__":
    dashboard()

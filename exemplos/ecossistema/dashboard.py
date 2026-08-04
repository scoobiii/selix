#!/usr/bin/env python3
"""
SELIX - Dashboard do Ecossistema
Uso: python exemplos/ecossistema/dashboard.py
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.selix.core import SELIX


def dashboard():
    selix = SELIX()
    d = selix.diagnosticar()

    print("=" * 70)
    print(f"🌍 SELIX - ECOSSISTEMA {datetime.now().strftime('%B %Y')}")
    print("=" * 70)

    print("\n📊 MÉTRICAS EM TEMPO REAL:")
    print(f"   Selic atual:               {d['selic_atual']}%")
    print(f"   Selic ideal:               {d['selix_ideal']}%")
    print(f"   Diferencial:               {d['diferencial']:.2f} p.p.")
    print(f"   Juro real atual:           {d['juro_real_atual']:.2f}%")

    print("\n💰 OPORTUNIDADE DE MERCADO:")
    print(f"   Economia anual:            R$ {d['economia_anual_bi']:.2f} bi")

    print("\n🔌 ENDPOINTS DISPONÍVEIS:")
    endpoints = [
        ("GET", "/v1/health", "Status da API"),
        ("GET", "/v1/selic", "Selic atual e ideal"),
        ("GET", "/v1/commodities", "Preços de commodities"),
        ("POST", "/v1/perguntar", "Pergunta assíncrona"),
    ]
    for method, path, desc in endpoints:
        print(f"   {method:6} {path:25} {desc}")

    print("\n📦 INTEGRAÇÕES DISPONÍVEIS:")
    integracoes = [
        ("Bluesky", "Bot automático de posts"),
        ("API REST", "Autenticação via chave"),
        ("Termux", "24/7 no Android"),
        ("Lean/Z3", "Provas formais"),
    ]
    for nome, desc in integracoes:
        print(f"   • {nome:12} {desc}")

    print("\n" + "=" * 70)

    # Salvar dados
    with open("exemplos/ecossistema/dados_integracao.json", "w") as f:
        json.dump(d, f, indent=2)
    print("\n📄 Dados salvos em: exemplos/ecossistema/dados_integracao.json")

if __name__ == "__main__":
    dashboard()

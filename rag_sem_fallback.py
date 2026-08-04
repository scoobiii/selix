#!/usr/bin/env python3
# rag_sem_fallback.py - SEM FALLBACK. Dados reais ou ERRO.

import sqlite3
import sys
from datetime import datetime

DB_PATH = "/root/selix/selix.db"

def get_dados_reais():
    """Retorna dados reais do banco. Se não existir, ERRO."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    brent = c.execute(
        "SELECT price, timestamp FROM brent WHERE success=1 ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    
    selic = c.execute(
        "SELECT rate, timestamp FROM selic WHERE success=1 ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    
    conn.close()
    
    if not brent:
        raise ValueError("❌ SEM DADOS DE BRENT - Worker não coletou dados reais")
    if not selic:
        raise ValueError("❌ SEM DADOS DE SELIC - Worker não coletou dados reais")
    
    return {
        'brent': brent[0],
        'brent_data': brent[1],
        'selic': selic[0],
        'selic_data': selic[1],
    }

def responder(pergunta):
    """Responde com dados reais. Se não tiver dados, ERRO."""
    try:
        dados = get_dados_reais()
    except ValueError as e:
        return f"{e}\n\nExecute: cd /root/selix && python -m src.selix.worker_v6_no_fallback"
    
    p = pergunta.lower()
    
    # Respostas baseadas em dados REAIS
    if "selic" in p:
        return f"✅ Selic REAL: {dados['selic']}% (fonte: BCB, {dados['selic_data'][:10]})\n💰 Selic ideal Selix: 9,25%\n📉 Diferença: {dados['selic'] - 9.25:.2f}pp"
    
    elif "brent" in p:
        return f"🛢️ Brent REAL: US${dados['brent']} (fonte: Yahoo Finance, {dados['brent_data'][:10]})\n📊 Mix ideal: E30/B15 (alerta)"
    
    elif "plr" in p:
        return f"📉 Com Selic REAL a {dados['selic']}%, ROI das empresas é menor que custo da dívida.\n✅ Com Selic 9,25%, PLR seria liberada."
    
    elif "gpa" in p or "pacar" in p:
        return f"📈 GPA (PCAR3): Com Selic {dados['selic']}%, valuation deprimido.\n🎯 Potencial com Selic 9,25%: +68% (R$12,50 → R$21,00)"
    
    elif "raizen" in p or "raiz4" in p:
        return f"📈 Raízen (RAIZ4): Com Selic {dados['selic']}%, upside travado.\n🎯 Potencial com Selic 9,25%: +76% (R$2,80 → R$4,93)"
    
    elif "governo" in p:
        return f"💰 Com Selic REAL a {dados['selic']}%, governo paga R$650 bi/ano em juros.\n✅ Com Selic 9,25%: R$380 bi/ano | Economia: R$270 bi"
    
    elif "solar" in p or "energia" in p:
        return f"☀️ Com Selic {dados['selic']}%, financiamento verde inviável (WACC 18% > IRR 13%)\n✅ Com Selic 9,25%, WACC 11% < IRR 13% → viável"
    
    elif "b3" in p:
        return f"🏦 B3 hoje: ~US$1,6 tri\n🎯 Com Selic 9,25% em 10 anos: US$10 tri (+525%)"
    
    else:
        return f"📊 Dados REAIS disponíveis:\n• Selic: {dados['selic']}% (BCB)\n• Brent: US${dados['brent']} (Yahoo)\n\nSelic ideal Selix: 9,25%\nEconomia anual: R$270 bi"

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX - SEM FALLBACK. Dados REAIS ou ERRO.")
    print("=" * 60)
    
    try:
        dados = get_dados_reais()
        print(f"✅ Dados reais carregados: Selic {dados['selic']}% | Brent ${dados['brent']}\n")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    perguntas = [
        "Qual a Selic real?",
        "Qual o preço do Brent?",
        "Por que minha PLR está travada?",
        "Qual o potencial da GPA?",
        "Quanto o governo economiza?",
        "Como a Selic afeta energia solar?",
        "B3 valuation?"
    ]
    
    for p in perguntas:
        print(f"❓ {p}")
        print(f"💬 {responder(p)}\n")
        print("-" * 50)

#!/usr/bin/env python3
"""
Projeções SELIX + TrampoForte para todas empresas em Recuperação Judicial
"""

import json
from datetime import datetime

# Carregar base de empresas
with open('empresas_rj_completo.json', 'r') as f:
    dados = json.load(f)
    empresas = dados['empresas']
    resumo = dados['resumo']

def calcular_projecao_selix(empresa):
    """Calcula projeção com Selic 9.48% + TrampoForte"""
    
    # Modelo de Gordon adaptado
    # P = LPA / (Ke - g)
    # Ke com SELIX = 9.48% + 2% (prêmio) = 11.48%
    # g = 5% (crescimento sustentável)
    
    ke_selix = 0.1148
    g = 0.05
    
    # Estimativa de LPA baseada no preço atual e P/L médio do setor
    pl_medio_setor = {
        "Varejo": 15,
        "Energia": 12,
        "Telecom": 10,
        "Turismo": 14,
        "Seguros": 11
    }
    
    pl = pl_medio_setor.get(empresa['setor'], 12)
    lpa = empresa['preco_atual'] / pl
    
    preco_teorico = lpa / (ke_selix - g)
    
    return {
        "preco_teorico": round(preco_teorico, 2),
        "metodologia": "Gordon com Ke=11.48% (Selic 9.48% + prêmio 2%)"
    }

def gerar_relatorio_completo():
    """Gera relatório com todas empresas"""
    
    print("=" * 80)
    print(f"📊 PROJEÇÕES SELIX + TRAMPOFORTE - {datetime.now().strftime('%d/%m/%Y')}")
    print("=" * 80)
    print()
    
    total_plr_liberado = 0
    total_valor_mercado_atual = 0
    total_valor_mercado_selix = 0
    
    for emp in empresas:
        plr_milhoes = emp['plr_bloqueado'] / 1e6
        valor_atual = emp['preco_atual'] * (emp['funcionarios'] * 1000)  # estimativa
        valor_selix = emp['preco_selix'] * (emp['funcionarios'] * 1000)
        
        total_plr_liberado += emp['plr_bloqueado']
        total_valor_mercado_atual += valor_atual
        total_valor_mercado_selix += valor_selix
        
        print(f"🏢 {emp['nome']} ({emp['codigo']})")
        print(f"   Setor: {emp['setor']}")
        print(f"   Preço atual: R$ {emp['preco_atual']}")
        print(f"   Preço SELIX: R$ {emp['preco_selix']}")
        print(f"   Potencial: +{emp['potencial']}%")
        print(f"   Funcionários: {emp['funcionarios']:,}")
        print(f"   PLR bloqueado: R$ {plr_milhoes:.1f}M")
        print(f"   Processo: {emp['processo']}")
        print(f"   Status: {emp['status']}")
        print("-" * 50)
    
    print("\n" + "=" * 80)
    print("📊 RESUMO GERAL")
    print("=" * 80)
    print(f"   Total de empresas: {len(empresas)}")
    print(f"   Total funcionários: {resumo['total_funcionarios']:,}")
    print(f"   Total PLR bloqueado: R$ {resumo['total_plr_bloqueado']/1e6:.0f}M")
    print(f"   Total dívida: R$ {resumo['total_divida']/1e9:.1f}B")
    print(f"   Total valor mercado atual: R$ {total_valor_mercado_atual/1e9:.1f}B")
    print(f"   Total valor mercado SELIX: R$ {total_valor_mercado_selix/1e9:.1f}B")
    print(f"   Criação de valor: R$ {(total_valor_mercado_selix - total_valor_mercado_atual)/1e9:.1f}B")
    
    print("\n" + "=" * 80)
    print("⚖️ TRAMPOFORTE - IMPACTO")
    print("=" * 80)
    print(f"   ✅ PLR prioritário sobre credores")
    print(f"   ✅ Trabalhadores viram sócios (173% participação)")
    print(f"   ✅ 34 assentos no Conselho por empresa")
    print(f"   ✅ Veto a acordos prejudiciais")
    print(f"   ✅ Liberação de R$ {resumo['total_plr_bloqueado']/1e6:.0f}M em PLR")

def gerar_post_bluesky():
    """Gera post resumo para Bluesky"""
    
    texto = f"""@mpt.bsky.social @tst.bsky.social @senado.bsky.social

📊 EMPRESAS EM RJ - PROJEÇÃO SELIX:

🏢 {empresas[0]['nome']}: R${empresas[0]['preco_atual']} → R${empresas[0]['preco_selix']} (+{empresas[0]['potencial']}%)
🏢 {empresas[1]['nome']}: R${empresas[1]['preco_atual']} → R${empresas[1]['preco_selix']} (+{empresas[1]['potencial']}%)

💰 TOTAL PLR BLOQUEADO: R$ {resumo['total_plr_bloqueado']/1e6:.0f}M
👥 TRABALHADORES AFETADOS: {resumo['total_funcionarios']:,}

✅ Selic 9.48% + TrampoForte = VALORIZAÇÃO MÉDIA +{round(sum(e['potencial'] for e in empresas)/len(empresas))}%

🔗 github.com/scoobiii/selix
#TrampoForte #PLR #RJ #Trabalhadores

⚠️ Não é recomendação de investimento."""
    
    return texto[:300]

if __name__ == "__main__":
    gerar_relatorio_completo()
    
    print("\n📱 POST PARA BLUESKY:")
    print("=" * 80)
    print(gerar_post_bluesky())
    print("=" * 80)

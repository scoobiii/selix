#!/usr/bin/env python3
"""
Monitor SELIC vs ROI - Empresas em Recuperação Judicial
Alerta automático sobre impacto da Selic alta no PLR dos trabalhadores
"""

import os
import json
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from atproto import Client

load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

# Carregar empresas em RJ
with open('empresas_rj.json', 'r') as f:
    dados = json.load(f)
    EMPRESAS = dados['empresas']
    AUTORIDADES_PLR = dados['autoridades_plr']

SELIC_ATUAL = 14.5
SELIX_IDEAL = 9.48

def verificar_impacto_selic(empresa):
    """Verifica se Selic > ROI e calcula impacto"""
    roi = empresa['roi_estimado']
    selic = SELIC_ATUAL
    
    if selic > roi:
        diferenca = selic - roi
        impacto_plr = (diferenca / 100) * empresa['plr_devido']
        
        return {
            'status': 'CRITICO',
            'diferenca': diferenca,
            'impacto_plr': impacto_plr,
            'mensagem': f"Selic {selic}% > ROI {roi}% → Rentismo come {diferenca:.1f}% do caixa"
        }
    return {'status': 'OK', 'mensagem': "ROI > Selic"}

def buscar_processos_rj():
    """Simula busca de processos RJ (integração com API do TJ)"""
    # Em produção: API do CNJ/TJ
    processos = []
    for empresa in EMPRESAS:
        processos.append({
            'empresa': empresa['nome'],
            'processo': empresa['processo'],
            'trabalhadores': empresa['trabalhadores'],
            'plr_bloqueado': empresa['plr_devido']
        })
    return processos

def postar_alerta_selic(empresa, impacto):
    """Publica alerta sobre Selic > ROI no Bluesky"""
    
    # Autoridades do trabalho e justiça
    autoridades = " ".join(AUTORIDADES_PLR)
    
    # Texto otimizado (<300 caracteres)
    texto = f"""{autoridades}

🚨 {empresa['nome']}: Selic {SELIC_ATUAL}% > ROI {empresa['roi_estimado']}%

→ PLR de R${empresa['plr_devido']/1e6:.1f}M BLOQUEADO
→ {empresa['trabalhadores']} trabalhadores afetados
→ Processo: {empresa['processo']}

💰 Rentismo: R${impacto['impacto_plr']/1e6:.1f}M/ano perdido

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #PLR #RJ #Trabalhadores"""

    # Limitar tamanho
    if len(texto) > 300:
        texto = texto[:297] + "..."
    
    try:
        client = Client()
        client.login(USERNAME, PASSWORD)
        post = client.send_post(texto)
        print(f"✅ Alerta {empresa['nome']}: {post.uri}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def postar_relatorio_completo():
    """Publica relatório completo com todas empresas"""
    
    print("\n📊 ANALISANDO EMPRESAS EM RJ...")
    print("=" * 50)
    
    alertas_enviados = []
    
    for empresa in EMPRESAS:
        impacto = verificar_impacto_selic(empresa)
        
        print(f"\n🏢 {empresa['nome']}")
        print(f"   ROI: {empresa['roi_estimado']}% | Selic: {SELIC_ATUAL}%")
        print(f"   Status: {impacto['status']}")
        print(f"   {impacto['mensagem']}")
        print(f"   PLR devido: R$ {empresa['plr_devido']:,.0f}")
        print(f"   Trabalhadores: {empresa['trabalhadores']}")
        
        if impacto['status'] == 'CRITICO':
            alertas_enviados.append(empresa['nome'])
            postar_alerta_selic(empresa, impacto)
            time.sleep(5)  # Evitar rate limit
    
    print("\n" + "=" * 50)
    print(f"✅ Alertas enviados para: {', '.join(alertas_enviados)}")
    
    # Post resumo
    if alertas_enviados:
        resumo = f"""@mpt.bsky.social @tst.bsky.social

📋 RELATÓRIO SELIC vs ROI:

{len(alertas_enviados)} empresas em RJ com Selic > ROI

💰 PLR total bloqueado: R$ {sum(e['plr_devido'] for e in EMPRESAS)/1e6:.1f}M
👥 Trabalhadores afetados: {sum(e['trabalhadores'] for e in EMPRESAS)}

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #PLR #JustiçaDoTrabalho"""

        try:
            client = Client()
            client.login(USERNAME, PASSWORD)
            client.send_post(resumo)
            print("✅ Relatório resumo enviado!")
        except Exception as e:
            print(f"❌ Erro no resumo: {e}")

def monitor_continuo():
    """Monitor contínuo a cada hora"""
    print("🚀 Iniciando Monitor SELIC vs ROI")
    print(f"📊 Monitorando {len(EMPRESAS)} empresas em RJ")
    print(f"🔍 Selic atual: {SELIC_ATUAL}% | SELIX ideal: {SELIX_IDEAL}%")
    
    while True:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Verificando...")
        
        for empresa in EMPRESAS:
            impacto = verificar_impacto_selic(empresa)
            if impacto['status'] == 'CRITICO':
                print(f"⚠️ {empresa['nome']}: {impacto['mensagem']}")
        
        # Verificar a cada hora
        time.sleep(3600)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            postar_relatorio_completo()
        elif sys.argv[1] == "--monitor":
            monitor_continuo()
        else:
            print("Uso: python monitor_selic_roi.py [--once|--monitor]")
    else:
        postar_relatorio_completo()

#!/usr/bin/env python3
"""
Notificador automático para Bluesky
Envia alertas sobre Mix Energético e Selic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.monitor_mix_energetico import MonitorMixEnergetico
from monitor.monitor_selic import MonitorSelic

# Adicionar path para post_seguro
sys.path.append('/root/selix/agents/bluesky_bot')
from post_seguro import postar_seguro

def enviar_alerta_mix():
    """Envia alerta sobre mix energético"""
    monitor = MonitorMixEnergetico()
    texto = monitor.gerar_relatorio_stakeholders()
    return postar_seguro(texto)

def enviar_alerta_selic():
    """Envia alerta sobre Selic"""
    monitor = MonitorSelic()
    texto = monitor.gerar_alerta_copom()
    return postar_seguro(texto)

def enviar_alerta_investimentos():
    """Envia alerta sobre investimentos"""
    monitor = MonitorMixEnergetico()
    texto = monitor.gerar_alerta_investimentos()
    return postar_seguro(texto)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python bluesky_notifier.py [mix|selic|investimentos]")
        sys.exit(1)
    
    opcao = sys.argv[1]
    
    if opcao == "mix":
        resultado = enviar_alerta_mix()
        print(f"✅ Alerta Mix: {resultado.get('url')}")
    elif opcao == "selic":
        resultado = enviar_alerta_selic()
        print(f"✅ Alerta Selic: {resultado.get('url')}")
    elif opcao == "investimentos":
        resultado = enviar_alerta_investimentos()
        print(f"✅ Alerta Investimentos: {resultado.get('url')}")
    else:
        print(f"Opção inválida: {opcao}")

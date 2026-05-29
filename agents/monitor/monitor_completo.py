#!/usr/bin/env python3
"""
Monitor Completo SELIX - Alertas automáticos
"""

import sys
import time
sys.path.insert(0, '/root/selix/agents/bluesky_bot')

from datetime import datetime
from fontes_confiaveis import FontesConfi
from post_seguro import postar_seguro

class MonitorCompleto:
    def __init__(self):
        self.fonte = FontesConfi()
        self.ultimos = {}
    
    def verificar_alertas_energia(self) -> bool:
        brent = self.fonte.brent_real()
        brent_anterior = self.ultimos.get('brent', brent['preco'])
        variacao = abs(brent['preco'] - brent_anterior) / brent_anterior if brent_anterior else 0
        
        if variacao > 0.02:
            self.ultimos['brent'] = brent['preco']
            return True
        return False
    
    def gerar_alerta_energia(self) -> str:
        brent = self.fonte.brent_real()
        ttf = self.fonte.ttf_real()
        mistura = self.fonte.recomendar_mistura()
        
        return f"""🚨 ALERTA SELIX - ENERGIA

🛢️ BRENT: US$ {brent['preco']}
🔥 TTF: € {ttf['preco']}/MWh

✅ RECOMENDAÇÃO: {mistura['mistura']} ({mistura['tempo']})

🔗 github.com/scoobiii/selix
#SELIX #Energia

⚠️ Não é recomendação de investimento."""
    
    def monitorar(self, intervalo=300):
        print("🚀 Monitor SELIX Iniciado")
        print(f"⏱️  Intervalo: {intervalo}s")
        
        while True:
            try:
                if self.verificar_alertas_energia():
                    print(f"[{datetime.now()}] ⚡ Alerta Energia!")
                    resultado = postar_seguro(self.gerar_alerta_energia())
                    print(f"   ✅ {resultado.get('url')}")
                time.sleep(intervalo)
            except KeyboardInterrupt:
                print("\n👋 Encerrado")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                time.sleep(intervalo)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        m = MonitorCompleto()
        m.monitorar()
    else:
        print("✅ Monitor configurado. Use --monitor para iniciar")

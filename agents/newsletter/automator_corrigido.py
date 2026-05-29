#!/usr/bin/env python3
"""
Automatiza envio da newsletter SELIX Pro via Substack API
"""

import os
import sys
import requests
from datetime import datetime

sys.path.append('/root/selix/agents/monitor')
sys.path.append('/root/selix/agents/bluesky_bot')

from fontes_confiaveis import FontesConfi
from post_seguro import postar_seguro

class NewsAutomator:
    def __init__(self):
        self.fonte = FontesConfi()
        self.substack_api = "https://substack.com/api/v1"
        self.publication_id = "selixpro"
        self.api_key = os.getenv('SUBSTACK_API_KEY', '')
    
    def buscar_dados(self):
        brent = self.fonte.brent_real()
        selic = self.fonte.selic_real()
        return {
            "brent": brent['preco'],
            "selic_atual": selic['selic'],
            "selic_selix": 9.48,
            "gpa_atual": 1.96,
            "gpa_selix": 17.60,
            "raizen_atual": 0.34,
            "raizen_selix": 11.15
        }
    
    def gerar_conteudo(self, dados):
        return f"""# 🔒 NEWSLETTER SELIX PRO

🚨 Brent: US$ {dados['brent']}
🏦 Selic: {dados['selic_atual']}% → {dados['selic_selix']}%

📈 GPA: R${dados['gpa_atual']} → R${dados['gpa_selix']}
📈 RAIZEN: R${dados['raizen_atual']} → R${dados['raizen_selix']}

⚖️ TrampoForte: PLR prioritário

⚠️ Não é recomendação de investimento."""
    
    def executar(self):
        dados = self.buscar_dados()
        conteudo = self.gerar_conteudo(dados)
        print(conteudo)
        return conteudo

if __name__ == "__main__":
    news = NewsAutomator()
    news.executar()

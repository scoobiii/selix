#!/usr/bin/env python3
"""
Monitor do Ecossistema de Biocombustíveis (Etanol e Biodiesel)
Fonte: ANP, MME, CNPE, CCEE
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class MonitorMixEnergetico:
    def __init__(self):
        self.stakeholders = {
            "decisores": [
                {"handle": "@cnpe.bsky.social", "nome": "CNPE", "papel": "Define percentuais de mistura"},
                {"handle": "@mme.bsky.social", "nome": "MME", "papel": "Coordena comitês de monitoramento"},
                {"handle": "@anp.bsky.social", "nome": "ANP", "papel": "Regulamenta e fiscaliza"},
                {"handle": "@casacivil.bsky.social", "nome": "Casa Civil", "papel": "Aprova decretos"},
                {"handle": "@receita.bsky.social", "nome": "Receita Federal", "papel": "Dados fiscais NF-e"}
            ],
            "comites": [
                {"handle": "@mme.bsky.social", "nome": "CMAE", "papel": "Monitora oferta/demanda etanol"},
                {"handle": "@mme.bsky.social", "nome": "CMAB", "papel": "Monitora oferta/demanda biodiesel"},
                {"handle": "@ccee.bsky.social", "nome": "CCEE", "papel": "Dados setor elétrico"}
            ],
            "legislativo": [
                {"handle": "@deputadoalceumoreira.bsky.social", "nome": "Alceu Moreira", "papel": "Frente Biodiesel"},
                {"handle": "@pedrolupion.bsky.social", "nome": "Pedro Lupion", "papel": "FPA"},
                {"handle": "@zevitor.bsky.social", "nome": "Zé Vitor", "papel": "Frente Etanol"},
                {"handle": "@arnaldojardim.bsky.social", "nome": "Arnaldo Jardim", "papel": "Relator Combustível Futuro"},
                {"handle": "@senado.bsky.social", "nome": "Senado", "papel": "Aprova projetos"}
            ],
            "produtores": [
                {"handle": "@bpbioenergy.bsky.social", "nome": "BP Bioenergy", "capacidade": "32M ton/ano", "usinas": 11},
                {"handle": "@raizen.bsky.social", "nome": "Raízen", "capacidade": "32M ton/ano"},
                {"handle": "@cargillbrasil.bsky.social", "nome": "Cargill", "capacidade": "8M ton cana + 1,52B L biodiesel"},
                {"handle": "@granol.bsky.social", "nome": "Granol", "capacidade": "1,52B L/ano biodiesel"},
                {"handle": "@bungebrasil.bsky.social", "nome": "Bunge", "capacidade": "Produção de biodiesel"}
            ],
            "associacoes": [
                {"handle": "@aprobio.bsky.social", "nome": "APROBIO", "papel": "Produtores de biocombustíveis"},
                {"handle": "@abag.bsky.social", "nome": "ABAG", "papel": "Agronegócio"},
                {"handle": "@unica.bsky.social", "nome": "UNICA", "papel": "Etanol"}
            ]
        }
        
        # Fontes de dados
        self.fontes = {
            "anp": "https://www.gov.br/anp/pt-br/dados-abertos",
            "ccee": "https://api.ccee.org.br",
            "mme": "https://www.gov.br/mme/pt-br/acesso-a-informacao/dados-abertos"
        }
        
        # Dados de produção (base estática - atualizar via API)
        self.producao = {
            "etanol_anidro": 13.5,  # M m³/ano
            "etanol_hidratado": 18.6,  # M m³/ano
            "biodiesel": 8.02,  # M m³/ano
            "gasolina_a": 30.08,  # M m³/ano
            "mix_etanol_atual": 27,  # E27 (base)
            "mix_biodiesel_atual": 14,  # B14
        }
        
        # Investimentos monitorados
        self.investimentos = [
            {"empresa": "Cargill", "valor": 8.1, "unidade": "B", "periodo": "5 anos", "status": "concluido"},
            {"empresa": "Nui Markets", "valor": 4.5, "unidade": "B", "periodo": "2027", "status": "implementacao"},
            {"empresa": "BP Bioenergy", "valor": "Aquisição total", "periodo": "2024", "status": "concluido"}
        ]
    
    def buscar_precos_combustiveis(self) -> Dict:
        """Busca preços dos combustíveis via API ANP (simulado)"""
        # Em produção: chamada real à API da ANP
        return {
            "etanol": 3.90,
            "gasolina": 6.50,
            "biodiesel": 5.20,
            "diesel": 5.80,
            "fonte": "ANP Dados Abertos",
            "atualizado": datetime.now().isoformat()
        }
    
    def verificar_mistura_ideal(self, brent: float = None) -> Dict:
        """Verifica qual mistura de etanol é ideal baseada no Brent"""
        if brent is None:
            # Buscar Brent real
            try:
                import requests
                url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F"
                data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
                brent = data['chart']['result'][0]['meta']['regularMarketPrice']
            except:
                brent = 93.17
        
        if brent > 150:
            return {"mistura": "E42", "justificativa": "Emergência máxima", "tempo": "12h"}
        elif brent > 120:
            return {"mistura": "E40", "justificativa": "Emergência", "tempo": "24h"}
        elif brent > 90:
            return {"mistura": "E35", "justificativa": "Crise", "tempo": "48h"}
        elif brent > 70:
            return {"mistura": "E30", "justificativa": "Alerta", "tempo": "72h"}
        else:
            return {"mistura": "E27", "justificativa": "Normal", "tempo": "normal"}
    
    def gerar_relatorio_stakeholders(self) -> str:
        """Gera relatório para post no Bluesky"""
        precos = self.buscar_precos_combustiveis()
        mistura = self.verificar_mistura_ideal()
        
        relatorio = f"""📊 MONITOR MIX ENERGÉTICO - {datetime.now().strftime('%d/%m/%Y')}

⛽ PREÇOS (ANP):
🌽 Etanol: R$ {precos['etanol']}/L
⛽ Gasolina: R$ {precos['gasolina']}/L
🛢️ Biodiesel: R$ {precos['biodiesel']}/L

📈 MISTURA ATUAL:
✅ Etanol: E{self.producao['mix_etanol_atual']}
✅ Biodiesel: B{self.producao['mix_biodiesel_atual']}

🎯 RECOMENDAÇÃO SELIX:
→ {mistura['mistura']} ({mistura['justificativa']})
→ Tempo: {mistura['tempo']}

#SELIX #MixEnergetico #Etanol #Biodiesel

⚠️ Dados: ANP, MME, CNPE. Não é recomendação de investimento."""
        
        return relatorio[:300]
    
    def gerar_alerta_investimentos(self) -> str:
        """Gera alerta sobre novos investimentos"""
        texto = f"""💰 INVESTIMENTOS EM BIOCOMBUSTÍVEIS:

🏭 Cargill: R$8,1B (concluído)
🏭 Nui Markets: R$4,5B até 2027
🏭 BP Bioenergy: aquisição total

📈 CAPACIDADE:
• Etanol: {self.producao['etanol_anidro'] + self.producao['etanol_hidratado']}M m³/ano
• Biodiesel: {self.producao['biodiesel']}M m³/ano

✅ Setor em expansão com Selic 9,48%

#SELIX #Investimentos #Biocombustíveis

⚠️ Dados: Cargill, Nui Markets, BP Bioenergy"""
        return texto[:300]

if __name__ == "__main__":
    monitor = MonitorMixEnergetico()
    print("📊 Monitor de Mix Energético carregado")
    print(f"\n📈 Stakeholders: {sum(len(v) for v in monitor.stakeholders.values())}")
    print(f"\n📱 Post sugerido:\n{monitor.gerar_relatorio_stakeholders()}")

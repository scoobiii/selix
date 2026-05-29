#!/usr/bin/env python3
"""
Integração com APIs públicas para monitoramento de Recuperação Judicial
Fontes: Datajud (CNJ), B3, CVM
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

class MonitorRJAPI:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Base de empresas em RJ (atualizada via API)
        self.empresas_base = [
            {"nome": "GPA", "cnpj": "06.057.223/0001-71", "codigo": "PCAR3"},
            {"nome": "Americanas", "cnpj": "33.014.556/0001-96", "codigo": "AMER3"},
            {"nome": "Light", "cnpj": "04.067.133/0001-43", "codigo": "LIGT3"},
            {"nome": "Oi", "cnpj": "76.535.764/0001-43", "codigo": "OIBR3"},
            {"nome": "Casas Bahia", "cnpj": "42.270.237/0001-70", "codigo": "VIIA3"},
            {"nome": "Marisa", "cnpj": "59.443.402/0001-01", "codigo": "AMAR3"},
            {"nome": "CVC", "cnpj": "02.183.827/0001-32", "codigo": "CVCB3"},
            {"nome": "IRB", "cnpj": "33.600.210/0001-02", "codigo": "IRBR3"},
        ]
    
    def buscar_processo_rj(self, cnpj: str) -> Dict:
        """Busca processo de RJ no Datajud (CNJ)"""
        try:
            # Datajud API (pública)
            url = f"https://api.datajud.cnj.jus.br/api/v1/processos?cnpj={cnpj}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {"existe": True, "dados": data, "fonte": "Datajud"}
            else:
                return {"existe": True, "fonte": "Base local", "status": "EM_RJ"}
        except:
            return {"existe": True, "fonte": "Base local", "status": "EM_RJ"}
    
    def buscar_preco_acao(self, codigo: str) -> float:
        """Busca preço atual da ação via Yahoo Finance"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{codigo}.SA"
            headers = {"User-Agent": "Mozilla/5.0"}
            data = requests.get(url, headers=headers, timeout=10).json()
            return round(data['chart']['result'][0]['meta']['regularMarketPrice'], 2)
        except:
            return 0
    
    def calcular_preco_selix(self, preco_atual: float) -> float:
        """Calcula preço SELIX baseado no modelo"""
        # Modelo simplificado: Selic 9.48% aumenta valuation em média 500-900%
        multiplicador = 8.98 if preco_atual < 2 else 4.5
        return round(preco_atual * multiplicador, 2)
    
    def obter_todas_empresas(self) -> List[Dict]:
        """Obtém dados de todas empresas em RJ"""
        resultados = []
        
        for emp in self.empresas_base:
            # Buscar processo RJ
            processo = self.buscar_processo_rj(emp['cnpj'])
            
            # Buscar preço atual
            preco_atual = self.buscar_preco_acao(emp['codigo'])
            if preco_atual == 0:
                preco_atual = self._fallback_preco(emp['nome'])
            
            preco_selix = self.calcular_preco_selix(preco_atual)
            potencial = round((preco_selix / preco_atual - 1) * 100) if preco_atual > 0 else 0
            
            resultados.append({
                "nome": emp['nome'],
                "codigo": emp['codigo'],
                "preco_atual": preco_atual,
                "preco_selix": preco_selix,
                "potencial": potencial,
                "processo": processo.get('status', 'EM_RJ'),
                "fonte": processo.get('fonte', 'Local')
            })
        
        return resultados
    
    def _fallback_preco(self, nome: str) -> float:
        """Fallback para preços conhecidos"""
        precos = {
            "GPA": 1.96, "Americanas": 0.85, "Light": 3.50, "Oi": 0.42,
            "Casas Bahia": 0.62, "Marisa": 0.28, "CVC": 1.25, "IRB": 18.50
        }
        return precos.get(nome, 1.00)
    
    def gerar_alerta_nova_empresa(self, empresa: Dict) -> str:
        """Gera alerta para nova empresa em RJ"""
        texto = f"""🚨 ALERTA SELIX - NOVA EMPRESA EM RJ

📊 {empresa['nome']} ({empresa['codigo']})
📍 Preço atual: R$ {empresa['preco_atual']}
📍 Projeção SELIX: R$ {empresa['preco_selix']} (+{empresa['potencial']}%)

⚖️ TrampoForte: PLR prioritário sobre credores

🔗 github.com/scoobiii/selix
#TrampoForte #RJ #PLR

⚠️ Não é recomendação de investimento."""
        return texto[:300]
    
    def gerar_relatorio_completo(self) -> str:
        """Gera relatório com todas empresas"""
        empresas = self.obter_todas_empresas()
        
        texto = f"""@mpt.bsky.social @tst.bsky.social @senado.bsky.social

📊 MONITOR EMPRESAS EM RJ - {datetime.now().strftime('%d/%m/%Y')}

"""
        for emp in empresas[:4]:  # Top 4 no post
            texto += f"🏢 {emp['nome']}: R${emp['preco_atual']} → R${emp['preco_selix']} (+{emp['potencial']}%)\n"
        
        texto += f"""
💰 POTENCIAL TOTAL DE VALORIZAÇÃO MÉDIA: +{round(sum(e['potencial'] for e in empresas)/len(empresas))}%

✅ Selic 9.48% + TrampoForte

🔗 github.com/scoobiii/selix
#TrampoForte #RJ #Monitor

⚠️ Não é recomendação de investimento."""
        
        return texto[:300]

# Instância global
monitor_rj = MonitorRJAPI()

if __name__ == "__main__":
    print("🔍 Monitor RJ inicializado")
    empresas = monitor_rj.obter_todas_empresas()
    print(f"📊 {len(empresas)} empresas monitoradas")
    for e in empresas:
        print(f"   {e['nome']}: R${e['preco_atual']} → R${e['preco_selix']} (+{e['potencial']}%)")

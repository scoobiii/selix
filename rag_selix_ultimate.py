#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_selix_ultimate.py - RAG completo com LLM local no A23
# Versão: 1.0.0-GOS3
# Responsabilidade: Responder stakeholders com dados reais + LLM local

import os
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# ========== CONFIGURAÇÕES ==========
OLLAMA_URL = "http://localhost:11434"
MODELO = "llama3.2:1b"  # Modelo leve para A23 (1.3B parâmetros)
# Alternativas: "phi3:mini" (3.8B), "tinyllama" (1.1B), "qwen2:0.5b"

YAHOO_API = "https://query1.finance.yahoo.com/v8/finance/chart/"

# ========== COLETA DE DADOS REAIS ==========
def get_preco_yahoo(simbolo: str) -> Dict:
    """Obtém preço em tempo real via Yahoo Finance"""
    try:
        url = f"{YAHOO_API}{simbolo}"
        params = {'interval': '1d', 'range': '1d'}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        preco = meta.get('regularMarketPrice', 0)
        variacao = meta.get('regularMarketChangePercent', 0)
        return {'preco': round(preco, 2), 'variacao': round(variacao, 2), 'success': True}
    except Exception as e:
        return {'preco': 0, 'variacao': 0, 'success': False, 'erro': str(e)}

def get_noticias_ddg(query: str, max_results: int = 5) -> List[str]:
    """Busca notícias via DuckDuckGo"""
    url = "https://api.duckduckgo.com/"
    params = {'q': query, 'format': 'json', 'no_html': 1}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        noticias = []
        if data.get('Abstract'):
            noticias.append(data['Abstract'][:300])
        for topic in data.get('RelatedTopics', [])[:max_results]:
            if isinstance(topic, dict) and topic.get('Text'):
                noticias.append(topic['Text'][:300])
        return noticias
    except:
        return []

def get_dados_selix() -> Dict[str, Any]:
    """Coleta todos os dados necessários para o RAG"""
    
    # Preços das empresas
    empresas = {
        'GPA (PCAR3)': get_preco_yahoo('PCAR3.SA'),
        'Raízen (RAIZ4)': get_preco_yahoo('RAIZ4.SA'),
        'Petrobras (PETR4)': get_preco_yahoo('PETR4.SA'),
        'Brent': get_preco_yahoo('BZ=F'),
        'WTI': get_preco_yahoo('CL=F'),
    }
    
    # Notícias relevantes
    noticias = {
        'selic': get_noticias_ddg('Selic Brasil juros'),
        'gpa': get_noticias_ddg('GPA Pão de Açúcar resultados'),
        'raizen': get_noticias_ddg('Raízen resultados'),
        'petrobras': get_noticias_ddg('Petrobras'),
    }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'precos': empresas,
        'noticias': noticias,
        'selic_ideal': 9.25,
        'selic_atual': 13.25,
        'economia_anual': 270,  # bilhões
        'pib_per_capita_projetado': 130000,
        'b3_valuation_projetado': 10  # trilhões
    }

# ========== RAG COM LLM LOCAL ==========
def query_ollama(prompt: str, contexto: str) -> str:
    """Consulta o LLM local rodando no Ollama"""
    full_prompt = f"""Você é o SELIX, um sistema de inteligência econômica que responde stakeholders. 
Use APENAS os dados fornecidos. Se não souber, diga "Não tenho essa informação nos dados atuais".

CONTEXTO:
{contexto}

PERGUNTA:
{prompt}

RESPOSTA (seja direto, objetivo, use emojis quando apropriado, mencione fontes):"""

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={'model': MODELO, 'prompt': full_prompt, 'stream': False},
            timeout=30
        )
        return resp.json().get('response', 'Erro ao gerar resposta')
    except Exception as e:
        return f"⚠️ LLM local indisponível: {e}\n\nUse os dados brutos abaixo:\n{contexto[:500]}"

def responder_stakeholder(stakeholder: str, pergunta: str) -> str:
    """Responde um stakeholder usando RAG + LLM local"""
    
    dados = get_dados_selix()
    
    # Monta contexto específico por stakeholder
    contextos = {
        'trabalhador': f"""
Dados econômicos atuais:
- Selic atual: {dados['selic_atual']}%
- Selic ideal (Selix): {dados['selic_ideal']}%
- Economia anual se Selic cair: R${dados['economia_anual']} bilhões
- Preço GPA: R${dados['precos']['GPA (PCAR3)']['preco']} ({dados['precos']['GPA (PCAR3)']['variacao']:+}%)
- Preço Raízen: R${dados['precos']['Raízen (RAIZ4)']['preco']} ({dados['precos']['Raízen (RAIZ4)']['variacao']:+}%)
- Notícias: {dados['noticias']['gpa'][:200] if dados['noticias']['gpa'] else 'Nenhuma notícia recente'}
""",
        'investidor': f"""
Dados de mercado:
- B3 projeção com Selic 9,25%: US$ {dados['b3_valuation_projetado']} trilhões
- PIB per capita projetado: US$ {dados['pib_per_capita_projetado']:,}
- Brent: US${dados['precos']['Brent']['preco']} ({dados['precos']['Brent']['variacao']:+}%)
- WTI: US${dados['precos']['WTI']['preco']} ({dados['precos']['WTI']['variacao']:+}%)
- Notícias mercado: {dados['noticias']['selic'][:200] if dados['noticias']['selic'] else 'Nenhuma'}
""",
        'governo': f"""
Indicadores macro:
- Selic atual: {dados['selic_atual']}% (ideal: {dados['selic_ideal']}%)
- Economia anual potencial: R$ {dados['economia_anual']} bilhões
- Projeção PIB per capita 10 anos: US$ {dados['pib_per_capita_projetado']:,}
- Preço do petróleo (Brent): US${dados['precos']['Brent']['preco']}
""",
        'ambientalista': f"""
Energia e clima:
- Preço Brent: US${dados['precos']['Brent']['preco']}
- Preço WTI: US${dados['precos']['WTI']['preco']}
- Selic alta ({dados['selic_atual']}%) encarece financiamento verde
- Selic ideal ({dados['selic_ideal']}%) liberaria R$ {dados['economia_anual']} bi/ano para energia solar
"""
    }
    
    contexto = contextos.get(stakeholder, contextos['trabalhador'])
    contexto += f"\n\nPergunta específica: {pergunta}"
    
    return query_ollama(pergunta, contexto)

# ========== INTERFACE ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG - Respostas Inteligentes para Stakeholders")
    print("=" * 60)
    
    # Verifica se Ollama está rodando
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            print("⚠️ Ollama não está rodando. Execute: ollama serve")
            print("   E depois: ollama pull llama3.2:1b")
    except:
        print("❌ Ollama não está rodando!")
        print("   Para ativar: cd /root/selix && ollama serve &")
        print("   E depois: ollama pull llama3.2:1b")
        exit(1)
    
    # Testes
    test_cases = [
        ('trabalhador', 'Por que a Selic alta está travando minha PLR?'),
        ('investidor', 'Qual o upside da GPA e Raízen com Selic 9,25%?'),
        ('governo', 'Quanto o governo economizaria com Selic a 9,25%?'),
        ('ambientalista', 'Como a Selic afeta o financiamento de energia solar?')
    ]
    
    for stakeholder, pergunta in test_cases:
        print(f"\n{'='*60}")
        print(f"👥 Stakeholder: {stakeholder.upper()}")
        print(f"❓ Pergunta: {pergunta}")
        print(f"{'='*60}")
        
        resposta = responder_stakeholder(stakeholder, pergunta)
        print(f"💬 Resposta SELIX:\n{resposta}\n")
        print("-" * 60)

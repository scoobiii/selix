#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_selix_ultimate_fixed.py - RAG com Ollama funcionando
# Versão: 2.0.0-GOS3

import os
import json
import requests
import sqlite3
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
OLLAMA_URL = "http://localhost:11434"
MODELO = "llama3.2:1b"
DB_PATH = "/root/selix/selix.db"

def get_dados_reais():
    """Busca dados reais do banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Busca último Brent
    brent = conn.execute("SELECT price, timestamp FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
    
    # Busca última Selic
    selic = conn.execute("SELECT rate, timestamp FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    
    # Busca empresas em RJ
    empresas = conn.execute("SELECT codigo_b3, nome, status FROM empresas_rj LIMIT 5").fetchall()
    
    conn.close()
    
    return {
        'brent': brent['price'] if brent else 97.36,
        'selic': selic['rate'] if selic else 13.25,
        'empresas_rj': [dict(e) for e in empresas],
        'selic_ideal': 9.25,
        'economia_anual': 270,
        'pib_per_capita_projetado': 130000,
        'b3_valuation_projetado': 10
    }

def query_ollama(prompt, contexto):
    """Consulta Ollama com timeout e retry"""
    full_prompt = f"""Você é o SELIX, um sistema de inteligência econômica.
Use APENAS os dados abaixo. Seja direto, use emojis quando apropriado.

DADOS ATUAIS:
{contexto}

PERGUNTA DO USUÁRIO: {prompt}

RESPOSTA (máximo 3 parágrafos, seja prático):"""
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={'model': MODELO, 'prompt': full_prompt, 'stream': False},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get('response', 'Resposta gerada com sucesso.')
        else:
            return f"⚠️ Ollama retornou status {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama não está rodando. Execute: ollama serve"
    except Exception as e:
        return f"⚠️ Erro: {e}"

def responder_stakeholder(stakeholder, pergunta):
    """Responde stakeholder com dados reais"""
    dados = get_dados_reais()
    
    contextos = {
        'trabalhador': f"""
- Selic atual: {dados['selic']}%
- Selic ideal (Selix): {dados['selic_ideal']}%
- Economia anual se Selic cair: R${dados['economia_anual']} bilhões
- Empresas em RJ: {', '.join([e['codigo_b3'] for e in dados['empresas_rj']])}
- Impacto na PLR: Selic alta (>ROI) trava pagamento de PLR
""",
        'investidor': f"""
- B3 projeção com Selic 9,25%: US$ {dados['b3_valuation_projetado']} trilhões
- PIB per capita projetado: US$ {dados['pib_per_capita_projetado']:,}
- Brent: US${dados['brent']}
- Empresas com potencial: GPA, Raízen (monitoramento)
""",
        'governo': f"""
- Selic atual: {dados['selic']}% (ideal: {dados['selic_ideal']}%)
- Economia anual potencial: R$ {dados['economia_anual']} bilhões
- PIB per capita 10 anos: US$ {dados['pib_per_capita_projetado']:,}
""",
        'ambientalista': f"""
- Preço Brent: US${dados['brent']}
- Selic atual: {dados['selic']}% (alta encarece financiamento verde)
- Selic ideal: {dados['selic_ideal']}% liberaria R${dados['economia_anual']} bi/ano para energia solar
"""
    }
    
    contexto = contextos.get(stakeholder, contextos['trabalhador'])
    return query_ollama(pergunta, contexto)

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG v2.0 - Com Ollama")
    print("=" * 60)
    
    # Verifica Ollama
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code != 200:
            print("❌ Ollama não está respondendo")
            print("   Execute: ollama serve")
            exit(1)
        print("✅ Ollama conectado")
    except:
        print("❌ Ollama não está rodando")
        print("   Execute: ollama serve")
        exit(1)
    
    # Testes
    testes = [
        ('trabalhador', 'Por que a Selic alta trava minha PLR?'),
        ('investidor', 'Qual o potencial da GPA e Raízen com Selic 9,25%?'),
        ('governo', 'Quanto o governo economizaria com Selic a 9,25%?'),
        ('ambientalista', 'Como a Selic afeta energia solar?')
    ]
    
    for stakeholder, pergunta in testes:
        print(f"\n{'='*60}")
        print(f"👤 {stakeholder.upper()}")
        print(f"❓ {pergunta}")
        print(f"{'='*60}")
        
        resposta = responder_stakeholder(stakeholder, pergunta)
        print(f"💬 {resposta}\n")

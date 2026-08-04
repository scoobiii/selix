#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_selix_otimizado.py - RAG otimizado para A23
# Versão: 4.0.0-GOS3

import os
import json
import sqlite3
import requests
from datetime import datetime
from functools import lru_cache

OLLAMA_URL = "http://localhost:11434"
MODELO = "selix-model-fast"  # Modelo quantizado e otimizado
DB_PATH = "/root/selix/selix.db"
TIMEOUT = 15  # Timeout menor (15s)

# Cache de respostas (expira a cada 5 minutos)
CACHE = {}
CACHE_TTL = 300

@lru_cache(maxsize=128)
def get_dados_reais():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    brent = conn.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
    selic = conn.execute("SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    conn.close()
    return {
        'brent': brent['price'] if brent else 97.36,
        'selic': selic['rate'] if selic else 14.25,
        'timestamp': datetime.now().isoformat()
    }

def query_ollama(pergunta, dados):
    """Consulta Ollama com timeout curto"""
    prompt = f"""Dados: Selic {dados['selic']}% | Brent ${dados['brent']}
Pergunta: {pergunta}
Resposta direta:"""
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={'model': MODELO, 'prompt': prompt, 'stream': False, 'temperature': 0.5, 'num_predict': 150},
            timeout=TIMEOUT
        )
        if resp.status_code == 200:
            texto = resp.json().get('response', '')
            # Remove textos estranhos que o modelo pode gerar
            if len(texto) > 10 and not texto.startswith("user:"):
                return texto[:500]
    except requests.exceptions.Timeout:
        print("⏱️ Timeout - usando fallback")
    except Exception as e:
        print(f"⚠️ Erro: {e}")
    return None

# Respostas diretas (fallback rápido)
RESPOSTAS_DIRETAS = {
    "selic": "✅ Selic ideal: 9,25% | Atual: 14,25% | Economia: R$270 bi/ano",
    "plr": "📉 PLR travada pela Selic alta. Com 9,25%, empresas voltam a pagar PLR.",
    "gpa": "📈 GPA: +68% com Selic 9,25% (R$12,50 → R$21,00)",
    "raizen": "📈 Raízen: +76% com Selic 9,25% (R$2,80 → R$4,93)",
    "governo": "💰 Governo economiza R$270 bi/ano com Selic 9,25%",
    "solar": "☀️ Selic 9,25% viabiliza +100 GW solares em 10 anos",
    "brent": "🛢️ Brent: monitorado via Yahoo Finance. Acima de US$120 exige E35/B20",
}

def responder(pergunta, usar_llm=True):
    """Responde usando cache, fallback rápido ou LLM"""
    dados = get_dados_reais()
    pergunta_lower = pergunta.lower()
    
    # 1. Cache
    cache_key = f"{pergunta}_{dados['brent']}_{dados['selic']}"
    if cache_key in CACHE and (datetime.now() - CACHE[cache_key]['time']).seconds < CACHE_TTL:
        return CACHE[cache_key]['resposta']
    
    # 2. Fallback rápido por palavra-chave
    for key, resp in RESPOSTAS_DIRETAS.items():
        if key in pergunta_lower:
            resposta = f"{resp}\n📊 Dados: Selic {dados['selic']}% | Brent ${dados['brent']}"
            CACHE[cache_key] = {'resposta': resposta, 'time': datetime.now()}
            return resposta
    
    # 3. LLM (opcional, só se necessário)
    if usar_llm:
        resposta_llm = query_ollama(pergunta, dados)
        if resposta_llm:
            resposta = f"{resposta_llm}\n📊 Selic {dados['selic']}% | Brent ${dados['brent']}"
            CACHE[cache_key] = {'resposta': resposta, 'time': datetime.now()}
            return resposta
    
    # 4. Fallback genérico
    return f"📊 Selic {dados['selic']}% | Brent ${dados['brent']} | Ideal: 9,25%. +info: github.com/scoobiii/selix"

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG v4.0 - Otimizado para A23")
    print("=" * 60)
    
    dados = get_dados_reais()
    print(f"📊 Dados atuais: Selic {dados['selic']}% | Brent ${dados['brent']}\n")
    
    perguntas = [
        "Qual a Selic ideal?",
        "Por que minha PLR está travada?",
        "Qual o potencial da GPA?",
        "Quanto o governo economiza?",
        "Como a Selic afeta energia solar?",
        "Qual o preço do Brent?"
    ]
    
    for p in perguntas:
        print(f"❓ {p}")
        print(f"💬 {responder(p, usar_llm=False)}\n")  # usar_llm=False para evitar timeout
        print("-" * 50)

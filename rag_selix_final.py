#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_selix_final.py - Versão final com modelo fine-tuned
# Versão: 3.0.0-GOS3

import os
import json
import sqlite3
import requests
from datetime import datetime
from difflib import SequenceMatcher

OLLAMA_URL = "http://localhost:11434"
MODELO = "selix-model"  # Modelo fine-tuned
DB_PATH = "/root/selix/selix.db"

# Fallback para matching local (caso Ollama falhe)
FALLBACK_RESPOSTAS = {
    "selic": "✅ Selic ideal: 9,25% (1 dígito). Selic atual: 14,25% | Economia anual: R$270 bi",
    "plr": "📉 PLR travada pela Selic alta. Com 9,25%, empresas voltam a pagar PLR.",
    "gpa": "📈 GPA (PCAR3): +68% com Selic 9,25% (R$12,50 → R$21,00)",
    "raizen": "📈 Raízen (RAIZ4): +76% com Selic 9,25% (R$2,80 → R$4,93)",
    "governo": "💰 Governo economiza R$270 bi/ano com Selic 9,25%",
    "solar": "☀️ Selic 9,25% viabiliza energia solar: +100 GW em 10 anos",
}

def get_dados_reais():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    brent = conn.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
    selic = conn.execute("SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    conn.close()
    return {
        'brent': brent['price'] if brent else 97.36,
        'selic': selic['rate'] if selic else 14.25,
    }

def query_ollama(pergunta, dados):
    prompt = f"""Dados atuais: Selic {dados['selic']}% | Brent US${dados['brent']}

Pergunta: {pergunta}

Responda como SELIX, especialista em economia brasileira. Seja direto e use emojis."""
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={'model': MODELO, 'prompt': prompt, 'stream': False, 'temperature': 0.7},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
    except Exception as e:
        print(f"⚠️ Ollama erro: {e}")
    return None

def responder(pergunta):
    dados = get_dados_reais()
    
    # Tenta LLM primeiro
    resposta = query_ollama(pergunta, dados)
    if resposta and len(resposta) > 10:
        return resposta
    
    # Fallback por keyword
    p_lower = pergunta.lower()
    for key, resp in FALLBACK_RESPOSTAS.items():
        if key in p_lower:
            return resp + f"\n\n📊 Dados: Selic {dados['selic']}% | Brent ${dados['brent']}"
    
    return f"📊 Com Selic {dados['selic']}% e Brent ${dados['brent']}, Selic ideal é 9,25%. +info: github.com/scoobiii/selix"

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG v3.0 - Modelo Fine-tuned")
    print("=" * 60)
    
    dados = get_dados_reais()
    print(f"📊 Dados: Selic {dados['selic']}% | Brent ${dados['brent']}\n")
    
    perguntas = [
        "Qual a Selic ideal?",
        "Por que minha PLR está travada?",
        "Qual o potencial da GPA?",
        "Quanto o governo economiza?",
        "Como a Selic afeta energia solar?"
    ]
    
    for p in perguntas:
        print(f"❓ {p}")
        print(f"💬 {responder(p)}\n")
        print("-" * 50)

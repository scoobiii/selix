#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_selix_with_sentiment.py
# Versão: 5.0.0-GOS3
# Responsabilidade: RAG com contexto de sentimento real de mercado
# Assinatura: GOS3/2026-06-03/src/selix/rag_selix_with_sentiment.py

import os
import sqlite3
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# ========== CONFIGURAÇÕES ==========
OLLAMA_URL = "http://localhost:11434"
MODELO = "smollm2:135m"  # ou "qwen2:0.5b"
DB_PATH = "/root/selix/selix.db"

# Respostas de fallback (apenas se LLM falhar)
FALLBACK_RESPOSTAS = {
    "selic": "✅ Selic ideal: 9,25% | Atual: 14,25% | Economia anual: R$270 bi",
    "plr": "📉 PLR travada pela Selic alta. Com 9,25%, empresas voltam a pagar PLR.",
    "gpa": "📈 GPA (PCAR3): +68% com Selic 9,25% (R$12,50 → R$21,00)",
    "raizen": "📈 Raízen (RAIZ4): +76% com Selic 9,25% (R$2,80 → R$4,93)",
    "governo": "💰 Governo economiza R$270 bi/ano com Selic 9,25%",
    "solar": "☀️ Selic 9,25% viabiliza +100 GW solares em 10 anos",
    "brent": "🛢️ Brent: monitorado via Yahoo Finance. Acima de US$120 exige E35/B20",
}

def get_dados_reais() -> Dict[str, Any]:
    """Busca dados reais do banco (Brent, Selic, sentimento)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Brent
    brent = c.execute("SELECT price, timestamp FROM brent WHERE success=1 ORDER BY timestamp DESC LIMIT 1").fetchone()
    # Selic
    selic = c.execute("SELECT rate, timestamp FROM selic WHERE success=1 ORDER BY timestamp DESC LIMIT 1").fetchone()
    # Sentimento (mais recente)
    sentimento = c.execute("SELECT sentimento, score, criado_em FROM sentimento_indicadores ORDER BY criado_em DESC LIMIT 1").fetchone()
    conn.close()
    
    return {
        'brent': brent['price'] if brent else 97.36,
        'brent_data': brent['timestamp'] if brent else None,
        'selic': selic['rate'] if selic else 14.25,
        'selic_data': selic['timestamp'] if selic else None,
        'sentimento': sentimento['sentimento'] if sentimento else "neutro",
        'sentimento_score': sentimento['score'] if sentimento else 0.0,
        'sentimento_data': sentimento['criado_em'] if sentimento else None,
        'selic_ideal': 9.25,
        'economia_anual': 270,
        'pib_per_capita': 130000,
        'b3_valuation': 10
    }

def query_ollama(pergunta: str, contexto: str) -> Optional[str]:
    """Consulta o LLM local via Ollama."""
    full_prompt = f"""{contexto}

Pergunta: {pergunta}

Responda como SELIX, especialista em economia brasileira. Use os dados acima. Seja direto, use emojis e mencione o sentimento de mercado quando relevante."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={'model': MODELO, 'prompt': full_prompt, 'stream': False, 'temperature': 0.7},
            timeout=45
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
    except Exception as e:
        print(f"⚠️ Ollama erro: {e}")
    return None

def responder(pergunta: str) -> str:
    """Responde usando dados reais + sentimento + LLM (ou fallback)."""
    dados = get_dados_reais()
    
    # Monta contexto enriquecido com sentimento
    contexto = f"""
Dados econômicos atuais (fonte: BCB, Yahoo Finance, Bloomberg):
- Selic real: {dados['selic']}% (atualizado em {dados['selic_data']})
- Selic ideal (Selix): {dados['selic_ideal']}%
- Brent: US${dados['brent']} (atualizado em {dados['brent_data']})
- Sentimento de mercado: **{dados['sentimento'].upper()}** (score {dados['sentimento_score']}, baseado em notícias financeiras reais, coletado em {dados['sentimento_data']})
- Economia anual com Selic ideal: R${dados['economia_anual']} bi
- B3 potencial: US${dados['b3_valuation']} tri
- PIB per capita potencial: US${dados['pib_per_capita']}
"""
    # Tenta LLM primeiro
    resposta = query_ollama(pergunta, contexto)
    if resposta and len(resposta) > 10:
        return resposta
    
    # Fallback por palavra-chave
    pergunta_lower = pergunta.lower()
    for key, resp in FALLBACK_RESPOSTAS.items():
        if key in pergunta_lower:
            return f"{resp}\n\n📊 Sentimento atual: {dados['sentimento'].upper()} (score {dados['sentimento_score']})"
    
    return f"📊 Selic {dados['selic']}% | Brent ${dados['brent']} | Sentimento {dados['sentimento'].upper()} | Selic ideal 9,25%. +info: github.com/scoobiii/selix"

def atualizar_treino_rag(pergunta: str, resposta: str, sentimento: str):
    """Registra interação para fine-tuning futuro (expansão do RAG)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interacoes_rag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT,
            resposta TEXT,
            sentimento TEXT,
            timestamp TEXT
        )
    """)
    conn.execute("INSERT INTO interacoes_rag (pergunta, resposta, sentimento, timestamp) VALUES (?, ?, ?, ?)",
                 (pergunta, resposta, sentimento, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print("📝 Interação registrada para fine-tuning futuro.")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG v5.0 - Com Sentimento Real de Mercado")
    print("=" * 60)
    
    dados = get_dados_reais()
    print(f"📊 Dados atuais:")
    print(f"   Selic: {dados['selic']}% | Brent: ${dados['brent']} | Sentimento: {dados['sentimento'].upper()} (score {dados['sentimento_score']})")
    
    perguntas = [
        "Qual a Selic ideal?",
        "Por que minha PLR está travada?",
        "Qual o potencial da GPA?",
        "Quanto o governo economiza?",
        "Como a Selic afeta energia solar?",
        "Qual o sentimento do mercado hoje?"
    ]
    
    for p in perguntas:
        print(f"\n❓ {p}")
        resp = responder(p)
        print(f"💬 {resp}")
        # Registrar para treino futuro
        atualizar_treino_rag(p, resp, dados['sentimento'])
        print("-" * 50)

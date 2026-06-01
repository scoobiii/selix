#!/usr/bin/env python3
"""
Selix Agent – DuckDuckGo como tool, Ollama como LLM
Zero manutenção de APIs externas.
"""

import os
import sys
import sqlite3
import requests
from duckduckgo_search import DDGS

sys.path.insert(0, '/root/selix')
from dotenv import load_dotenv

load_dotenv('/root/selix/.env')
DB_PATH = os.getenv('SELIX_DB_PATH', '/root/selix/selix.db')
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "phi3:mini"  # ou qwen2.5:0.5b

# ============================================================
# TOOLS
# ============================================================
def get_brent():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT preco_usd FROM commodities ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_selic():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT valor FROM selic_historico ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def search_web(pergunta: str) -> str:
    """Busca no DuckDuckGo e retorna contexto"""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(pergunta, max_results=3, region='br-pt')
            if results:
                return "\n\n".join([f"- {r['body'][:300]}" for r in results if r['body']])
    except Exception as e:
        print(f"Erro na busca: {e}")
    return ""

# ============================================================
# LLM CALL
# ============================================================
def call_ollama(prompt: str) -> str:
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 256, "temperature": 0.7}
        }, timeout=60)
        if resp.status_code == 200:
            return resp.json().get('response', '')
    except Exception as e:
        return f"Erro: {e}"
    return ""

# ============================================================
# ROUTER + RESPOSTA
# ============================================================
def responder(pergunta: str) -> str:
    # 1. Tenta responder com dados locais primeiro
    brent = get_brent()
    selic = get_selic()
    
    local_context = []
    if brent:
        local_context.append(f"Brent: US${brent}")
    if selic:
        local_context.append(f"Selic: {selic}%")
    
    local_info = "; ".join(local_context) if local_context else "Dados locais indisponíveis"
    
    # 2. Decide se precisa de busca na web
    need_web = any(kw in pergunta.lower() for kw in [
        'preço', 'cotação', 'brent', 'petróleo', 'dólar', 'euro',
        'gasolina', 'diesel', 'selic', 'juros'
    ])
    
    if need_web:
        contexto = search_web(pergunta)
        if contexto:
            prompt = f"""{local_info}

Busca na web:
{contexto}

Pergunta: {pergunta}

Responda com base nos dados acima. Use português. Seja direto."""
        else:
            prompt = f"{local_info}\n\nPergunta: {pergunta}\n\nResponda com base no seu conhecimento, mas avise se não souber."
    else:
        prompt = f"{local_info}\n\nPergunta: {pergunta}\n\nResponda em português, de forma direta."
    
    return call_ollama(prompt)

# ============================================================
# TESTE INTERATIVO
# ============================================================
if __name__ == "__main__":
    print("Selix Agent (DuckDuckGo + Ollama) iniciado.")
    print(f"Modelo: {DEFAULT_MODEL}")
    print("Digite 'exit' para sair.\n")
    
    while True:
        pergunta = input("> ")
        if pergunta.lower() in ['exit', 'quit']:
            break
        resposta = responder(pergunta)
        print(f"\n{resposta}\n{'-'*50}\n")

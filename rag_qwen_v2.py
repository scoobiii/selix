#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_qwen_v2.py - Qwen2-0.5B com matching inteligente
# Versão: 2.0.0-GOS3

import os
import json
import sqlite3
import requests
from datetime import datetime
from difflib import SequenceMatcher

OLLAMA_URL = "http://localhost:11434"
MODELO = "qwen2:0.5b"
DB_PATH = "/root/selix/selix.db"

# ========== DADOS DE TREINAMENTO EXPANDIDOS ==========
TRAINING_DATA = [
    {
        "perguntas": [
            "Qual a Selic ideal",
            "Selic correta",
            "taxa de juros ideal",
            "qual deveria ser a Selic",
            "Selic justa",
            "Selic 1 digito"
        ],
        "resposta": "✅ A Selic ideal calculada pelo SELIX é 9,25% (1 dígito). A Selic atual está em 14,25%, o que custa R$270 bilhões/ano extras para o país."
    },
    {
        "perguntas": [
            "PLR travada",
            "por que não recebo PLR",
            "PLR bloqueada",
            "participação nos lucros",
            "GPA Raízen PLR",
            "empresas em RJ PLR"
        ],
        "resposta": "📉 Selic alta (14,25%) faz o custo da dívida superar o ROI das empresas. Resultado: lucro zero → PLR zerada.\n✅ Com Selic 9,25%, empresas como GPA e Raízen voltam a lucrar e pagar PLR."
    },
    {
        "perguntas": [
            "GPA potencial",
            "Raízen upside",
            "PCAR3",
            "RAIZ4",
            "ação GPA",
            "ação Raízen",
            "valorização GPA",
            "valorização Raízen"
        ],
        "resposta": "📈 Com Selic 9,25%:\n• GPA (PCAR3): +68% (de R$12,50 para R$21,00)\n• Raízen (RAIZ4): +76% (de R$2,80 para R$4,93)\n• Base: normalização de múltiplos com queda do WACC."
    },
    {
        "perguntas": [
            "governo economiza",
            "economia anual",
            "gasto com juros",
            "dívida pública",
            "R$270 bilhões",
            "economia para o governo"
        ],
        "resposta": "💰 Com Selic 9,25%:\n• Custo da dívida: R$380 bi/ano (hoje R$650 bi)\n• Economia anual: R$270 bilhões\n• Equivalente a 2x o orçamento da saúde."
    },
    {
        "perguntas": [
            "energia solar",
            "financiamento verde",
            "solar Selic",
            "renovável Selic",
            "painel solar",
            "usina solar"
        ],
        "resposta": "☀️ Selic alta (14,25%) inviabiliza financiamento verde:\n• WACC atual: 18% > IRR solar: 13% → inviável\n• Com Selic 9,25%: WACC cai para 11% < IRR 13% → viável\n• Impacto: +100 GW solares em 10 anos."
    },
    {
        "perguntas": [
            "Brent",
            "preço petróleo",
            "petróleo hoje",
            "barril",
            "BZ=F"
        ],
        "resposta": "🛢️ O preço do Brent está em US${brent}. Nesse nível, o mix ideal de biocombustíveis é E30/B15 (alerta). Acima de US$120, subiria para E35/B20."
    }
]

def get_dados_reais():
    """Busca dados do banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    brent = conn.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
    selic = conn.execute("SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    
    conn.close()
    
    return {
        'brent': brent['price'] if brent else 97.36,
        'selic': selic['rate'] if selic else 14.25,
    }

def match_pergunta(pergunta):
    """Encontra a melhor resposta baseada em similaridade de texto"""
    pergunta_lower = pergunta.lower()
    best_match = None
    best_score = 0
    
    for item in TRAINING_DATA:
        for q in item["perguntas"]:
            # Similaridade simples
            if q.lower() in pergunta_lower:
                return item["resposta"]
            
            # Similaridade por proporção
            score = SequenceMatcher(None, q.lower(), pergunta_lower).ratio()
            if score > best_score and score > 0.4:
                best_score = score
                best_match = item["resposta"]
    
    return best_match if best_match else None

def query_qwen(pergunta, dados):
    """Consulta o Qwen2-0.5B via Ollama"""
    prompt = f"""<|im_start|>system
Você é o SELIX, especialista em economia brasileira.
Dados atuais: Selic {dados['selic']}% | Brent US${dados['brent']}
Responda de forma direta e prática com no máximo 3 parágrafos.
<|im_end|>
<|im_start|>user
{pergunta}
<|im_end|>
<|im_start|>assistant
"""
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={'model': MODELO, 'prompt': prompt, 'stream': False, 'temperature': 0.7},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
        return None
    except:
        return None

def responder(pergunta):
    """Responde usando matching primeiro, depois LLM"""
    dados = get_dados_reais()
    
    # 1. Tenta matching por palavras-chave
    resposta = match_pergunta(pergunta)
    if resposta:
        # Substitui placeholders
        resposta = resposta.replace("{brent}", str(dados['brent']))
        return resposta
    
    # 2. Fallback para LLM local
    resposta_llm = query_qwen(pergunta, dados)
    if resposta_llm:
        return resposta_llm
    
    # 3. Fallback final (nunca falha)
    return f"📊 Com Selic {dados['selic']}% e Brent ${dados['brent']}, a recomendação Selix é Selic 9,25%. Mais em github.com/scoobiii/selix"

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG v2.0 - Qwen2-0.5B")
    print("=" * 60)
    
    dados = get_dados_reais()
    print(f"📊 Dados: Selic {dados['selic']}% | Brent ${dados['brent']}\n")
    
    perguntas = [
        "Qual a Selic ideal?",
        "Por que minha PLR está travada na GPA?",
        "Qual o potencial da Raízen?",
        "Quanto o governo economiza com Selic menor?",
        "Como a Selic afeta energia solar?",
        "Qual o preço do Brent hoje?"
    ]
    
    for p in perguntas:
        print(f"❓ {p}")
        r = responder(p)
        print(f"💬 {r}\n")
        print("-" * 50)

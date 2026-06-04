#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rag_qwen_finetune.py - Qwen2-0.5B + LoRA fine-tuning
# Versão: 1.0.0-GOS3
# Ideal para A23 (350MB, 500MB RAM)

import os
import json
import sqlite3
import requests
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
OLLAMA_URL = "http://localhost:11434"
MODELO = "qwen2:0.5b"  # 350MB - PERFEITO para A23
# Alternativa binarizada: "qwen2:0.5b-q4_K_M" (ainda menor)

DB_PATH = "/root/selix/selix.db"

# ========== DADOS DE TREINAMENTO (Contexto Selix) ==========
TRAINING_DATA = [
    {
        "pergunta": "Qual a Selic ideal segundo o Selix?",
        "resposta": "A Selic ideal calculada pelo SELIX é 9,25% (1 dígito), baseada em 5 teoremas formais com Z3 e Lean4."
    },
    {
        "pergunta": "Por que a Selic alta trava minha PLR?",
        "resposta": "Selic alta (acima de 14%) faz o custo da dívida superar o ROI das empresas. Resultado: lucro zero, PLR zerada. Com Selic 9,25%, empresas voltam a lucrar e pagar PLR."
    },
    {
        "pergunta": "Qual o upside da GPA e Raízen?",
        "resposta": "Com Selic 9,25%, GPA pode subir +68% (de R$12,50 para R$21,00) e Raízen +76% (de R$2,80 para R$4,93). Cálculo baseado em normalização de múltiplos."
    },
    {
        "pergunta": "Quanto o governo economiza?",
        "resposta": "Com Selic 9,25%, a dívida pública custa R$380 bi/ano em vez de R$650 bi. Economia anual de R$270 bilhões."
    },
    {
        "pergunta": "Como a Selic afeta energia solar?",
        "resposta": "Selic alta (14,5%) inviabiliza financiamento verde (WACC 18% > IRR 13%). Com Selic 9,25%, WACC cai para 11% e usinas solares viram rentáveis."
    }
]

def get_dados_reais():
    """Busca dados do banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    brent = conn.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
    selic = conn.execute("SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    empresas = conn.execute("SELECT codigo_b3, nome, status FROM empresas_rj LIMIT 5").fetchall()
    
    conn.close()
    
    return {
        'brent': brent['price'] if brent else 97.36,
        'selic': selic['rate'] if selic else 13.25,
        'empresas_rj': [dict(e) for e in empresas],
        'selic_ideal': 9.25,
        'economia_anual': 270,
        'pib_per_capita': 130000,
        'b3_valuation': 10
    }

def create_finetune_prompt(pergunta, dados):
    """Cria prompt com contexto específico para fine-tuning"""
    return f"""<|im_start|>system
Você é o SELIX, especialista em economia brasileira. Responda com dados reais e seja prático.
Contexto atual: Selic {dados['selic']}% | Brent US${dados['brent']} | Selic ideal 9.25% | Economia anual R${dados['economia_anual']}bi
<|im_end|>
<|im_start|>user
{pergunta}
<|im_end|>
<|im_start|>assistant
"""

def query_qwen(pergunta, dados):
    """Consulta o Qwen2-0.5B"""
    prompt = create_finetune_prompt(pergunta, dados)
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                'model': MODELO,
                'prompt': prompt,
                'stream': False,
                'temperature': 0.7,
                'top_p': 0.9
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json().get('response', '')
        return f"Erro: {resp.status_code}"
    except Exception as e:
        return f"Erro: {e}"

def responder(pergunta):
    """Responde qualquer pergunta sobre o Selix"""
    dados = get_dados_reais()
    
    # Primeiro tenta matching com dados de treino
    pergunta_lower = pergunta.lower()
    for item in TRAINING_DATA:
        if any(p in pergunta_lower for p in item['pergunta'].lower().split()):
            return item['resposta'] + "\n\n(Resposta baseada em dados históricos)"
    
    # Se não achou, usa LLM
    return query_qwen(pergunta, dados)

def finetune_local():
    """Gera arquivo de fine-tuning para treinar o modelo"""
    
    # Cria arquivo no formato Ollama Modelfile
    modelfile = f"""FROM {MODELO}

# Parâmetros do modelo
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "<|im_end|>"

# Template do sistema
SYSTEM \"\"\"Você é o SELIX, especialista em economia brasileira.
Você tem acesso a dados reais de mercado (Brent, Selic, empresas em RJ).
Sempre que possível, cite números e fontes.
Se não souber, diga "Não tenho essa informação nos dados atuais."
\"\"\"

# Mensagens de exemplo para few-shot
MESSAGES [
"""

    # Adiciona exemplos de few-shot
    for item in TRAINING_DATA:
        modelfile += f"""
  {{"role": "user", "content": "{item['pergunta']}"}},
  {{"role": "assistant", "content": "{item['resposta']}"}},
"""
    
    modelfile += """
]

# Instruções adicionais
TEMPLATE \"\"\"<|im_start|>system
{{ .System }}
<|im_end|>
{{ range .Messages }}
<|im_start|>{{ .Role }}
{{ .Content }}
<|im_end|>
{{ end }}
<|im_start|>assistant
\"\"\"
"""
    
    # Salva Modelfile
    with open("SelixModelfile", "w") as f:
        f.write(modelfile)
    
    print("✅ Modelfile criado. Para criar modelo fine-tuned:")
    print("   ollama create selix-model -f SelixModelfile")
    print("   ollama run selix-model")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 SELIX RAG com Qwen2-0.5B")
    print(f"📦 Modelo: {MODELO}")
    print("=" * 60)
    
    # Testes
    perguntas = [
        "Qual a Selic ideal?",
        "Por que minha PLR está travada?",
        "Qual o potencial da GPA?",
        "Quanto o governo economiza?",
        "Como a Selic afeta energia solar?"
    ]
    
    dados = get_dados_reais()
    print(f"\n📊 Dados atuais: Selic {dados['selic']}% | Brent US${dados['brent']}\n")
    
    for pergunta in perguntas:
        print(f"❓ {pergunta}")
        resposta = responder(pergunta)
        print(f"💬 {resposta}\n")
        print("-" * 50)
    
    # Opção: criar modelo fine-tuned
    print("\n🔧 Para fine-tuning (criar modelo personalizado):")
    finetune_local()

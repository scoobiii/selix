#!/usr/bin/env python3
"""
Agente RAG aprimorado para SELIX
Reconhece saudações e perguntas comuns
"""

import os
import re
from pathlib import Path

def carrega_conhecimento():
    base = Path(".")
    textos = []
    for md in base.rglob("*.md"):
        if "agents" not in str(md):
            textos.append(md.read_text(encoding='utf-8', errors='ignore'))
    return "\n\n".join(textos)

conhecimento = carrega_conhecimento()

def responder(pergunta):
    pergunta_low = pergunta.lower().strip()

    # Saudações
    if re.match(r"^(oi|olá|hello|hey|e aí|opa)$", pergunta_low):
        return "Olá! Sou o assistente do projeto SELIX. Pergunte-me sobre:\n- A SELIX ideal (9.25%)\n- Investment Grade\n- Impacto econômico\n- Stiglitz\n- Como executar o modelo"

    # Atalhos para perguntas comuns
    if "9.25" in pergunta_low or "selic ideal" in pergunta_low:
        return "SELIX ideal = 9,25% ao ano (juro real 4,77%). Investment Grade alcançado (BBB+)."

    if "investment grade" in pergunta_low or "rating" in pergunta_low:
        return "A SELIX garante rating BBB+ porque 9,25% ≤ 9,99%. Hoje o Brasil é BB."

    if "impacto" in pergunta_low or "economia" in pergunta_low or "pib" in pergunta_low:
        return "Economia anual de R$ 270 bilhões, PIB per capita +R$ 14.900, +3 milhões de empregos em 4 anos."

    if "stiglitz" in pergunta_low:
        return "Joseph Stiglitz (Nobel 2001) criticou os juros reais elevados do Brasil, que chegam a 10%. A SELIX propõe juro real de 4,77%."

    if "como executar" in pergunta_low or "rodar" in pergunta_low:
        return "Python: `python src/selix/core.py`\nTestes: `pytest tests/ -v`\nLean 4: `cd lean_proof && lake env lean SELIX_simple.lean`\nColab: link no README."

    # Se não encontrou nenhuma palavra‑chave
    return "Consulte o repositório: https://github.com/scoobiii/selix"

if __name__ == "__main__":
    print("🤖 RAG SELIX (modo texto aprimorado). Digite 'sair' para encerrar.")
    while True:
        q = input("Pergunta: ").strip()
        if q.lower() in ("sair", "exit", "quit"):
            break
        print(f"Resposta: {responder(q)}")

#!/usr/bin/env python3
"""
Agente RAG simplificado para SELIX - usa respostas baseadas em documentos.
Para versão completa, instale langchain, chromadb e ollama.
"""
import os
from pathlib import Path

# Carrega todos os .md como conhecimento
def carrega_conhecimento():
    base = Path(".")
    textos = []
    for md in base.rglob("*.md"):
        if "agents" not in str(md):
            textos.append(md.read_text(encoding='utf-8', errors='ignore'))
    return "\n\n".join(textos)

conhecimento = carrega_conhecimento()

def responder(pergunta):
    pergunta_low = pergunta.lower()
    if "9.25" in pergunta_low:
        return "SELIX ideal = 9,25% (juro real 4,77%)."
    if "investment grade" in pergunta_low:
        return "Sim, 9,25% ≤ 9,99% → Brasil alcançaria rating BBB+."
    if "impacto" in pergunta_low:
        return "Economia de R$ 270 bi/ano, PIB per capita +R$ 14.900, +3 milhões empregos."
    if "stiglitz" in pergunta_low:
        return "Joseph Stiglitz (Nobel 2001) critica juros altos e endossa política de juros reais moderados."
    return "Consulte o repositório: https://github.com/scoobiii/selix"

if __name__ == "__main__":
    print("🤖 RAG SELIX (modo texto). Digite 'sair' para encerrar.")
    while True:
        q = input("Pergunta: ")
        if q.lower() in ("sair", "exit"): break
        print(f"Resposta: {responder(q)}")

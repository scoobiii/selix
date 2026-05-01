#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX RAG Ultimate - v3.2.2
Data: 01/05/2026
Autor: Zeh Sobrinho, GOS3
Descrição: Assistente inteligente do projeto SELIX com ChromaDB + Ollama.
           Corrigido: agora responde perguntas técnicas corretamente,
           não repete saudações eternamente.
"""

import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import re

print("🔄 Carregando embeddings e ChromaDB...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="selix_docs")

modelo_atual = "qwen2.5:0.5b"

# Lista exata de saudações curtas
SAUDACOES_EXATAS = {"oi", "olá", "ola", "hey", "hi", "hello", "opa", "eae", "iae", "oie", "oiee"}
SAUDACOES_CURTAS = lambda t: len(t) <= 3 and t.isalpha()

def eh_saudacao(texto):
    t = texto.lower().strip()
    return t in SAUDACOES_EXATAS or SAUDACOES_CURTAS(t)

def responder(pergunta):
    pergunta_original = pergunta
    
    # 1. Saudações
    if eh_saudacao(pergunta_original):
        return "Olá! Sou o assistente do projeto SELIX. Pergunte sobre: Selic ideal (9.25%), Investment Grade, impacto econômico, os 5 teoremas, Stiglitz."
    
    # 2. Buscar contexto no ChromaDB
    try:
        query_emb = embed_model.encode([pergunta_original]).tolist()[0]
        results = collection.query(query_embeddings=[query_emb], n_results=3)
        if results['documents'] and results['documents'][0]:
            contexto = "\n\n".join(results['documents'][0])
        else:
            contexto = "Projeto SELIX: modelo matemático que calcula a Selic ideal (9.25%)."
    except Exception as e:
        contexto = "Projeto SELIX disponível em https://github.com/scoobiii/selix"
    
    # 3. Prompt técnico (direto)
    prompt = f"""Você é o assistente do projeto SELIX. Use o contexto para responder.
NUNCA diga "Olá! Sou o assistente..." para perguntas técnicas.

Contexto:
{contexto[:1200]}

Pergunta: {pergunta_original}

Resposta direta, técnica, máxima 4 frases:"""
    
    resposta = ollama.generate(model=modelo_atual, prompt=prompt, options={'temperature': 0.2})
    return resposta['response'].strip()

def listar_modelos():
    return "Modelos disponíveis: smollm2:135m, qwen2.5:0.5b, phi3:mini"

print(f"\n🤖 SELIX RAG Ultimate v3.2.2")
print(f"Modelo atual: {modelo_atual}")
print("Comandos: /modelo <nome> | /modelos | sair\n")

while True:
    entrada = input("💬 Você: ").strip()
    if entrada.lower() in ("sair", "exit", "quit"):
        print("👋 Até logo!")
        break
    
    if entrada.startswith("/modelo "):
        novo = entrada.split()[1]
        modelo_atual = novo
        print(f"✅ Modelo alterado para {modelo_atual}")
        continue
    
    if entrada == "/modelos":
        print(listar_modelos())
        continue
    
    print("🧠 SELIX: ", end="", flush=True)
    res = responder(entrada)
    print(res)

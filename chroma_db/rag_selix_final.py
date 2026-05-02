#!/usr/bin/env python3
# RAG SELIX - versão que respeita a troca de modelo

import chromadb
from sentence_transformers import SentenceTransformer
import ollama

print("🔄 Carregando embeddings...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="selix_docs")

modelo_atual = "qwen2.5:0.5b"  # padrão agora

def responder(pergunta, model_name="qwen2.5:0.5b", top_k=3):
    # Busca documentos relevantes
    query_emb = embed_model.encode([pergunta]).tolist()[0]
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    context = "\n\n".join(results['documents'][0])
    
    # Prompt simplificado para o modelo
    prompt = f"""Baseado nos documentos do projeto SELIX, responda:

Pergunta: {pergunta}

Resposta curta e direta:"""
    
    try:
        resposta = ollama.generate(model=model_name, prompt=prompt, options={'temperature': 0.2})
        return resposta['response'].strip()
    except Exception as e:
        return f"Erro: {str(e)[:100]}"

print("\n🤖 SELIX RAG (versão final)")
print(f"Modelo padrão: {modelo_atual}")
print("Comandos: /modelo <nome>  ou  /modelos  ou  sair")
print("Ex: /modelo qwen2.5:0.5b\n")

while True:
    entrada = input("💬 Você: ").strip()
    if entrada.lower() in ("sair", "exit", "quit"):
        break
    
    if entrada.startswith("/modelo "):
        novo_modelo = entrada.split()[1]
        modelo_atual = novo_modelo
        print(f"✅ Modelo alterado para {modelo_atual}")
        continue
    
    if entrada == "/modelos":
        print("Modelos disponíveis: smollm2:135m, qwen2.5:0.5b, phi3:mini")
        continue
    
    print(f"🧠 SELIX ({modelo_atual}): ", end="", flush=True)
    resposta = responder(entrada, model_name=modelo_atual)
    print(resposta)

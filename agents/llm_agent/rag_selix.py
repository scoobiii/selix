from sentence_transformers import SentenceTransformer
import chromadb
import os

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
chroma_client = chromadb.PersistentClient(path="/root/selix/memory/chroma_db")
collection = chroma_client.get_or_create_collection("selix_docs")

# Adicionar documentos (README, posts, whitepaper)
docs = [
    "Selic ideal é 9,25% provado com Z3 e Lean4.",
    "TrampoForte prioriza trabalhadores em recuperação judicial.",
    "Energy Predictor calcula mix E/B baseado no Brent."
]
for i, doc in enumerate(docs):
    collection.add(documents=[doc], ids=[f"doc_{i}"])

def search_context(query, n_results=2):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results['documents'][0] if results else []

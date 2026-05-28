#!/usr/bin/env python3
"""
Apaga posts com erro de formatação (R,60 / R7,60)
Versão corrigida com a API correta
"""

from atproto import Client
from atproto import models
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

print("🔍 ANALISANDO POSTS RECENTES:")
print("=" * 60)

# Buscar os últimos posts
feed = client.get_author_feed(actor=client.me.did, limit=30)

posts_para_apagar = []

for post in feed.feed:
    text = post.post.record.text
    uri = post.post.uri
    
    # Identificar posts com erro de formatação
    if 'R,60' in text or 'R7,60' in text or 'R,20' in text or 'R3,40' in text:
        # Extrair o rkey do URI
        rkey = uri.split('/')[-1]
        
        posts_para_apagar.append({
            'uri': uri,
            'rkey': rkey,
            'text': text[:100]
        })
        print(f"\n❌ POST COM ERRO:")
        print(f"   {text[:120]}...")
        print(f"   URI: {uri}")
        print(f"   RKEY: {rkey}")

print("\n" + "=" * 60)
print(f"📊 Total de posts com erro: {len(posts_para_apagar)}")

# Apagar os posts
if posts_para_apagar:
    print("\n🗑️ APAGANDO POSTS ERRADOS...")
    for post in posts_para_apagar:
        try:
            # Usar a API correta com o parâmetro 'data'
            client.com.atproto.repo.delete_record(
                data=models.ComAtprotoRepoDeleteRecord.Data(
                    repo=client.me.did,
                    collection='app.bsky.feed.post',
                    rkey=post['rkey']
                )
            )
            print(f"   ✅ Apagado: {post['text'][:50]}...")
        except Exception as e:
            print(f"   ❌ Erro ao apagar: {e}")
else:
    print("\n✅ Nenhum post com erro encontrado!")

print("\n✨ PRONTO! Agora publique as versões corrigidas.")

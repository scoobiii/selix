#!/usr/bin/env python3
"""
Apaga posts com erro de formatação (R,60 / R7,60)
"""

from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

# Buscar os últimos posts
feed = client.get_author_feed(actor=client.me.did, limit=20)

print("🔍 ANALISANDO POSTS RECENTES:")
print("=" * 60)

posts_para_apagar = []

for post in feed.feed:
    text = post.post.record.text
    uri = post.post.uri
    
    # Identificar posts com erro de formatação
    if 'R,60' in text or 'R7,60' in text or 'R,20' in text or 'R3,40' in text:
        posts_para_apagar.append({
            'uri': uri,
            'text': text[:80]
        })
        print(f"\n❌ POST COM ERRO:")
        print(f"   {text[:100]}...")
        print(f"   URI: {uri}")

print("\n" + "=" * 60)
print(f"📊 Total de posts com erro: {len(posts_para_apagar)}")

# Apagar os posts
if posts_para_apagar:
    print("\n🗑️ APAGANDO POSTS ERRADOS...")
    for post in posts_para_apagar:
        try:
            client.com.atproto.repo.delete_record(
                repo=client.me.did,
                collection='app.bsky.feed.post',
                rkey=post['uri'].split('/')[-1]
            )
            print(f"   ✅ Apagado: {post['text'][:50]}...")
        except Exception as e:
            print(f"   ❌ Erro ao apagar: {e}")
else:
    print("\n✅ Nenhum post com erro encontrado!")

print("\n✨ PRONTO! Agora publique as versões corrigidas.")

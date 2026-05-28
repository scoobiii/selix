#!/usr/bin/env python3
"""
Lista, apaga e republica posts corrigidos
"""

from atproto import Client, models
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

print("🔍 Buscando posts com erro de formatação...")
print("=" * 60)

# Buscar posts
feed = client.get_author_feed(actor=client.me.did, limit=30)

posts_errados = []

for post in feed.feed:
    text = post.post.record.text
    if any(err in text for err in ['R,60', 'R7,60', 'R,20', 'R3,40']):
        rkey = post.post.uri.split('/')[-1]
        posts_errados.append({'rkey': rkey, 'text': text[:80]})
        print(f"❌ Encontrado: {text[:80]}...")

print(f"\n📊 Total: {len(posts_errados)} posts para apagar")

# Apagar
for p in posts_errados:
    try:
        client.com.atproto.repo.delete_record(
            data=models.ComAtprotoRepoDeleteRecord.Data(
                repo=client.me.did,
                collection='app.bsky.feed.post',
                rkey=p['rkey']
            )
        )
        print(f"✅ Apagado: {p['text']}...")
    except Exception as e:
        print(f"❌ Erro: {e}")

# Publicar versão corrigida
print("\n📝 Publicando versão corrigida...")

texto_corrigido = """@b3.bsky.social @cvm.bsky.social

📈 GPA + RAIZEN com SELIX+TrampoForte:

GPA: R$ 2,60 → R$ 17,60 (+577%)
RAIZ4: R$ 3,20 → R$ 23,40 (+631%)

✅ PLR garantido
✅ Trabalhadores sócios
✅ Empresas sólidas

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #RAIZ4"""

post = client.send_post(texto_corrigido)
print(f"✅ Versão corrigida publicada: {post.uri}")
print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")

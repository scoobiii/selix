from atproto import Client, models
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

# Buscar todos os posts
feed = client.get_author_feed(actor=client.me.did, limit=30)

print("🔍 Procurando post com 'R,60'...")
print("=" * 50)

for post in feed.feed:
    text = post.post.record.text
    if 'R,60' in text:
        rkey = post.post.uri.split('/')[-1]
        print(f"\n❌ POST ERRADO ENCONTRADO:")
        print(f"   Conteúdo: {text[:100]}...")
        print(f"   RKEY: {rkey}")
        
        # Apagar
        client.com.atproto.repo.delete_record(
            data=models.ComAtprotoRepoDeleteRecord.Data(
                repo=client.me.did,
                collection='app.bsky.feed.post',
                rkey=rkey
            )
        )
        print(f"   ✅ APAGADO COM SUCESSO!")
        break
else:
    print("   Nenhum post com 'R,60' encontrado")

print("\n✨ Post errado removido!")

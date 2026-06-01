from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

feed = client.get_author_feed(actor=client.me.did, limit=10)

print("\n📋 POSTS ATUAIS NO PERFIL:")
print("=" * 60)

for i, post in enumerate(feed.feed, 1):
    text = post.post.record.text[:80]
    uri = post.post.uri
    
    # Marcar se tem erro
    if 'R,60' in text or 'R7,60' in text:
        status = "❌ AINDA ERRADO"
    elif 'R$ 2,60' in text:
        status = "✅ CORRETO"
    else:
        status = "📄 OUTRO"
    
    print(f"{i}. {status}")
    print(f"   {text}...")
    print(f"   🔗 https://bsky.app/profile/{client.me.handle}/post/{uri.split('/')[-1]}")
    print()


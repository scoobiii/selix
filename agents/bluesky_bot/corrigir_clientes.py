from atproto import Client, models
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

# Buscar o post dos clientes
feed = client.get_author_feed(actor=client.me.did, limit=20)

for post in feed.feed:
    text = post.post.record.text
    if 'R63K' in text or 'CLIENTES GPA' in text:
        rkey = post.post.uri.split('/')[-1]
        print(f"❌ Apagando post antigo: {text[:60]}...")
        
        client.com.atproto.repo.delete_record(
            data=models.ComAtprotoRepoDeleteRecord.Data(
                repo=client.me.did,
                collection='app.bsky.feed.post',
                rkey=rkey
            )
        )
        print("   ✅ Apagado!")

# Publicar versão corrigida
texto_corrigido = """@consumidor.bsky.social

🛒 CLIENTES GPA

Com o fortalecimento da empresa:
✅ R$ 163 mil investimento por loja
✅ Mais qualidade nos produtos
✅ Lojas mais modernas
✅ 5M clientes/dia beneficiados

🔗 github.com/scoobiii/selix
#SELIX #Clientes #Qualidade"""

post = client.send_post(texto_corrigido)
print(f"\n✅ Post corrigido publicado: {post.uri}")
print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")

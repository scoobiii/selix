from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = """@b3.bsky.social @cvm.bsky.social @itau.bsky.social @bradesco.bsky.social @mpt.bsky.social

📈 GPA+RAIZEN c/ SELIX+TrampoForte:

GPA: R$2,60→R$17,60 (+577%)
RAIZ4: R$3,20→R$23,40 (+631%)

✅ PLR prioritário | ✅ Trabalhadores sócios

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #RAIZ4"""

print(f"📏 Tamanho do post: {len(texto)} caracteres (limite: 300)")

if len(texto) <= 300:
    post = client.send_post(texto)
    print(f"\n✅ POST PUBLICADO COM SUCESSO!")
    print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")
    print("\n📋 STAKEHOLDERS MARCADOS:")
    for s in ["@b3.bsky.social", "@cvm.bsky.social", "@itau.bsky.social",
              "@bradesco.bsky.social", "@mpt.bsky.social"]:
        print(f"   ✓ {s}")
else:
    print(f"❌ ERRO: Ainda excede o limite por {len(texto)-300} caracteres.")

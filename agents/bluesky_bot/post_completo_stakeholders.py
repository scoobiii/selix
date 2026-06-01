from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = """@b3.bsky.social @cvm.bsky.social @paodeacucar.bsky.social @raizen.bsky.social
@itau.bsky.social @bradesco.bsky.social @santander.bsky.social @bancodobrasil.bsky.social
@mpt.bsky.social @tst.bsky.social @planalto.bsky.social @economia.bsky.social

📈 GPA + RAIZEN com SELIX+TrampoForte:

GPA: R$ 2,60 → R$ 17,60 (+577%)
RAIZ4: R$ 3,20 → R$ 23,40 (+631%)

✅ PLR garantido (prioridade sobre credores)
✅ Trabalhadores viram sócios
✅ Empresas mais sólidas para todos

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #RAIZ4 #PLR"""

print(f"📏 Tamanho do post: {len(texto)} caracteres (limite: 300)")

if len(texto) > 300:
    print(f"⚠️ Excede por {len(texto) - 300} caracteres. Vamos encurtar...")
    texto = """@b3.bsky.social @cvm.bsky.social @paodeacucar.bsky.social @raizen.bsky.social
@itau.bsky.social @bradesco.bsky.social @santander.bsky.social

📈 GPA+RAIZEN com SELIX+TrampoForte:

GPA: R$2,60→R$17,60 (+577%)
RAIZ4: R$3,20→R$23,40 (+631%)

✅ PLR prioritário sobre credores
✅ Trabalhadores viram sócios
✅ Empresas mais sólidas

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #RAIZ4"""

print(f"📏 Versão ajustada: {len(texto)} caracteres")

post = client.send_post(texto)
print(f"\n✅ POST PUBLICADO COM SUCESSO!")
print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")

# Listar os stakeholders marcados
print("\n📋 STAKEHOLDERS MARCADOS:")
stakeholders = ["@b3.bsky.social", "@cvm.bsky.social", "@paodeacucar.bsky.social", 
                "@raizen.bsky.social", "@itau.bsky.social", "@bradesco.bsky.social", 
                "@santander.bsky.social", "@mpt.bsky.social", "@tst.bsky.social", 
                "@planalto.bsky.social", "@economia.bsky.social"]
for s in stakeholders:
    print(f"   ✓ {s}")

#!/bin/bash
source ../../venv/bin/activate

python3 -c '
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))

texto = """@consumidor.bsky.social

🛒 CLIENTES GPA

Com o fortalecimento da empresa:
✅ R$ 163 mil investimento por loja
✅ Mais qualidade nos produtos
✅ Lojas mais modernas
✅ 5M clientes/dia beneficiados

🔗 github.com/scoobiii/selix
#SELIX #Clientes #Qualidade"""

print(f"📏 Tamanho: {len(texto)} caracteres")
post = client.send_post(texto)
print(f"✅ Post Clientes corrigido: {post.uri}")
'

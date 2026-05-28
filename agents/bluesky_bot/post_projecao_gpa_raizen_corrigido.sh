#!/bin/bash
source ../../venv/bin/activate

python3 -c '
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))

texto = """@b3.bsky.social @cvm.bsky.social

📈 GPA + RAIZEN com SELIX+TrampoForte:

GPA: R$ 2,60 → R$ 17,60 (+577%)
RAIZ4: R$ 3,20 → R$ 23,40 (+631%)

✅ PLR garantido
✅ Trabalhadores sócios
✅ Empresas sólidas

🔗 github.com/scoobiii/selix
#SELIX #TrampoForte #GPA #RAIZ4"""

print(f"📏 Tamanho: {len(texto)} caracteres")
post = client.send_post(texto)
print(f"✅ Post corrigido: {post.uri}")
'

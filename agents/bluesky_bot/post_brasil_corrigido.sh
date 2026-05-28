#!/bin/bash
source ../../venv/bin/activate

python3 -c '
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))

texto = """@planalto.bsky.social @economia.bsky.social

🇧🇷 BENEFÍCIO PARA O BRASIL

Com reestruturação do GPA:
✅ +6.525 novos empregos
✅ +R$ 111M/ano em impostos
✅ 500 municípios beneficiados
✅ Empresa sustentável

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #Empregos #Brasil"""

print(f"📏 Tamanho: {len(texto)} caracteres")
post = client.send_post(texto)
print(f"✅ Post Brasil corrigido: {post.uri}")
'

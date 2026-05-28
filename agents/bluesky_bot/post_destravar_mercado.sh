#!/bin/bash
source ../../venv/bin/activate

python -c "
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@cvm.bsky.social @b3.bsky.social @economia.bsky.social

📊 DESTRAVANDO O MERCADO COM SELIX + TRAMPOFORTE

Cenário atual: IPOs congelados, B3 travada

Com SELIX (Selic 9.48%) + TrampoForte:

✅ B3 valoriza +122% (R$12.50 → R$27.75)
✅ R$84B reativados em IPOs
✅ 35 IPOs descongelados
✅ Risco trabalhista reduz 71%
✅ Investment Grade BBB+

🔗 github.com/scoobiii/selix
#SELIX #MercadoDeCapitais #B3 #IPOs\"\"\"

post = client.send_post(texto)
print(f'✅ Post publicado: {post.uri}')
"

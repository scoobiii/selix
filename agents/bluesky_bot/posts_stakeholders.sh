#!/bin/bash
source ../../venv/bin/activate

echo "🚀 Publicando posts por stakeholder..."
echo ""

# Post 1: Para COLABORADORES
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@mpt.bsky.social

📢 COLABORADORES GPA

Com a solução SELIX:
✅ PLR de R$2.000 para 70.000 trabalhadores
✅ Participação de 173% no capital
✅ 34 assentos no Conselho
✅ Empresa mais forte e sustentável

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #PLR #GPA #Valorização\"\"\"

post = client.send_post(texto)
print(f'✅ Post Colaboradores: {post.uri}')
"

sleep 5

# Post 2: Para INVESTIDORES
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@cvm.bsky.social @b3.bsky.social

📈 INVESTIDORES GPA

Com reestruturação SELIX:
✅ Economia anual: R$326M em juros
✅ Potencial valorização: +4.038%
✅ Rating: BBB+ (Investment Grade)
✅ Risco de crédito reduzido

🔗 github.com/scoobiii/selix
#SELIX #Investimentos #GPA\"\"\"

post = client.send_post(texto)
print(f'✅ Post Investidores: {post.uri}')
"

sleep 5

# Post 3: Para CLIENTES
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@consumidor.bsky.social

🛒 CLIENTES GPA

Com o fortalecimento da empresa:
✅ R$163K investimento por loja
✅ Mais qualidade nos produtos
✅ Lojas mais modernas
✅ 5M clientes/dia beneficiados

🔗 github.com/scoobiii/selix
#SELIX #Clientes #Qualidade\"\"\"

post = client.send_post(texto)
print(f'✅ Post Clientes: {post.uri}')
"

sleep 5

# Post 4: Para o PAÍS
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@planalto.bsky.social @economia.bsky.social

🇧🇷 BENEFÍCIO PARA O BRASIL

Com reestruturação do GPA:
✅ +6.525 novos empregos
✅ +R$111M/ano em impostos
✅ 500 municípios beneficiados
✅ Empresa sustentável

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #Empregos #Brasil\"\"\"

post = client.send_post(texto)
print(f'✅ Post País: {post.uri}')
"

sleep 5

# Post 5: Resumo executivo
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv
load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@mme.bsky.social @cvm.bsky.social @mpt.bsky.social

📊 SOLUÇÃO SELIX - GANHA-GANHA

Resultado da reestruturação:

✅ Colaboradores: R$140M PLR + 173% participação
✅ Investidores: +4.038% valorização
✅ Clientes: R$163K/loja investimento
✅ País: +6.525 empregos + R$111M impostos

Empresa mais sólida para TODOS!

🔗 github.com/scoobiii/selix
#SELIX #Reestruturação\"\"\"

post = client.send_post(texto)
print(f'✅ Post Resumo: {post.uri}')
"

echo ""
echo "✅ TODOS OS 5 POSTS PUBLICADOS!"
echo "🔗 https://bsky.app/profile/selixbr.bsky.social"

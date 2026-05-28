#!/bin/bash
# Post sobre Market Cap dos Índices com fontes
source ../../venv/bin/activate

echo "🚀 Publicando posts sobre Market Cap dos Índices..."
echo ""

# Post 1: Comparativo IBOVESPA vs S&P 500
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@b3.bsky.social @cvm.bsky.social

📊 TAMANHO DO MERCADO BRASILEIRO

IBOVESPA: US$ 420B (R$ 2.3T)
S&P 500:   US$ 45.000B

O Brasil é APENAS 0.93% do mercado americano!

Com SELIX + TrampoForte:
→ IBOVESPA vai a US$ 1.418B
→ 3.15% do S&P 500
→ Crescimento de +238%

🔗 github.com/scoobiii/selix
📊 Fonte: B3, S&P Global, Yahoo Finance

#SELIX #MercadoFinanceiro #Brasil #EUA\"\"\"

post = client.send_post(texto)
print(f'✅ Post 1 (Comparativo): {post.uri}')
"

sleep 5

# Post 2: Potencial de crescimento com SELIX
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@mme.bsky.social @economia.bsky.social

🚀 POTENCIAL DO BRASIL COM SELIX

Hoje:
• Selic 14.5%
• P/L Brasil: 7.6x
• Market Cap: US$ 420B

Com SELIX (9.48%):
• P/L: 19.0x (+150%)
• Market Cap: US$ 1.418B
• IPOs descongelados: 35/ano

+238% de valorização potencial!

🔗 github.com/scoobiii/selix
📊 Cálculo: Modelo de Gordon + CAPM

#SELIX #Valuation #Crescimento #Brasil\"\"\"

post = client.send_post(texto)
print(f'✅ Post 2 (Potencial): {post.uri}')
"

sleep 5

# Post 3: Transparência das fontes de dados
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@dadosabertos.bsky.social

📡 TRANSPARÊNCIA: Fontes dos Dados

IBOVESPA:
• B3 Dados Abertos
• BCB (Olinda)
• IBGE SIDRA

DOW JONES & S&P 500:
• S&P Global
• Yahoo Finance API
• FRED (Federal Reserve)

TODOS os dados são públicos e verificáveis!

🔗 github.com/scoobiii/selix
📊 Metodologia: github.com/scoobiii/selix/src/api

#DadosAbertos #Transparência #SELIX\"\"\"

post = client.send_post(texto)
print(f'✅ Post 3 (Fontes): {post.uri}')
"

sleep 5

# Post 4: Resumo executivo - comparação global
python3 -c "
from atproto import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

texto = \"\"\"@planalto.bsky.social @senado.bsky.social

🌍 BRASIL NO CONTEXTO GLOBAL

Market Cap (US$ bilhões):

IBOVESPA:      US$ 420B   ████
DOW JONES:     US$ 12.500B ████████████████████████████████████████████
S&P 500:       US$ 45.000B ████████████████████████████████████████████████████████████████████████

Com SELIX + TrampoForte:
IBOVESPA:      US$ 1.418B ████████████████████████████████

Crescimento: +238%

🔗 github.com/scoobiii/selix
#Brasil #Economia #SELIX #TrampoForte\"\"\"

post = client.send_post(texto)
print(f'✅ Post 4 (Global): {post.uri}')
"

echo ""
echo "✅ TODOS OS POSTS PUBLICADOS!"
echo "🔗 https://bsky.app/profile/selixbr.bsky.social"

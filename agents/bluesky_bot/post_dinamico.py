import os
import requests
from atproto import Client

# Carrega credenciais do .env (se não estiverem exportadas)
from dotenv import load_dotenv
load_dotenv()

# Busca dados da API local
try:
    r = requests.get('http://localhost:5000/v1/energia/mistura')
    data = r.json()
    brent = data['brent_usd']
    etanol = data['etanol']['mistura']
    biodiesel = data['biodiesel']['mistura']
    post = f"SELIX: Selic ideal 9,25% (vs 14,50%). Brent US$ {brent} → {etanol}/{biodiesel}. Economia de R$ 270 bi/ano. #Selix #Economia"
except Exception as e:
    post = f"SELIX: Selic ideal 9,25% (vs 14,50%). Economia de R$ 270 bi/ano. #Selix #Economia (dados temporários)"

# Posta no Bluesky
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))
client.send_post(post)
print("✅ Post enviado!")

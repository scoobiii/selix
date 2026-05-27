import os
from dotenv import load_dotenv
from atproto import Client

load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

print(f"Tentando autenticar: {USERNAME}")
print(f"Senha (primeiros 4 chars): {APP_PASSWORD[:4]}...")

try:
    client = Client()
    client.login(USERNAME, APP_PASSWORD)
    print("✅ Autenticação bem-sucedida!")
    print(f"   Perfil: {client.me.display_name}")
except Exception as e:
    print(f"❌ Falha: {e}")

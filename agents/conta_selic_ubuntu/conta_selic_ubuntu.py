#!/usr/bin/env python3
"""
🤖 SELIX Agent - Ubuntu (Termux/proot)
Monitora X (Twitter) sobre Selic, juros, Copom e responde com frases impactantes
"""

import tweepy
import time
import os
import json
import random
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES (use variáveis de ambiente ou preencha aqui)
# ============================================================
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
API_KEY = os.getenv("TWITTER_API_KEY", "")
API_SECRET = os.getenv("TWITTER_API_SECRET", "")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# Verificar se as credenciais estão configuradas
if not BEARER_TOKEN or not API_KEY:
    print("⚠️ Credenciais do Twitter não configuradas!")
    print("   Defina as variáveis de ambiente ou edite o arquivo .env")
    print("   TWITTER_BEARER_TOKEN, TWITTER_API_KEY, etc.")
    exit(1)

# Palavras-chave para monitorar
KEYWORDS = [
    "selic", "juros", "copom", "bcb", "banco central",
    "taxa de juros", "selic caiu", "selic subiu", "corte de juros"
]

# Respostas impactantes (viralizáveis)
RESPOSTAS = [
    "Selic ideal: 9,48% (não 14,50%). Economia de R$ 270 bi/ano. github.com/scoobiii/selix #SELIX",
    "Juro real a 10% trava o Brasil. SELIX: 9,48% resolve. github.com/scoobiii/selix",
    "Copom discricionário? SELIX é regra pública, código aberto, provada com Z3. github.com/scoobiii/selix",
    "R$ 270 bi/ano é o que o Brasil perde com juros altos. SELIX: github.com/scoobiii/selix",
    "Por que o BCB não adota uma regra pública? SELIX: 5 teoremas provados. github.com/scoobiii/selix",
    "Selic atual: 14,50%. Selic ideal (SELIX): 9,48%. Diferença: R$ 270 bi/ano. github.com/scoobiii/selix",
    "O Brasil é o país com maior juro real do mundo. SELIX reduz para 4,77%. github.com/scoobiii/selix",
    "Cada 0,25 pp de corte na Selic economiza R$ 17 bi/ano. SELIX acelera o ritmo. github.com/scoobiii/selix",
]

# ============================================================
# BOT PRINCIPAL
# ============================================================
class SelixBot(tweepy.StreamingClient):
    def __init__(self, bearer_token, api_key, api_secret, access_token, access_token_secret):
        super().__init__(bearer_token)
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
        self.api = tweepy.API(self.auth)
        self.respondidos = set()
        self.carregar_respondidos()
        print(f"🤖 SELIX Agent iniciado!")
        print(f"   Monitorando: {', '.join(KEYWORDS[:5])}...")
        print(f"   Respostas: {len(RESPOSTAS)} frases prontas")

    def carregar_respondidos(self):
        if os.path.exists("respondidos.json"):
            with open("respondidos.json", "r") as f:
                self.respondidos = set(json.load(f))

    def salvar_respondidos(self):
        with open("respondidos.json", "w") as f:
            json.dump(list(self.respondidos), f)

    def on_tweet(self, tweet):
        if tweet.id in self.respondidos:
            return

        texto = tweet.text.lower()
        if any(kw in texto for kw in KEYWORDS):
            resposta = random.choice(RESPOSTAS)
            try:
                self.api.update_status(
                    status=f"{resposta}\n\n(em resposta a @{tweet.author_id})",
                    in_reply_to_status_id=tweet.id,
                    auto_populate_reply_metadata=True
                )
                self.respondidos.add(tweet.id)
                self.salvar_respondidos()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Respondeu a @{tweet.author_id}")
                time.sleep(30)  # evitar rate limit
            except Exception as e:
                print(f"✗ Erro ao responder: {e}")

    def adicionar_regras(self):
        """Adiciona regras de streaming"""
        regras_existentes = self.get_rules()
        if regras_existentes.data:
            for rule in regras_existentes.data:
                self.delete_rules(rule.id)
        
        for kw in KEYWORDS:
            try:
                self.add_rules(tweepy.StreamRule(f'"{kw}" lang:pt'))
                print(f"   ✓ Regra adicionada: '{kw}'")
            except Exception as e:
                print(f"   ✗ Erro ao adicionar regra '{kw}': {e}")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("🤖 SELIX AGENT - UBUNTU (TERMUX/PROOT)")
    print("="*60)
    
    bot = SelixBot(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    bot.adicionar_regras()
    
    print("\n🚀 Agente em execução... Pressione Ctrl+C para parar")
    bot.sample()

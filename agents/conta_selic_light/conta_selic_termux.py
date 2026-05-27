#!/usr/bin/env python3
"""
🤖 SELIX Light Agent - Para Termux (celular)
Monitora X (Twitter) e responde com frases fixas + variações
Sem RAG, sem LLM, sem Docker - apenas respostas prontas e aleatórias
"""

import tweepy
import time
import os
import json
import random
from datetime import datetime

# ============================================================
# CONFIGURAÇÕES (preencha com seus tokens do X)
# ============================================================
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "SEU_TOKEN_AQUI")
API_KEY = os.getenv("TWITTER_API_KEY", "SUA_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET", "SUA_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "SEU_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "SEU_ACCESS_TOKEN_SECRET")

# Palavras-chave para monitorar
KEYWORDS = [
    "selic", "juros", "copom", "bcb", "banco central",
    "taxa de juros", "selic caiu", "selic subiu", "corte de juros"
]

# Respostas prontas (viralizáveis)
RESPOSTAS = [
    "Selic ideal: 9,48% (não 14,50%). Economia de R$ 270 bi/ano. github.com/scoobiii/selix #SELIX",
    "Juro real a 10% trava o Brasil. SELIX: 9,48% resolve. github.com/scoobiii/selix",
    "Copom discricionário? SELIX é regra pública, código aberto, provada com Z3. github.com/scoobiii/selix",
    "R$ 270 bi/ano é o que o Brasil perde com juros altos. SELIX: github.com/scoobiii/selix",
    "Por que o BCB não adota uma regra pública? SELIX: 5 teoremas provados. github.com/scoobiii/selix",
    "Selic atual: 14,50%. Selic ideal (SELIX): 9,48%. Diferença: R$ 270 bi/ano. github.com/scoobiii/selix",
]

# ============================================================
# BOT SIMPLIFICADO
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
                print(f"[{datetime.now()}] Respondeu ao tweet {tweet.id}")
                time.sleep(30)
            except Exception as e:
                print(f"Erro: {e}")

    def adicionar_regras(self):
        for kw in KEYWORDS:
            try:
                self.add_rules(tweepy.StreamRule(f'"{kw}" lang:pt'))
            except:
                pass

if __name__ == "__main__":
    print("🤖 SELIX Light Agent rodando...")
    bot = SelixBot(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    bot.adicionar_regras()
    bot.sample()

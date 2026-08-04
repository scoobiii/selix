#!/usr/bin/env python3
import os
import random
import requests
from dotenv import load_dotenv
from atproto import Client

load_dotenv()
client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

# Dados da API
api = "http://localhost:5000"
r = requests.get(f"{api}/v1/energia/mistura")
energia = r.json()
brent = energia['brent_usd']
e_mix = energia['etanol']['mistura']
b_mix = energia['biodiesel']['mistura']

# Públicos e suas mensagens base
publicos = {
    "trabalhadores": f"Selic 14,5% corrói seu PLR. Com Selix 9,25%, você receberia até R$ X a mais. Exija #TrampoForte!",
    "bancos": f"Spread bancário com Selic 9,25% ainda é lucrativo. A economia de R$270 bi/ano fortalece o sistema.",
    "governo": f"Selix 9,25%: investment grade BBB+, redução da dívida/PIB. Viável e sem choque fiscal.",
    "politicos": f"Apoie o PL da TrampoForte e a redução da Selic. É bom para o trabalhador e para a economia.",
    "midia": f"Estudo formal (Z3+Lean4) prova que Selic deveria ser 9,25%. Reportagem exclusiva conosco.",
    "justica": f"Selic > ROI viola direito à PLR (art.7° da CF). Prioridade dos créditos trabalhistas é urgente.",
    "sindicatos": f"Selic 14,5% bloqueia PLR em empresas em RJ. Mobilização pela Selix 9,25% já!",
    "influencers": f"Dado inegável: Selic ideal é 9,25% (Z3+Lean4). Compartilhe e pressione o Copom."
}

# Empresas e dados financeiros
empresas = [
    {"nome": "GPA", "plr_devido": "2 milhões", "funcionarios": 45000, "upside": 68, "acao": "PCAR3"},
    {"nome": "Americanas", "plr_devido": "3,5 milhões", "funcionarios": 30000, "upside": 45, "acao": "AMER3"},
    {"nome": "Light", "plr_devido": "1,5 milhões", "funcionarios": 8000, "upside": 30, "acao": "LIGT3"},
    {"nome": "Oi", "plr_devido": "2,8 milhões", "funcionarios": 12000, "upside": 55, "acao": "OIBR3"},
]

# Escolhe um público e uma empresa aleatoriamente
pub = random.choice(list(publicos.keys()))
emp = random.choice(empresas)
base_msg = publicos[pub]

# Personaliza a mensagem
msg = f"🧵 Thread do dia – Público: {pub}\n\n"
msg += f"🏢 {emp['nome']} ({emp['acao']}): Selic 14,5% > ROI.\n"
msg += f"⚠️ PLR devido de R$ {emp['plr_devido']} para {emp['funcionarios']} trabalhadores está bloqueado pelo rentismo.\n"
msg += f"✅ Com Selix 9,25%, o valor justo da ação subiria {emp['upside']}% e a PLR seria paga.\n\n"
msg += base_msg + f"\n\n🌍 Brent US${brent} → {e_mix}/{b_mix} (mix energético otimizado).\n"
msg += f"📊 Selic ideal 9,25% (vs 14,50%). Economia anual de R$ 270 bi.\n"
msg += f"🔗 github.com/scoobiii/selix\n#Selix #TrampoForte #PLR #Economia"

# Publica (Bluesky tem limite de 300 caracteres, mas vamos usar até 300 para segurança)
client.send_post(msg[:300])
print(f"✅ Post para público '{pub}' sobre empresa '{emp['nome']}' enviado.")

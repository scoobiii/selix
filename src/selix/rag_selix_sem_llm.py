#!/usr/bin/env python3
import sqlite3
from datetime import datetime

DB_PATH = "/root/selix/selix.db"

def get_dados():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    brent = c.execute("SELECT price FROM brent ORDER BY timestamp DESC LIMIT 1").fetchone()
    selic = c.execute("SELECT rate FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
    sent = c.execute("SELECT sentimento, score FROM sentimento_indicadores ORDER BY criado_em DESC LIMIT 1").fetchone()
    conn.close()
    return {
        'brent': brent[0] if brent else 97.36,
        'selic': selic[0] if selic else 14.25,
        'sentimento': sent[0] if sent else "neutro",
        'score': sent[1] if sent else 0.0
    }

RESPOSTAS = {
    "selic": "✅ Selic ideal: 9,25% | Atual: {selic}% | Economia anual: R$270 bi",
    "plr": "📉 PLR travada pela Selic alta. Com 9,25%, empresas voltam a pagar PLR.",
    "gpa": "📈 GPA (PCAR3): +68% com Selic 9,25% (R$12,50 → R$21,00)",
    "raizen": "📈 Raízen (RAIZ4): +76% com Selic 9,25% (R$2,80 → R$4,93)",
    "governo": "💰 Governo economiza R$270 bi/ano com Selic 9,25%",
    "solar": "☀️ Selic 9,25% viabiliza +100 GW solares em 10 anos",
    "brent": "🛢️ Brent: US${brent} – mix ideal E30/B15 (alerta)",
    "tarifa": "🇺🇸 Tarifas de Trump afetam exportações. Selic alta agrava. Selix 9,25% reduz custo de capital e melhora competitividade.",
}

def responder(pergunta):
    dados = get_dados()
    p = pergunta.lower()
    for key, resp in RESPOSTAS.items():
        if key in p:
            texto = resp.format(selic=dados['selic'], brent=dados['brent'])
            return f"{texto}\n📊 Sentimento atual: {dados['sentimento'].upper()} (score {dados['score']})"
    return f"📊 Selic {dados['selic']}% | Brent ${dados['brent']} | Sentimento {dados['sentimento'].upper()} | Selic ideal 9,25%. +info: github.com/scoobiii/selix"

if __name__ == "__main__":
    dados = get_dados()
    print(f"Selic {dados['selic']}% | Brent ${dados['brent']} | Sentimento {dados['sentimento']}")
    for q in ["Qual a Selic ideal?", "Por que minha PLR está travada?", "Qual o impacto das tarifas de Trump?", "Qual o sentimento do mercado hoje?"]:
        print(f"\n❓ {q}\n💬 {responder(q)}")

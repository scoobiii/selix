#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# sentiment_collector_v2.py
# Coletor de sentimento usando Yahoo Finance + TextBlob

import yfinance as yf
import sqlite3
import logging
import time
from datetime import datetime
from textblob import TextBlob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "/root/selix/selix.db"
TICKERS = ["^BVSP", "PETR4.SA", "VALE3.SA", "ITUB4.SA"]  # Ibovespa + principais ações

def analyze_sentiment(text):
    """Retorna sentimento e score usando TextBlob (polarity -1 a 1)."""
    if not text:
        return "neutro", 0.0
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positivo", round(polarity, 2)
    elif polarity < -0.1:
        return "negativo", round(polarity, 2)
    else:
        return "neutro", round(polarity, 2)

def fetch_news_and_sentiment(ticker):
    """Busca notícias do ticker via yfinance e calcula sentimento médio."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if not news:
            logging.warning(f"Sem notícias para {ticker}")
            return None
        sentiments = []
        for article in news[:10]:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = title + " " + summary
            sent, score = analyze_sentiment(text)
            sentiments.append(score)
        avg_score = sum(sentiments) / len(sentiments) if sentiments else 0.0
        if avg_score > 0.1:
            final_sent = "positivo"
        elif avg_score < -0.1:
            final_sent = "negativo"
        else:
            final_sent = "neutro"
        return {"sentimento": final_sent, "score": avg_score, "fontes": len(news)}
    except Exception as e:
        logging.error(f"Erro ao buscar notícias para {ticker}: {e}")
        return None

def save_sentiment(sentiment_data):
    """Salva no banco."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sentimento_indicadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentimento TEXT,
            score REAL,
            fontes TEXT,
            criado_em TIMESTAMP
        )
    """)
    conn.execute("""
        INSERT INTO sentimento_indicadores (sentimento, score, fontes, criado_em)
        VALUES (?, ?, ?, ?)
    """, (sentiment_data['sentimento'], sentiment_data['score'], 
          str(sentiment_data['fontes']), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    logging.info(f"Sentimento salvo: {sentiment_data['sentimento']} (score={sentiment_data['score']})")

def collect():
    all_scores = []
    for ticker in TICKERS:
        res = fetch_news_and_sentiment(ticker)
        if res:
            all_scores.append(res['score'])
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        if avg_score > 0.1:
            sent = "positivo"
        elif avg_score < -0.1:
            sent = "negativo"
        else:
            sent = "neutro"
        save_sentiment({"sentimento": sent, "score": avg_score, "fontes": len(TICKERS)})
    else:
        logging.warning("Nenhum dado de sentimento coletado.")

if __name__ == "__main__":
    collect()

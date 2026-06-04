#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# sentiment_collector.py
# Versão: 1.0.0-GOS3
# Responsabilidade: Coletar notícias e calcular sentimento de mercado
# Assinatura: GOS3/2026-06-03/src/selix/sentiment_collector.py

import os
import re
import json
import time
import sqlite3
import requests
import logging
from datetime import datetime
from typing import Dict, List, Tuple

# ========== CONFIGURAÇÕES ==========
DB_PATH = "/root/selix/selix.db"
LOG_DIR = "/root/selix/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/sentiment_collector.log",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Fontes de notícias (gratuitas)
NEWS_SOURCES = [
    "https://www.valor.com.br/rss/economia",      # Valor Econômico
    "https://feeds.folha.uol.com.br/mercado/rss091.htm",  # Folha
    "https://www.estadao.com.br/rss/economia.xml", # Estadão
]

# Palavras-chave para análise de sentimento
POSITIVE_WORDS = [
    'crescimento', 'lucro', 'recuperação', 'alta', 'otimista', 'positivo',
    'ganho', 'valorização', 'superávit', 'investment grade', 'upgrade'
]

NEGATIVE_WORDS = [
    'crise', 'queda', 'perda', 'negativo', 'pessimista', 'recessão',
    'inflação', 'juros', 'selic alta', 'desemprego', 'dívida', 'rombo'
]

# ========== COLETA DE NOTÍCIAS ==========
def fetch_news_from_rss(url: str) -> List[Dict]:
    """Busca notícias de um feed RSS."""
    try:
        import feedparser
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:5]:  # últimas 5 notícias
            articles.append({
                'title': entry.get('title', ''),
                'summary': entry.get('summary', ''),
                'published': entry.get('published', ''),
                'link': entry.get('link', ''),
                'source': url.split('/')[2]
            })
        return articles
    except Exception as e:
        logging.warning(f"Erro ao acessar RSS {url}: {e}")
        return []

def fetch_news_from_ddg(query: str = "economia brasileira Selic") -> List[Dict]:
    """Busca notícias via DuckDuckGo (fallback)."""
    url = "https://api.duckduckgo.com/"
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        articles = []
        # Pega abstract se disponível
        if data.get('Abstract'):
            articles.append({
                'title': data.get('Heading', query),
                'summary': data.get('Abstract', ''),
                'published': datetime.now().isoformat(),
                'source': 'DuckDuckGo'
            })
        # Pega RelatedTopics
        for topic in data.get('RelatedTopics', []):
            if isinstance(topic, dict) and topic.get('Text'):
                articles.append({
                    'title': topic.get('Text', '')[:100],
                    'summary': topic.get('Text', ''),
                    'published': datetime.now().isoformat(),
                    'source': 'DuckDuckGo'
                })
        return articles[:5]
    except Exception as e:
        logging.error(f"DDG falhou: {e}")
        return []

# ========== ANÁLISE DE SENTIMENTO ==========
def analyze_sentiment(text: str) -> Tuple[str, float]:
    """Analisa sentimento de um texto e retorna (classificação, score)."""
    text_lower = text.lower()
    positive_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        return "neutro", 0.0
    
    score = (positive_count - negative_count) / total
    if score > 0.2:
        return "positivo", score
    elif score < -0.2:
        return "negativo", score
    else:
        return "neutro", score

def aggregate_sentiment(articles: List[Dict]) -> Dict:
    """Agrega sentimento de múltiplas notícias."""
    if not articles:
        return {"sentimento": "neutro", "score": 0.0, "fontes": 0}
    
    scores = []
    sentiments = []
    for art in articles:
        sent, score = analyze_sentiment(art['title'] + " " + art['summary'])
        sentiments.append(sent)
        scores.append(score)
    
    # Média dos scores
    avg_score = sum(scores) / len(scores)
    # Classificação final
    if avg_score > 0.2:
        final_sent = "positivo"
    elif avg_score < -0.2:
        final_sent = "negativo"
    else:
        final_sent = "neutro"
    
    return {
        "sentimento": final_sent,
        "score": round(avg_score, 2),
        "fontes": len(articles),
        "detalhes": [{"titulo": a['title'][:100], "sentimento": s} for a, s in zip(articles, sentiments)]
    }

# ========== WORKER DE SENTIMENTO ==========
def save_sentiment_to_db(sentiment_data: Dict):
    """Salva o sentimento no banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sentimento_indicadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentimento TEXT,
            score REAL,
            fontes TEXT,
            detalhes TEXT,
            criado_em TIMESTAMP
        )
    """)
    conn.execute("""
        INSERT INTO sentimento_indicadores (sentimento, score, fontes, detalhes, criado_em)
        VALUES (?, ?, ?, ?, ?)
    """, (
        sentiment_data['sentimento'],
        sentiment_data['score'],
        sentiment_data['fontes'],
        json.dumps(sentiment_data.get('detalhes', []), ensure_ascii=False),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    logging.info(f"Sentimento salvo: {sentiment_data['sentimento']} (score={sentiment_data['score']}, fontes={sentiment_data['fontes']})")

def collect_sentiment_cycle():
    """Ciclo completo de coleta de sentimento."""
    all_articles = []
    
    # 1. Tenta RSS feeds
    for url in NEWS_SOURCES:
        articles = fetch_news_from_rss(url)
        all_articles.extend(articles)
        time.sleep(1)
    
    # 2. Fallback: DuckDuckGo (se necessário)
    if len(all_articles) < 3:
        ddg_articles = fetch_news_from_ddg()
        all_articles.extend(ddg_articles)
    
    # 3. Analisa sentimento
    if not all_articles:
        logging.warning("Nenhuma notícia obtida. Sentimento não atualizado.")
        return
    
    sentiment = aggregate_sentiment(all_articles)
    save_sentiment_to_db(sentiment)

def sentiment_worker_loop():
    """Loop principal para coletar sentimento periodicamente."""
    logging.info("🚀 Sentiment Collector iniciado")
    while True:
        try:
            collect_sentiment_cycle()
        except Exception as e:
            logging.error(f"Erro no ciclo: {e}")
        time.sleep(3600)  # Coleta a cada 1 hora

if __name__ == "__main__":
    # Executa uma vez
    collect_sentiment_cycle()

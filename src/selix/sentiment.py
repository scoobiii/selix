import requests
import feedparser
from textblob import TextBlob
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Feeds RSS mais acessíveis (alguns podem exigir User-Agent)
RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.valor.com.br/rss/economia",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
]
KEYWORDS = ["petróleo", "brent", "selic", "juros", "inflação", "gás", "energia", "geopolítica", "opep"]

def fetch_news_articles(hours_back=24):
    cutoff = datetime.now() - timedelta(hours=hours_back)
    articles = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for feed_url in RSS_FEEDS:
        try:
            resp = requests.get(feed_url, headers=headers, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                if pub_date and pub_date < cutoff:
                    continue
                title = entry.title.lower()
                if any(kw in title for kw in KEYWORDS):
                    articles.append({'title': entry.title, 'link': entry.link})
        except Exception as e:
            logger.warning(f"Erro no feed {feed_url}: {e}")
    return articles

def analyze_sentiment(articles):
    if not articles:
        return {"sentimento": "NEUTRO", "score": 0.0, "fontes": 0}
    scores = []
    for art in articles:
        blob = TextBlob(art['title'])
        scores.append(blob.sentiment.polarity)
    avg = sum(scores) / len(scores)
    if avg > 0.1:
        sent = "POSITIVO"
    elif avg < -0.1:
        sent = "NEGATIVO"
    else:
        sent = "NEUTRO"
    return {"sentimento": sent, "score": round(avg, 3), "fontes": len(articles)}

def get_market_sentiment():
    articles = fetch_news_articles()
    return analyze_sentiment(articles)

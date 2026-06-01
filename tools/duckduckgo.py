# tools/duckduckgo.py
from duckduckgo_search import DDGS

def search_web(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=2, region='br-pt')
            if results:
                return "\n".join([f"- {r['body'][:300]}" for r in results if r['body']])
    except:
        pass
    return ""

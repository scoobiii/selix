#!/usr/bin/env python3
"""
Router burro e rápido. LLM só chama se necessário.
"""

import re
from tools.brent import get_brent_local
from tools.selic import get_selic_local
from tools.duckduckgo import search_web

def route(pergunta: str) -> dict:
    p = pergunta.lower()
    
    # 1. REGRAS DETERMINÍSTICAS (rápido, zero LLM)
    if re.search(r'(brent|petróleo|petroleo|preço.*petr)', p):
        dados = get_brent_local()
        if dados and dados.get('source') != 'fallback':
            return {"tool": "brent", "data": dados, "need_llm": False}
        else:
            web = search_web("preço do barril de petróleo Brent hoje")
            return {"tool": "brent_fallback", "data": web, "need_llm": True}
    
    if re.search(r'(selic|juros|copom|taxa selic)', p):
        dados = get_selic_local()
        if dados:
            return {"tool": "selic", "data": dados, "need_llm": False}
        else:
            web = search_web("taxa Selic hoje")
            return {"tool": "selic_fallback", "data": web, "need_llm": True}
    
    if re.search(r'(memory|memória|lembra|lembrei)', p):
        return {"tool": "memory", "need_llm": True}
    
    # 2. SE NENHUMA REGRA, chama LLM para decidir
    return {"tool": "llm_router", "need_llm": True, "fallback": pergunta}

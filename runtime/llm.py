#!/usr/bin/env python3
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:0.5b"  # mais leve que phi3:mini

def llm_generate(prompt: str) -> str:
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt[:1500],
            "stream": False,
            "options": {"num_predict": 128, "temperature": 0.5}
        }, timeout=30)
        if resp.status_code == 200:
            return resp.json().get('response', '')
    except:
        pass
    return "Não consegui processar sua pergunta."

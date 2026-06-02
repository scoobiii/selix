#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# post_from_respostas.py
# Versão: 2.0.0-GOS3
# Responsabilidade: Publica threads de resposta do banco SQL com stakeholders reais (handles_bot.json)
# Assinatura: GOS3/2026-06-02/agents/bluesky_bot/post_from_respostas.py

import os
import sys
import json
import sqlite3
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/root/selix/.env')

# ========== CONFIGURAÇÕES ==========
DB_PATH = "/root/selix/selix.db"
REPO_LINK = "https://github.com/scoobiii/selix"

# Credenciais Bluesky
USERNAME = os.getenv('BLUESKY_USERNAME')
PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')
if not USERNAME or not PASSWORD:
    print("❌ Credenciais do Bluesky não encontradas")
    sys.exit(1)

# ========== FUNÇÕES AUXILIARES ==========
def carregar_handles_reais():
    """Carrega handles ativos do discovery (handles_bot.json) ou retorna dict vazio."""
    try:
        with open('handles_bot.json', 'r') as f:
            data = json.load(f)
        print("✅ Handles reais carregados do discovery")
        return data
    except FileNotFoundError:
        print("⚠️  handles_bot.json não encontrado. Execute agentes_discovery.py primeiro.")
        return {}
    except json.JSONDecodeError:
        print("⚠️  Erro ao ler handles_bot.json. Usando fallback.")
        return {}

def get_resposta_aleatoria(segmento, dor_keyword=None):
    """Busca uma resposta do banco (thread JSON) para o segmento e dor (opcional)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if dor_keyword:
        cur.execute("""
            SELECT thread_json, cc_handles, resposta
            FROM respostas_banco
            WHERE segmento = ? AND dor_keyword = ?
            ORDER BY RANDOM() LIMIT 1
        """, (segmento, dor_keyword))
    else:
        cur.execute("""
            SELECT thread_json, cc_handles, resposta
            FROM respostas_banco
            WHERE segmento = ? OR segmento = 'geral'
            ORDER BY RANDOM() LIMIT 1
        """, (segmento,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None, None, None
    thread_json = json.loads(row['thread_json'])
    cc_handles = row['cc_handles']
    if cc_handles:
        cc_handles = [h.strip() for h in cc_handles.split(',')]
    else:
        cc_handles = []
    return thread_json, cc_handles, row['resposta']

def substituir_handles(texto, handles_reais_por_eco, ecossistema):
    """
    Substitui os handles fixos (do SQL) por handles reais do discovery,
    limitando a 3 menções e mantendo a formatação @handle.
    """
    # Obtém lista de handles reais para este ecossistema
    handles_reais = handles_reais_por_eco.get(ecossistema, [])
    if not handles_reais:
        return texto  # mantém os fixos
    # Pega até 3 handles com mais seguidores
    top_handles = handles_reais[:3]
    mencoes = " ".join(f"@{h['handle']}" for h in top_handles)
    # Se o texto já contém algum cc, substitui; senão adiciona ao final
    if "CC:" in texto or "cc" in texto.lower():
        # Remove qualquer linha de cc existente e adiciona a nova
        import re
        texto = re.sub(r'(?i)(^|\n)(CC|cc):[^\n]*', '', texto)
        texto = texto.rstrip() + f"\n\nCC: {mencoes}"
    else:
        texto = texto.rstrip() + f"\n\nCC: {mencoes}"
    return texto

def post_thread_http(textos):
    """Publica thread usando HTTP requests (fallback robusto)."""
    # Cria sessão
    resp = requests.post(
        'https://bsky.social/xrpc/com.atproto.server.createSession',
        json={'identifier': USERNAME, 'password': PASSWORD}
    )
    resp.raise_for_status()
    token = resp.json()['accessJwt']

    prev_uri = None
    for i, texto in enumerate(textos):
        payload = {
            'collection': 'app.bsky.feed.post',
            'repo': USERNAME,
            'record': {
                '$type': 'app.bsky.feed.post',
                'text': texto,
                'createdAt': datetime.now().isoformat() + 'Z'
            }
        }
        if prev_uri:
            payload['record']['reply'] = {
                'parent': {'uri': prev_uri},
                'root': {'uri': prev_uri}
            }
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.post(
            'https://bsky.social/xrpc/com.atproto.repo.createRecord',
            headers=headers, json=payload
        )
        resp.raise_for_status()
        uri = resp.json()['uri']
        print(f"✅ Post {i+1}/{len(textos)}: {uri}")
        prev_uri = uri
        time.sleep(1.2)  # respeita rate limit

def publicar_resposta(segmento, dor_keyword=None):
    """Publica uma thread de resposta para o segmento/dor, usando handles reais se disponíveis."""
    print(f"📢 Preparando resposta para segmento '{segmento}'...")
    handles_reais_por_eco = carregar_handles_reais()
    thread_parts, cc_fixos, resposta_curta = get_resposta_aleatoria(segmento, dor_keyword)
    if not thread_parts:
        print(f"❌ Nenhuma resposta encontrada para {segmento}/{dor_keyword}")
        return

    # Adapta cada parte da thread: substitui handles e adiciona link do repositório se necessário
    textos_finais = []
    for i, part in enumerate(thread_parts):
        # Substitui handles fixos pelos reais
        part = substituir_handles(part, handles_reais_por_eco, segmento)
        # Garante que o link esteja presente (se não estiver)
        if REPO_LINK not in part and i == len(thread_parts)-1:
            part += f"\n🔗 {REPO_LINK}"
        textos_finais.append(part[:300])  # Bluesky: 300 caracteres máx

    print(f"🧵 Publicando thread com {len(textos_finais)} partes...")
    post_thread_http(textos_finais)
    print("✅ Publicação concluída!")

def main():
    if len(sys.argv) < 2:
        print("Uso: python post_from_respostas.py <segmento> [dor_keyword]")
        print("Exemplo: python post_from_respostas.py trabalhadores plr")
        print("Segmentos disponíveis: trabalhadores, investidores, ambientalistas, governo, geral")
        sys.exit(1)
    segmento = sys.argv[1]
    dor = sys.argv[2] if len(sys.argv) > 2 else None
    publicar_resposta(segmento, dor)

if __name__ == "__main__":
    main()

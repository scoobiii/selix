#!/bin/bash
# diagnostic_selix.sh - Diagnóstico completo do SELIX

echo "=========================================="
echo "🔍 DIAGNÓSTICO COMPLETO - SELIX"
echo "=========================================="

cd /root/selix

echo ""
echo "1️⃣ WATCHDOG STATUS"
echo "-------------------"
if pgrep -f watchdog_selix.sh > /dev/null; then
    echo "✅ Watchdog rodando"
    ps aux | grep watchdog_selix.sh | grep -v grep
else
    echo "❌ Watchdog NÃO está rodando"
fi

echo ""
echo "2️⃣ WORKER STATUS"
echo "-----------------"
if pgrep -f "worker_v.*\.py" > /dev/null; then
    echo "✅ Worker rodando"
    ps aux | grep worker | grep -v grep
else
    echo "❌ Worker NÃO está rodando"
fi

echo ""
echo "3️⃣ ÚLTIMOS POSTS (Bluesky)"
echo "---------------------------"
python3 << 'PYEOF'
import requests
from datetime import datetime, timezone

url = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'
params = {'actor': 'zeh-sobrinho.bsky.social', 'limit': 3}

try:
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    
    if 'feed' in data and data['feed']:
        for i, post in enumerate(data['feed'][:3], 1):
            created = post['post']['record']['createdAt']
            text = post['post']['record']['text'][:80]
            post_time = datetime.fromisoformat(created.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            diff_hours = (now - post_time).total_seconds() / 3600
            print(f"{i}. {diff_hours:.1f}h atrás: {text}...")
    else:
        print("❌ Nenhum post encontrado")
except Exception as e:
    print(f"❌ Erro: {e}")
PYEOF

echo ""
echo "4️⃣ LOGS RECENTES"
echo "-----------------"
echo "📋 watchdog.log (últimas 10 linhas):"
tail -10 watchdog.log 2>/dev/null || echo "❌ watchdog.log não encontrado"

echo ""
echo "📋 worker.log (últimas 10 linhas):"
tail -10 worker.log 2>/dev/null || echo "❌ worker.log não encontrado"

echo ""
echo "5️⃣ ERROS DETECTADOS"
echo "--------------------"
echo "🔍 Erros no worker.log:"
grep -i "error\|exception\|traceback" worker.log 2>/dev/null | tail -5 || echo "✅ Nenhum erro encontrado"

echo ""
echo "=========================================="
echo "✅ Diagnóstico concluído"
echo "=========================================="#!/bin/bash

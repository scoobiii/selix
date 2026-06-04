#!/bin/bash
# debug_worker.sh - Diagnóstico completo do loop de reinício

set -e

cd /root/selix

echo "🔍 DIAGNÓSTICO COMPLETO - LOOP DE REINÍCIO"
echo "============================================"

# 1. Parar tudo
echo "1️⃣ Parando processos..."
pkill -f watchdog_selix.sh 2>/dev/null || true
pkill -f worker_v7.py 2>/dev/null || true
sleep 3
echo "   ✅ Processos parados"

# 2. Verificar worker manualmente
echo ""
echo "2️⃣ Executando worker manualmente (30 segundos)..."
echo "=================================================="
timeout 30 python3 worker_v7.py 2>&1 | tee /tmp/worker_manual.log

EXIT_CODE=$?
echo ""
echo "   Exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 124 ]; then
    echo "   ✅ Worker rodou por 30 segundos sem crashar"
elif [ $EXIT_CODE -eq 0 ]; then
    echo "   ✅ Worker terminou normalmente"
else
    echo "   ❌ Worker crashou com código $EXIT_CODE"
fi

# 3. Analisar output
echo ""
echo "3️⃣ Análise do output:"
echo "======================"

# Procurar erros
ERRORS=$(grep -i "error\|exception\|traceback" /tmp/worker_manual.log | wc -l)
echo "   Erros encontrados: $ERRORS"

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "   📋 ERROS DETECTADOS:"
    grep -i "error\|exception\|traceback" /tmp/worker_manual.log | head -10
fi

# 4. Verificar se worker está tentando postar
echo ""
echo "4️⃣ Verificando lógica de postagem:"
echo "===================================="

# Verificar se há credenciais Bluesky
if [ -z "$BSKY_PASSWORD" ]; then
    echo "   ⚠️  BSKY_PASSWORD não configurado!"
    echo "   💡 Execute: export BSKY_PASSWORD='sua_senha_aqui'"
else
    echo "   ✅ BSKY_PASSWORD configurado"
fi

# 5. Verificar intervalos no código
echo ""
echo "5️⃣ Verificando intervalos no código:"
echo "======================================"
grep -n "sleep\|interval\|POST_INTERVAL" worker_v7.py | head -10

# 6. Mostrar últimas linhas do log
echo ""
echo "6️⃣ Últimas 50 linhas do log:"
echo "=============================="
tail -50 /tmp/worker_manual.log

# 7. Reiniciar watchdog
echo ""
echo "7️⃣ Reiniciando watchdog..."
nohup ./watchdog_selix.sh > watchdog.log 2>&1 &
echo "   ✅ Watchdog iniciado (PID: $!)"

sleep 5

echo ""
echo "📊 STATUS FINAL:"
echo "================"
ps aux | grep -E "(watchdog|worker)" | grep -v grep

echo ""
echo "✅ Diagnóstico concluído!"

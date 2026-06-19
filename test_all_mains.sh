#!/bin/bash
# ============================================================
# SELIX – TESTE DE TODOS OS MAINS (PROOF 20 CAGADAS)
# ============================================================

cd ~/selix
source venv/bin/activate 2>/dev/null || true

LOG_FILE="logs/test_mains_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

echo "========================================" | tee -a "$LOG_FILE"
echo "🧪 TESTE DE TODOS OS MAINS" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Lista de mains para testar
MAINS=(
    "src/api/main_v4.py"
    "src/api/main_v3.py"
    "src/api/server_v6.py"
    "src/api/server_v5.py"
    "src/api/server_v4.py"
    "src/api/main.py"
    "src/api/server.py"
)

# Chaves para testar
MASTER_KEY="f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6"
SELIX_KEY="a7b3f8e2c9d4a1f6e3b8c7d2a9f4e6b1"

for main in "${MAINS[@]}"; do
    if [ ! -f "$main" ]; then
        echo "❌ $main não existe" | tee -a "$LOG_FILE"
        continue
    fi
    
    echo "=== TESTANDO: $main ===" | tee -a "$LOG_FILE"
    
    # Mata processos anteriores
    pkill -f "$main" 2>/dev/null || true
    pkill -f "python.*$main" 2>/dev/null || true
    
    # Inicia o main
    python "$main" > logs/"$(basename $main)_output.log" 2>&1 &
    MAIN_PID=$!
    
    echo "   PID: $MAIN_PID" | tee -a "$LOG_FILE"
    
    # Aguarda subir (timeout 10s)
    WAIT=0
    while [ $WAIT -lt 10 ]; do
        if curl -s http://localhost:5000/v1/health >/dev/null 2>&1; then
            break
        fi
        sleep 1
        WAIT=$((WAIT + 1))
    done
    
    # Testa endpoints
    echo "   📡 Testando endpoints..." | tee -a "$LOG_FILE"
    
    # Health (público)
    HEALTH=$(curl -s http://localhost:5000/v1/health 2>/dev/null)
    if echo "$HEALTH" | grep -q "ok"; then
        echo "   ✅ /v1/health: OK" | tee -a "$LOG_FILE"
    else
        echo "   ❌ /v1/health: FALHOU" | tee -a "$LOG_FILE"
    fi
    
    # Selic com MASTER_KEY
    SELIC=$(curl -s -H "X-API-Key: $MASTER_KEY" http://localhost:5000/v1/selic 2>/dev/null)
    if echo "$SELIC" | grep -q "rate\|selic"; then
        echo "   ✅ /v1/selic (MASTER): OK" | tee -a "$LOG_FILE"
    elif echo "$SELIC" | grep -q "erro"; then
        echo "   ⚠️ /v1/selic (MASTER): Erro de auth" | tee -a "$LOG_FILE"
    else
        echo "   ❌ /v1/selic (MASTER): FALHOU" | tee -a "$LOG_FILE"
    fi
    
    # Selic com SELIX_KEY
    SELIC2=$(curl -s -H "X-API-Key: $SELIX_KEY" http://localhost:5000/v1/selic 2>/dev/null)
    if echo "$SELIC2" | grep -q "rate\|selic"; then
        echo "   ✅ /v1/selic (SELIX): OK" | tee -a "$LOG_FILE"
    elif echo "$SELIC2" | grep -q "erro"; then
        echo "   ⚠️ /v1/selic (SELIX): Erro de auth" | tee -a "$LOG_FILE"
    else
        echo "   ❌ /v1/selic (SELIX): FALHOU" | tee -a "$LOG_FILE"
    fi
    
    # Commodities
    COMM=$(curl -s -H "X-API-Key: $MASTER_KEY" http://localhost:5000/v1/commodities 2>/dev/null)
    if echo "$COMM" | grep -q "brent\|commodity"; then
        echo "   ✅ /v1/commodities: OK" | tee -a "$LOG_FILE"
    elif echo "$COMM" | grep -q "erro"; then
        echo "   ⚠️ /v1/commodities: Erro de auth" | tee -a "$LOG_FILE"
    else
        echo "   ❌ /v1/commodities: FALHOU" | tee -a "$LOG_FILE"
    fi
    
    # Perguntar (RAG)
    RAG=$(curl -s -X POST -H "X-API-Key: $MASTER_KEY" -H "Content-Type: application/json" -d '{"pergunta": "teste"}' http://localhost:5000/v1/perguntar 2>/dev/null)
    if echo "$RAG" | grep -q "task_id"; then
        echo "   ✅ /v1/perguntar: OK" | tee -a "$LOG_FILE"
    elif echo "$RAG" | grep -q "erro"; then
        echo "   ⚠️ /v1/perguntar: Erro" | tee -a "$LOG_FILE"
    else
        echo "   ❌ /v1/perguntar: FALHOU" | tee -a "$LOG_FILE"
    fi
    
    # Mata o processo
    kill -9 "$MAIN_PID" 2>/dev/null || true
    pkill -f "$main" 2>/dev/null || true
    
    echo "" | tee -a "$LOG_FILE"
done

echo "========================================" | tee -a "$LOG_FILE"
echo "✅ TESTE CONCLUÍDO!" | tee -a "$LOG_FILE"
echo "📋 Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

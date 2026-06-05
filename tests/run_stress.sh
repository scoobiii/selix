#!/bin/bash
# run_stress.sh — executa stress test sem expor chaves no terminal
# Uso: bash run_stress.sh
# As chaves são lidas do .env — NUNCA passadas como argumento visível

set -e
cd /root/selix

# ── 1. Carrega .env de forma segura (sem printar) ─────────────
set -a
source .env 2>/dev/null || true
set +a

# ── 2. Verifica se API está de pé ─────────────────────────────
echo "🔍 Verificando API..."
if ! curl -sf http://localhost:5000/v1/health > /dev/null 2>&1; then
    echo "❌ API offline. Iniciando..."
    source venv/bin/activate
    # Tenta flask primeiro, depois uvicorn
    if python -c "import uvicorn" 2>/dev/null; then
        nohup python -m uvicorn src.api.main_v4:app \
            --host 0.0.0.0 --port 5000 \
            > logs/api.log 2>&1 &
    else
        nohup python -m src.api.main_v4 \
            > logs/api.log 2>&1 &
    fi
    echo "⏳ Aguardando API subir (máx 20s)..."
    for i in $(seq 1 20); do
        if curl -sf http://localhost:5000/v1/health > /dev/null 2>&1; then
            echo "✅ API online em ${i}s"
            break
        fi
        sleep 1
        if [ $i -eq 20 ]; then
            echo "❌ API não subiu em 20s"
            echo "   Ver logs: tail -20 logs/api.log"
            exit 1
        fi
    done
fi

# ── 3. Roda stress test com chave via -e (não aparece em ps aux) ──
echo ""
echo "🚀 Iniciando stress test..."
echo "   Base URL: http://localhost:5000"
echo "   API Key:  ${SELIX_API_KEY:0:8}... (truncada)"
echo ""

# k6 lê a chave via variável de ambiente já setada
# Alternativa segura: -e SELIX_API_KEY="${SELIX_API_KEY}"
k6 run \
    -e BASE_URL=http://localhost:5000 \
    -e SELIX_API_KEY="${SELIX_API_KEY}" \
    --out json=logs/stress_results.json \
    tests/stress_test_full.js

echo ""
echo "📊 Resultados salvos em logs/stress_results.json"

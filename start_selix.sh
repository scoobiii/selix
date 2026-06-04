#!/bin/bash
# start_selix.sh — v2.0.0-GOS3
# Inicia todos os serviços Selix na ordem correta
# Uso: bash start_selix.sh [--restart]

set -e
cd /root/selix
source venv/bin/activate

LOG_DIR="/root/selix/logs"
mkdir -p "$LOG_DIR"

echo "════════════════════════════════════════"
echo "  SELIX v4.0 — START ALL SERVICES"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════"

# ── 1. MATAR PROCESSOS ANTIGOS ────────────────────────
echo ""
echo "⏹  Parando processos antigos..."
pkill -f "worker_v" 2>/dev/null        && echo "  ✓ worker parado"   || true
pkill -f "src.api.main" 2>/dev/null    && echo "  ✓ api parada"      || true
pkill -f "metrics_agent" 2>/dev/null   && echo "  ✓ metrics parado"  || true
pkill -f "campaign_supervisor" 2>/dev/null && echo "  ✓ supervisor parado" || true
pkill -f "watchdog.sh" 2>/dev/null     && echo "  ✓ watchdog parado" || true
sleep 2

# ── 2. GARANTIR TABELA metrics_history ───────────────
echo ""
echo "🗄  Verificando banco..."
sqlite3 /root/selix/selix.db << 'SQL'
CREATE TABLE IF NOT EXISTS metrics_history (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT,
    cpu_percent       REAL,
    memory_percent    REAL,
    disk_percent      REAL,
    temperature_c     REAL,
    api_healthy       INTEGER DEFAULT 0,
    worker_running    INTEGER DEFAULT 0,
    last_post_success INTEGER DEFAULT 0,
    brent_available   INTEGER DEFAULT 0,
    selic_available   INTEGER DEFAULT 0,
    load_avg          TEXT,
    raw_json          TEXT
);
SQL
echo "  ✓ metrics_history OK"

# ── 3. WORKER ─────────────────────────────────────────
echo ""
echo "🔧 Iniciando worker..."
nohup python -m src.selix.worker_v6_no_fallback \
    > "$LOG_DIR/worker.log" 2>&1 &
WORKER_PID=$!
echo "  ✓ worker PID=$WORKER_PID"

# ── 4. API ────────────────────────────────────────────
echo "🌐 Iniciando API..."
nohup python -m src.api.main_v4 \
    > "$LOG_DIR/api.log" 2>&1 &
API_PID=$!
echo "  ✓ api PID=$API_PID"

# ── 5. AGUARDAR API SUBIR ─────────────────────────────
echo "⏳ Aguardando API (máx 30s)..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:5000/v1/health > /dev/null 2>&1; then
        echo "  ✅ API online em ${i}s"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "  ⚠️  API não respondeu em 30s — continuando mesmo assim"
    fi
done

# ── 6. METRICS AGENT ─────────────────────────────────
echo "📊 Iniciando metrics_agent..."
nohup python scripts/metrics_agent.py \
    > "$LOG_DIR/metrics.log" 2>&1 &
METRICS_PID=$!
echo "  ✓ metrics PID=$METRICS_PID"

# ── 7. CAMPAIGN SUPERVISOR ────────────────────────────
echo "📅 Iniciando campaign_supervisor..."
nohup python scripts/campaign_supervisor.py \
    > "$LOG_DIR/supervisor.log" 2>&1 &
SUP_PID=$!
echo "  ✓ supervisor PID=$SUP_PID"

# ── 8. WATCHDOG ───────────────────────────────────────
echo "🐕 Iniciando watchdog..."
cat > /tmp/watchdog_selix.sh << 'WD'
#!/bin/bash
while true; do
    if ! pgrep -f "campaign_supervisor.py" > /dev/null; then
        echo "$(date) watchdog: supervisor caiu, reiniciando..." >> /root/selix/logs/watchdog.log
        cd /root/selix && source venv/bin/activate
        nohup python scripts/campaign_supervisor.py >> /root/selix/logs/supervisor.log 2>&1 &
    fi
    if ! pgrep -f "metrics_agent.py" > /dev/null; then
        echo "$(date) watchdog: metrics caiu, reiniciando..." >> /root/selix/logs/watchdog.log
        cd /root/selix && source venv/bin/activate
        nohup python scripts/metrics_agent.py >> /root/selix/logs/metrics.log 2>&1 &
    fi
    sleep 60
done
WD
chmod +x /tmp/watchdog_selix.sh
nohup /tmp/watchdog_selix.sh > /dev/null 2>&1 &
echo "  ✓ watchdog PID=$!"

# ── 9. STATUS FINAL ───────────────────────────────────
sleep 3
echo ""
echo "════════════════════════════════════════"
echo "  STATUS DOS SERVIÇOS"
echo "════════════════════════════════════════"
for nome in "worker_v" "src.api.main" "metrics_agent" "campaign_supervisor"; do
    if pgrep -f "$nome" > /dev/null; then
        pid=$(pgrep -f "$nome" | head -1)
        echo "  ✅ $nome (PID $pid)"
    else
        echo "  ❌ $nome — NÃO RODANDO"
    fi
done

echo ""
echo "📋 COMANDOS ÚTEIS:"
echo "   Ver logs:     tail -f logs/supervisor.log"
echo "   Ver métricas: sqlite3 selix.db 'SELECT timestamp,cpu_percent,memory_percent,api_healthy,worker_running FROM metrics_history ORDER BY timestamp DESC LIMIT 5;'"
echo "   Testar post:  python agents/bluesky_bot/selix_campaign.py --day 1"
echo "   Health:       curl http://localhost:5000/v1/health"
echo ""

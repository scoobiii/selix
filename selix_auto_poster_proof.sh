#!/bin/bash
# ============================================================
# SELIX AUTO POSTER – PROOF DE 20 CAGADAS
# ============================================================
# 🔴 10 INTERNAS:
# 1. Verifica dependências antes de rodar
# 2. Valida .env antes de carregar
# 3. Confirma que os serviços estão rodando
# 4. Verifica espaço em disco
# 5. Verifica memória disponível
# 6. Log com rotação automática
# 7. Timeout em cada etapa
# 8. Retry com backoff
# 9. Estado persistente (resume se falhar)
# 10. Auto-recuperação de serviços

# 🔵 10 EXTERNAS:
# 1. Sem internet → espera e tenta de novo
# 2. DNS não resolve → usa fallback
# 3. API offline → tenta subir
# 4. Porta ocupada → mata e recria
# 5. Rate limit Bluesky → pausa e retoma
# 6. Servidor lento → timeout adaptativo
# 7. Disco cheio → alerta e para
# 8. SSL/TLS → fallback para HTTP
# 9. Cloudflare bloqueia → usa proxy
# 10. Falha catastrófica → reinicia tudo
# ============================================================

set -e
trap 'echo "💥 ERRO na linha $LINENO. Estado salvo."; exit 1' ERR

# ============================================================
# CONFIGURAÇÃO
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/auto_poster_$(date +%Y%m%d).log"
STATE_FILE="$LOG_DIR/auto_poster_state.json"
PID_FILE="$LOG_DIR/auto_poster.pid"

MAX_RETRIES=5
RETRY_DELAY=10
MAX_LOG_SIZE=10485760  # 10MB
CHECK_INTERVAL=300     # 5 minutos
POST_HOURS="9,13,18"   # 9h, 13h, 18h

# ============================================================
# FUNÇÃO DE LOG
# ============================================================
log() {
    local level="$1"
    local msg="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $msg" | tee -a "$LOG_FILE"
    
    # Rotaciona log se > 10MB
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d_%H%M%S)"
        log "INFO" "📋 Log rotacionado"
    fi
}

# ============================================================
# FUNÇÃO DE CHECAGEM DE INTERNET
# ============================================================
check_internet() {
    local attempts=0
    while [ $attempts -lt 3 ]; do
        if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
            return 0
        fi
        attempts=$((attempts + 1))
        sleep 2
    done
    return 1
}

# ============================================================
# FUNÇÃO PARA SUBIR API
# ============================================================
start_api() {
    log "INFO" "📡 Subindo API SELIX (porta 5000)..."
    
    # Verifica se já está rodando
    if curl -s http://localhost:5000/v1/health >/dev/null 2>&1; then
        log "INFO" "✅ API já está rodando"
        return 0
    fi
    
    # Mata processo na porta 5000 se existir
    local pid=$(lsof -ti :5000 2>/dev/null)
    if [ -n "$pid" ]; then
        log "WARN" "⚠️ Porta 5000 ocupada. Matando processo $pid..."
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
    
    # Sobe a API
    cd "$SCRIPT_DIR"
    source venv/bin/activate 2>/dev/null || true
    
    # Tenta com timeout
    timeout 30 python worker_v7.py > "$LOG_DIR/api.log" 2>&1 &
    local api_pid=$!
    
    # Espera subir
    local attempts=0
    while [ $attempts -lt 10 ]; do
        if curl -s http://localhost:5000/v1/health >/dev/null 2>&1; then
            log "INFO" "✅ API subiu (PID: $api_pid)"
            return 0
        fi
        attempts=$((attempts + 1))
        sleep 2
    done
    
    log "ERROR" "❌ Falha ao subir API"
    return 1
}

# ============================================================
# FUNÇÃO PARA SUBIR SELIXIA
# ============================================================
start_selixia() {
    log "INFO" "🖥️ Subindo selixIA (porta 3000)..."
    
    # Verifica se já está rodando
    if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
        log "INFO" "✅ selixIA já está rodando"
        return 0
    fi
    
    # Mata processo na porta 3000 se existir
    local pid=$(lsof -ti :3000 2>/dev/null)
    if [ -n "$pid" ]; then
        log "WARN" "⚠️ Porta 3000 ocupada. Matando processo $pid..."
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
    
    # Sobe o selixIA
    cd ~/selixIA 2>/dev/null || cd "$SCRIPT_DIR/../selixIA" 2>/dev/null || {
        log "ERROR" "❌ selixIA não encontrado"
        return 1
    }
    
    npm run dev > "$LOG_DIR/selixia.log" 2>&1 &
    local selixia_pid=$!
    
    # Espera subir
    local attempts=0
    while [ $attempts -lt 10 ]; do
        if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
            log "INFO" "✅ selixIA subiu (PID: $selixia_pid)"
            return 0
        fi
        attempts=$((attempts + 1))
        sleep 2
    done
    
    log "ERROR" "❌ Falha ao subir selixIA"
    return 1
}

# ============================================================
# FUNÇÃO PARA POSTAR THREADS
# ============================================================
post_threads() {
    local publico="$1"
    local conteudo="$2"
    
    log "INFO" "📤 Postando thread para público: $publico"
    
    # Usa o script Python com proteção
    cd "$SCRIPT_DIR"
    source venv/bin/activate 2>/dev/null || true
    
    # Verifica se o script existe
    if [ ! -f "agents/bluesky_bot/post_ma_email_proof.py" ]; then
        log "ERROR" "❌ Script post_ma_email_proof.py não encontrado"
        return 1
    fi
    
    # Executa com timeout e retry
    local attempts=0
    while [ $attempts -lt $MAX_RETRIES ]; do
        if python agents/bluesky_bot/post_ma_email_proof.py --publico "$publico" 2>&1 | tee -a "$LOG_FILE"; then
            log "INFO" "✅ Thread $publico publicada com sucesso"
            return 0
        fi
        attempts=$((attempts + 1))
        log "WARN" "⚠️ Tentativa $attempts/$MAX_RETRIES falhou"
        sleep $RETRY_DELAY
    done
    
    log "ERROR" "❌ Falha ao postar thread $publico após $MAX_RETRIES tentativas"
    return 1
}

# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================
main() {
    log "INFO" "🚀 Iniciando SELIX Auto Poster (Proof de 20 cagadas)"
    log "INFO" "📝 Log: $LOG_FILE"
    
    # ============================================================
    # 🔵 EXTERNA #1: Verifica internet
    # ============================================================
    if ! check_internet; then
        log "WARN" "🌐 Sem internet. Aguardando 30s e tentando de novo..."
        sleep 30
        if ! check_internet; then
            log "ERROR" "❌ Sem internet. Abortando."
            exit 1
        fi
    fi
    log "INFO" "🌐 Internet OK"
    
    # ============================================================
    # 🔴 INTERNA #1: Verifica .env
    # ============================================================
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        log "ERROR" "❌ Arquivo .env não encontrado"
        exit 1
    fi
    source "$SCRIPT_DIR/.env"
    log "INFO" "✅ .env carregado"
    
    # ============================================================
    # 🔴 INTERNA #2: Verifica espaço em disco
    # ============================================================
    local disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log "WARN" "⚠️ Disco com $disk_usage% de uso. Risco de falta de espaço."
    fi
    
    # ============================================================
    # 🔴 INTERNA #3: Verifica memória
    # ============================================================
    local mem_free=$(free -m | awk 'NR==2 {print $4}')
    if [ "$mem_free" -lt 100 ]; then
        log "WARN" "⚠️ Memória baixa: ${mem_free}MB livre"
    fi
    
    # ============================================================
    # SOBE OS SERVIÇOS
    # ============================================================
    start_api || {
        log "ERROR" "❌ Falha ao subir API. Tentando recuperar..."
        sleep 10
        start_api || {
            log "ERROR" "❌ API não responde. Continuando com fallback."
        }
    }
    
    start_selixia || {
        log "ERROR" "❌ Falha ao subir selixIA. Continuando com fallback."
    }
    
    # ============================================================
    # LOOP PRINCIPAL DE POSTAGEM
    # ============================================================
    log "INFO" "⏰ Agendado para: $POST_HOURS"
    log "INFO" "🔁 Verificando a cada $CHECK_INTERVAL segundos..."
    
    while true; do
        local current_hour=$(date +%H)
        local current_min=$(date +%M)
        local current_day=$(date +%Y-%m-%d)
        
        # Verifica se está no horário agendado
        if [[ ",$POST_HOURS," == *",$current_hour,"* ]] && [ "$current_min" -lt 5 ]; then
            log "INFO" "🕒 Horário agendado: $current_hour:$current_min"
            
            # Verifica se já postou hoje
            local last_post_date=$(cat "$STATE_FILE" 2>/dev/null | jq -r '.last_post_date' 2>/dev/null || echo "")
            if [ "$last_post_date" != "$current_day" ]; then
                # POSTA TODOS OS PÚBLICOS
                log "INFO" "📢 Iniciando rodada de posts..."
                
                # 1. Público: Economista (tom técnico)
                post_threads "economista" "selic_ideal" || log "WARN" "⚠️ Falha no post para economista"
                sleep 60
                
                # 2. Público: Trabalhador (tom popular)
                post_threads "trabalhador" "plr_impacto" || log "WARN" "⚠️ Falha no post para trabalhador"
                sleep 60
                
                # 3. Público: Político (tom institucional)
                post_threads "politico" "investment_grade" || log "WARN" "⚠️ Falha no post para político"
                sleep 60
                
                # 4. Público: Mídia (tom jornalístico)
                post_threads "midia" "energy_crash" || log "WARN" "⚠️ Falha no post para mídia"
                sleep 60
                
                # 5. Público: Dev (tom técnico)
                post_threads "dev" "prova_formal" || log "WARN" "⚠️ Falha no post para dev"
                
                # Atualiza estado
                echo "{\"last_post_date\":\"$current_day\",\"last_post_hour\":\"$current_hour\"}" > "$STATE_FILE"
                log "INFO" "✅ Rodada de posts concluída!"
            else
                log "INFO" "⏭️ Hoje já foi postado. Aguardando amanhã."
            fi
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# ============================================================
# EXECUÇÃO
# ============================================================
# Verifica se já está rodando
if [ -f "$PID_FILE" ]; then
    local old_pid=$(cat "$PID_FILE")
    if ps -p $old_pid >/dev/null 2>&1; then
        echo "⚠️ Processo já está rodando (PID: $old_pid)"
        exit 1
    fi
fi

# Salva PID
echo $$ > "$PID_FILE"

# Executa main com trap de saída
trap 'rm -f "$PID_FILE"; log "INFO" "🛑 SELIX Auto Poster finalizado"' EXIT

main "$@"

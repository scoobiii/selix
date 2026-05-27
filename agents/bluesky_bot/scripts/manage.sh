#!/bin/bash
# Gerenciador do Bluesky Bot

PID_FILE="/tmp/bluesky_bot.pid"
LOG_FILE="/root/selix/agents/bluesky_bot/logs/bot.log"

start() {
    if [ -f "$PID_FILE" ]; then
        echo "❌ Bot já está rodando"
        exit 1
    fi
    
    cd /root/selix/agents/bluesky_bot
    source ../venv/bin/activate
    
    echo "🚀 Iniciando bot..."
    nohup python scripts/auto_bot.py >> logs/bot.log 2>&1 &
    echo $! > $PID_FILE
    echo "✅ Bot iniciado (PID: $!)"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Bot não está rodando"
        exit 1
    fi
    
    kill $(cat $PID_FILE)
    rm $PID_FILE
    echo "✅ Bot parado"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
        echo "✅ Bot rodando (PID: $(cat $PID_FILE))"
        tail -n 5 $LOG_FILE
    else
        echo "❌ Bot parado"
    fi
}

post() {
    cd /root/selix/agents/bluesky_bot
    source ../venv/bin/activate
    python scripts/auto_bot.py $1
}

case "$1" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    post) post $2 ;;
    *) echo "Uso: $0 {start|stop|status|post <1-5>}" ;;
esac

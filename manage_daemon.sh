#!/bin/bash
# Gerenciador do daemon SELIX

PID_FILE="/tmp/selix_monitor.pid"
LOG_FILE="/root/selix/logs/monitor_daemon.log"

start() {
    if [ -f "$PID_FILE" ]; then
        echo "❌ Monitor já está rodando (PID: $(cat $PID_FILE))"
        exit 1
    fi
    
    echo "🚀 Iniciando SELIX Monitor Daemon..."
    nohup /root/selix/daemon_monitor.sh > /dev/null 2>&1 &
    echo $! > $PID_FILE
    echo "✅ Monitor iniciado (PID: $(cat $PID_FILE))"
    echo "📝 Logs: tail -f $LOG_FILE"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "❌ Monitor não está rodando"
        exit 1
    fi
    
    echo "🛑 Parando monitor..."
    kill $(cat $PID_FILE)
    rm $PID_FILE
    echo "✅ Monitor parado"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat $PID_FILE) 2>/dev/null; then
        echo "✅ Monitor rodando (PID: $(cat $PID_FILE))"
        echo ""
        echo "📊 Últimas 5 linhas do log:"
        tail -5 $LOG_FILE
    else
        echo "❌ Monitor parado"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    restart) stop; sleep 2; start ;;
    *)
        echo "Uso: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac

#!/bin/bash
# Daemon de monitoramento SELIX (alternativa ao cron)

LOG_FILE="/root/selix/logs/monitor_daemon.log"
mkdir -p /root/selix/logs

echo "🚀 Iniciando Daemon SELIX Monitor..." | tee -a $LOG_FILE

while true; do
    echo "[$(date)] Executando análise..." >> $LOG_FILE
    
    # Executar predictor e salvar resultado
    cd /root/selix
    source venv/bin/activate
    python src/energy/selix_predictor.py >> $LOG_FILE 2>&1
    
    # Verificar se precisa enviar alerta (a cada 6 horas)
    HOUR=$(date +%H)
    if [ $HOUR -eq 0 ] || [ $HOUR -eq 6 ] || [ $HOUR -eq 12 ] || [ $HOUR -eq 18 ]; then
        echo "[$(date)] Enviando alerta para Bluesky..." >> $LOG_FILE
        cd /root/selix/agents/bluesky_bot
        ./scripts/alerta_crise.sh >> $LOG_FILE 2>&1
    fi
    
    # Aguardar 15 minutos
    sleep 900
done

#!/bin/bash
# Configurar jobs automáticos para monitor Selic vs ROI

echo "📅 Configurando jobs automáticos..."

# Se tiver cron disponível
if command -v crontab &> /dev/null; then
    (crontab -l 2>/dev/null; echo "# SELIX - Monitor Selic vs ROI") | crontab -
    (crontab -l 2>/dev/null; echo "0 */6 * * * /root/selix/agents/bluesky_bot/alerta_autoridades_trabalhistas.sh >> /root/selix/logs/selic_roi.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 8,14,20 * * * /root/selix/agents/bluesky_bot/scripts/alerta_cc.sh >> /root/selix/logs/energia.log 2>&1") | crontab -
    
    echo "✅ Cron configurado!"
    crontab -l | grep SELIX
else
    echo "⚠️ Cron não disponível. Use o daemon:"
    echo "   python monitor_selic_roi.py --monitor &"
fi

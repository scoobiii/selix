#!/bin/bash
while true; do
    if ! pgrep -f "campaign_supervisor.py" > /dev/null; then
        echo "Supervisor caiu. Reiniciando..."
        cd /root/selix && source venv/bin/activate && nohup python scripts/campaign_supervisor.py > logs/supervisor.log 2>&1 &
    fi
    sleep 30
done

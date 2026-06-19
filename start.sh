#!/bin/bash
cd /root/selix
source venv/bin/activate
mkdir -p logs

# Cria sessao tmux persistente
if ! tmux has-session -t selix 2>/dev/null; then
    tmux new-session -d -s selix
    tmux send-keys -t selix 'cd /root/selix && source venv/bin/activate && nohup python src/selix/worker_v4.py > logs/worker.log 2>&1 &' Enter
    tmux send-keys -t selix 'python src/api/main_v4_fixed.py >> logs/api.log 2>&1' Enter
    echo API e Worker iniciados na sessao tmux selix
else
    echo Sessao selix ja existe
fi

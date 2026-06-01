#!/bin/bash
# ============================================================
# SELIX - Atualização do Risco Geoenergético
# Executar via cron: 0 */6 * * *
# ============================================================

cd /root/selix
source venv/bin/activate
python confidence/geo_energy_risk.py >> /root/selix/logs/geo_risk.log 2>&1

echo "[$(date)] Risco geoenergético atualizado" >> /root/selix/logs/geo_risk.log

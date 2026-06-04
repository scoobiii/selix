#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# campaign_supervisor.py — v2.0.0-GOS3
# BUG FIX: dia calculado por rotação 1-30, não pelo dia do ano (1-365)

import os, sys, time, subprocess, sqlite3, json
import schedule
from datetime import datetime, date

LOG_FILE = "/root/selix/logs/campaign.log"
DB_PATH  = "/root/selix/selix.db"
CAMPAIGN = "/root/selix/agents/bluesky_bot/selix_campaign.py"
VENV_PY  = "/root/selix/venv/bin/python"

# Dia de início da campanha (ajuste para hoje se for o 1º dia)
START_DATE = date(2026, 6, 3)   # ← DATA DE INÍCIO DA CAMPANHA

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} — {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)

def get_campaign_day():
    """
    FIX CRÍTICO: calcula dia da campanha (1-30) pela diferença
    desde START_DATE, não pelo dia do ano (que vai até 365).
    """
    delta = (date.today() - START_DATE).days
    dia = (delta % 30) + 1   # rotação contínua 1-30
    return dia

def mark_post_result(success: bool):
    """Atualiza last_post_success na tabela de métricas."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            UPDATE metrics_history
            SET last_post_success = ?
            WHERE id = (SELECT MAX(id) FROM metrics_history)
        """, (1 if success else 0,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def run_campaign(modo="thread"):
    dia = get_campaign_day()
    log(f"🚀 Iniciando campanha dia {dia} (modo={modo})")

    flag = "--thread" if modo == "thread" else ""
    cmd = [VENV_PY, CAMPAIGN, "--day", str(dia), "--post"]
    if flag:
        cmd.append(flag)

    try:
        result = subprocess.run(
            cmd,
            cwd="/root/selix",
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            log(f"✅ Dia {dia} OK\n{result.stdout[-300:]}")
            mark_post_result(True)
        else:
            log(f"❌ Dia {dia} ERRO\n{result.stderr[-300:]}")
            mark_post_result(False)
    except subprocess.TimeoutExpired:
        log(f"⏱️  Dia {dia} TIMEOUT (120s)")
        mark_post_result(False)
    except Exception as e:
        log(f"❌ Exceção: {e}")
        mark_post_result(False)

def run_09h():
    run_campaign("independente")   # post individual, maior alcance no feed

def run_13h():
    run_campaign("independente")

def run_18h():
    run_campaign("thread")         # thread no fim do dia

def main():
    log("campaign_supervisor v2.0.0 iniciado")
    dia_hoje = get_campaign_day()
    log(f"📅 Dia da campanha hoje: {dia_hoje}/30 (início: {START_DATE})")

    # Agenda os 3 horários diários
    schedule.every().day.at("09:00").do(run_09h)
    schedule.every().day.at("13:00").do(run_13h)
    schedule.every().day.at("18:00").do(run_18h)

    log("⏰ Agendamentos: 09:00 | 13:00 | 18:00")
    log(f"⏭️  Próximo: {schedule.next_run()}")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()

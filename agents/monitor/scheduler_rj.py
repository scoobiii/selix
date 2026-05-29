#!/usr/bin/env python3
"""
Agendador de alertas RJ - 3x ao dia
"""

import subprocess
import time
from datetime import datetime

def enviar_alerta_rj():
    print(f"[{datetime.now()}] 📢 Enviando alerta RJ...")
    subprocess.run(["python3", "publicar_alerta_rj.py"])

def main():
    print("🚨 RJ Alert Scheduler")
    print("📅 Envios: 09:00, 15:00, 21:00")
    
    while True:
        now = datetime.now()
        h = now.hour
        
        if h in [9, 15, 21] and now.minute == 0:
            enviar_alerta_rj()
            time.sleep(60)
        
        time.sleep(30)

if __name__ == "__main__":
    main()

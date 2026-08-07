#!/usr/bin/env python3
"""
SELIX — Registro de previsões (track record)
Cria um histórico auditável das previsões do SELIX antes do Copom.
"""

import csv
import os
from datetime import datetime
from pathlib import Path

from src.selix.config import SELIC_IDEAL

def registrar_previsao():
    """Registra a previsão atual com timestamp."""
    data = datetime.now().isoformat()
    selic_atual = 14.25
    selic_ideal = SELIC_IDEAL

    arquivo = Path("previsoes.csv")
    arquivo_existe = arquivo.exists()

    with open(arquivo, 'a', newline='') as f:
        writer = csv.writer(f)
        if not arquivo_existe:
            writer.writerow(["data", "selic_ideal", "selic_atual", "selic_real_pos_copom", "acertou"])
        writer.writerow([data, selic_ideal, selic_atual, "", ""])

    print(f"✅ Previsão registrada: {data} → {selic_ideal}%")

if __name__ == "__main__":
    registrar_previsao()

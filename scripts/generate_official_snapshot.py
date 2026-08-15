#!/usr/bin/env python3
"""Snapshot oficial: ideal do modelo + selic_atual do BCB. Sem hardcode de mercado."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.getcwd())


def main():
    from src.selix.config import SELIC_IDEAL, get_selic_atual_from_bcb, get_diferencial

    bcb = get_selic_atual_from_bcb()
    if not bcb.get("success"):
        print("ERRO FATAL: BCB não retornou Selic — snapshot NÃO gerado com número inventado.")
        print(bcb)
        sys.exit(1)

    selic_atual = round(float(bcb["rate"]), 2)
    diferencial = get_diferencial(selic_atual)

    snapshot = {
        "selic_ideal": float(SELIC_IDEAL),
        "diferencial": diferencial,
        "selic_atual": selic_atual,
        "selic_atual_fonte": bcb.get("source"),
        "selic_atual_serie": bcb.get("serie"),
        "selic_atual_data_bcb": bcb.get("data_bcb"),
        "fonte": "src.selix.config + BCB SGS",
        "versao": "v7.2.3",
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "disclaimer": "Ferramenta de apoio à decisão — não substitui o COPOM.",
    }

    out = Path("public")
    out.mkdir(exist_ok=True)
    path = out / "selix-official.json"
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("✅ Snapshot oficial gerado:")
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    print(f"Arquivo: {path}")


if __name__ == "__main__":
    main()

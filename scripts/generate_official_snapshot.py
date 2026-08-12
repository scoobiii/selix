#!/usr/bin/env python3
"""
Gera o snapshot oficial do SELIX a partir da Fonte Única de Verdade.
Saída: public/selix-official.json (ou docs/selix-official.json)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.getcwd())

def main():
    try:
        from src.selix.config import SELIC_IDEAL, DIFERENCIAL
    except Exception as e:
        print(f"ERRO FATAL: não foi possível importar src.selix.config: {e}")
        sys.exit(1)

    selic_atual = round(float(SELIC_IDEAL) + float(DIFERENCIAL), 2)

    snapshot = {
        "selic_ideal": float(SELIC_IDEAL),
        "diferencial": float(DIFERENCIAL),
        "selic_atual": selic_atual,
        "fonte": "src.selix.config",
        "versao": "v7.2.2",
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "disclaimer": "Ferramenta de apoio à decisão — não substitui o COPOM."
    }

    # Garante que a pasta existe
    output_dir = Path("public")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "selix-official.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print("✅ Snapshot oficial gerado:")
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    print(f"\nArquivo salvo em: {output_path}")

if __name__ == "__main__":
    main()

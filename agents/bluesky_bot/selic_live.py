"""Fonte única de Selic atual para os bots — nunca hardcode."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / "public" / "selix-official.json"


def get_selic_atual() -> float:
    # 1) snapshot oficial
    if OFFICIAL.exists():
        try:
            data = json.loads(OFFICIAL.read_text(encoding="utf-8"))
            return float(data["selic_atual"])
        except Exception:
            pass
    # 2) BCB ao vivo
    try:
        from src.selix.config import get_selic_atual_from_bcb
        r = get_selic_atual_from_bcb()
        if r.get("success") or r.get("rate") is not None:
            return float(r["rate"])
    except Exception:
        pass
    # 3) último recurso (só se tudo falhar)
    return 14.0

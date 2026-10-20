#!/usr/bin/env python3
"""Monitor de Selic baseado na meta oficial do BCB SGS 432, sem valores fixos."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any

from src.selix.spi import fetch_current_selic
from src.selix.config import get_selic_ideal


class MonitorSelic:
    def __init__(self):
        self.stakeholders = {
            "decisores": [
                {"handle": "@bancocentral.bsky.social", "nome": "BCB/COPOM", "papel": "Define a meta Selic"},
                {"handle": "@fazenda.bsky.social", "nome": "Ministério da Fazenda", "papel": "Política econômica"},
                {"handle": "@febraban.bsky.social", "nome": "Febraban", "papel": "Representação bancária"},
                {"handle": "@fiesp.bsky.social", "nome": "FIESP", "papel": "Representação industrial"},
            ]
        }

    def buscar_selic_real(self) -> Dict[str, Any]:
        """Retorna a observação oficial validada; propaga erro em vez de inventar fallback."""
        result = fetch_current_selic()
        return {
            "selic": result["rate"],
            "fonte": result["source"],
            "serie": result["serie"],
            "observed_at": result["data_bcb"],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "REAL",
        }

    def calcular_impacto_selic(self) -> Dict[str, Any]:
        """Calcula apenas diferenciais verificáveis; não inventa economia ou rating."""
        atual = self.buscar_selic_real()
        ideal = float(get_selic_ideal())
        return {
            "selic_atual": atual["selic"],
            "selic_ideal": ideal,
            "reducao_pp": round(atual["selic"] - ideal, 2),
            "fonte": atual["fonte"],
            "serie": atual["serie"],
            "observed_at": atual["observed_at"],
            "fetched_at": atual["fetched_at"],
            "status": "REAL",
        }

    def gerar_alerta_copom(self) -> str:
        """Gera alerta sem inventar data ou expectativa para reunião futura."""
        dados = self.calcular_impacto_selic()
        texto = (
            "META SELIC — DADO OFICIAL\n"
            f"Meta atual: {dados['selic_atual']:.2f}% a.a.\n"
            f"SELIX ideal (modelo): {dados['selic_ideal']:.2f}% a.a.\n"
            f"Diferencial do modelo: {dados['reducao_pp']:.2f} p.p.\n"
            f"Fonte: {dados['fonte']} (série {dados['serie']})\n"
            f"Observação BCB: {dados['observed_at']}\n"
            "O diferencial é uma saída de modelo, não uma previsão ou decisão do COPOM."
        )
        return texto[:300]


if __name__ == "__main__":
    monitor = MonitorSelic()
    print(monitor.gerar_alerta_copom())

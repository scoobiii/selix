#!/usr/bin/env python3
"""Monitor Selic vs ROI; exige observação BCB SGS 432 validada antes de alertar."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from atproto import Client

from src.selix.spi import fetch_current_selic
from src.selix.config import get_selic_ideal

load_dotenv()

USERNAME = os.getenv("BLUESKY_USERNAME")
PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

with open("empresas_rj.json", "r", encoding="utf-8") as f:
    dados = json.load(f)
    EMPRESAS = dados["empresas"]
    AUTORIDADES_PLR = dados["autoridades_plr"]


def obter_contexto_selic() -> dict:
    """Consulta e valida a taxa a cada execução; indisponibilidade bloqueia alertas."""
    obs = fetch_current_selic()
    return {
        "selic": float(obs["rate"]),
        "ideal": float(get_selic_ideal()),
        "source": obs["source"],
        "series": obs["serie"],
        "observation_date": obs["data_bcb"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def verificar_impacto_selic(empresa: dict, selic_atual: float) -> dict:
    """Calcula diferença aritmética usando a taxa explicitamente validada pelo chamador."""
    roi = float(empresa["roi_estimado"])
    diferenca = round(selic_atual - roi, 4)
    impacto_plr = (diferenca / 100.0) * float(empresa["plr_devido"]) if diferenca > 0 else 0.0
    return {
        "status": "CRITICO" if diferenca > 0 else "OK",
        "diferenca": diferenca,
        "impacto_plr_estimado": impacto_plr,
        "mensagem": (
            f"Meta Selic oficial {selic_atual:.2f}% a.a. {'>' if diferenca > 0 else '<='} "
            f"ROI estimado {roi:.2f}% a.a.; diferença {diferenca:.2f} p.p."
        ),
    }


def buscar_processos_rj() -> list[dict]:
    """Lista somente os processos já contidos no arquivo de dados local."""
    return [
        {
            "empresa": empresa["nome"],
            "processo": empresa["processo"],
            "trabalhadores": empresa["trabalhadores"],
            "plr_bloqueado": empresa["plr_devido"],
        }
        for empresa in EMPRESAS
    ]


def postar_alerta_selic(empresa: dict, impacto: dict, contexto: dict) -> bool:
    """Publica apenas com proveniência BCB validada; não inventa taxa em falha."""
    autoridades = " ".join(AUTORIDADES_PLR)
    texto = (
        f"{autoridades}\n\n"
        f"{empresa['nome']}: meta Selic BCB {contexto['selic']:.2f}% a.a. "
        f"> ROI estimado {empresa['roi_estimado']}%.\n"
        f"Diferença: {impacto['diferenca']:.2f} p.p.\n"
        f"Observação BCB: {contexto['observation_date']} | SGS {contexto['series']}\n"
        "Estimativa aritmética; não comprova causalidade nem bloqueio de PLR.\n"
        "github.com/scoobiii/TrampoForte #PLR #RJ"
    )
    texto = texto if len(texto) <= 300 else texto[:297] + "..."
    if not USERNAME or not PASSWORD:
        print("Bluesky não configurado; alerta não publicado.")
        return False
    try:
        client = Client()
        client.login(USERNAME, PASSWORD)
        post = client.send_post(texto)
        print(f"Alerta {empresa['nome']} publicado: {post.uri}")
        return True
    except Exception as exc:
        print(f"Falha ao publicar alerta: {exc}")
        return False


def postar_relatorio_completo() -> None:
    """Falha antes de publicar qualquer alerta se o BCB não fornecer dado válido."""
    contexto = obter_contexto_selic()
    print(
        f"Selic BCB: {contexto['selic']:.2f}% a.a.; série {contexto['series']}; "
        f"observação {contexto['observation_date']}; SELIX ideal {contexto['ideal']:.2f}%."
    )
    alertas_enviados = []
    for empresa in EMPRESAS:
        impacto = verificar_impacto_selic(empresa, contexto["selic"])
        print(f"{empresa['nome']}: {impacto['mensagem']}")
        if impacto["status"] == "CRITICO":
            if postar_alerta_selic(empresa, impacto, contexto):
                alertas_enviados.append(empresa["nome"])
            time.sleep(5)
    print(f"Alertas publicados: {', '.join(alertas_enviados) if alertas_enviados else 'nenhum'}")


def monitor_continuo() -> None:
    """Atualiza a observação em cada ciclo e falha fechada quando o BCB está indisponível."""
    print("Iniciando monitor Selic vs ROI; ciclo de 1 hora.")
    while True:
        try:
            contexto = obter_contexto_selic()
            print(
                f"[{datetime.now(timezone.utc).isoformat()}] Selic {contexto['selic']:.2f}% "
                f"(BCB SGS {contexto['series']}, observação {contexto['observation_date']})"
            )
            for empresa in EMPRESAS:
                impacto = verificar_impacto_selic(empresa, contexto["selic"])
                if impacto["status"] == "CRITICO":
                    print(f"{empresa['nome']}: {impacto['mensagem']}")
        except Exception as exc:
            # Nenhuma taxa antiga é reaproveitada e nenhum alerta é publicado.
            print(f"Selic indisponível; ciclo bloqueado sem fallback: {exc}")
        time.sleep(3600)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_continuo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--once":
        try:
            postar_relatorio_completo()
        except Exception as exc:
            raise SystemExit(f"Selic BCB indisponível; nenhum alerta publicado: {exc}")
    else:
        print("Uso: python monitor_selic_roi.py [--once|--monitor]")

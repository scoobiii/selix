"""
forecast_alert.py — SELIX v4.0
Verifica metas usando as tabelas reais: metas + metricas_reais + posts
As metas são lidas do banco (tabela metas), não hardcoded.
Executa via cron: 0 9 * * * (diário às 9h)
"""

import os
import json
import sqlite3
import logging
import datetime
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
DB_PATH     = os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")
LOG_PATH    = "/root/selix/logs/forecast_alert.log"
REPORT_JSON = Path("/root/selix/logs/conversao_ultima.json")

# Fallback: metas padrão caso a tabela metas esteja vazia
METAS_FALLBACK = {
    ("geral",    "mrr"):             5_000.0,
    ("geral",    "clientes_pagos"):  10.0,
    ("bluesky",  "clientes_pagos"):  3.0,
    ("conteudo", "posts_cta"):       5.0,
    ("conteudo", "cliques"):         50.0,
    ("conteudo", "taxa_conversao"):  1.0,
}

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ALERT_TO  = os.getenv("ALERT_EMAIL", "")

Path("/root/selix/logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

# ── Banco ───────────────────────────────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def metrica_real(conn, segmento: str, indicador: str) -> float:
    """Valor mais recente de metricas_reais."""
    row = conn.execute(
        """SELECT valor FROM metricas_reais
           WHERE segmento = ? AND indicador = ?
           ORDER BY data_coleta DESC LIMIT 1""",
        (segmento, indicador),
    ).fetchone()
    return float(row["valor"]) if row else 0.0


def meta_do_banco(conn, segmento: str, indicador: str) -> float:
    """Meta da tabela metas; usa METAS_FALLBACK se não encontrar."""
    row = conn.execute(
        """SELECT meta_valor FROM metas
           WHERE segmento = ? AND indicador = ?
           ORDER BY criado_em DESC LIMIT 1""",
        (segmento, indicador),
    ).fetchone()
    if row:
        return float(row["meta_valor"])
    return METAS_FALLBACK.get((segmento, indicador), 0.0)


def posts_cta_semana(conn) -> int:
    """Posts com CTA nos últimos 7 dias (tabela posts)."""
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    row = conn.execute(
        """SELECT COUNT(*) AS total FROM posts
           WHERE criado_em >= ?
             AND (conteudo LIKE '%scoobiii/selix%'
                  OR conteudo LIKE '%github.com/scoobiii%'
                  OR conteudo LIKE '%selix.com/plano%')""",
        (since,),
    ).fetchone()
    return row["total"] if row else 0

# ── Relatório de conversão ──────────────────────────────────────────────────────

def ler_relatorio() -> dict:
    if not REPORT_JSON.exists():
        log.warning("conversao_ultima.json não encontrado — rode relatorio_conversao.py.")
        return {}
    try:
        return json.loads(REPORT_JSON.read_text())
    except Exception as exc:
        log.error("Erro ao ler relatório: %s", exc)
        return {}

# ── Verificação de metas ────────────────────────────────────────────────────────

def verificar_metas(conn) -> list:
    alertas = []
    funil   = ler_relatorio().get("funil", {})

    # Define cada check: (label, atual, segmento, indicador, unidade, ação)
    checks = [
        (
            "MRR total",
            metrica_real(conn, "geral", "mrr"),
            "geral", "mrr", "R$",
            "Aumentar posts com CTA e converter leads do Bluesky.",
        ),
        (
            "Clientes pagos (total)",
            metrica_real(conn, "geral", "clientes_pagos"),
            "geral", "clientes_pagos", "",
            "Ampliar distribuição do bot e responder mais menções.",
        ),
        (
            "Clientes via Bluesky (semana)",
            metrica_real(conn, "bluesky", "clientes_pagos"),
            "bluesky", "clientes_pagos", "",
            "Adicionar ?ref=bluesky em todos os links do bot.",
        ),
        (
            "Taxa conversão clique→cliente (%)",
            funil.get("taxa_conversao_pct", 0),
            "conteudo", "taxa_conversao", "%",
            "Melhorar CTA: urgência, benefício claro, link direto.",
        ),
        (
            "Posts com CTA (semana)",
            posts_cta_semana(conn),
            "conteudo", "posts_cta", "",
            "Bot deve incluir link CTA em todo post de cenário.",
        ),
        (
            "Cliques nos links (semana)",
            funil.get("cliques_links", 0),
            "conteudo", "cliques", "",
            "Publicar em horários de pico e usar Bitly rastreável.",
        ),
    ]

    for label, atual, seg, ind, unidade, acao in checks:
        alvo = meta_do_banco(conn, seg, ind)
        if alvo == 0:
            log.info("Meta não definida para %s/%s — pulando.", seg, ind)
            continue
        if atual < alvo:
            gap = alvo - atual
            fmt = lambda v: f"{unidade}{v:.2f}" if isinstance(v, float) else f"{unidade}{v}"
            alertas.append({
                "meta":  label,
                "atual": fmt(atual),
                "alvo":  fmt(alvo),
                "gap":   fmt(gap),
                "acao":  acao,
            })

    return alertas

# ── Resumo de situação ──────────────────────────────────────────────────────────

def logar_situacao(conn):
    """Loga snapshot da situação atual mesmo sem alertas."""
    funil = ler_relatorio().get("funil", {})
    log.info("── Snapshot atual ──────────────────────────────────────")
    log.info("  MRR total        : R$ %.2f", metrica_real(conn, "geral", "mrr"))
    log.info("  Clientes pagos   : %.0f",    metrica_real(conn, "geral", "clientes_pagos"))
    log.info("  Clientes Bluesky : %.0f",    metrica_real(conn, "bluesky", "clientes_pagos"))
    log.info("  Posts com CTA    : %d",      posts_cta_semana(conn))
    log.info("  Cliques (Bitly)  : %d",      funil.get("cliques_links", 0))
    log.info("  Conversão        : %.2f%%",  funil.get("taxa_conversao_pct", 0))
    log.info("────────────────────────────────────────────────────────")

# ── E-mail ──────────────────────────────────────────────────────────────────────

def enviar_email(alertas: list):
    if not SMTP_HOST or not ALERT_TO:
        log.info("SMTP não configurado — alertas somente no log.")
        return
    hoje  = datetime.date.today()
    corpo = f"⚠️  Forecast SELIX — {hoje}\n\n"
    for a in alertas:
        corpo += f"• {a['meta']}: {a['atual']} / alvo {a['alvo']} (gap {a['gap']})\n"
        corpo += f"  → {a['acao']}\n\n"
    msg            = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = f"[SELIX] {len(alertas)} meta(s) abaixo do alvo — {hoje}"
    msg["From"]    = SMTP_USER
    msg["To"]      = ALERT_TO
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [ALERT_TO], msg.as_string())
        log.info("E-mail enviado para %s", ALERT_TO)
    except Exception as exc:
        log.error("Falha ao enviar e-mail: %s", exc)

# ── Main ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Verificando metas de forecast…")
    conn = get_conn()
    logar_situacao(conn)
    alertas = verificar_metas(conn)
    conn.close()

    if alertas:
        log.warning("%d meta(s) abaixo do alvo:", len(alertas))
        for a in alertas:
            log.warning("  ❌ %-38s atual=%-12s alvo=%-12s → %s",
                        a["meta"], a["atual"], a["alvo"], a["acao"])
        enviar_email(alertas)
    else:
        log.info("✅ Todas as metas atingidas!")

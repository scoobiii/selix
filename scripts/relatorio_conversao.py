"""
relatorio_conversao.py — SELIX v4.0
Relatório semanal de monetização usando tabelas reais do selix.db:
  posts, respostas_banco, metas, metricas_reais
Executa via cron: 0 10 * * 1 (toda segunda às 10h)
"""

import os
import json
import sqlite3
import logging
import datetime
import requests
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
DB_PATH        = os.getenv("SELIX_DB_PATH", "/root/selix/selix.db")
BITLY_TOKEN    = os.getenv("BITLY_TOKEN", "")
BITLY_GROUP_ID = os.getenv("BITLY_GROUP_ID", "")
LOG_PATH       = "/root/selix/logs/conversao.log"
JANELA_DIAS    = 7

Path("/root/selix/logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

# ── Utilitários ─────────────────────────────────────────────────────────────────

def ago(dias: int) -> str:
    return (datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Queries sobre tabelas reais ─────────────────────────────────────────────────

def posts_publicados(conn, dias: int) -> int:
    """Total de posts criados nos últimos N dias (tabela: posts)."""
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM posts WHERE criado_em >= ?", (ago(dias),)
    ).fetchone()
    return row["total"] if row else 0


def posts_com_cta(conn, dias: int) -> int:
    """Posts com link CTA para o repositório ou plano pago (tabela: posts)."""
    row = conn.execute(
        """SELECT COUNT(*) AS total FROM posts
           WHERE criado_em >= ?
             AND (conteudo LIKE '%scoobiii/selix%'
                  OR conteudo LIKE '%selix.com/plano%'
                  OR conteudo LIKE '%github.com/scoobiii%')""",
        (ago(dias),),
    ).fetchone()
    return row["total"] if row else 0


def posts_por_tipo(conn, dias: int) -> dict:
    """Contagem de posts agrupados por tipo: fato/cenario/alerta/opiniao."""
    rows = conn.execute(
        """SELECT tipo, COUNT(*) AS total FROM posts
           WHERE criado_em >= ?
           GROUP BY tipo""",
        (ago(dias),),
    ).fetchall()
    return {r["tipo"] or "sem_tipo": r["total"] for r in rows}


def respostas_usadas(conn, dias: int) -> int:
    """Respostas do banco utilizadas nos últimos N dias (tabela: respostas_banco).
    Proxy de 'menções respondidas': uso_count > 0 e ultimo_uso recente."""
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=dias)).strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM respostas_banco WHERE ultimo_uso >= ?",
        (since,),
    ).fetchone()
    return row["total"] if row else 0


def top_respostas(conn, dias: int, limite: int = 3) -> list:
    """Respostas mais usadas no período (para identificar dores mais frequentes)."""
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=dias)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """SELECT segmento, dor_keyword, uso_count FROM respostas_banco
           WHERE ultimo_uso >= ?
           ORDER BY uso_count DESC LIMIT ?""",
        (since, limite),
    ).fetchall()
    return [dict(r) for r in rows]


def metrica_real(conn, segmento: str, indicador: str) -> float:
    """Último valor real registrado para um indicador (tabela: metricas_reais)."""
    row = conn.execute(
        """SELECT valor FROM metricas_reais
           WHERE segmento = ? AND indicador = ?
           ORDER BY data_coleta DESC LIMIT 1""",
        (segmento, indicador),
    ).fetchone()
    return float(row["valor"]) if row else 0.0


def meta_valor(conn, segmento: str, indicador: str) -> float:
    """Meta definida para um segmento/indicador (tabela: metas)."""
    row = conn.execute(
        """SELECT meta_valor FROM metas
           WHERE segmento = ? AND indicador = ?
           ORDER BY criado_em DESC LIMIT 1""",
        (segmento, indicador),
    ).fetchone()
    return float(row["meta_valor"]) if row else 0.0

# ── Bitly (opcional) ────────────────────────────────────────────────────────────

def cliques_bitly(dias: int) -> int:
    if not BITLY_TOKEN or not BITLY_GROUP_ID:
        log.info("Bitly não configurado — cliques = 0.")
        return 0
    headers = {"Authorization": f"Bearer {BITLY_TOKEN}"}
    try:
        links = requests.get(
            f"https://api-ssl.bitly.com/v4/groups/{BITLY_GROUP_ID}/bitlinks",
            headers=headers, timeout=10,
        ).json().get("links", [])
        total = 0
        for link in links:
            lid = link["id"].replace("https://", "").replace("/", "%2F")
            c = requests.get(
                f"https://api-ssl.bitly.com/v4/bitlinks/{lid}/clicks/summary"
                f"?unit=day&units={dias}",
                headers=headers, timeout=10,
            )
            total += c.json().get("total_clicks", 0)
        return total
    except Exception as exc:
        log.error("Erro Bitly: %s", exc)
        return 0

# ── Relatório ───────────────────────────────────────────────────────────────────

def gerar_relatorio() -> dict:
    conn    = get_conn()
    cliques = cliques_bitly(JANELA_DIAS)

    # Métricas de conteúdo (posts + respostas)
    n_posts    = posts_publicados(conn, JANELA_DIAS)
    n_cta      = posts_com_cta(conn, JANELA_DIAS)
    n_respostas = respostas_usadas(conn, JANELA_DIAS)
    por_tipo   = posts_por_tipo(conn, JANELA_DIAS)
    top_resp   = top_respostas(conn, JANELA_DIAS)

    # Métricas de conversão vindas de metricas_reais
    clientes_bluesky = metrica_real(conn, "bluesky", "clientes_pagos")
    mrr_bluesky      = metrica_real(conn, "bluesky", "mrr")
    mrr_total        = metrica_real(conn, "geral",   "mrr")
    clientes_total   = metrica_real(conn, "geral",   "clientes_pagos")

    # Metas para comparação (lidas da tabela metas)
    meta_clientes = meta_valor(conn, "bluesky", "clientes_pagos")
    meta_mrr      = meta_valor(conn, "geral",   "mrr")

    conn.close()

    funil = {
        "posts_publicados":    n_posts,
        "posts_com_cta":       n_cta,
        "respostas_usadas":    n_respostas,
        "cliques_links":       cliques,
        "clientes_bluesky":    clientes_bluesky,
        "mrr_bluesky_brl":     mrr_bluesky,
        "mrr_total_brl":       mrr_total,
        "clientes_total":      clientes_total,
        "posts_por_tipo":      por_tipo,
        "top_dores":           top_resp,
        "meta_clientes_bluesky": meta_clientes,
        "meta_mrr_total_brl":    meta_mrr,
    }

    funil["taxa_clique_por_cta"] = (
        round(cliques / n_cta, 2) if n_cta > 0 else 0
    )
    funil["taxa_conversao_pct"] = (
        round(clientes_bluesky / cliques * 100, 2) if cliques > 0 else 0
    )
    funil["gap_clientes"] = max(0, meta_clientes - clientes_bluesky)
    funil["gap_mrr_brl"]  = max(0, meta_mrr - mrr_total)

    return {"periodo_dias": JANELA_DIAS, "data_geracao": now_iso(), "funil": funil}


def salvar_relatorio(r: dict):
    out = Path("/root/selix/logs/conversao_ultima.json")
    out.write_text(json.dumps(r, indent=2, ensure_ascii=False))
    f = r["funil"]
    log.info("═══════ Relatório de Conversão — últimos %d dias ═══════", JANELA_DIAS)
    log.info("📝 Posts publicados    : %d (CTA: %d)", f["posts_publicados"], f["posts_com_cta"])
    log.info("💬 Respostas usadas    : %d", f["respostas_usadas"])
    log.info("🔗 Cliques (Bitly)     : %d", f["cliques_links"])
    log.info("👥 Clientes Bluesky    : %.0f / meta %.0f (gap %.0f)",
             f["clientes_bluesky"], f["meta_clientes_bluesky"], f["gap_clientes"])
    log.info("💰 MRR total           : R$ %.2f / meta R$ %.2f (gap R$ %.2f)",
             f["mrr_total_brl"], f["meta_mrr_total_brl"], f["gap_mrr_brl"])
    log.info("📈 Conversão clique→cli: %.2f%%", f["taxa_conversao_pct"])
    log.info("🔥 Top dores: %s", [d.get("dor_keyword") for d in f["top_dores"]])
    log.info("════════════════════════════════════════════════════════")


if __name__ == "__main__":
    log.info("Iniciando relatório de conversão…")
    r = gerar_relatorio()
    salvar_relatorio(r)
    log.info("✅ Salvo em /root/selix/logs/conversao_ultima.json")

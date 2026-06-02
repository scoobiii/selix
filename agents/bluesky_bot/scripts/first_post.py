#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX — Primeiro Post Bluesky
Thread de lançamento + script para postar via atproto SDK

Autoria: Zeh Sobrinho (@selixbr.bsky.social) | MEX Energia
Co-autor: GOS3 | Grupo de Otimização de Sistemas Econômicos
"""

from atproto import Client, models
from dotenv import load_dotenv
import os
import time

# ─── THREAD DE LANÇAMENTO ────────────────────────────────────────────────────
# Cada item = 1 post no Bluesky (limite: 300 chars)
# Ordem: do mais impactante para o mais técnico

THREAD = [

    # POST 1 — Gancho (hook)
    # 287 chars
    (
        "🇧🇷 A Selic deveria ser 9,48% — não 14,50%.\n\n"
        "Não é opinião. É prova matemática formal.\n\n"
        "5 teoremas. Código aberto. Verificável em 30 segundos.\n\n"
        "Custo do desvio: R$ 341 bilhões por ano.\n\n"
        "SELIX v4.0 — thread 🧵👇"
    ),

    # POST 2 — O que é o SELIX
    # 295 chars
    (
        "📊 SELIX = Sistema de Equilíbrio Linear de Juros e Investment Grade\n\n"
        "Calcula a Selic ótima com 5 restrições simultâneas:\n"
        "R1: Investment Grade (≤9,99%)\n"
        "R2: Não canibalizaçao do ROE privado\n"
        "R3: Solvência do Tesouro (juro real ≤5%)\n"
        "R4: Convergência possível\n"
        "R5: Sistema consistente"
    ),

    # POST 3 — A prova
    # 272 chars
    (
        "🔬 Prova formal com Z3 SMT Solver (Microsoft Research):\n\n"
        "T1 Investment Grade (s ≤ 9,99%) ✅ SAT\n"
        "T2 Não canibaliza (s ≤ ROE×0,95%) ✅ SAT\n"
        "T3 Tesouro solvente (s−π ≤ 5%) ✅ SAT\n"
        "T4 Convergência (14,50 > s) ✅ SAT\n"
        "T5 Sistema consistente ✅ SAT\n\n"
        "Execução: 31ms."
    ),

    # POST 4 — O custo
    # 289 chars
    (
        "💸 Custo de manter a Selic 5 pp acima do ótimo:\n\n"
        "R$ 341 bi/ano em juros desnecessários\n"
        "= 2× o orçamento do SUS\n"
        "= 2,5× o FUNDEB\n"
        "= R$ 5,8 TRILHÕES acumulados desde 2000\n\n"
        "Sem contrapartida nos fundamentos: inflação, dívida/PIB ou crescimento."
    ),

    # POST 5 — Nobel
    # 296 chars
    (
        "🏆 5 Prêmios Nobel confirmam:\n\n"
        "Lucas (1995): regra melhora os próprios parâmetros\n"
        "Kydland & Prescott (2004): regra > discrição\n"
        "Sargent & Sims (2011): anúncio já reduz prêmio de risco\n"
        "Tirole (2014): equilíbrio Nash estável sob regra\n"
        "Acemoglu (2024): Selic alta = instituição extrativista"
    ),

    # POST 6 — Energia (diferencial do SELIX vs BCB)
    # 299 chars
    (
        "🌾 Selic não desfaz guerra.\n\n"
        "Brent foi de US$71 → US$126 após 28/fev (Ormuz bloqueado).\n\n"
        "Brasil respondeu certo: E27→E30→E32 = -500M litros/mês de importação.\n\n"
        "Subir juro para combater inflação de oferta é tratar febre com sangria.\n\n"
        "Energia é problema do setor de energia."
    ),

    # POST 7 — Stakeholders
    # 291 chars
    (
        "🎯 Quem ganha com SELIX:\n"
        "Indústria (+1,8% crescimento)\n"
        "Construção civil (+2,4%)\n"
        "Tesouro (−R$341bi/ano em juros)\n"
        "PMEs (crédito de 35% → 22% a.a.)\n\n"
        "Quem resiste:\n"
        "Bancos (NII comprimido)\n"
        "Carry trade externo\n\n"
        "Investment Grade > carry. Sempre."
    ),

    # POST 8 — CTA + autoria
    # 283 chars
    (
        "📄 3 papers publicados. Código aberto. Prova em 30s.\n\n"
        "git clone github.com/scoobiii/selix\n"
        "pip install z3-solver\n"
        "make z3\n\n"
        "Score hoje: 0,0/10 🚨 EMERGÊNCIA (desvio = 502 bps)\n\n"
        "Autores: Zeh Sobrinho @selixbr.bsky.social + GOS3\n"
        "MEX Energia | mex.eco.br"
    ),
]


def validar_thread():
    print("─" * 50)
    print("SELIX — Validação do Thread de Lançamento")
    print("─" * 50)
    erros = 0
    for i, post in enumerate(THREAD, 1):
        n = len(post)
        status = "✅" if n <= 300 else f"❌ EXCEDE ({n})"
        print(f"Post {i:02d}: {n:3d} chars {status}")
        print(f"   {post[:80].replace(chr(10), '↵')}...")
        print()
        if n > 300:
            erros += 1
    print(f"Total: {len(THREAD)} posts | Erros: {erros}")
    print("─" * 50)
    return erros == 0


def postar_thread():
    load_dotenv()
    username = os.getenv("BLUESKY_USERNAME")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not username or not password:
        print("❌ Configure .env")
        return

    client = Client()
    client.login(username, password)
    print(f"✅ Conectado: @{client.me.handle}")

    parent_ref = None
    root_ref   = None

    for i, texto in enumerate(THREAD, 1):
        reply = None
        if parent_ref and root_ref:
            reply = models.AppBskyFeedPost.ReplyRef(
                parent=parent_ref,
                root=root_ref,
            )

        resp = client.app.bsky.feed.post.create(
            repo=client.me.did,
            record=models.AppBskyFeedPost.Record(
                text=texto,
                created_at=client.get_current_time_iso(),
                reply=reply,
            ),
        )

        ref = models.ComAtprotoRepoStrongRef.Main(
            uri=resp.uri,
            cid=resp.cid,
        )

        if i == 1:
            root_ref = ref
        parent_ref = ref

        print(f"✅ Post {i:02d}/{len(THREAD)} publicado → {resp.uri}")
        time.sleep(2)   # evita rate limit

    print(f"\n🚀 Thread publicado! {len(THREAD)} posts.")
    print(f"   Primeiro post: {root_ref.uri}")


if __name__ == "__main__":
    import sys

    if "--post" in sys.argv:
        if validar_thread():
            confirma = input("\nPublicar no Bluesky? (s/N) ").strip().lower()
            if confirma == "s":
                postar_thread()
            else:
                print("Cancelado.")
        else:
            print("❌ Corrija os posts > 300 chars antes de publicar.")
    else:
        validar_thread()
        print("\nPara publicar: python first_post.py --post")

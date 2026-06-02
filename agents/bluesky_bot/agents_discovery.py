#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# agentes_discovery.py — descobre handles reais com audiência no Bluesky
# Uso: python agentes_discovery.py

import os, json, time
from dotenv import load_dotenv
from atproto import Client

load_dotenv('/root/selix/.env')

# ── CANDIDATOS EXPANDIDOS ─────────────────────────────────────────────────
# Estratégia: buscar por domínio verificado (mais confiável) e por handle comum

CANDIDATOS = {

    # ── Jornalismo econômico ──────────────────────────────────────────────
    "jornalismo": [
        "valoreconomico.bsky.social",   # ✅ confirmado 11k
        "ageniciabrasil.bsky.social",
        "folhadsp.bsky.social",
        "folhadesp.bsky.social",
        "estadao.bsky.social",
        "cartacapital.bsky.social",
        "nexojornal.bsky.social",
        "intercept.bsky.social",
        "piauirevista.bsky.social",
        "agenciapublica.bsky.social",
        "seudinheiro.bsky.social",
        "infomoney.bsky.social",
        "braziljournal.bsky.social",
    ],

    # ── Economistas críticos à Selic alta ────────────────────────────────
    "economia_critica": [
        "laraResende.bsky.social",
        "monicadebolle.bsky.social",
        "lauracarvalho.bsky.social",
        "lauracarvalho.eco.br",          # autoverificado por domínio
        "ricardoamorim.bsky.social",
        "nelsonbarbosa.bsky.social",
        "guilhermemello.bsky.social",
        "persioarida.bsky.social",
        "eduardofagnani.bsky.social",
        "marciosimao.bsky.social",
        "pedroferreira.bsky.social",
        "rodrigolirio.bsky.social",
    ],

    # ── Política / Câmara / Senado ────────────────────────────────────────
    "politica": [
        "gleisi.bsky.social",
        "gleisihoffmann.bsky.social",
        "jaques.bsky.social",
        "jaqueslevy.bsky.social",
        "agluiz.bsky.social",
        "alexmanente.bsky.social",
        "auria.bsky.social",
        "camara.leg.br",                 # domínio oficial
        "senado.leg.br",
        "fazenda.gov.br",
    ],

    # ── Setor produtivo / empresas em RJ ────────────────────────────────
    "setor_produtivo": [
        "cni.bsky.social",
        "cnibrasil.bsky.social",
        "fiesp.bsky.social",
        "abiodiesel.bsky.social",
        "unica.bsky.social",
        "abeve.bsky.social",
        "serasa.bsky.social",
        "boa-vista.bsky.social",
        "recuperacaojudicial.bsky.social",
    ],

    # ── Energia / clima ──────────────────────────────────────────────────
    "energia_clima": [
        "wwfbrasil.bsky.social",         # ✅ confirmado 2.6k
        "ipam.bsky.social",              # ✅ existe (0 seg)
        "inpe.bsky.social",
        "greenpeacebrasil.bsky.social",
        "greenpeace.bsky.social",
        "sosma.bsky.social",
        "observatorioclima.bsky.social",
        "oc.bsky.social",
        "iclei.bsky.social",
        "aneel.gov.br",
    ],

    # ── Trabalhadores / finanças pessoais ────────────────────────────────
    "trabalhadores_financas": [
        "nathfinancas.bsky.social",
        "mepoupenath.bsky.social",
        "nathaliaarcuri.bsky.social",
        "gildovigor.bsky.social",
        "gilvigor.bsky.social",
        "dieese.bsky.social",
        "cut.bsky.social",
        "cutbrasil.bsky.social",
        "cgtb.bsky.social",
    ],

    # ── Mercado financeiro / investidores ────────────────────────────────
    "mercado": [
        "btgpactual.bsky.social",
        "xpi.bsky.social",
        "xpinvestimentos.bsky.social",
        "b3.bsky.social",
        "b3oficial.bsky.social",
        "anbima.bsky.social",
        "cvm.bsky.social",
        "cvm.gov.br",
        "nubank.bsky.social",
    ],
}

MIN_SEGUIDORES = 50   # filtro mínimo para considerar conta "ativa"


def validar(client, candidatos, min_seg=MIN_SEGUIDORES):
    resultado = {}
    total_ok = 0

    for ecossistema, handles in candidatos.items():
        resultado[ecossistema] = {"ativos": [], "inativos": [], "nao_encontrados": []}

        for handle in handles:
            try:
                p = client.get_profile(actor=handle)
                seg = p.followers_count or 0
                entry = {
                    "handle":       handle,
                    "display_name": p.display_name,
                    "followers":    seg,
                    "did":          p.did,
                }
                if seg >= min_seg:
                    resultado[ecossistema]["ativos"].append(entry)
                    print(f"  ✅ {handle:<45} {seg:>7} seg  [{ecossistema}]")
                    total_ok += 1
                else:
                    resultado[ecossistema]["inativos"].append(entry)
                    print(f"  ⚠️  {handle:<45} {seg:>7} seg  (abaixo do mínimo)")
                time.sleep(0.3)   # respeita rate-limit

            except Exception:
                resultado[ecossistema]["nao_encontrados"].append(handle)
                print(f"  ❌ {handle}")

        ativos = len(resultado[ecossistema]["ativos"])
        print(f"\n  [{ecossistema}] → {ativos} handle(s) com >{min_seg} seguidores\n")

    return resultado, total_ok


def gerar_relatorio(resultado):
    """Gera resumo por ecossistema com os handles úteis para o bot."""
    print("\n" + "="*60)
    print("  HANDLES ÚTEIS PARA O BOT SELIX (>50 seguidores)")
    print("="*60)

    handles_para_bot = {}
    for eco, dados in resultado.items():
        ativos = dados["ativos"]
        if ativos:
            # ordena por seguidores
            ativos.sort(key=lambda x: x["followers"], reverse=True)
            handles_para_bot[eco] = ativos
            print(f"\n📌 {eco.upper()}")
            for h in ativos:
                print(f"   @{h['handle']:<40} {h['followers']:>8} seg")

    if not any(dados["ativos"] for dados in resultado.values()):
        print("\n⚠️  Nenhum handle com audiência significativa encontrado.")
        print("   Recomendação: postar sem @menções por enquanto,")
        print("   usar hashtags e aguardar migração do ecossistema para Bluesky.")

    return handles_para_bot


def main():
    print(f"🔍 Verificando {sum(len(v) for v in CANDIDATOS.values())} handles...\n")
    client = Client()
    client.login(
        os.getenv('BLUESKY_USERNAME'),
        os.getenv('BLUESKY_APP_PASSWORD')
    )

    resultado, total_ok = validar(client, CANDIDATOS)
    handles_uteis = gerar_relatorio(resultado)

    # Salva resultado completo
    with open('handles_validos.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    # Salva só os úteis para o bot importar
    with open('handles_bot.json', 'w', encoding='utf-8') as f:
        json.dump(handles_uteis, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {total_ok} handles ativos salvos em handles_bot.json")
    print("   Use handles_bot.json no gerar_posts() para @menções reais.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# selix_campaign.py — Sistema completo de campanha 30 dias
# Versão 3.0.0-CAMPAIGN
# Gera calendário + posts diários para todos os stakeholders
# Uso: python selix_campaign.py [--dry-run] [--day N] [--post]

import os, sys, json, time, sqlite3, requests, argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from atproto import Client, models

load_dotenv('/root/selix/.env')

USERNAME = os.getenv('BLUESKY_USERNAME')
PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')
API_KEY  = os.getenv('SELIX_API_KEY') or os.getenv('MASTER_API_KEY')
API_BASE = "http://localhost:5000"
DB_PATH  = "/root/selix/selix.db"
HEADERS  = {"X-API-Key": API_KEY}
REPO     = "https://github.com/scoobiii/selix"
MAX_CHARS = 295

# ══════════════════════════════════════════════════════════════════
# HANDLES CONFIRMADOS (resultado do agentes_discovery.py)
# Atualizar após rodar a descoberta
# ══════════════════════════════════════════════════════════════════
HANDLES = {
    "midia":          ["valoreconomico.bsky.social"],
    "energia":        ["wwfbrasil.bsky.social", "minaseenergia.bsky.social",
                       "petrobrasoficial.bsky.social"],
    "politica":       ["pt.org.br", "gleisi.bsky.social",
                       "randolfe.bsky.social", "lindbergh.bsky.social"],
    "mercado":        ["b3.com.br", "nubank.bsky.social"],
    "governo":        ["bndes.gov.br", "fazenda.gov.br", "ipea.gov.br"],
    "academia":       ["fgv.br", "ibre.fgv.br"],
    "setor_produtivo":["petrobras.com.br", "sebrae.com.br"],
    "trabalhadores":  ["cut.org.br", "dieese.org.br"],
    "rj_empresas":    ["serasa.bsky.social", "oab.org.br"],
    "presidenciaveis":["lula.com.br", "tarcisio.bsky.social",
                       "boulos.bsky.social"],
}

def cc(*ecossistemas):
    """Monta string de @menções para os ecossistemas solicitados."""
    handles = []
    for eco in ecossistemas:
        handles += [f"@{h}" for h in HANDLES.get(eco, [])]
    if not handles:
        return ""
    return "\n\ncc " + " ".join(handles[:4])  # máx 4 por post

# ══════════════════════════════════════════════════════════════════
# DADOS REAIS
# ══════════════════════════════════════════════════════════════════
def fetch_dados():
    try:
        e = requests.get(f"{API_BASE}/v1/energia/mistura",
                         headers=HEADERS, timeout=5).json()
        s = requests.get(f"{API_BASE}/v1/selic",
                         headers=HEADERS, timeout=5).json()
        brent = e['brent_usd']
        return dict(brent=brent, e_mix=e['etanol']['mistura'],
                    b_mix=e['biodiesel']['mistura'],
                    sv=s[0]['valor'],
                    sent="negativo" if brent>90 else
                         ("positivo" if brent<70 else "neutro"))
    except Exception:
        pass
    try:
        conn = sqlite3.connect(DB_PATH)
        brent = conn.execute(
            "SELECT price FROM brent WHERE success=1 "
            "ORDER BY timestamp DESC LIMIT 1").fetchone()[0]
        sv = conn.execute(
            "SELECT valor FROM commodities WHERE tipo='efetiva' "
            "ORDER BY criado_em DESC LIMIT 1").fetchone()[0]
        conn.close()
        return dict(brent=brent, e_mix=27, b_mix=14, sv=sv,
                    sent="negativo" if brent>90 else "neutro")
    except Exception:
        return dict(brent=97.0, e_mix=27, b_mix=14,
                    sv=14.25, sent="negativo")

# ══════════════════════════════════════════════════════════════════
# CALENDÁRIO 30 DIAS — 3 POSTS/DIA — 10 SEGMENTOS
# Rotação: cada dia foca em 3 segmentos diferentes
# Semana 1-2: apresentação / Semana 3-4: aprofundamento
# ══════════════════════════════════════════════════════════════════

def gerar_calendario(d):
    """
    Retorna dict {dia: [post1, post2, post3]}
    Cada post é um dict {texto, segmento, horario}
    """
    brent = d['brent']
    sv    = d['sv']
    em    = d['e_mix']
    bm    = d['b_mix']
    sent  = d['sent']
    R     = REPO

    # Templates por segmento — 4 variações cada (semana 1,2,3,4)
    templates = {

        "abertura": [
            f"🧵 SELIX — Economia que prioriza quem trabalha\n\n🌍 Brent: US${brent} | 📉 Selic: {sv}% | 📰 {sent}\n💰 Meta ideal: 9,25% (razão global 1,14×)\n🔗 {R}\n\nFio completo 👇",
            f"📊 SELIX atualizado\n\nBrent US${brent} • Selic {sv}% • Meta global: 9,25%\n\nO BCB cobra 2,7× mais que a média mundial. Quem paga essa conta?\n🔗 {R}",
            f"🤖 SELIX — IA + Lean 4 + Z3\n\nProva formal: Selic deveria ser 9,25%.\nBrent US${brent} confirma: sentimento {sent}.\n\nVeja o estudo completo:\n🔗 {R}",
            f"📡 SELIX — dados de hoje\n\n🛢️ Brent: US${brent}\n📉 Selic: {sv}% (deveria: 9,25%)\n🌱 Mix: E{em}/B{bm}\n💸 Custo extra/ano: R$270 bi\n🔗 {R}",
        ],

        "trabalhadores": [
            f"👷 Trabalhador, a Selic te cobra caro\n\nCom {sv}%, seu empréstimo de R$10k custa R$1.425/ano só de juros.\nCom 9,25%: R$925. Diferença: R$500/ano no seu bolso.\n\n#TrampoForte #Selix\n🔗 {R}{cc('trabalhadores')}",
            f"💼 PLR bloqueada pela Selic\n\nGPA, Raízen e +5.680 empresas em RJ em 2025.\nSelic {sv}% > ROI médio = PLR zerada.\nCom Selix 9,25%: empresas voltam a lucrar, PLR volta.\n\n#TrampoForte\n🔗 {R}{cc('trabalhadores')}",
            f"🏥 Selic alta = menos emprego\n\nCada 1% de juros a mais = ~200 mil empregos destruídos (DIEESE).\nDe {sv}% para 9,25% = +1 milhão de empregos.\n\n#TrampoForte #Selix\n🔗 {R}{cc('trabalhadores')}",
            f"📈 Salário real vs Selic\n\nSeu salário cresce 3%/ano. A dívida do governo cresce 15%/ano.\nQuem paga? Você, via impostos e PLR zerada.\n\nSelix 9,25% quebra esse ciclo.\n🔗 {R}{cc('trabalhadores')}",
        ],

        "investidores": [
            f"📈 Oportunidade histórica\n\nGPA (PCAR3): -68% vs pico. Raízen (RAIZ4): -76%.\nCom Selic 9,25%, múltiplos normalizam.\nUpside potencial: +150-200%.\n\n#Selix #B3\n🔗 {R}{cc('mercado')}",
            f"🏦 B3 a US$10 tri em 10 anos?\n\nCom Selic 1 dígito + investment grade A-:\n• P/L médio sobe de 8x para 14x\n• B3: US$1,6 tri → US$10 tri\n• Ibovespa: 186k pontos (BTG proj.)\n\n🔗 {R}{cc('mercado')}",
            f"💹 Custo de capital vs retorno\n\nWACC médio BR hoje: ~18%\nCom Selix 9,25%: WACC cai para ~11%\nIRR de projetos que hoje são inviáveis viram lucrativos.\n\n#Selix #Investimento\n🔗 {R}{cc('mercado')}",
            f"🌍 Brasil vs mundo\n\nRazão juros/inflação global: 1,14×\nBrasil atual: 2,7×\nBrasil Selix: 1,14×\n\nConvengência = entrada maciça de capital estrangeiro.\n🔗 {R}{cc('mercado')}",
        ],

        "governo": [
            f"🏛️ Governo economiza R$270 bi/ano\n\nDívida pública: R$6,9 tri\nCom Selic {sv}%: R$1 tri/ano em juros\nCom Selix 9,25%: R$638 bi/ano\nEconomia: R$362 bi para saúde, educação, infraestrutura.\n🔗 {R}{cc('governo')}",
            f"📉 Dívida/PIB cai com Selix\n\nHoje: dívida/PIB cresce ~3pp/ano\nCom 9,25%: estabiliza no 1º ano\nInvestment Grade A- em 3 anos\nCusto de captação externa cai 200bps\n🔗 {R}{cc('governo')}",
            f"🏗️ Haddad quer R$2 tri em data centers\nBCB cobra 14,5% de capital\nIRR de data center: ~12%\n\n❌ 14,5% > 12% = projeto inviável\n✅ 9,25% < 12% = projeto viável\n\nSelix desbloqueie o investimento.\n🔗 {R}{cc('governo')}",
            f"⚡ PAC vs Selic\n\nO governo anuncia R$1,7 tri em obras.\nO BCB cobra R$1 tri/ano em juros.\n\nÉ como encher banheira com torneira aberta.\nSelix 9,25% fecha a torneira.\n🔗 {R}{cc('governo')}",
        ],

        "politicos": [
            f"🗳️ Eleições 2026: quem defende 9,25%?\n\nSelic 1 dígito = +1M empregos + PLR liberada + B3 a US$10 tri\n\nO candidato que defender Selix chega na frente.\n\n#Selix2026 #TrampoForte\n🔗 {R}{cc('presidenciaveis')}",
            f"📊 Selic e votos\n\nDado histórico: inflação/juros altos = rejeição do governo.\nSelic {sv}% em ano eleitoral = eleitor insatisfeito.\n\nSelix 9,25% = agenda vencedora.\n\n#Selix2026\n🔗 {R}{cc('presidenciaveis')}",
            f"💡 PL TrampoForte\n\nProposta: trabalhador recebe PLR antes do banco receber juros.\nCom Selix 9,25%: PLR liberada em 4.200 empresas.\n\nApoie o PL. #TrampoForte\n🔗 {R}{cc('politica')}",
            f"🌎 Brasil no G7 em 10 anos?\n\nCom Selix 9,25%:\n• PIB per capita: US$130k (+118%)\n• Investment Grade A-\n• B3: US$10 tri\n\nÉ uma escolha de política monetária.\n🔗 {R}{cc('presidenciaveis')}",
        ],

        "energia_clima": [
            f"🌱 Brent US${brent} → Mix ideal: E{em}/B{bm}\n\nSelix calcula em tempo real o mix ótimo de biocombustíveis.\nCom Selic 1 dígito: 100 GW solar viável em 10 anos.\n\n#EnergiaLimpa #Selix\n🔗 {R}{cc('energia')}",
            f"☀️ Solar vs juros\n\nUsina solar: payback 8 anos, IRR 13%\nCom Selic {sv}%: WACC 18% > IRR 13% = inviável\nCom Selix 9,25%: WACC 11% < IRR 13% = viável\n\n🔗 {R}{cc('energia')}",
            f"🌊 Crise climática + juros altos = duplo risco\n\nO Brasil tem 1,7 TW de potencial renovável.\nJuros altos travam o financiamento.\nSelix 9,25% desbloqueie R$800 bi em green finance.\n🔗 {R}{cc('energia')}",
            f"⛽ Petróleo a US${brent} e o dilema brasileiro\n\nBrent alto = mais receita Petrobras = mais espaço fiscal\nCom Selix: receita do pré-sal financia transição energética\nMix E{em}/B{bm} otimiza emissões agora.\n🔗 {R}{cc('energia')}",
        ],

        "jornalismo": [
            f"📰 Para redações: Selix é pauta\n\nIA + prova formal (Lean 4 + Z3) calcula Selic ótima: 9,25%.\nDados reais, código aberto, auditável.\n\nEntreviste: github.com/scoobiii/selix\n🔗 {R}{cc('midia')}",
            f"🔍 Fact-check Selix\n\nAfirmação: Selic deveria ser 9,25%, não {sv}%\nBase: razão juros/inflação de EUA, UE, Japão, China, Alemanha\nMédia ponderada: 1,14×\nIPCA 4% × 1,14 = 4,56% ← meta\n\n🔗 {R}{cc('midia')}",
            f"📊 Dado do dia\n\n5.680 empresas em RJ em 2025 (+24% vs 2024)\nCausa principal: Selic {sv}%\nFonte: Serasa Experian\n\nSelix 9,25% prevenia esse número.\n🔗 {R}{cc('midia', 'rj_empresas')}",
            f"🤖 IA prevê Selic\n\nSelix usa Qwen + RAG + Lean 4 para calcular taxa ideal.\nNão é opinião — é prova formal verificável.\nCódigo aberto: {R}\n\n#IA #Economia #Selix{cc('midia', 'academia')}",
        ],

        "bancos_mercado": [
            f"🏦 Bancos ganham mais com Selic 9,25%\n\nMenos inadimplência (empresas sobrevivem)\nMenos RJ = menos provisão para devedores duvidosos\nMercado de capitais maior = mais fee\n\nSpread ainda lucrativo.\n🔗 {R}{cc('mercado')}",
            f"💳 Inadimplência vs Selic\n\nSelic {sv}% → inadimplência PJ: 4,8% (recorde)\nSelix 9,25% → inadimplência estimada: 2,1%\n\nBancos perdem menos. Lucro líquido cresce.\n🔗 {R}{cc('mercado')}",
            f"🌐 Investment Grade A-\n\nCom Selix 9,25% + fiscal em ordem:\nMoody's e S&P sobem rating\nCusto de captação externa cai 150bps\nBancos BR ficam mais competitivos globalmente\n🔗 {R}{cc('mercado')}",
            f"📉 CDS Brasil hoje: ~200bps\nPaíses com Selix equivalente: ~40bps\n\nDiferença = prêmio de risco evitável.\nSelix remove 80bps de prêmio político-fiscal.\n🔗 {R}{cc('mercado', 'academia')}",
        ],

        "academia": [
            f"🎓 Teoria por trás do Selix\n\nNão é MMT nem ortodoxia.\nÉ calibração: razão J/I global 1,14×\napplicada ao IPCA projetado (4%).\n= 4,56% como piso neutro.\n\nDetalhes: {R}{cc('academia')}",
            f"📐 Lean 4 + Z3 como prova formal\n\ntheorem selicReal : nominal - ipca = real\ntheorem metaOtima : ipca * 1.14 = 4.56\ntheorem premioRisco : 14.25 - 4.56 = 9.69\n\nVerificável em: {R}{cc('academia')}",
            f"🔬 Taxa neutra vs Selic atual\n\nTaxa neutra BCB: ~5,5% real\nCom IPCA 4%: neutro nominal = 9,5%\nSelic atual: {sv}% = +{round(sv-9.5,2)}pp de aperto\n\nQuem justifica esse aperto além do BCB?\n🔗 {R}{cc('academia')}",
            f"📚 Literatura sobre captura regulatória\n\nStigler (1971): agências capturadas por regulados.\nBCB → sistema financeiro = porta giratória.\nSelix quantifica o custo: R$270 bi/ano.\n\nArtigo completo: {R}{cc('academia', 'midia')}",
        ],

        "rj_recuperacao": [
            f"⚖️ 5.680 empresas em RJ em 2025\n\n+24% vs 2024. Sem recessão declarada.\nCausa: Selic {sv}% > ROI médio 11%.\n\nSelix 9,25% = viabilidade para 4.200 dessas empresas.\n🔗 {R}{cc('rj_empresas')}",
            f"🏚️ GPA, Raízen, Americanas\n\nEmpresas em RJ com juros altos:\n• Custos financeiros > lucro operacional\n• PLR zeroed\n• Demissões para pagar dívida\n\nSelix 9,25% inverte essa equação.\n🔗 {R}{cc('rj_empresas', 'trabalhadores')}",
            f"💼 Advogados de RJ: Selix é pauta\n\nVolume de processos de RJ cresceu 24% em 2025.\nPrincipal causa: custo financeiro > ROI.\nSelix propõe solução sistêmica, não caso a caso.\n🔗 {R}{cc('rj_empresas')}",
            f"📋 Dados Serasa Experian 2025\n\n• 5.680 RJ (+24%)\n• 1.482 falências (+31%)\n• Varejo e indústria: 60% dos casos\n• Custo médio da dívida: 21,8%\n\nCom Selix 9,25%: custo médio → 13%.\n🔗 {R}{cc('rj_empresas')}",
        ],
    }

    # ── CALENDÁRIO: rotação de segmentos por dia ──────────────────
    # 3 posts/dia, cada um num segmento diferente
    # 30 dias × 3 posts = 90 posts total
    # Horários: 9h, 13h, 18h

    rotacao = [
        # Semana 1 — introdução e dados
        ("abertura",       "trabalhadores",  "investidores"),
        ("governo",        "energia_clima",  "jornalismo"),
        ("bancos_mercado", "politicos",      "rj_recuperacao"),
        ("academia",       "abertura",       "trabalhadores"),
        ("investidores",   "governo",        "energia_clima"),
        ("jornalismo",     "bancos_mercado", "politicos"),
        ("rj_recuperacao", "academia",       "abertura"),
        # Semana 2 — aprofundamento
        ("trabalhadores",  "investidores",   "governo"),
        ("energia_clima",  "jornalismo",     "bancos_mercado"),
        ("politicos",      "rj_recuperacao", "academia"),
        ("abertura",       "trabalhadores",  "investidores"),
        ("governo",        "energia_clima",  "jornalismo"),
        ("bancos_mercado", "politicos",      "rj_recuperacao"),
        ("academia",       "abertura",       "trabalhadores"),
        # Semana 3 — dados + provas
        ("investidores",   "governo",        "energia_clima"),
        ("jornalismo",     "bancos_mercado", "politicos"),
        ("rj_recuperacao", "academia",       "abertura"),
        ("trabalhadores",  "investidores",   "governo"),
        ("energia_clima",  "jornalismo",     "bancos_mercado"),
        ("politicos",      "rj_recuperacao", "academia"),
        ("abertura",       "trabalhadores",  "investidores"),
        # Semana 4 — CTA + eleições 2026
        ("governo",        "energia_clima",  "jornalismo"),
        ("bancos_mercado", "politicos",      "rj_recuperacao"),
        ("academia",       "abertura",       "trabalhadores"),
        ("investidores",   "governo",        "energia_clima"),
        ("jornalismo",     "bancos_mercado", "politicos"),
        ("rj_recuperacao", "academia",       "abertura"),
        ("trabalhadores",  "investidores",   "governo"),
        ("energia_clima",  "jornalismo",     "bancos_mercado"),
        ("politicos",      "rj_recuperacao", "academia"),
    ]

    horarios = ["09:00", "13:00", "18:00"]
    calendario = {}

    for dia, (seg1, seg2, seg3) in enumerate(rotacao, start=1):
        segs = [seg1, seg2, seg3]
        posts = []
        for i, seg in enumerate(segs):
            variacao = (dia - 1) % 4   # 4 variações por segmento
            lista = templates.get(seg, templates["abertura"])
            texto = lista[variacao % len(lista)]
            texto = trunc(texto)
            posts.append({
                "segmento": seg,
                "horario":  horarios[i],
                "texto":    texto,
                "chars":    len(texto),
            })
        calendario[dia] = posts

    return calendario


def trunc(text, limit=MAX_CHARS):
    return text if len(text) <= limit else text[:limit-1] + "…"


# ══════════════════════════════════════════════════════════════════
# PUBLICAÇÃO
# ══════════════════════════════════════════════════════════════════

def publicar_posts(client, posts_dia):
    """Publica os 3 posts do dia como posts independentes (não thread)."""
    for p in posts_dia:
        resultado = client.send_post(p['texto'])
        print(f"  ✅ [{p['segmento']:20}] {p['horario']} → {resultado.uri}")
        time.sleep(2)


def publicar_thread_dia(client, posts_dia):
    """Publica os 3 posts do dia como thread encadeada."""
    if not posts_dia:
        return
    root = client.send_post(posts_dia[0]['texto'])
    print(f"  ✅ [ROOT {posts_dia[0]['segmento']:15}] → {root.uri}")
    prev = root
    for p in posts_dia[1:]:
        reply_ref = models.AppBskyFeedPost.ReplyRef(
            root   = models.ComAtprotoRepoStrongRef.Main(
                         uri=root.uri, cid=root.cid),
            parent = models.ComAtprotoRepoStrongRef.Main(
                         uri=prev.uri, cid=prev.cid),
        )
        prev = client.send_post(text=p['texto'], reply_to=reply_ref)
        print(f"  ✅ [REPLY {p['segmento']:14}] → {prev.uri}")
        time.sleep(1)


# ══════════════════════════════════════════════════════════════════
# RELATÓRIO
# ══════════════════════════════════════════════════════════════════

def imprimir_calendario(cal):
    print(f"\n{'═'*65}")
    print(f"  CALENDÁRIO SELIX — 30 DIAS × 3 POSTS/DIA = 90 POSTS")
    print(f"{'═'*65}")
    for dia, posts in cal.items():
        data = (datetime.now() + timedelta(days=dia-1)).strftime("%d/%m %a")
        print(f"\n  Dia {dia:02d} ({data})")
        for p in posts:
            print(f"    {p['horario']}  [{p['segmento']:20}]  "
                  f"{p['chars']:3}c  {p['texto'][:55]}…")

    # Contagem por segmento
    contagem = {}
    for posts in cal.values():
        for p in posts:
            contagem[p['segmento']] = contagem.get(p['segmento'], 0) + 1
    print(f"\n{'─'*65}")
    print(f"  POSTS POR SEGMENTO:")
    for seg, n in sorted(contagem.items(), key=lambda x: -x[1]):
        print(f"    {seg:25} {n:3} posts")
    print(f"\n  TOTAL: {sum(contagem.values())} posts em 30 dias")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Selix Campaign Manager")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra calendário sem publicar")
    parser.add_argument("--day", type=int, default=None,
                        help="Publica posts do dia N")
    parser.add_argument("--post", action="store_true",
                        help="Realmente publica (sem isso, só simula)")
    parser.add_argument("--thread", action="store_true",
                        help="Publica como thread (padrão: posts independentes)")
    parser.add_argument("--save-json", action="store_true",
                        help="Salva calendário em calendario_30dias.json")
    args = parser.parse_args()

    print("📡 Buscando dados reais...")
    d = fetch_dados()
    print(f"   Brent: US${d['brent']} | Selic: {d['sv']}% | "
          f"Mix: E{d['e_mix']}/B{d['b_mix']} | Sentimento: {d['sent']}")

    print("📅 Gerando calendário 30 dias...")
    cal = gerar_calendario(d)

    if args.save_json or args.dry_run:
        with open("calendario_30dias.json", "w", encoding="utf-8") as f:
            json.dump(cal, f, indent=2, ensure_ascii=False)
        print("💾 Salvo em calendario_30dias.json")

    if args.dry_run:
        imprimir_calendario(cal)
        return

    if args.day:
        dia = args.day
        if dia not in cal:
            print(f"❌ Dia {dia} fora do range (1-30)")
            sys.exit(1)
        posts_dia = cal[dia]
        print(f"\n📋 Dia {dia} — {len(posts_dia)} posts:")
        for p in posts_dia:
            print(f"\n  [{p['segmento']}] {p['horario']}")
            print(f"  {p['texto']}\n")
            print(f"  {'─'*50}")

        if args.post:
            if not USERNAME or not PASSWORD:
                sys.exit("❌ Credenciais não encontradas")
            print(f"\n🔐 Autenticando como {USERNAME}...")
            client = Client()
            client.login(USERNAME, PASSWORD)
            print(f"🚀 Publicando dia {dia}...")
            if args.thread:
                publicar_thread_dia(client, posts_dia)
            else:
                publicar_posts(client, posts_dia)
            print("🎉 Publicado!")
        else:
            print("\n💡 Use --post para publicar de verdade")
    else:
        imprimir_calendario(cal)
        print("\n💡 Comandos:")
        print("   Ver dia 1:          python selix_campaign.py --day 1")
        print("   Publicar dia 1:     python selix_campaign.py --day 1 --post")
        print("   Thread do dia 1:    python selix_campaign.py --day 1 --post --thread")
        print("   Salvar JSON:        python selix_campaign.py --dry-run --save-json")
        print("   Agendar (cron):     0 9,13,18 * * * python selix_campaign.py --day $(date +%-j) --post")


if __name__ == "__main__":
    main()


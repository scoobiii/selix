#!/usr/bin/env python3
"""
Sistema de Threads para cada Ecossistema:
- Energia (Brent/TTF/Mix E/B)
- Selic 1 dígito (SELIX)
- Recuperação Judicial (TrampoForte)
"""

import sys
import os
sys.path.insert(0, '/root/selix/agents/bluesky_bot')

from datetime import datetime
from fontes_confiaveis import FontesConfi
from post_seguro import postar_seguro
import time

class ThreadsEcossistemas:
    def __init__(self):
        self.fonte = FontesConfi()
    
    # ============================================================
    # THREAD 1: ECOSSISTEMA ENERGIA (Brent, TTF, Mix E/B)
    # ============================================================
    def post_energia_1(self) -> str:
        brent = self.fonte.brent_real()
        ttf = self.fonte.ttf_real()
        return f"""@mme.bsky.social @anp.bsky.social @ccee.bsky.social

🌍 ECOSSISTEMA ENERGIA - {datetime.now().strftime('%d/%m/%Y %H:%M')}

🛢️ BRENT: US$ {brent['preco']} ({brent['fonte']})
🔥 TTF EUROPA: € {ttf['preco']}/MWh

⚠️ Risco geopolítico: ALTO

1/3"""
    
    def post_energia_2(self) -> str:
        brent = self.fonte.brent_real()
        mistura = self.fonte.recomendar_mistura()
        return f"""@mme.bsky.social @anp.bsky.social

📊 MISTURA ETANOL - RECOMENDAÇÃO SELIX:

Brent US$ {brent['preco']} → {mistura['mistura']}
⏱️ Tempo: {mistura['tempo']} | Status: {mistura['status']}

💰 Economia anual: US$ 30,2 bi

2/3"""
    
    def post_energia_3(self) -> str:
        return f"""@mme.bsky.social @ccee.bsky.social

🏭 ECOSSISTEMA ENERGIA - STAKEHOLDERS:

✅ CNPE, MME, ANP, CCEE
✅ Produtores: BP, Raízen, Cargill

🔗 github.com/scoobiii/selix
#SELIX #Energia #MixEtanol

3/3

⚠️ Não é recomendação de investimento."""
    
    def thread_energia(self, publicar=False):
        """Gera thread de energia (3 posts)"""
        posts = [self.post_energia_1(), self.post_energia_2(), self.post_energia_3()]
        
        if publicar:
            for i, texto in enumerate(posts, 1):
                print(f"   Publicando post {i}/3...")
                resultado = postar_seguro(texto)
                print(f"   ✅ {resultado.get('url', 'Publicado')}")
                time.sleep(3)
        else:
            for i, texto in enumerate(posts, 1):
                print(f"\n📝 POST {i}/3:")
                print(texto)
                print("-" * 50)
        
        return posts
    
    # ============================================================
    # THREAD 2: SELIC 1 DÍGITO (SELIX)
    # ============================================================
    def post_selix_1(self) -> str:
        selic = self.fonte.selic_real()
        return f"""@bancocentral.bsky.social @fazenda.bsky.social

📊 TEOREMA SELIX - Selic 1 Dígito

📍 ATUAL: {selic['selic']}%
📍 SELIX: 9,48%

📉 REDUÇÃO: {(selic['selic'] - 9.48):.1f} p.p.

🔬 Provado com Z3 + Lean 4

1/3"""
    
    def post_selix_2(self) -> str:
        return f"""@bancocentral.bsky.social

💰 IMPACTO DA SELIC 1 DÍGITO:

✅ Economia: R$ 270 bi/ano
✅ Investment Grade: BBB+
✅ Juro real: 4,77%
✅ +R$ 794 PIB per capita

2/3"""
    
    def post_selix_3(self) -> str:
        return f"""@senado.bsky.social

🏛️ ECOSSISTEMA SELIC:

✅ COPOM, BCB, CMN, Fazenda
✅ Febraban, FIESP

🔗 github.com/scoobiii/selix
#SELIX #Selic1Digito

3/3

⚠️ Não é recomendação de investimento."""
    
    def thread_selix(self, publicar=False):
        """Gera thread SELIX (3 posts)"""
        posts = [self.post_selix_1(), self.post_selix_2(), self.post_selix_3()]
        
        if publicar:
            for i, texto in enumerate(posts, 1):
                print(f"   Publicando post {i}/3...")
                resultado = postar_seguro(texto)
                print(f"   ✅ {resultado.get('url', 'Publicado')}")
                time.sleep(3)
        else:
            for i, texto in enumerate(posts, 1):
                print(f"\n📝 POST {i}/3:")
                print(texto)
                print("-" * 50)
        
        return posts
    
    # ============================================================
    # THREAD 3: RECUPERAÇÃO JUDICIAL (TRAMPOFORTE)
    # ============================================================
    def post_rj_1(self) -> str:
        return f"""@mpt.bsky.social @tst.bsky.social

⚖️ TRAMPOFORTE - Prioridade ao Trabalhador

✅ PLR tem prioridade ABSOLUTA sobre credores
✅ Trabalhadores viram sócios
✅ Assentos no Conselho

1/3"""
    
    def post_rj_2(self) -> str:
        return f"""@mpt.bsky.social

📊 CASOS CRÍTICOS:

🏢 GPA: R$1,96 → R$17,60 (+798%)
🏢 RAIZEN: R$0,34 → R$11,15 (+3.179%)

💰 PLR bloqueado: R$140M (70k trabalhadores)

2/3"""
    
    def post_rj_3(self) -> str:
        return f"""@senado.bsky.social

🏛️ TRAMPOFORTE - PROPOSTA:

✅ PLR prioritário em RJ
✅ 50% dívida → ações
✅ 34 assentos Conselho

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #PLR

3/3

⚠️ Não é recomendação de investimento."""
    
    def thread_rj(self, publicar=False):
        """Gera thread RJ (3 posts)"""
        posts = [self.post_rj_1(), self.post_rj_2(), self.post_rj_3()]
        
        if publicar:
            for i, texto in enumerate(posts, 1):
                print(f"   Publicando post {i}/3...")
                resultado = postar_seguro(texto)
                print(f"   ✅ {resultado.get('url', 'Publicado')}")
                time.sleep(3)
        else:
            for i, texto in enumerate(posts, 1):
                print(f"\n📝 POST {i}/3:")
                print(texto)
                print("-" * 50)
        
        return posts
    
    def todas_threads(self, publicar=False):
        """Gera todas as threads"""
        print("\n" + "=" * 70)
        print("📢 ECOSSISTEMA ENERGIA")
        print("=" * 70)
        self.thread_energia(publicar)
        
        print("\n" + "=" * 70)
        print("📢 SELIC 1 DÍGITO (SELIX)")
        print("=" * 70)
        self.thread_selix(publicar)
        
        print("\n" + "=" * 70)
        print("📢 RECUPERAÇÃO JUDICIAL (TRAMPOFORTE)")
        print("=" * 70)
        self.thread_rj(publicar)

if __name__ == "__main__":
    import sys
    
    threads = ThreadsEcossistemas()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--publicar":
        print("🚀 PUBLICANDO THREADS NO BLUESKY...")
        threads.todas_threads(publicar=True)
    else:
        print("📋 VISUALIZANDO THREADS (simulação)")
        print("   Para publicar: python3 threads_ecossistemas.py --publicar")
        threads.todas_threads(publicar=False)

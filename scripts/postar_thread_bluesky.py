#!/usr/bin/env python3
"""
SELIX v6.1 - Postar Thread no Bluesky
Uso: python scripts/postar_thread_bluesky.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Adicionar caminho do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from atproto import Client
except ImportError:
    print("❌ atproto não instalado. Execute: pip install atproto")
    sys.exit(1)


class BlueskyPoster:
    """Posta threads no Bluesky"""

    def __init__(self):
        self.client = Client()
        self.handle = os.getenv("BLUESKY_HANDLE", "zeh-sobrinho.bsky.social")
        self.password = os.getenv("BLUESKY_PASSWORD")

        if not self.password:
            print("❌ BLUESKY_PASSWORD não configurado no .env")
            print("   Crie um arquivo .env com:")
            print("   BLUESKY_HANDLE=zeh-sobrinho.bsky.social")
            print("   BLUESKY_PASSWORD=sua_senha")
            sys.exit(1)

    def login(self):
        """Faz login no Bluesky"""
        try:
            self.client.login(self.handle, self.password)
            print(f"✅ Login realizado: {self.handle}")
            return True
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return False

    def post_thread(self, posts):
        """Publica uma thread no Bluesky"""
        if not posts:
            print("❌ Nenhum post para publicar")
            return

        print(f"\n📝 Publicando thread com {len(posts)} posts...")
        print("=" * 60)

        parent_ref = None
        parent_uri = None

        for i, text in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}] {text[:80]}...")

            try:
                if parent_ref is None:
                    # Primeiro post
                    response = self.client.send_post(text)
                else:
                    # Posts seguintes (reply)
                    response = self.client.send_post(
                        text,
                        reply_to={
                            "root": {"uri": parent_uri, "cid": parent_ref},
                            "parent": {"uri": parent_uri, "cid": parent_ref},
                        },
                    )

                # Atualizar referências para o próximo post
                parent_uri = response.uri
                parent_ref = response.cid

                print(f"   ✅ Post {i} publicado!")
                time.sleep(1)  # Pausa para evitar rate limit

            except Exception as e:
                print(f"   ❌ Erro no post {i}: {e}")
                return

        print("\n" + "=" * 60)
        print(f"✅ Thread publicada com {len(posts)} posts!")


def gerar_thread():
    """Gera os posts da thread v6.1"""
    return [
        """SELIX v6.1 está no ar — modelo regime-dependente com multiplicador de credibilidade.

A equação que captura por que o Brasil precisa de juros ~2x maiores que os EUA:

juro_real = inflação × (1 + prêmio_risco) × (1 + (1 - credibilidade) × 0.5) + 0.5 × gap_produto

Isso não é opinião. É prova formal no Lean/Z3. 🧵↓""",

        """Os números de hoje:

Selic atual: 14,25%
Selic ideal (SELIX): 9,25%
Diferencial: 5,00 p.p.
Economia anual: R$ 345 bi (dívida pública R$ 6,9 tri × 5,00 p.p.)

O custo de manter a Selic em 2 dígitos é de ~R$ 345 bi por ano.
Isso é dinheiro que poderia estar no bolso de empresas, investidores e trabalhadores.""",

        """O que o SELIX é:
✅ Ferramenta de auditoria aritmética
✅ Prova formal no Lean/Z3
✅ Código aberto, dados públicos, rastreável
✅ Roda 24/7 no Termux/Android

O que o SELIX NÃO é:
❌ Modelo DSGE (não substitui o COPOM)
❌ Substituto do BACEN
❌ Previsão estocástica""",

        """Provas formais já entregues no Lean:

T7: r* (taxa natural) e risk_premium derivados de dados históricos (BCB/CDS)
T8: Impacto econômico R$ 345 bi provado formalmente
T9: Reconciliação 9.48% (contínuo) vs 9.25% (quantizado)
T11: Multiplicador de credibilidade — Brasil ~2× EUA

93/93 testes. 100% cobertura. Código aberto.""",

        """Roadmap v7.0 (Accountability Total):

🔜 API Focus (expectativas de mercado em tempo real)
🔜 EMBI+ em tempo real (prêmio de risco endógeno)
🔜 Credibilidade derivada do histórico de metas
🔜 Choques exógenos (oil/TTF) como variáveis de estado
🔜 Intervalos de confiança (86%) com derivação de incerteza

Quando essas 5 peças estiverem no lugar, o modelo terá accountability institucional.""",

        """O SELIX não é o COPOM. É uma ferramenta de apoio à decisão.

Se você quer saber se a Selic atual faz sentido, rode o código.

Repositório: https://github.com/scoobiii/selix
Bluesky: @zeh-sobrinho.bsky.social
Versão: v6.1.0

O custo de não saber é R$ 345 bi por ano."""
    ]


def main():
    print("=" * 60)
    print("📝 SELIX v6.1 - Postar Thread no Bluesky")
    print("=" * 60)

    # Gerar a thread
    posts = gerar_thread()
    print(f"\n📋 Thread gerada com {len(posts)} posts")

    # Exibir preview
    print("\n📄 PREVIEW:")
    print("-" * 60)
    for i, post in enumerate(posts, 1):
        print(f"\n[{i}/{len(posts)}]")
        print(post[:120] + ("..." if len(post) > 120 else ""))
    print("-" * 60)

    # Confirmar
    confirm = input("\n❓ Publicar thread no Bluesky? (s/N): ").strip().lower()
    if confirm != "s":
        print("❌ Publicação cancelada.")
        return

    # Postar
    poster = BlueskyPoster()
    if poster.login():
        poster.post_thread(posts)
    else:
        print("❌ Não foi possível publicar.")


if __name__ == "__main__":
    main()

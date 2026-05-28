#!/usr/bin/env python3
"""
SELIX Agent LUZIA - Respostas Automáticas no Bluesky
Monitora menções @selixbr.bsky.social e responde usando LUZIA
"""

import sys
import os
import time
from dotenv import load_dotenv
from atproto import Client, models

# Adicionar caminho para importar LUZIA
sys.path.append('/root/selix/notebooks')

# Tentar importar LUZIA
try:
    from selix_agent_luzia import LuziaAgent
    LUZIA_DISPONIVEL = True
    print("✅ LUZIA carregada com sucesso!")
except ImportError as e:
    print(f"⚠️ LUZIA não disponível: {e}")
    print("📝 Usando modo básico...")
    LUZIA_DISPONIVEL = False

load_dotenv()

class LuziaBlueskyBot:
    def __init__(self):
        self.client = Client()
        self.client.login(
            os.getenv('BLUESKY_USERNAME'),
            os.getenv('BLUESKY_APP_PASSWORD')
        )
        self.respondidos = set()
        self.meu_handle = self.client.me.handle
        print(f"✅ Conectado como @{self.meu_handle}")
        
        # Criar LUZIA básica se não disponível
        if not LUZIA_DISPONIVEL:
            self.luzia = self.LuziaBasica()
        else:
            self.luzia = LuziaAgent()
    
    class LuziaBasica:
        """Versão básica da LUZIA para fallback"""
        def responder(self, pergunta):
            pergunta_lower = pergunta.lower()
            respostas = {
                "preço justo do gpa": "R$ 17,60 (+577% com conversão de dívida)",
                "trampoforte": "PLR prioritário sobre credores em recuperação judicial",
                "selic ideal": "9.48% (teorema provado com Z3 + Lean 4)",
                "b3 valuation": "R$ 231 bilhões (+238% com SELIX)",
            }
            for key, resp in respostas.items():
                if key in pergunta_lower:
                    return f"[LUZIA] {resp}"
            return f"[LUZIA] Consulte github.com/scoobiii/selix para: {pergunta}"
    
    def responder_mencoes(self):
        """Busca menções recentes e responde"""
        print("\n🔍 Buscando menções @selixbr...")
        
        try:
            # Buscar feed do usuário
            feed = self.client.get_author_feed(
                actor=self.client.me.did,
                limit=30
            )
            
            for post in feed.feed:
                uri = post.post.uri
                text = post.post.record.text
                author = post.post.author.handle
                
                # Evitar responder a si mesmo
                if author == self.meu_handle:
                    continue
                
                # Verificar se é uma menção a nós
                if '@selixbr' in text.lower() or '@selix' in text.lower():
                    if uri in self.respondidos:
                        continue
                    
                    print(f"\n📝 Menção de @{author}: {text[:100]}...")
                    
                    # Extrair pergunta (remover menções)
                    pergunta = text
                    for palavra in ['@selixbr', '@selix', f'@{self.meu_handle}']:
                        pergunta = pergunta.replace(palavra, '')
                    pergunta = pergunta.strip()
                    
                    if not pergunta:
                        pergunta = "Qual sua análise sobre o mercado?"
                    
                    # LUZIA responde
                    resposta = self.luzia.responder(pergunta)
                    
                    # Publicar resposta
                    resposta_texto = f"@{author} {resposta}"
                    
                    # Verificar limite
                    if len(resposta_texto) > 300:
                        resposta_texto = resposta_texto[:297] + "..."
                    
                    try:
                        # Responder em thread
                        post_ref = models.ComAtprotoRepoStrongRef.Main(uri=uri)
                        reply = self.client.send_post(
                            text=resposta_texto,
                            reply_to=models.AppBskyFeedPost.ReplyRef(parent=post_ref, root=post_ref)
                        )
                        print(f"✅ Respondido: {reply.uri}")
                        self.respondidos.add(uri)
                    except Exception as e:
                        print(f"❌ Erro ao responder: {e}")
                    
                    time.sleep(3)  # Evitar rate limit
                    
        except Exception as e:
            print(f"❌ Erro ao buscar menções: {e}")
    
    def monitorar_continuamente(self, intervalo=60):
        """Monitora menções a cada N segundos"""
        print(f"\n🚀 LUZIA iniciou monitoramento do Bluesky")
        print(f"📱 Perfil: @{self.meu_handle}")
        print(f"⏱️ Verificando a cada {intervalo} segundos...")
        print("🔴 Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                self.responder_mencoes()
                time.sleep(intervalo)
        except KeyboardInterrupt:
            print("\n👋 Monitoramento encerrado.")

if __name__ == "__main__":
    import sys
    
    bot = LuziaBlueskyBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        bot.monitorar_continuamente()
    else:
        # Executar uma vez
        bot.responder_mencoes()
        print("\n✅ Execução única concluída!")
        print("📝 Para monitorar continuamente: python luzia_responder_automatico.py --monitor")

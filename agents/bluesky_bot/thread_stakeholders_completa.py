from atproto import Client, models
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))

# ============================================================
# POST 1: Governo e Economia (já tem Planalto, falta outros)
# ============================================================
post1 = """@planalto.bsky.social @economia.bsky.social @mme.bsky.social @fazenda.bsky.social

🇧🇷 IMPACTO MACROECONÔMICO SELIX:

Com reestruturação GPA+Raízen:
✅ +6.525 empregos
✅ +R$111M/ano impostos
✅ +R$163K/loja investimento
✅ 500 municípios beneficiados

🔗 github.com/scoobiii/TrampoForte
#SELIX #TrampoForte #Governo #Empregos"""

# ============================================================
# POST 2: Empresas faltantes (Santander, BB, Raízen, GPA)
# ============================================================
post2 = """@santander.bsky.social @bancodobrasil.bsky.social @paodeacucar.bsky.social @raizen.bsky.social

📊 BENEFÍCIOS PARA EMPRESAS E CREDORES:

✅ Dívida convertida em ações
✅ Empresas mais sólidas
✅ Risco de crédito REDUZIDO
✅ Rating: BBB+ (Investment Grade)

🔗 github.com/scoobiii/selix
#SELIX #Reestruturação #Credores #Empresas"""

# ============================================================
# POST 3: Trabalhadores faltantes (TST, Força Vendas)
# ============================================================
post3 = """@tst.bsky.social @forcavendas.bsky.social @midiaindustrial.bsky.social

👷 DIREITOS DOS TRABALHADORES:

✅ PLR de R$2.000 GARANTIDO
✅ Prioridade sobre credores
✅ Trabalhadores viram SÓCIOS
✅ Assentos no Conselho

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #PLR #Trabalhadores #JustiçaDoTrabalho"""

print("=" * 60)
print("🧵 PUBLICANDO THREAD COM 3 POSTS")
print("=" * 60)

# Publicar thread
parent_ref = None
root_ref = None

for i, texto in enumerate([post1, post2, post3], 1):
    print(f"\n📝 Post {i}/3")
    print(f"📏 Tamanho: {len(texto)} caracteres")
    
    try:
        if parent_ref and root_ref:
            post = client.send_post(
                text=texto,
                reply_to=parent_ref,
                root=root_ref
            )
        else:
            post = client.send_post(texto)
        
        print(f"✅ Publicado: {post.uri}")
        print(f"🔗 https://bsky.app/profile/{client.me.handle}/post/{post.uri.split('/')[-1]}")
        
        # Atualizar referências para o próximo post
        if i == 1:
            root_ref = post
        parent_ref = post
        
        # Aguardar 5 segundos entre posts
        if i < 3:
            print("   ⏳ Aguardando 5 segundos...")
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ Erro no post {i}: {e}")

print("\n" + "=" * 60)
print("✅ THREAD COMPLETA PUBLICADA!")
print("=" * 60)

# Listar stakeholders por post
print("\n📋 STAKEHOLDERS MARCADOS:")
print("-" * 40)
print("Post 1 (Governo):")
for s in ["@planalto.bsky.social", "@economia.bsky.social", "@mme.bsky.social", "@fazenda.bsky.social"]:
    print(f"   ✓ {s}")
print("\nPost 2 (Empresas/Credores):")
for s in ["@santander.bsky.social", "@bancodobrasil.bsky.social", "@paodeacucar.bsky.social", "@raizen.bsky.social"]:
    print(f"   ✓ {s}")
print("\nPost 3 (Trabalhadores):")
for s in ["@tst.bsky.social", "@forcavendas.bsky.social", "@midiaindustrial.bsky.social"]:
    print(f"   ✓ {s}")

print("\n🔗 Perfil: https://bsky.app/profile/selixbr.bsky.social")

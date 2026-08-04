#!/usr/bin/env python3
"""
SELIX – Posta thread à prova de 20 cagadas
10 internas + 10 externas
Robustez: retry com backoff exponencial + fallbacks
"""

import os
import sys
import time
import json
import logging
import socket
import ssl
from getpass import getpass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

# ============================================================
# CONFIGURAÇÃO
# ============================================================
STATE_FILE = Path("/root/selix/logs/ma_email_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
LOG_FILE = STATE_FILE.parent / "ma_email.log"

MAX_RETRIES = 5
BASE_DELAY = 8
MAX_DELAY = 60
POST_DELAY = 10
MAX_POSTS_PER_DAY = 8

# ============================================================
# LOGGING COM ROTAÇÃO
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("selix_proof")

# ============================================================
# THREAD (10 posts)
# ============================================================
THREAD = [
    "1/10\n📧 PROÁLCOOL PREDITIVO, ENERGY CRASH E O CUSTO DA SELIC ERRADA\n\nO que o M&A não está contando.\n\nA análise da quinzena está cirúrgica — Raízen, Braskem, Grupo João Santos, Mercuria, juro alto e balanço apertado.\n\nMas há uma camada que os números não capturam.\n\n@zeh-sobrinho.bsky.social",
    "2/10\n🧠 O QUE O SELIX JÁ PROVOU MATEMATICAMENTE\n\nEnquanto o Bacen sustenta Selic 14% para compensar Brent/TTF, o SELIX (Z3+Lean4) prova que a Selic ideal é 9,48%.\n\n• Economia anual: R$ 270 bi\n• Blindagem ecológica Ex/Bx\n• Investment Grade BBB+\n\n🔗 github.com/scoobiii/selix",
    "3/10\n⚡ A GEOPOLÍTICA QUE O M&A ESTÁ PRECIFICANDO (MAS NÃO NOMEANDO)\n\nO crash energético de 2026 — POTUS + Netanyahu + TTF — é o mesmo padrão do choque do petróleo nos anos 70.\n\nO Proálcool original foi criado para combater isso. A mistura preditiva Ex/Bx poderia ter nos isolado.",
    "4/10\n🌍 O PLANO QUE FLOPOU\n\nNord Stream (€20/MWh) → GNL do Qatar → flopou.\nUcrânia → Marrocos (FIFA 2030) → flopou.\n\nEnquanto isso, o Brasil ficou assistindo. MME falhou na mistura preditiva. Bacen mantém a Selic como o 'tigrinho oficial'.",
    "5/10\n📉 O QUE ISSO SIGNIFICA PARA O M&A\n\nCom Selic em 14%:\n• Raízen (R$ 75,3 bi em dívida) sendo canibalizada\n• Braskem (PL negativo R$ 16,5 bi) na corda bamba\n• Ativos estratégicos vendidos a preço de banana para traders como Mercuria",
    "6/10\n💸 NÚMEROS QUE ASSUSTAM\n\n• 2.466 CNPJs em RJ (recorde Serasa 2025)\n• Mercuria comprou downstream da Raízen por US$ 1,42 bi\n• Grupo João Santos vendeu última jazida de calcário de SP por R$ 250 mi\n\nQuando se vende a opcionalidade, é porque não há mais margem.",
    "7/10\n🔐 A SAÍDA EXISTE (E É MATEMÁTICA)\n\nO SELIX não é teoria — é prova formal com Z3 e Lean 4.\n\nSe o Brasil adotasse a mistura preditiva e a Selic de 9,48%:\n• Empresas não precisariam vender ativos\n• PIB per capita não seria medíocre\n• Investment Grade seria realidade",
    "8/10\n🏆 O FUTURO QUE PODERÍAMOS TER\n\nEmpatar com Maricá/RJ (GDP per capita US$ 130k).\n\nRating soberano A+.\nInvestment Grade certification.\nCapital de verdade fluindo.\n\nEconomia que prioriza quem trabalha.",
    "9/10\n🔗 LINKS\n\n• Whitepaper: github.com/scoobiii/selix\n• Dashboard: selix-555922434592.us-west2.run.app\n• Agente Moltbook: moltbook.com/u/selixbr\n\nEstamos à disposição para apresentação técnica.",
    "10/10\n📱 DESIGNED & POWERED BY GALAXY A23\n\nSELIX rodando em hardware restrito — prova de que eficiência não depende de nuvem.\n\n#EnergyCrash #SelicIdeal #Proalcool #M&A #InvestmentGrade\n\n@zeh-sobrinho.bsky.social"
]

# ============================================================
# FUNÇÕES DE ESTADO (com fallback)
# ============================================================
def load_state() -> Dict:
    """Carrega estado com fallback se arquivo corrompido"""
    try:
        if STATE_FILE.exists():
            content = STATE_FILE.read_text()
            if not content.strip():
                return {"published": []}
            return json.loads(content)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        logger.warning(f"⚠️ Estado corrompido: {e}. Reiniciando.")
        # Backup do corrupto
        try:
            backup = STATE_FILE.with_suffix(".json.bak")
            STATE_FILE.rename(backup)
        except:
            pass
    return {"published": []}

def save_state(state: Dict) -> bool:
    """Salva estado com verificação de escrita"""
    try:
        temp = STATE_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(state, indent=2))
        temp.rename(STATE_FILE)
        return True
    except (OSError, IOError, json.JSONEncoderError) as e:
        logger.error(f"❌ Erro ao salvar estado: {e}")
        return False

# ============================================================
# FUNÇÃO DE RETRY COM BACKOFF EXPONENCIAL
# ============================================================
def retry_with_backoff(func, *args, **kwargs):
    """Executa função com retry e backoff exponencial"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            # Erros que NÃO devem retentar (irrecuperáveis)
            if "Invalid identifier" in error_msg or "Unauthorized" in error_msg:
                logger.error(f"❌ Credencial inválida. Abortando.")
                raise
            if "RateLimitExceeded" in error_msg:
                logger.warning(f"⏳ Rate limit. Aguardando {MAX_DELAY}s...")
                time.sleep(MAX_DELAY)
                continue
            # Erros de rede: retry com backoff
            delay = min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
            logger.warning(f"⚠️ Tentativa {attempt}/{MAX_RETRIES} falhou: {e}")
            logger.info(f"⏳ Aguardando {delay}s antes de tentar novamente...")
            time.sleep(delay)
    logger.error(f"❌ Falha após {MAX_RETRIES} tentativas.")
    raise

# ============================================================
# CLASSE CLIENTE PROOF
# ============================================================
class ProofClient:
    """Wrapper do Client com proteções extras"""
    
    def __init__(self):
        self.client = None
        self.handle = None
    
    def login(self, handle: str, password: str) -> bool:
        """Login com timeout e tratamento de erros"""
        self.handle = handle
        try:
            from atproto import Client
            from atproto.exceptions import AtProtocolError
            
            # Timeout global
            import httpx
            timeout = httpx.Timeout(30.0, connect=15.0)
            
            self.client = Client()
            self.client._client = httpx.Client(timeout=timeout)
            
            # Tenta login com timeout
            self.client.login(handle, password)
            logger.info(f"✅ Conectado a {handle}")
            return True
            
        except (socket.timeout, ssl.SSLError, socket.gaierror) as e:
            logger.error(f"❌ Erro de rede: {e}")
            return False
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            logger.error(f"❌ Timeout: {e}")
            return False
        except Exception as e:
            error_msg = str(e)
            if "Unauthorized" in error_msg or "Invalid identifier" in error_msg:
                logger.error("❌ Credencial inválida! Verifique .env")
            elif "RateLimitExceeded" in error_msg:
                logger.error("❌ Rate limit excedido. Aguarde 24h.")
            else:
                logger.error(f"❌ Erro no login: {e}")
            return False
    
    def send_post(self, text: str, reply_to: Optional[Dict] = None) -> Optional[Dict]:
        """Envia post com timeout e retry"""
        if not self.client:
            logger.error("❌ Cliente não autenticado.")
            return None
        
        # Verifica tamanho do post (máx 300 chars)
        if len(text) > 300:
            logger.warning(f"⚠️ Post com {len(text)} chars > 300. Truncando.")
            text = text[:297] + "..."
        
        def _send():
            if reply_to:
                from atproto import models
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    parent=models.ComAtprotoRepoStrongRef.Main(
                        uri=reply_to["uri"],
                        cid=reply_to["cid"]
                    ),
                    root=models.ComAtprotoRepoStrongRef.Main(
                        uri=reply_to.get("root_uri", reply_to["uri"]),
                        cid=reply_to.get("root_cid", reply_to["cid"])
                    )
                )
                return self.client.send_post(text=text, reply_to=reply_ref)
            return self.client.send_post(text=text)
        
        try:
            post = retry_with_backoff(_send)
            return {"uri": post.uri, "cid": post.cid}
        except Exception as e:
            logger.error(f"❌ Falha ao enviar post: {e}")
            return None

# ============================================================
# FUNÇÃO PRINCIPAL DE POSTAGEM
# ============================================================
def post_thread_proof(client: ProofClient, posts: List[str]) -> bool:
    """Publica thread com proteção máxima"""
    
    # Carrega estado
    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")
    thread_id = "ma_email_2026_06_16"
    
    # Verifica se já foi concluída
    if thread_id in state.get("published", []):
        logger.info(f"⏭️ Thread '{thread_id}' já concluída.")
        return True
    
    # Verifica limite diário
    today_posts = [p for p in state.get("published", []) if p.startswith(today)]
    if len(today_posts) >= MAX_POSTS_PER_DAY:
        logger.warning(f"⚠️ Limite diário ({MAX_POSTS_PER_DAY}) atingido.")
        logger.info(f"   Posts de hoje: {len(today_posts)}")
        return False
    
    # Encontra onde parou
    start_index = 0
    for i in range(len(posts)):
        post_key = f"{today}_{i+1}"
        if post_key in state.get("published", []):
            start_index = i + 1
        else:
            break
    
    if start_index > 0:
        logger.info(f"🔄 Retomando do post {start_index+1}")
    
    parent_ref = None
    root_ref = None
    
    # Se já tem posts publicados, precisamos do último pra continuar a thread
    # Aqui você precisaria buscar o último post da thread via API
    # Para simplificar, vamos usar o estado salvo
    if "last_post" in state:
        parent_ref = state["last_post"]
        if "root_post" in state:
            root_ref = state["root_post"]
    
    for i in range(start_index, len(posts)):
        post_key = f"{today}_{i+1}"
        
        # Verifica limite diário antes de cada post
        if len([p for p in state.get("published", []) if p.startswith(today)]) >= MAX_POSTS_PER_DAY:
            logger.warning(f"⚠️ Limite diário atingido. Parando.")
            save_state(state)
            return False
        
        # Verifica se já foi publicado (segurança extra)
        if post_key in state.get("published", []):
            logger.info(f"⏭️ Post {i+1} já publicado. Pulando.")
            continue
        
        # Prepara reply
        reply_to = None
        if parent_ref and root_ref:
            reply_to = {
                "uri": parent_ref["uri"],
                "cid": parent_ref["cid"],
                "root_uri": root_ref["uri"],
                "root_cid": root_ref["cid"]
            }
        
        # Tenta publicar
        result = client.send_post(posts[i], reply_to)
        if not result:
            logger.error(f"❌ Falha no post {i+1}. Estado salvo para retomada.")
            save_state(state)
            return False
        
        # Atualiza referências
        if not parent_ref:
            root_ref = result
        parent_ref = result
        
        # Salva estado
        state.setdefault("published", []).append(post_key)
        state["last_post"] = parent_ref
        state["root_post"] = root_ref
        if not save_state(state):
            logger.warning("⚠️ Falha ao salvar estado, mas post foi publicado.")
        
        logger.info(f"✅ Post {i+1}/{len(posts)} publicado")
        
        # Delay entre posts (menor se for o último)
        if i < len(posts) - 1:
            delay = POST_DELAY if len([p for p in state.get("published", []) if p.startswith(today)]) < 5 else POST_DELAY * 2
            logger.info(f"⏳ Aguardando {delay}s...")
            time.sleep(delay)
    
    # Marca thread como concluída
    state.setdefault("published", []).append(thread_id)
    save_state(state)
    logger.info("🎉 THREAD COMPLETA PUBLICADA!")
    return True

# ============================================================
# MAIN (com checagem de internet)
# ============================================================
def check_internet() -> bool:
    """Verifica conectividade com a internet"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        logger.error("❌ Sem conexão com a internet!")
        return False

def main():
    print("\n" + "="*55)
    print("🛡️ SELIX – Posta thread à prova de 20 cagadas")
    print("="*55 + "\n")
    
    # Cagada externa #1: Verifica internet
    if not check_internet():
        logger.info("🔁 Tentando novamente em 30s...")
        time.sleep(30)
        if not check_internet():
            logger.error("❌ Sem internet. Abortando.")
            return
    
    # Carrega credenciais
    handle = os.environ.get("BLUESKY_USERNAME", "zeh-sobrinho.bsky.social")
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    
    if not password:
        try:
            password = getpass(f"🔐 App Password para {handle}: ")
        except (KeyboardInterrupt, EOFError):
            logger.error("❌ Entrada cancelada.")
            return
    
    if not handle or not password:
        logger.error("❌ Credenciais incompletas.")
        return
    
    # Cria cliente proof
    client = ProofClient()
    if not client.login(handle, password):
        logger.error("❌ Falha no login. Verifique credenciais e rede.")
        return
    
    # Publica thread
    success = post_thread_proof(client, THREAD)
    
    if success:
        print(f"\n🔗 Ver em: https://bsky.app/profile/{handle}")
        print("📁 Estado salvo em:", STATE_FILE)
    else:
        print("\n⚠️ Thread incompleta.")
        print("   Execute novamente para continuar de onde parou.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido pelo usuário. Estado salvo.")
    except Exception as e:
        logger.error(f"💥 Erro inesperado: {e}")
        # Última tentativa de salvar estado
        try:
            state = load_state()
            save_state(state)
        except:
            pass

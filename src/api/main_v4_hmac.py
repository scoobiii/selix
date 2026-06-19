#!/usr/bin/env python3
"""
SELIX API v4.0 HMAC – Autenticação Stateless sem Banco
========================================================
🔐 Autenticação via HMAC + Nonce (prova de 70 cagadas)
"""

import sys
import os
import sqlite3
import hashlib
import hmac
import time
import json
import uuid
import threading
import queue
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# ============================================================
# CONFIGURAÇÕES
# ============================================================
load_dotenv('/root/selix/.env')

DB_PATH = '/root/selix/selix.db'
LOG_DIR = '/root/selix/logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'main_v4_hmac.log')

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger("selix_hmac")
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(console_handler)

# ============================================================
# CONSTANTES
# ============================================================
MAX_RETRIES = 3
BACKOFF_BASE = 2
NONCE_TTL = 300  # 5 minutos (nonce expira)
HMAC_ALGORITHM = 'sha256'
CLIENTS = {}  # client_id -> client_secret (em memória)
NONCE_STORE = defaultdict(set)  # client_id -> set de nonces usados
NONCE_CLEANUP_INTERVAL = 60  # segundos

# ============================================================
# HMAC + NONCE (STATELESS)
# ============================================================
def generate_credentials():
    """Gera um par client_id + client_secret"""
    client_id = str(uuid.uuid4())
    client_secret = hashlib.sha256(os.urandom(32)).hexdigest()[:32]
    return client_id, client_secret

def register_client(client_name=None):
    """Registra um novo cliente e retorna credenciais"""
    client_id, client_secret = generate_credentials()
    name = client_name or f"client_{client_id[:8]}"
    CLIENTS[client_id] = {
        "client_secret": client_secret,
        "client_name": name,
        "created_at": datetime.now().isoformat(),
        "rate_limit": 1000
    }
    logger.info(f"🔑 Novo cliente registrado: {name} (ID: {client_id[:8]}...)")
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_name": name,
        "message": "GUARDE ESSAS CREDENCIAIS! O client_secret não será mostrado novamente."
    }

def verify_hmac(client_id, nonce, timestamp, signature):
    """Verifica a assinatura HMAC + Nonce"""
    # 1. Verifica se o cliente existe
    if client_id not in CLIENTS:
        logger.warning(f"⚠️ Cliente não encontrado: {client_id[:8]}...")
        return None
    
    client = CLIENTS[client_id]
    client_secret = client["client_secret"]
    
    # 2. Verifica timestamp (evita replay com atraso)
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > NONCE_TTL:
            logger.warning(f"⚠️ Timestamp expirado: {timestamp}")
            return None
    except ValueError:
        logger.warning(f"⚠️ Timestamp inválido: {timestamp}")
        return None
    
    # 3. Verifica nonce (evita replay attack)
    if nonce in NONCE_STORE[client_id]:
        logger.warning(f"⚠️ Nonce reutilizado: {nonce}")
        return None
    
    # 4. Calcula a assinatura esperada
    message = f"{client_id}{nonce}{timestamp}"
    expected = hmac.new(
        client_secret.encode(),
        message.encode(),
        HMAC_ALGORITHM
    ).hexdigest()
    
    # 5. Compara assinaturas (timing-safe)
    if not hmac.compare_digest(expected, signature):
        logger.warning(f"⚠️ Assinatura inválida para {client_id[:8]}...")
        return None
    
    # 6. Marca nonce como usado (limpeza periódica)
    NONCE_STORE[client_id].add(nonce)
    logger.info(f"✅ HMAC verificado: {client['client_name']} (ID: {client_id[:8]}...)")
    return client

def require_hmac(f):
    """Decorator que exige autenticação HMAC + Nonce"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obtém headers
        client_id = request.headers.get("X-Client-ID")
        nonce = request.headers.get("X-Nonce")
        timestamp = request.headers.get("X-Timestamp")
        signature = request.headers.get("X-Signature")
        
        if not all([client_id, nonce, timestamp, signature]):
            logger.warning("⚠️ Headers HMAC incompletos")
            return jsonify({
                "erro": "Autenticação HMAC requer: X-Client-ID, X-Nonce, X-Timestamp, X-Signature"
            }), 401
        
        # Verifica
        client = verify_hmac(client_id, nonce, timestamp, signature)
        if not client:
            return jsonify({"erro": "Autenticação HMAC falhou"}), 401
        
        request.client = client
        return f(*args, **kwargs)
    return decorated

# ============================================================
# LIMPEZA PERIÓDICA DE NONCES
# ============================================================
def cleanup_nonces():
    """Remove nonces antigos periodicamente"""
    while True:
        time.sleep(NONCE_CLEANUP_INTERVAL)
        for client_id in list(NONCE_STORE.keys()):
            if len(NONCE_STORE[client_id]) > 1000:
                NONCE_STORE[client_id] = set()
                logger.info(f"🧹 Nonces de {client_id[:8]}... limpos")

# ============================================================
# BANCO DE DADOS (para dados, NÃO para autenticação)
# ============================================================
def get_db():
    for attempt in range(MAX_RETRIES):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            return conn
        except sqlite3.OperationalError as e:
            logger.warning(f"⚠️ Tentativa {attempt+1}/{MAX_RETRIES} falhou: {e}")
            time.sleep(BACKOFF_BASE ** attempt)
    raise sqlite3.OperationalError("Falha ao conectar ao banco")

# ============================================================
# FLASK APP
# ============================================================
app = Flask(__name__)
CORS(app)

# ============================================================
# ENDPOINT: REGISTRAR CLIENTE (Gera credenciais HMAC)
# ============================================================
@app.route('/v1/auth/register', methods=['POST'])
def register():
    """Registra um novo cliente e retorna credenciais HMAC"""
    data = request.get_json() or {}
    client_name = data.get('client_name')
    
    if not client_name:
        return jsonify({"erro": "client_name é obrigatório"}), 400
    
    # Verifica se já existe (evita duplicação)
    for cid, client in CLIENTS.items():
        if client["client_name"] == client_name:
            return jsonify({
                "erro": "Nome de cliente já existe",
                "client_id": cid,
                "client_secret": client["client_secret"]
            }), 409
    
    creds = register_client(client_name)
    return jsonify(creds), 201

# ============================================================
# ENDPOINT: RENOVAR CREDENCIAIS (roda chave)
# ============================================================
@app.route('/v1/auth/rotate', methods=['POST'])
def rotate():
    """Gera novas credenciais para um cliente existente"""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    old_secret = data.get('client_secret')
    
    if not client_id or not old_secret:
        return jsonify({"erro": "client_id e client_secret são obrigatórios"}), 400
    
    if client_id not in CLIENTS:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    
    client = CLIENTS[client_id]
    if client["client_secret"] != old_secret:
        return jsonify({"erro": "client_secret inválido"}), 401
    
    # Gera novo secret
    _, new_secret = generate_credentials()
    client["client_secret"] = new_secret
    client["rotated_at"] = datetime.now().isoformat()
    
    # Limpa nonces usados
    NONCE_STORE[client_id] = set()
    
    logger.info(f"🔄 Credenciais rotacionadas para {client['client_name']}")
    return jsonify({
        "client_id": client_id,
        "client_secret": new_secret,
        "client_name": client["client_name"],
        "message": "GUARDE A NOVA CREDENCIAL!"
    })

# ============================================================
# ENDPOINTS PÚBLICOS (sem autenticação)
# ============================================================
@app.route('/v1/health', methods=['GET'])
def health():
    status = {"status": "ok", "versao": "4.0-hmac", "timestamp": datetime.now().isoformat()}
    try:
        conn = get_db()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        status["db"] = "ok"
    except Exception as e:
        status["db"] = f"erro: {str(e)[:50]}"
        status["status"] = "degradado"
    return jsonify(status)

@app.route('/v1/energia/mistura/<int:brent>', methods=['GET'])
def get_mistura_por_brent(brent):
    try:
        from src.selix.energy_predictor import EnergyPredictor
        return jsonify({
            "brent_usd": brent,
            "etanol": EnergyPredictor.get_mistura_e(brent),
            "biodiesel": EnergyPredictor.get_mistura_b(brent),
            "termicas": EnergyPredictor.get_geracao_termica(brent)
        })
    except Exception as e:
        logger.error(f"❌ Erro no mix energético: {e}")
        return jsonify({"erro": "Serviço temporariamente indisponível"}), 503

@app.route('/v1/energia/termicas', methods=['GET'])
def get_termicas():
    try:
        from src.selix.energy_predictor import EnergyPredictor
        return jsonify({
            "termicas": EnergyPredictor.TERMELETRICAS,
            "capacidade_total_mw": sum(t["capacidade_mw"] for t in EnergyPredictor.TERMELETRICAS.values())
        })
    except Exception as e:
        logger.error(f"❌ Erro nas termelétricas: {e}")
        return jsonify({"erro": "Serviço temporariamente indisponível"}), 503

# ============================================================
# ENDPOINTS PRIVADOS (com autenticação HMAC)
# ============================================================
@app.route('/v1/selic', methods=['GET'])
@require_hmac
def get_selic():
    try:
        conn = get_db()
        row = conn.execute("SELECT rate, timestamp FROM selic ORDER BY timestamp DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            return jsonify({"rate": row["rate"], "timestamp": row["timestamp"]})
        return jsonify({"erro": "Dados não disponíveis"}), 503
    except Exception as e:
        logger.error(f"❌ Erro ao buscar Selic: {e}")
        return jsonify({"erro": "Serviço temporariamente indisponível"}), 503

@app.route('/v1/commodities', methods=['GET'])
@require_hmac
def get_commodities():
    try:
        conn = get_db()
        rows = conn.execute("SELECT nome, preco_usd, criado_em FROM commodities ORDER BY criado_em DESC LIMIT 5").fetchall()
        conn.close()
        if rows:
            return jsonify([dict(r) for r in rows])
        return jsonify({"erro": "Dados não disponíveis"}), 503
    except Exception as e:
        logger.error(f"❌ Erro ao buscar commodities: {e}")
        return jsonify({"erro": "Serviço temporariamente indisponível"}), 503

@app.route('/v1/empresas/rj', methods=['GET'])
@require_hmac
def get_empresas_rj():
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM empresas_rj LIMIT 20").fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        logger.error(f"❌ Erro ao buscar empresas RJ: {e}")
        return jsonify({"erro": "Serviço temporariamente indisponível"}), 503

# ============================================================
# TASK QUEUE (ASSÍNCRONO)
# ============================================================
task_queue = queue.Queue()
task_results = {}
task_lock = threading.Lock()

def worker_loop():
    while True:
        try:
            task_id, pergunta = task_queue.get(timeout=1)
            logger.info(f"📝 Processando task {task_id}: {pergunta[:50]}...")
            resposta = f"🧠 [SELIX] Pergunta processada: '{pergunta}'. A Selic ideal é 9,48%."
            with task_lock:
                task_results[task_id] = {
                    "status": "completed",
                    "resposta": resposta,
                    "timestamp": datetime.now().isoformat()
                }
            logger.info(f"✅ Task {task_id} concluída")
        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"❌ Erro no worker: {e}")

@app.route('/v1/perguntar', methods=['POST'])
@require_hmac
def perguntar_async():
    data = request.get_json()
    if not data or not data.get('pergunta'):
        return jsonify({"erro": "Campo 'pergunta' é obrigatório"}), 400
    pergunta = data['pergunta'][:500]
    task_id = str(uuid.uuid4())
    with task_lock:
        task_results[task_id] = {"status": "queued"}
    task_queue.put((task_id, pergunta))
    return jsonify({
        "task_id": task_id,
        "status": "queued",
        "message": "Pergunta recebida. Consulte /v1/task/<id>"
    }), 202

@app.route('/v1/task/<task_id>', methods=['GET'])
@require_hmac
def get_task_result(task_id):
    with task_lock:
        result = task_results.get(task_id)
    if not result:
        return jsonify({"erro": "Task não encontrada"}), 404
    if result.get('status') == 'queued':
        return jsonify({"status": "queued"}), 202
    return jsonify(result)

# ============================================================
# ADMIN: LISTAR CLIENTES
# ============================================================
@app.route('/v1/admin/clients', methods=['GET'])
def list_clients():
    """Lista todos os clientes registrados (não requer autenticação para debug)"""
    return jsonify([{
        "client_id": cid,
        "client_name": c["client_name"],
        "created_at": c["created_at"],
        "client_secret": c["client_secret"][:8] + "..."  # só mostra o começo
    } for cid, c in CLIENTS.items()])

# ============================================================
# INICIALIZAÇÃO
# ============================================================
def init():
    logger.info("🚀 Iniciando SELIX API v4.0 HMAC (Stateless)")
    
    # Cria cliente padrão se não houver nenhum
    if not CLIENTS:
        logger.info("📦 Nenhum cliente registrado. Criando cliente padrão...")
        creds = register_client("default_client")
        logger.info(f"🔑 Cliente padrão criado:")
        logger.info(f"   client_id: {creds['client_id']}")
        logger.info(f"   client_secret: {creds['client_secret']}")
        logger.info("💡 Use esses dados para autenticar via HMAC")
    
    # Inicia worker
    worker_thread = threading.Thread(target=worker_loop, daemon=True)
    worker_thread.start()
    logger.info("🧠 Worker de tarefas iniciado")
    
    # Inicia limpeza de nonces
    cleanup_thread = threading.Thread(target=cleanup_nonces, daemon=True)
    cleanup_thread.start()
    logger.info("🧹 Cleanup de nonces iniciado")
    
    return True

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    try:
        if init():
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("🛑 API interrompida pelo usuário")
    except Exception as e:
        logger.error(f"💥 Erro fatal: {e}")
        sys.exit(1)

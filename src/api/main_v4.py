#!/usr/bin/env python3
import sys, os, sqlite3
#from datetime import datetime  - comentado 02 junho 15:45
from datetime import datetime, timedelta # add, timedelta na mesma data
from functools import wraps
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from src.selix.energy_predictor import EnergyPredictor
from src.api.key_manager import verify_api_key, create_api_key

load_dotenv('/root/selix/.env')
app = Flask(__name__)
CORS(app)
DB_PATH = '/root/selix/selix.db'

# ============================================================
# RATE LIMITING E AUTENTICAÇÃO
# ============================================================
rate_limit_store = defaultdict(list)

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"erro": "API key não fornecida"}), 401

        client = verify_api_key(api_key)
        if not client:
            return jsonify({"erro": "API key inválida, inativa ou expirada"}), 401

        now = datetime.now()
        key_requests = rate_limit_store[client["id"]]
        key_requests = [ts for ts in key_requests if ts > now - timedelta(minutes=1)]
        if len(key_requests) >= client["rate_limit_per_minute"]:
            return jsonify({"erro": "Limite de requisições excedido"}), 429

        key_requests.append(now)
        rate_limit_store[client["id"]] = key_requests

        return f(*args, **kwargs)
    return decorated

def require_master_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key")
        master = os.getenv("MASTER_API_KEY", "")
        if not key or key != master:
            return jsonify({"erro": "Acesso administrativo não autorizado"}), 403
        return f(*args, **kwargs)
    return decorated

# ============================================================
# AUXILIAR
# ============================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================
# ENDPOINTS PÚBLICOS (sem chave)
# ============================================================
@app.route('/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "versao": "4.0", "timestamp": datetime.now().isoformat()})

@app.route('/v1/energia/mistura/<int:brent>', methods=['GET'])
def get_mistura_por_brent(brent):
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent)
    })

@app.route('/v1/energia/termicas', methods=['GET'])
def get_termicas():
    return jsonify({
        "termicas": EnergyPredictor.TERMELETRICAS,
        "capacidade_total_mw": sum(t["capacidade_mw"] for t in EnergyPredictor.TERMELETRICAS.values())
    })

@app.route('/v1/energia/gatilhos', methods=['GET'])
def get_gatilhos():
    return jsonify({
        "etanol": [{"brent_minimo": g["limite"], "mistura": g["mistura"], "tempo": g["tempo"], "status": g["status"]} for g in EnergyPredictor.GATILHOS_E],
        "biodiesel": [{"brent_minimo": g["limite"], "mistura": g["mistura"], "tempo": g["tempo"], "status": g["status"]} for g in EnergyPredictor.GATILHOS_B]
    })

# ============================================================
# ENDPOINTS PRIVADOS (exigem API key)
# ============================================================
@app.route('/v1/energia/mistura', methods=['GET'])
@require_api_key
def get_mistura():
    conn = get_db()
    cur = conn.execute("SELECT preco_usd FROM commodities WHERE nome='Brent' ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Dados de Brent não disponíveis"}), 503
    brent = row['preco_usd']
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent),
        "data": datetime.now().isoformat()
    })

@app.route('/v1/commodities', methods=['GET'])
@require_api_key
def get_commodities():
    conn = get_db()
    cur = conn.execute("SELECT nome, preco_usd, unidade, fonte, criado_em FROM commodities ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de commodities não disponíveis"}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/empresas/rj', methods=['GET'])
@require_api_key
def get_empresas_rj():
    conn = get_db()
    cur = conn.execute("SELECT nome, codigo_b3, setor, preco_atual, preco_selix, potencial_percentual, status FROM empresas_rj ORDER BY potencial_percentual DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de empresas em RJ não disponíveis"}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/selic', methods=['GET'])
@require_api_key
def get_selic():
    conn = get_db()
    cur = conn.execute("SELECT tipo, valor, fonte, criado_em FROM selic_historico ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de Selic não disponíveis"}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/precos/energeticos', methods=['GET'])
@require_api_key
def get_precos_energeticos():
    conn = get_db()
    cur = conn.execute("SELECT produto, preco_usd, unidade, fonte, criado_em FROM precos_energeticos ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de preços energéticos não disponíveis"}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/sentimento', methods=['GET'])
@require_api_key
def get_sentimento():
    conn = get_db()
    cur = conn.execute("SELECT sentimento, score, fontes, criado_em FROM sentimento_indicadores ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Dados de sentimento não disponíveis"}), 503
    return jsonify(dict(row))

@app.route('/v1/alertas/geral', methods=['GET'])
@require_api_key
def alertas_geral():
    conn = get_db()
    cur = conn.execute('SELECT produto, preco_usd FROM precos_energeticos ORDER BY criado_em DESC')
    precos = {row['produto']: row['preco_usd'] for row in cur.fetchall()}
    cur = conn.execute('SELECT valor FROM selic_historico WHERE tipo="efetiva" ORDER BY criado_em DESC LIMIT 1')
    selic_row = cur.fetchone()
    conn.close()
    if not selic_row:
        return jsonify({"erro": "Dados de Selic não disponíveis para alertas"}), 503
    selic_atual = selic_row['valor']
    alertas = []
    if precos.get('Gasolina', 0) > 7.0:
        alertas.append(f"Gasolina alta: R${precos['Gasolina']}/l")
    if precos.get('Diesel', 0) > 6.5:
        alertas.append(f"Diesel alto: R${precos['Diesel']}/l")
    if selic_atual > 9.5:
        alertas.append(f"Selic elevada: {selic_atual}% (ideal 9,25%)")
    if not alertas:
        return jsonify({"mensagem": "Nenhum alerta no momento."}), 200
    return jsonify({"alertas": alertas, "selic_atual": selic_atual})

@app.route('/v1/faq', methods=['GET'])
@require_api_key
def faq():
    import json
    pergunta = request.args.get('q', '').lower()
    faq_file = '/root/selix/agents/bluesky_bot/faq.json'
    if not os.path.exists(faq_file):
        return jsonify({"erro": "FAQ não encontrado"}), 404
    with open(faq_file) as f:
        faqs = json.load(f)
    for item in faqs:
        if any(kw in pergunta for kw in item['keywords']):
            return jsonify({"pergunta": pergunta, "resposta": item['resposta']})
    return jsonify({"pergunta": pergunta, "resposta": "Não entendi. Consulte github.com/scoobiii/selix"}), 404

@app.route('/v1/perguntar', methods=['POST'])
@require_api_key
def perguntar_selix():
    try:
        from src.api.schemas import PerguntaRequest
        data = PerguntaRequest(**request.get_json())
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    pergunta = data.pergunta
    # aqui você pode integrar com Groq ou RAG
    resposta = f"Processando pergunta: {pergunta} (modo placeholder)"
    return jsonify({"pergunta": pergunta, "resposta": resposta, "timestamp": datetime.now().isoformat()})

# ============================================================
# ADMIN – GERAR CHAVE DE API
# ============================================================
MASTER_API_KEY = os.getenv("MASTER_API_KEY", "")

@app.route('/v1/admin/generate_key', methods=['POST'])
@require_master_key
def admin_generate_key():
    data = request.get_json() or {}
    client_name = data.get('client_name')
    if not client_name:
        return jsonify({"erro": "client_name é obrigatório"}), 400
    plan = data.get('plan', 'free')
    days_valid = data.get('days_valid', 365)
    if plan not in ['free', 'pro', 'enterprise']:
        return jsonify({"erro": "plano inválido"}), 400
    new_key = create_api_key(client_name, plan, days_valid)
    return jsonify(new_key), 201

if __name__ == '__main__':
    print("\n🚀 SELIX API v4.0 – com autenticação e validação")
    app.run(host='0.0.0.0', port=5000, debug=False)

# ============================================================
# ADMIN – GESTÃO DE API KEYS (listar, revogar, renovar)
# ============================================================

@app.route('/v1/admin/list_keys', methods=['GET'])
@require_master_key
def admin_list_keys():
    conn = get_db()
    cur = conn.execute('''
        SELECT id, client_name, plan, rate_limit_per_minute, expires_at, is_active, created_at, last_used_at, total_requests
        FROM api_keys
        ORDER BY created_at DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/v1/admin/revoke_key', methods=['POST'])
@require_master_key
def admin_revoke_key():
    data = request.get_json() or {}
    key_hash = data.get('key_hash')
    if not key_hash:
        return jsonify({"erro": "key_hash é obrigatório"}), 400
    conn = get_db()
    conn.execute("UPDATE api_keys SET is_active = 0 WHERE key_hash = ?", (key_hash,))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Chave revogada com sucesso"}), 200

@app.route('/v1/admin/renew_key', methods=['POST'])
@require_master_key
def admin_renew_key():
    data = request.get_json() or {}
    key_hash = data.get('key_hash')
    extra_days = data.get('extra_days', 30)
    if not key_hash:
        return jsonify({"erro": "key_hash é obrigatório"}), 400
    conn = get_db()
    cur = conn.execute("SELECT expires_at FROM api_keys WHERE key_hash = ?", (key_hash,))
    row = cur.fetchone()
    if not row:
        return jsonify({"erro": "Chave não encontrada"}), 404
    from datetime import datetime, timedelta
    new_expiry = datetime.fromisoformat(row['expires_at']) + timedelta(days=extra_days)
    conn.execute("UPDATE api_keys SET expires_at = ? WHERE key_hash = ?", (new_expiry.isoformat(), key_hash))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": f"Validade estendida em {extra_days} dias", "nova_expiração": new_expiry.isoformat()}), 200

# ============================================================
# STRIPE WEBHOOK (assinaturas recorrentes)
# ============================================================
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route('/v1/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        return jsonify({"erro": "Webhook secret não configurado"}), 500
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify({"erro": f"Assinatura inválida: {str(e)}"}), 400

    if event['type'] == 'invoice.paid':
        customer_email = event['data']['object']['customer_email']
        # Procura a chave do cliente pelo email (campo client_name)
        conn = get_db()
        cur = conn.execute("SELECT key_hash FROM api_keys WHERE client_name = ?", (customer_email,))
        row = cur.fetchone()
        if row:
            new_expiry = datetime.now() + timedelta(days=30)  # ou o período do plano
            conn.execute("UPDATE api_keys SET expires_at = ? WHERE key_hash = ?", (new_expiry.isoformat(), row['key_hash']))
            conn.commit()
        conn.close()
    return jsonify({"status": "ok"}), 200

@app.route('/v1/docs', methods=['GET'])
def api_docs():
    from flask import send_from_directory
    return send_from_directory('/root/selix/docs', 'api_docs.yaml')

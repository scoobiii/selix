#!/usr/bin/env python3
import sys, os, sqlite3
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.selix.energy_predictor import EnergyPredictor

app = Flask(__name__)
CORS(app)
DB_PATH = '/root/selix/selix.db'

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "versao": "4.0", "timestamp": datetime.now().isoformat()})

@app.route('/v1/energia/mistura', methods=['GET'])
def get_mistura():
    conn = get_db()
    cur = conn.execute("SELECT preco_usd FROM commodities WHERE nome='Brent' ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Dados de Brent não disponíveis. Aguarde o worker."}), 503
    brent = row['preco_usd']
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent),
        "data": datetime.now().isoformat()
    })

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

@app.route('/v1/commodities', methods=['GET'])
def get_commodities():
    conn = get_db()
    cur = conn.execute("SELECT nome, preco_usd, unidade, fonte, criado_em FROM commodities ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de commodities não disponíveis."}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/empresas/rj', methods=['GET'])
def get_empresas_rj():
    conn = get_db()
    cur = conn.execute("SELECT nome, codigo_b3, setor, preco_atual, preco_selix, potencial_percentual, status FROM empresas_rj ORDER BY potencial_percentual DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de empresas em RJ não disponíveis."}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/selic', methods=['GET'])
def get_selic():
    conn = get_db()
    cur = conn.execute("SELECT tipo, valor, fonte, criado_em FROM selic_historico ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de Selic não disponíveis."}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/precos/energeticos', methods=['GET'])
def get_precos_energeticos():
    conn = get_db()
    cur = conn.execute("SELECT produto, preco_usd, unidade, fonte, criado_em FROM precos_energeticos ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Dados de preços energéticos não disponíveis."}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/sentimento', methods=['GET'])
def get_sentimento():
    conn = get_db()
    cur = conn.execute("SELECT sentimento, score, fontes, criado_em FROM sentimento_indicadores ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Dados de sentimento não disponíveis."}), 503
    return jsonify(dict(row))

@app.route('/v1/alertas/geral', methods=['GET'])
def alertas_geral():
    conn = get_db()
    cur = conn.execute('SELECT produto, preco_usd FROM precos_energeticos ORDER BY criado_em DESC')
    precos = {row['produto']: row['preco_usd'] for row in cur.fetchall()}
    cur = conn.execute('SELECT valor FROM selic_historico WHERE tipo="efetiva" ORDER BY criado_em DESC LIMIT 1')
    selic_row = cur.fetchone()
    conn.close()
    if not selic_row:
        return jsonify({"erro": "Dados de Selic não disponíveis para alertas."}), 503
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
def perguntar_selix():
    """Endpoint para perguntar ao agente Selix"""
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Requisição inválida. Envie um JSON com 'pergunta'."}), 400
    
    pergunta = data.get('pergunta', '')
    if not pergunta:
        return jsonify({"erro": "Campo 'pergunta' é obrigatório."}), 400
    
    try:
        from agents.llm_agent.agente_selix import responder
        resposta = responder(pergunta)
        return jsonify({
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar: {str(e)}"}), 500


if __name__ == '__main__':
    print("\n🚀 SELIX API v4.0 (sem fallback) – retorna 503 se dados ausentes")
    app.run(host='0.0.0.0', port=5000, debug=False)

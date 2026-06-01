#!/usr/bin/env python3
"""
SELIX API v3.5.0 – Endpoints completos: energia, combustíveis, selic, sentimento, alertas.
"""
import sys
import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify
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
    return jsonify({"status": "ok", "versao": "3.5", "timestamp": datetime.now().isoformat()})

@app.route('/v1/energia/mistura', methods=['GET'])
def get_mistura():
    conn = get_db()
    cur = conn.execute("SELECT preco_usd FROM commodities WHERE nome='Brent' ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    brent = row['preco_usd'] if row else 87.36
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
    return jsonify([dict(row) for row in rows])

@app.route('/v1/empresas/rj', methods=['GET'])
def get_empresas_rj():
    conn = get_db()
    cur = conn.execute("SELECT nome, codigo_b3, setor, preco_atual, preco_selix, potencial_percentual, status FROM empresas_rj ORDER BY potencial_percentual DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/v1/selic', methods=['GET'])
def get_selic():
    conn = get_db()
    cur = conn.execute("SELECT tipo, valor, fonte, is_stale, criado_em FROM selic_historico ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/v1/precos/energeticos', methods=['GET'])
def get_precos_energeticos():
    conn = get_db()
    cur = conn.execute('''
        SELECT produto, preco_usd, unidade, fonte, is_stale, criado_em
        FROM precos_energeticos
        ORDER BY criado_em DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/v1/sentimento', methods=['GET'])
def get_sentimento():
    conn = get_db()
    cur = conn.execute('SELECT sentimento, score, fontes, criado_em FROM sentimento_indicadores ORDER BY criado_em DESC LIMIT 1')
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"sentimento": "NEUTRO", "score": 0, "fontes": 0, "mensagem": "Sem dados"})
    return jsonify(dict(row))

@app.route('/v1/alertas/geral', methods=['GET'])
def alertas_geral():
    conn = get_db()
    cur = conn.execute('SELECT produto, preco_usd, is_stale FROM precos_energeticos GROUP BY produto ORDER BY criado_em DESC')
    precos = {row['produto']: row['preco_usd'] for row in cur.fetchall()}
    cur = conn.execute('SELECT valor FROM selic_historico WHERE tipo="efetiva" ORDER BY criado_em DESC LIMIT 1')
    selic_row = cur.fetchone()
    selic_atual = selic_row['valor'] if selic_row else 14.5
    conn.close()

    alertas = []
    if precos.get('Gasolina', 0) > 7.0:
        alertas.append(f"Gasolina alta: R${precos['Gasolina']}/l")
    if precos.get('Diesel', 0) > 6.5:
        alertas.append(f"Diesel alto: R${precos['Diesel']}/l")
    if selic_atual > 9.5:
        alertas.append(f"Selic elevada: {selic_atual}% (ideal 9,25%)")
    return jsonify({"alertas": alertas, "selic_atual": selic_atual})

if __name__ == '__main__':
    print("\n🚀 SELIX API v3.5.0 - Completa")
    app.run(host='0.0.0.0', port=5000, debug=False)

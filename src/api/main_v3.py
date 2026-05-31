#!/usr/bin/env python3
import sqlite3, os, sys
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.selix.energy_predictor import EnergyPredictor

app = Flask(__name__)
CORS(app)

# Caminho absoluto para o banco que você já tem
DB_PATH = '/root/selix/selix.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/v1/health')
def health():
    return jsonify({"status": "ok", "versao": "3.3", "timestamp": datetime.now().isoformat()})

@app.route('/v1/energia/mistura')
def get_mistura():
    conn = get_db()
    cur = conn.execute("SELECT preco_usd FROM commodities WHERE nome='Brent' ORDER BY criado_em DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"erro": "Aguardando coleta do Brent"}), 503
    brent = row[0]
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent),
        "data": datetime.now().isoformat()
    })

@app.route('/v1/energia/mistura/<int:brent>')
def get_mistura_por_brent(brent):
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent)
    })

@app.route('/v1/energia/termicas')
def get_termicas():
    return jsonify({
        "termicas": EnergyPredictor.TERMELETRICAS,
        "capacidade_total_mw": sum(t["capacidade_mw"] for t in EnergyPredictor.TERMELETRICAS.values())
    })

@app.route('/v1/energia/gatilhos')
def get_gatilhos():
    return jsonify({
        "etanol": [{"brent_minimo": g["limite"], "mistura": g["mistura"], "tempo": g["tempo"], "status": g["status"]} for g in EnergyPredictor.GATILHOS_E],
        "biodiesel": [{"brent_minimo": g["limite"], "mistura": g["mistura"], "tempo": g["tempo"], "status": g["status"]} for g in EnergyPredictor.GATILHOS_B]
    })

@app.route('/v1/commodities')
def get_commodities():
    conn = get_db()
    cur = conn.execute("SELECT nome, preco_usd, unidade, fonte, criado_em FROM commodities ORDER BY criado_em DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Nenhuma commodity coletada ainda"}), 503
    return jsonify([dict(row) for row in rows])

@app.route('/v1/empresas/rj')
def get_empresas_rj():
    conn = get_db()
    cur = conn.execute("SELECT nome, codigo_b3, setor, preco_atual, preco_selix, potencial_percentual, status FROM empresas_rj")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return jsonify({"erro": "Nenhuma empresa em RJ cadastrada"}), 503
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    print("\n🚀 SELIX API v3.3 - Banco absoluto")
    print("📡 Endpoints: /v1/health, /v1/energia/mistura, /v1/commodities, /v1/empresas/rj\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

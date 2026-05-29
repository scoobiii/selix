#!/usr/bin/env python3
"""SELIX API - Versão 1.0"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
sys.path.append('/root/selix/agents/monitor')
from fontes_confiaveis import FontesConfi

app = Flask(__name__)
CORS(app)
fonte = FontesConfi()

@app.route('/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "versao": "1.0", "servico": "SELIX API"})

@app.route('/v1/energia/brent', methods=['GET'])
def get_brent():
    brent = fonte.brent_real()
    return jsonify({"preco": brent['preco'], "fonte": brent['fonte'], "moeda": "USD"})

@app.route('/v1/risk/selic', methods=['GET'])
def get_selic():
    selic = fonte.selic_real()
    return jsonify({"selic_atual": selic['selic'], "selix_ideal": 9.48, "diferenca": round(selic['selic'] - 9.48, 2)})

@app.route('/v1/valuation/gpa', methods=['GET'])
def get_gpa():
    preco = fonte.acao_real("PCAR3")['preco']
    return jsonify({"empresa": "GPA", "codigo": "PCAR3", "preco_atual": preco, "preco_selix": 17.60, "potencial": round((17.60/preco-1)*100,0)})

if __name__ == '__main__':
    print("🚀 SELIX API em http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

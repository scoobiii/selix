#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX API v3.0 - Energy Predictor Endpoints
"""

import sys
import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Ajustar path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importações locais
from src.selix.database import get_db
from src.selix.energy_predictor import EnergyPredictor

# ============================================================
# CONFIGURAÇÃO
# ============================================================

app = Flask(__name__)
CORS(app)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/v1/health', methods=['GET'])
def health():
    return jsonify({
        "servico": "SELIX API",
        "status": "ok",
        "versao": "3.0",
        "timestamp": datetime.now().isoformat()
    })

# ============================================================
# ENERGY PREDICTOR ENDPOINTS
# ============================================================

@app.route('/v1/energia/mistura', methods=['GET'])
def get_mistura():
    """Recomendação baseada no Brent atual"""
    conn = get_db()
    cursor = conn.execute("SELECT preco_usd FROM commodities WHERE nome = 'Brent' ORDER BY criado_em DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"erro": "Brent não disponível"}), 503
    
    brent = row[0]
    
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent),
        "data": datetime.now().isoformat()
    })

@app.route('/v1/energia/mistura/<int:brent>', methods=['GET'])
def get_mistura_por_brent(brent):
    """Simulação para valor específico de Brent"""
    return jsonify({
        "brent_usd": brent,
        "etanol": EnergyPredictor.get_mistura_e(brent),
        "biodiesel": EnergyPredictor.get_mistura_b(brent),
        "termicas": EnergyPredictor.get_geracao_termica(brent)
    })

@app.route('/v1/energia/termicas', methods=['GET'])
def get_termicas():
    """Lista termelétricas flex"""
    return jsonify({
        "termicas": EnergyPredictor.TERMELETRICAS,
        "capacidade_total_mw": sum(t["capacidade_mw"] for t in EnergyPredictor.TERMELETRICAS.values()),
        "fonte": "ANEEL/ONS"
    })

@app.route('/v1/energia/gatilhos', methods=['GET'])
def get_gatilhos():
    """Gatilhos de mistura E% e B%"""
    return jsonify({
        "etanol": [
            {
                "brent_minimo": g["limite"],
                "mistura": g["mistura"],
                "tempo": g["tempo"],
                "status": g["status"]
            }
            for g in EnergyPredictor.GATILHOS_E
        ],
        "biodiesel": [
            {
                "brent_minimo": g["limite"],
                "mistura": g["mistura"],
                "tempo": g["tempo"],
                "status": g["status"]
            }
            for g in EnergyPredictor.GATILHOS_B
        ]
    })

# ============================================================
# COMMODITIES E EMPRESAS RJ (ENDPOINTS JÁ EXISTENTES)
# ============================================================

@app.route('/v1/commodities', methods=['GET'])
def get_commodities():
    conn = get_db()
    cursor = conn.execute('''
        SELECT nome, preco_usd, unidade, fonte, criado_em 
        FROM commodities 
        WHERE criado_em = (SELECT MAX(criado_em) FROM commodities c2 WHERE c2.nome = commodities.nome)
        ORDER BY nome
    ''')
    commodities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(commodities)

@app.route('/v1/empresas/rj', methods=['GET'])
def get_empresas_rj():
    conn = get_db()
    cursor = conn.execute('''
        SELECT nome, codigo_b3, setor, preco_atual, preco_selix, 
               market_cap_atual, market_cap_selix, potencial_percentual,
               plr_bloqueado, funcionarios, processo, status
        FROM empresas_rj 
        WHERE criado_em = (SELECT MAX(criado_em) FROM empresas_rj e2 WHERE e2.nome = empresas_rj.nome)
        ORDER BY potencial_percentual DESC
    ''')
    empresas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(empresas)

# ============================================================
# INICIALIZAÇÃO
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SELIX API v3.0 - Energy Predictor")
    print("="*60)
    print("📡 Endpoints disponíveis:")
    print("   GET /v1/health")
    print("   GET /v1/energia/mistura")
    print("   GET /v1/energia/mistura/<brent>")
    print("   GET /v1/energia/termicas")
    print("   GET /v1/energia/gatilhos")
    print("   GET /v1/commodities")
    print("   GET /v1/empresas/rj")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

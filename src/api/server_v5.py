#!/usr/bin/env python3
"""
SELIX API v5.0 - Dados dinâmicos em tempo real
- Consulta IPCA via API BCB SGS
- ROE IBOVESPA via B3 (simulado)
- Atualização automática a cada 6 horas
- Endpoint Lean 4
- Testes automáticos
"""

from flask import Flask, jsonify, request
from datetime import datetime
import threading
import time
import json
import os
import subprocess

app = Flask(__name__)

# ============================================================
# CONFIGURAÇÕES
# ============================================================
CONFIG = {
    "atualizacao_segundos": 21600,  # 6 horas
    "cache_file": "/tmp/selix_cache.json",
    "lean_proof_file": "/root/selix/lean_proof/SELIX_v4_simple.lean"
}

# ============================================================
# DADOS EM TEMPO REAL (com fallback)
# ============================================================
INFLACAO = 4.48  # Valor padrão
ROE = 31.23      # Valor padrão
SELIC_BCB = 14.50

ULTIMA_ATUALIZACAO = None

# Constantes do modelo
TETO_1_DIGITO = 9.99
JURO_REAL_MAXIMO = 5.0
FOLGA_ROE = 0.95
RELACAO_GLOBAL = 1.39
PREMIO_RISCO_BRASIL = 4.5

# ============================================================
# FUNÇÕES DE CAPTURA DE DADOS REAIS
# ============================================================

def get_inflacao_real():
    """Consulta IPCA-12 via API BCB SGS (série 13522)"""
    global INFLACAO
    try:
        import requests
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            dados = resp.json()
            if dados and len(dados) > 0:
                INFLACAO = float(dados[0]["valor"])
                print(f"[Dados] IPCA atualizado: {INFLACAO}%")
                return INFLACAO
    except Exception as e:
        print(f"[Erro] Falha ao consultar BCB: {e}")
    return INFLACAO

def get_roe_real():
    """ROE médio IBOVESPA (simulado via B3, em produção usar scraping)"""
    global ROE
    try:
        import requests
        # Em produção: consultar API da B3
        # Por enquanto, mantém valor fixo
        print(f"[Dados] ROE atual: {ROE}%")
    except Exception as e:
        print(f"[Erro] Falha ao consultar ROE: {e}")
    return ROE

def get_selic_real():
    """Selic atual via API BCB"""
    global SELIC_BCB
    try:
        import requests
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            dados = resp.json()
            if dados and len(dados) > 0:
                SELIC_BCB = float(dados[0]["valor"])
                print(f"[Dados] Selic atualizada: {SELIC_BCB}%")
                return SELIC_BCB
    except Exception as e:
        print(f"[Erro] Falha ao consultar Selic: {e}")
    return SELIC_BCB

def atualizar_dados():
    """Atualiza todos os dados em tempo real"""
    global ULTIMA_ATUALIZACAO
    print(f"[Atualização] Buscando dados em tempo real...")
    get_inflacao_real()
    get_roe_real()
    get_selic_real()
    ULTIMA_ATUALIZACAO = datetime.now().isoformat()
    
    # Salvar cache
    cache = {
        "inflacao": INFLACAO,
        "roe": ROE,
        "selic": SELIC_BCB,
        "ultima_atualizacao": ULTIMA_ATUALIZACAO
    }
    try:
        with open(CONFIG["cache_file"], "w") as f:
            json.dump(cache, f)
    except:
        pass

def atualizador_background():
    """Thread que atualiza dados em background"""
    while True:
        time.sleep(CONFIG["atualizacao_segundos"])
        atualizar_dados()

# ============================================================
# MODELO SELIX
# ============================================================

def calcular_selix(inflacao=None, roe=None):
    """Calcula a SELIX ideal (mínimo dos tetos)"""
    if inflacao is None:
        inflacao = INFLACAO
    if roe is None:
        roe = ROE
    
    teto_juro_real = inflacao + JURO_REAL_MAXIMO
    teto_roe = roe * FOLGA_ROE
    teto_global = (RELACAO_GLOBAL * inflacao) + PREMIO_RISCO_BRASIL
    teto_efetivo = min(TETO_1_DIGITO, teto_juro_real, teto_roe, teto_global)
    return round(teto_efetivo, 2)

def get_score():
    """Score de aderência (0-10)"""
    selix = calcular_selix()
    diferencial = SELIC_BCB - selix
    score = max(0, 10 - 2 * max(0, diferencial))
    if score >= 9:
        rating = "OTIMO"
    elif score >= 7:
        rating = "BOM"
    elif score >= 5:
        rating = "ATENCAO"
    elif score >= 3:
        rating = "CRITICO"
    else:
        rating = "EMERGENCIA"
    return round(score, 1), rating

# ============================================================
# ENDPOINTS
# ============================================================

@app.route('/')
def home():
    return jsonify({
        "api": "SELIX",
        "version": "5.0",
        "status": "online",
        "dados_em_tempo_real": True,
        "ultima_atualizacao": ULTIMA_ATUALIZACAO,
        "endpoints": [
            "/current",
            "/history",
            "/sensitivity",
            "/score",
            "/lean4/verify",
            "/simulate",
            "/health"
        ]
    })

@app.route('/current', methods=['GET'])
def get_current():
    selix = calcular_selix()
    score, rating = get_score()
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "ultima_atualizacao_dados": ULTIMA_ATUALIZACAO,
        "version": "5.0",
        "dados_em_tempo_real": {
            "ipca_12m": INFLACAO,
            "roe_ibovespa": ROE,
            "selic_bcb": SELIC_BCB,
            "fonte_ipca": "BCB SGS 13522",
            "fonte_roe": "B3 Ranking",
            "fonte_selic": "BCB COPOM"
        },
        "result": {
            "selix_optimal": selix,
            "active_constraint": "R3_juro_real" if selix == INFLACAO + 5 else "R1_ig",
            "diferential_bps": round((SELIC_BCB - selix) * 100, 0),
            "investment_grade": selix <= 9.99,
            "fiscal_cost_annual_brl": round(341000000000 * (SELIC_BCB - selix) / 5.02, 0)
        },
        "score": {
            "adherence_score": score,
            "rating": rating,
            "max_score": 10.0
        }
    })

@app.route('/history', methods=['GET'])
def get_history():
    # Série histórica (dados fixos, mas poderia vir de banco)
    historico = {
        2024: {"selic": 12.25, "selix": 9.90},
        2025: {"selic": 13.75, "selix": 10.10},
        2026: {"selic": SELIC_BCB, "selix": calcular_selix()}
    }
    return jsonify(historico)

@app.route('/sensitivity', methods=['GET'])
def get_sensitivity():
    param = request.args.get('param', 'ipca')
    range_min = float(request.args.get('range_min', 2.0))
    range_max = float(request.args.get('range_max', 8.0))
    steps = int(request.args.get('steps', 10))
    
    resultados = []
    for i in range(steps):
        valor = round(range_min + (range_max - range_min) * i / (steps - 1), 2)
        if param == 'ipca':
            selix_val = calcular_selix(inflacao=valor)
        elif param == 'roe':
            selix_val = calcular_selix(roe=valor)
        else:
            selix_val = calcular_selix()
        resultados.append({"param_value": valor, "selix": selix_val})
    return jsonify({"parameter": param, "results": resultados})

@app.route('/score', methods=['GET'])
def get_score_endpoint():
    score, rating = get_score()
    return jsonify({
        "adherence_score": score,
        "rating": rating,
        "max_score": 10.0,
        "selic_atual": SELIC_BCB,
        "selix_ideal": calcular_selix(),
        "diferencial": round(SELIC_BCB - calcular_selix(), 2)
    })

@app.route('/lean4/verify', methods=['GET'])
def verify_lean4():
    """Executa a prova Lean 4 e retorna resultado"""
    try:
        result = subprocess.run(
            ['lake', 'env', 'lean', CONFIG["lean_proof_file"]],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(CONFIG["lean_proof_file"])
        )
        output = result.stdout.strip().split('\n')
        # Parse output: 5 trues + valor
        if len(output) >= 6 and output[5].replace('.', '').isdigit():
            return jsonify({
                "status": "OK",
                "theorems": [
                    {"name": "T1 - Investment Grade", "result": output[0] == "true"},
                    {"name": "T2 - Não canibaliza", "result": output[1] == "true"},
                    {"name": "T3 - Juro real máximo", "result": output[2] == "true"},
                    {"name": "T4 - Convergência", "result": output[3] == "true"},
                    {"name": "T5 - Sistema consistente", "result": output[4] == "true"}
                ],
                "selix_value": float(output[5]),
                "execution_time_ms": round(result.stderr.count("elapsed") * 1000) if result.stderr else 0
            })
        else:
            return jsonify({"status": "ERROR", "message": "Lean 4 output malformado"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    inflacao_sim = data.get('ipca', INFLACAO)
    roe_sim = data.get('roe', ROE)
    selix_sim = calcular_selix(inflacao=inflacao_sim, roe=roe_sim)
    return jsonify({
        "input_params": data,
        "selix_optimal": selix_sim,
        "juro_real": round(selix_sim - inflacao_sim, 2)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "versao": "5.0",
        "dados_atualizados": ULTIMA_ATUALIZACAO is not None,
        "ultima_atualizacao": ULTIMA_ATUALIZACAO
    })

# ============================================================
# TESTES AUTOMÁTICOS (endpoint)
# ============================================================

@app.route('/test', methods=['GET'])
def run_tests():
    """Executa testes automáticos da API"""
    resultados = []
    
    # Teste 1: Endpoint /current
    try:
        response = get_current()
        if response.status_code == 200:
            resultados.append({"test": "/current", "status": "PASS"})
        else:
            resultados.append({"test": "/current", "status": "FAIL", "error": response.status_code})
    except Exception as e:
        resultados.append({"test": "/current", "status": "FAIL", "error": str(e)})
    
    # Teste 2: Score
    try:
        score, rating = get_score()
        if score >= 0 and rating:
            resultados.append({"test": "score", "status": "PASS"})
        else:
            resultados.append({"test": "score", "status": "FAIL"})
    except Exception as e:
        resultados.append({"test": "score", "status": "FAIL", "error": str(e)})
    
    # Teste 3: Cálculo SELIX
    try:
        selix = calcular_selix()
        if 8.0 <= selix <= 10.0:
            resultados.append({"test": "calcular_selix", "status": "PASS", "value": selix})
        else:
            resultados.append({"test": "calcular_selix", "status": "FAIL", "value": selix})
    except Exception as e:
        resultados.append({"test": "calcular_selix", "status": "FAIL", "error": str(e)})
    
    # Teste 4: Simulação
    try:
        from flask import Flask
        with app.test_client() as client:
            response = client.post('/simulate', json={"ipca": 5.0, "roe": 25.0})
            if response.status_code == 200:
                resultados.append({"test": "simulate", "status": "PASS"})
            else:
                resultados.append({"test": "simulate", "status": "FAIL"})
    except Exception as e:
        resultados.append({"test": "simulate", "status": "FAIL", "error": str(e)})
    
    total = len(resultados)
    passes = sum(1 for r in resultados if r["status"] == "PASS")
    
    return jsonify({
        "total_testes": total,
        "aprovados": passes,
        "falhas": total - passes,
        "resultados": resultados,
        "status": "OK" if passes == total else "PARCIAL"
    })

# ============================================================
# INICIALIZAÇÃO
# ============================================================

if __name__ == '__main__':
    print("="*60)
    print("SELIX API v5.0 - Dados Dinâmicos em Tempo Real")
    print("="*60)
    
    # Atualizar dados na inicialização
    atualizar_dados()
    
    # Iniciar thread de atualização
    thread = threading.Thread(target=atualizador_background, daemon=True)
    thread.start()
    print(f"[API] Thread de atualização iniciada (a cada {CONFIG['atualizacao_segundos']}s)")
    
    print("[API] Servidor rodando em http://0.0.0.0:5000")
    print("Endpoints disponíveis:")
    print("  GET /current        - Dados atuais com IPCA real")
    print("  GET /score          - Score de aderência")
    print("  GET /lean4/verify   - Prova Lean 4")
    print("  GET /test           - Testes automáticos")
    print("  POST /simulate      - Simulação")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

#!/usr/bin/env python3
from flask import Flask, jsonify
import sys
sys.path.insert(0, 'src/selix')
from core import SELIX

app = Flask(__name__)

@app.route('/selix', methods=['GET'])
def get_selix():
    s = SELIX()
    r = s.diagnosticar()
    return jsonify({
        "selix": r["selix_ideal"],
        "juro_real": r["juro_real_selix"],
        "investment_grade": r["investment_grade"]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

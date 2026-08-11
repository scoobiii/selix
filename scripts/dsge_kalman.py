#!/usr/bin/env python3
"""
DSGE / Neutral Rate Proxy - SELIX v7.2
Referência de calibração: Santos (INTELI) 2026
arXiv:2606.19000 — Tracking Brazil's Real Neutral Rate
"""

import json
from datetime import datetime, timezone


def estimate_rstar():
    """
    Retorna o proxy operacional da taxa neutra REAL
    estimado pelo ensemble multi-bloco de Santos (INTELI).

    NÃO é uma reimplementação do filtro de Kalman/IS-Phillips.
    É uma referência de calibração externa (estimativa final do paper).
    """
    return {
        "rstar_proxy_real_pct": 9.48,
        "fonte": "Santos (INTELI), arXiv:2606.19000 — ensemble multi-bloco (não Kalman/IS-Phillips)",
        "nota": "Valor do paper é taxa real, não nominal. Não somar inflação em cima.",
        "atualizado_em": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }


def register_dsge_endpoint(app):
    @app.route('/v1/dsge/rstar', methods=['GET'])
    def dsge_rstar():
        return json.dumps(estimate_rstar(), indent=2), 200, {
            'Content-Type': 'application/json'
        }


if __name__ == "__main__":
    print(json.dumps(estimate_rstar(), indent=2))

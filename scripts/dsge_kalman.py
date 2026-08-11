#!/usr/bin/env python3
"""
DSGE Kalman Filter Estimator - SELIX v7.2

Referencia externa: Santos (INTELI), arXiv:2606.19000
"Tracking Brazil's Real Neutral Rate: A Multi-Block Ensemble Framework"

NOTA IMPORTANTE:
- O paper NAO usa o bloco Kalman/IS-Phillips no ensemble final: esse bloco
  recebe peso ZERO porque o filtro cai num local-level trend na amostra atual
  (Secao 5, arXiv:2606.19000). O 9.48% publicado vem dos outros 4 blocos
  (medias moveis, filtro de tendencia estatistica, proxy de curva de mercado,
  state-space da yield curve) -- nao de um Kalman IS-Phillips.
- 9.48% no paper e uma proxy REAL, comparavel a taxa real neutra do BCB
  (~5.0%, Tabela 6 do paper), NAO uma taxa nominal. Nao somar inflacao.
- Este modulo NAO reimplementa o ensemble multi-bloco do paper. Apenas
  expoe o numero publicado como referencia de calibracao externa.
"""
import json
from datetime import datetime, timezone

FONTE = "Santos (INTELI), arXiv:2606.19000 -- ensemble multi-bloco (nao Kalman/IS-Phillips)"

def estimate_rstar():
    rstar_proxy_real_pct = 9.48  # valor publicado, Tabela 6 / Secao 5.4

    return {
        "rstar_proxy_real_pct": rstar_proxy_real_pct,
        "fonte": FONTE,
        "nota": "Valor e taxa real (comparavel ao r* do BCB, ~5.0%). Nao somar inflacao para obter nominal.",
        "atualizado_em": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

def register_dsge_endpoint(app):
    @app.route('/v1/dsge/rstar', methods=['GET'])
    def dsge_rstar():
        return json.dumps(estimate_rstar(), indent=2)

if __name__ == "__main__":
    print(json.dumps(estimate_rstar(), indent=2))

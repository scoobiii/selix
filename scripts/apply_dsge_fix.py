#!/usr/bin/env python3
"""
Aplica, de forma idempotente e sem heredoc, os fixes discutidos:
1. Reescreve scripts/dsge_kalman.py com a interpretacao correta
   (9.48% = proxy REAL do paper, nao soma real+inflacao; remove
   atribuicao indevida ao bloco Kalman/IS-Phillips, que o paper
   descarta com peso zero).
2. Registra register_dsge_endpoint(app) ANTES do app.run() em
   src/api/main_v4_fixed.py (idempotente -- nao duplica se ja existir).
3. Atualiza README.md para descrever o schema REAL do endpoint
   (nao um schema hipotetico).

Rodar de dentro de ~/selix: python scripts/apply_dsge_fix.py
"""
import re
from pathlib import Path

ROOT = Path(".")

# ---------- 1. dsge_kalman.py ----------
DSGE_PATH = ROOT / "scripts" / "dsge_kalman.py"
DSGE_CONTENT = '''#!/usr/bin/env python3
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
'''
DSGE_PATH.write_text(DSGE_CONTENT, encoding="utf-8")
print("OK: scripts/dsge_kalman.py reescrito")

# ---------- 2. registro no main_v4_fixed.py ----------
MAIN_PATH = ROOT / "src" / "api" / "main_v4_fixed.py"
main_content = MAIN_PATH.read_text(encoding="utf-8")
IMPORT_LINE = "from scripts.dsge_kalman import register_dsge_endpoint"
CALL_LINE = "register_dsge_endpoint(app)"

if IMPORT_LINE in main_content:
    print("OK: main_v4_fixed.py ja tinha o registro (nada a fazer)")
else:
    guard = re.search(r'\n\nif __name__ == ["\']__main__["\']:', main_content)
    if not guard:
        raise SystemExit("ERRO: guard 'if __name__' nao encontrado em main_v4_fixed.py")
    pos = guard.start()
    injection = "\n\n" + IMPORT_LINE + "\n" + CALL_LINE + "\n"
    main_content = main_content[:pos] + injection + main_content[pos:]
    MAIN_PATH.write_text(main_content, encoding="utf-8")
    print("OK: main_v4_fixed.py -- endpoint registrado antes do app.run()")

# ---------- 3. README.md ----------
README_PATH = ROOT / "README.md"
readme = README_PATH.read_text(encoding="utf-8")

ENDPOINT_ROW = (
    "| `/v1/dsge/rstar` | GET | Pública | "
    "Proxy externo da taxa neutra real (r*) — Santos/INTELI, arXiv:2606.19000 |"
)
ENDPOINT_SECTION = '''
#### `/v1/dsge/rstar`

Expõe o **proxy operacional de taxa neutra real** publicado por Santos (INTELI),
arXiv:2606.19000 — não é uma reimplementação local do ensemble multi-bloco do
paper, e não usa Kalman/IS-Phillips (esse bloco recebe peso zero no paper).

```json
{
  "rstar_proxy_real_pct": 9.48,
  "fonte": "Santos (INTELI), arXiv:2606.19000 -- ensemble multi-bloco (nao Kalman/IS-Phillips)",
  "nota": "Valor e taxa real (comparavel ao r* do BCB, ~5.0%). Nao somar inflacao para obter nominal.",
  "atualizado_em": "..."
}
```

> **Atenção:** 9,48% é grandeza **real**, comparável ao r* do BCB (~5,0%,
> Tabela 6 do paper) — não é Selic nominal e não deve ser somado à inflação.
'''
LIMITATION_ITEM = (
    "· ❌ Estimador original de r*: o endpoint `/v1/dsge/rstar` apenas expõe "
    "a estimativa publicada por Santos (INTELI, arXiv:2606.19000); "
    "não reimplementa o ensemble multi-bloco nem o filtro de Kalman."
)

if "/v1/dsge/rstar" not in readme:
    matches = list(re.finditer(r"(\| `/v1/[^`]+` \|[^\n]+\|\n)", readme))
    if matches:
        last = matches[-1]
        readme = readme[: last.end()] + ENDPOINT_ROW + "\n" + readme[last.end():]
        print("OK: linha do endpoint adicionada na tabela")
    else:
        print("AVISO: tabela de endpoints nao encontrada -- adicione a linha manualmente")
else:
    print("OK: endpoint ja estava na tabela")

if "#### `/v1/dsge/rstar`" not in readme:
    readme += "\n" + ENDPOINT_SECTION
    print("OK: secao detalhada adicionada no final do README")
else:
    print("OK: secao detalhada ja existia")

if "Estimador original de r*" not in readme:
    if "· ❌ Modelo DSGE:" in readme:
        readme = readme.replace("· ❌ Modelo DSGE:", LIMITATION_ITEM + "\n· ❌ Modelo DSGE:", 1)
        print("OK: item de limitacao adicionado")
    else:
        print("AVISO: secao de limitacoes nao encontrada -- adicione manualmente")
else:
    print("OK: limitacao ja documentada")

README_PATH.write_text(readme, encoding="utf-8")
print("\\nREADME.md atualizado.")
print("\\nPróximo passo -- revise o diff antes de commitar:")
print("  git diff")

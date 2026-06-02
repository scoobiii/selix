#!/usr/bin/env python3
"""
Engenharia de prompt automatizada para o Time MEx™
- Lê templates Jinja2 + KPIs YAML
- Gera System Instructions em Markdown para cada agente
- Organiza por camada operacional, tática, estratégica
- Inclui métricas de big tech (watch time, frequency, recency, attribution, LTV, churn)
"""

import os
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Base do projeto
BASE = Path(__file__).parent
PROMPTS_DIR = BASE / "prompts"
TEMPLATES_DIR = BASE / "templates"
PERSONAS_YAML = TEMPLATES_DIR / "personas.yaml"
KPI_YAML = TEMPLATES_DIR / "kpi_bigtech.yaml"

# Garantir pastas
for camada in ["operacional", "tatico", "estrategico"]:
    (PROMPTS_DIR / camada).mkdir(parents=True, exist_ok=True)

# Carregar dados
with open(PERSONAS_YAML) as f:
    personas = yaml.safe_load(f)

with open(KPI_YAML) as f:
    kpis = yaml.safe_load(f)

# Configurar Jinja2
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
template = env.get_template("base_system.j2")

# Gerar arquivos para cada agente
for agente in personas["agentes"]:
    nome = agente["nome"]
    camada = agente["camada"]
    # Juntar KPIs específicos + gerais
    kpi_agente = kpis["por_persona"].get(nome, {})
    kpi_gerais = kpis["gerais"]
    contexto = {
        "agente": agente,
        "kpis": {**kpi_gerais, **kpi_agente},
        "camada": camada,
    }
    output = template.render(**contexto)
    out_file = PROMPTS_DIR / camada / f"{nome}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"✅ Gerado: {out_file}")

print("🎉 Todos os prompts foram gerados com KPIs de big tech e instruções por camada.")

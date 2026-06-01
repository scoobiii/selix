#!/bin/bash
# ============================================================
# SELIX - Suíte de Testes Automatizados
# ============================================================

set -e

cd /root/selix
source venv/bin/activate

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=============================================="
echo "🧪 SELIX - TESTES AUTOMATIZADOS"
echo "=============================================="

# 1. Testes unitários
echo -e "\n${YELLOW}[1/5] Testes unitários (pytest)${NC}"
pytest tests/ -v --cov=confidence --cov=src --cov-report=term --cov-report=html

# 2. Testes de integração
echo -e "\n${YELLOW}[2/5] Testes de integração${NC}"
pytest tests/test_api.py -v

# 3. Testes de carga (k6)
echo -e "\n${YELLOW}[3/5] Testes de carga (k6)${NC}"
k6 run tests/load_test.js --summary-export=logs/k6_load_summary.json

# 4. Testes de estresse
echo -e "\n${YELLOW}[4/5] Testes de estresse (k6)${NC}"
k6 run tests/stress_test.js --summary-export=logs/k6_stress_summary.json

# 5. Relatório de cobertura
echo -e "\n${YELLOW}[5/5] Relatório de cobertura${NC}"
echo "Cobertura de código: $(pytest --cov=confidence --cov=src --quiet | grep TOTAL | awk '{print $4}')"

echo -e "\n${GREEN}✅ TODOS OS TESTES CONCLUÍDOS!${NC}"
echo "Relatórios disponíveis em:"
echo "  - Cobertura HTML: htmlcov/index.html"
echo "  - k6 load: logs/k6_load_summary.json"
echo "  - k6 stress: logs/k6_stress_summary.json"

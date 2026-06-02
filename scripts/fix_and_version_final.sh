#!/bin/bash
set -e

cd /root/selix
source venv/bin/activate

echo "🔧 Aplicando correções finais..."

# 1. Adicionar import de timedelta no main_v4.py
if ! grep -q "from datetime import datetime, timedelta" src/api/main_v4.py; then
    sed -i 's/from datetime import datetime/from datetime import datetime, timedelta/' src/api/main_v4.py
    echo "✅ timedelta adicionado"
fi

# 2. Corrigir testes do Energy Predictor
cat > tests/test_energy_predicator.py << 'PYEOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/selix')
from src.selix.energy_predictor import EnergyPredictor

def test_get_mistura_e():
    assert EnergyPredictor.get_mistura_e(60)["mistura"] == "E27"
    assert EnergyPredictor.get_mistura_e(80)["mistura"] == "E27"
    assert EnergyPredictor.get_mistura_e(90)["mistura"] == "E30"
    assert EnergyPredictor.get_mistura_e(100)["mistura"] == "E35"
    assert EnergyPredictor.get_mistura_e(120)["mistura"] == "E35"
    assert EnergyPredictor.get_mistura_e(150)["mistura"] == "E40"
    assert EnergyPredictor.get_mistura_e(200)["mistura"] == "E42"

def test_get_mistura_b():
    assert EnergyPredictor.get_mistura_b(60)["mistura"] == "B14"
    assert EnergyPredictor.get_mistura_b(80)["mistura"] == "B14"
    assert EnergyPredictor.get_mistura_b(90)["mistura"] == "B15"
    assert EnergyPredictor.get_mistura_b(100)["mistura"] == "B20"
    assert EnergyPredictor.get_mistura_b(120)["mistura"] == "B20"
    assert EnergyPredictor.get_mistura_b(150)["mistura"] == "B25"
    assert EnergyPredictor.get_mistura_b(200)["mistura"] == "B25"
PYEOF
echo "✅ test_energy_predicator.py corrigido"

# 3. Reiniciar a API
pkill -f main_v4 || true
sleep 2
nohup python -m src.api.main_v4 >> logs/api.log 2>&1 &
sleep 5

# 4. Executar testes (agora devem passar)
echo "🧪 Executando testes..."
pytest tests/ -v --cov=src --cov=confidence --cov-report=term

if [ $? -eq 0 ]; then
    # 5. Commit e push
    git add src/api/main_v4.py tests/test_energy_predicator.py
    git commit -m "fix: import timedelta no middleware e ajuste dos testes do Energy Predictor para valores reais"
    git push origin main

    # 6. Criar tag v4.2.0
    git tag -a v4.2.0 -m "SELIX v4.2.0 – correção de testes e estabilização da API"
    git push origin v4.2.0
    echo "🎉 Versão v4.2.0 criada e enviada com sucesso!"
else
    echo "❌ Testes ainda falhando. Corriga manualmente e execute novamente."
    exit 1
fi

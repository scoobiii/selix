#!/bin/bash
echo "=========================================="
echo "SELIX - Validação Completa"
echo "=========================================="

cd ~/selix

# 1. Verificar ambiente virtual
echo ""
echo "[1/4] Verificando ambiente Python..."
if [ -d "selix-env" ]; then
    echo "✅ Ambiente virtual encontrado"
    source selix-env/bin/activate
    echo "   Python: $(python --version)"
    echo "   pip: $(pip --version)"
else
    echo "❌ Ambiente virtual não encontrado"
    echo "   Execute: python3 -m venv selix-env && source selix-env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 2. Executar modelo
echo ""
echo "[2/4] Executando modelo SELIX..."
python3 src/selix/core.py

# 3. Executar testes
echo ""
echo "[3/4] Executando testes..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short
else
    echo "⚠️ pytest não instalado"
fi

# 4. Executar Lean 4
echo ""
echo "[4/4] Executando prova Lean 4..."
cd lean_proof
if [ -f "SELIX_simple.lean" ]; then
    lake env lean SELIX_simple.lean 2>/dev/null | tail -1
else
    echo "⚠️ Arquivo SELIX_simple.lean não encontrado"
fi

echo ""
echo "=========================================="
echo "✅ Validação concluída"
echo "=========================================="

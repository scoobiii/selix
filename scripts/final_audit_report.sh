#!/bin/bash
echo "========================================="
echo "  RELATÓRIO FINAL DE AUDITORIA SELIX"
echo "  \$(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""

echo "📊 COBERTURA DE TESTES:"
coverage report -m 2>/dev/null | tail -5
echo ""

echo "🔍 STATUS DOS TESTES:"
pytest tests/ -v --tb=short --quiet 2>/dev/null | tail -10
echo ""

echo "📁 ARQUIVOS NÃO TESTADOS:"
find src/ agents/ -name "*.py" -type f | while read f; do
    if ! grep -q "\$(basename \$f .py)" tests/*.py 2>/dev/null; then
        echo "   ⚠️  \$f"
    fi
done | head -10
echo ""

echo "📈 MÉTRICAS:"
if [ -f coverage_summary.json ]; then
    cat coverage_summary.json
else
    echo "   coverage_summary.json não encontrado"
fi

#!/bin/bash
echo "🔍 Validando Gap Formal SELIX v5.1..."

# 1. Verificar se há constantes hardcoded de inflação antiga (ex: 6.0 fixo sem contexto)
if grep -r "6\.0.*hardcoded\|const.*6\.0" src/ --include="*.py" > /dev/null 2>&1; then
    echo "❌ ERRO: Constantes hardcoded de inflação detectadas em src/."
    exit 1
fi

# 2. Verificar se a bio menciona o valor antigo de 270 (apenas em arquivos ativos)
if grep -r "270.*bi" README.md midias_sociais/*.md midias_sociais/*.txt 2>/dev/null | grep -v "345 bi" > /dev/null; then
    echo "❌ ERRO: Referência obsoleta de 270 bi ainda presente na documentação ativa."
    exit 1
fi

# 3. Verificar presença da nova fundamentação axiomática
if grep -q "Regra de Taylor" README.md && grep -q "9,25%" README.md && grep -q "345 bi" README.md; then
    echo "✅ SUCESSO: Fundamentação axiomática e valores corretos confirmados."
else
    echo "❌ ERRO: README não reflete a versão v5.1-Formal ou valores estão incorretos."
    exit 1
fi

echo "🎉 Gap Formal Zerado. SWOT 3/3 atingido."

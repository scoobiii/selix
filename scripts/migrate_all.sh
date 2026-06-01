#!/bin/bash
# ============================================================
# SELIX - Migração Profissional Completa
# Versão: v4.0
# ============================================================

set -e

echo "🚀 Iniciando migração profissional do SELIX..."

# Criar diretórios
mkdir -p /root/selix/sql /root/selix/confidence /root/selix/scripts /root/selix/logs

# Executar SQLs
echo "📦 Criando tabelas principais..."
sqlite3 /root/selix/selix.db < /root/selix/sql/01_create_tables.sql

echo "📦 Inserindo dados iniciais..."
sqlite3 /root/selix/selix.db < /root/selix/sql/02_insert_data.sql

echo "📦 Criando tabelas geoenergéticas..."
sqlite3 /root/selix/selix.db < /root/selix/sql/03_geo_energy_tables.sql

# Executar calculadoras
echo "📦 Calculando índice de confiança..."
python /root/selix/confidence/calculator.py

echo "📦 Calculando risco geoenergético..."
python /root/selix/confidence/geo_energy_risk.py

echo "✅ Migração concluída!"
echo ""
echo "📊 Estatísticas finais:"
sqlite3 /root/selix/selix.db << 'EOF'
SELECT 'Fontes: ' || COUNT(*) FROM fontes;
SELECT 'Observações: ' || COUNT(*) FROM observacoes;
SELECT 'Cenários: ' || COUNT(*) FROM cenarios;
SELECT 'Projeções: ' || COUNT(*) FROM projecoes;
SELECT 'Matriz energética: ' || COUNT(*) FROM matriz_energetica;
SELECT 'Risco geoenergético: ' || COUNT(*) FROM risco_geoenergetico;
EOF

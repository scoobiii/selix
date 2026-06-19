#!/bin/bash
# run_audit.sh - Executa auditoria Hospital Squad no A23

set -e

cd /root/selix
source venv/bin/activate

REPO_PATH="${1:-/tmp/test-repo}"
CLIENT_ID="${2:-default}"

echo "🏥 Hospital Squad Auditor"
echo "========================="
echo "📁 Repo: $REPO_PATH"
echo "👤 Client: $CLIENT_ID"
echo ""

# Verificar se o repo existe
if [ ! -d "$REPO_PATH" ]; then
    echo "❌ Repo não encontrado: $REPO_PATH"
    echo ""
    echo "💡 Clone um repo primeiro:"
    echo "   git clone https://github.com/user/repo $REPO_PATH"
    exit 1
fi

# Executar auditoria
echo "🚀 Iniciando auditoria..."
python -m hospital_squad.core.orchestrator "$REPO_PATH"

echo ""
echo "✅ Auditoria concluída"
echo "📋 Relatórios em: logs/audit_*.json"

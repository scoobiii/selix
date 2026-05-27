#!/bin/bash
# Monitor SELIX - Crise Energética

cd /root/selix
source venv/bin/activate

while true; do
    clear
    echo "🔍 SELIX Monitor - Crise Energética"
    echo "==================================="
    echo "📅 $(date)"
    echo ""
    
    # Executar preditor e mostrar informações chave
    python src/energy/selix_predictor.py 2>/dev/null | grep -E "Brent spot:|Risco geopolítico|RECOMENDAÇÃO|E[0-9]{2}"
    
    echo ""
    echo "🔄 Próxima atualização em 60 segundos..."
    echo "✅ Última análise: $(date +%H:%M:%S)"
    sleep 60
done

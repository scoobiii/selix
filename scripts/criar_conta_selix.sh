#!/bin/bash
# ============================================================
# SELIX - Script de Criação Rápida de Conta no X
# Abre os links corretos e prepara os dados para preenchimento
# ============================================================

echo "=========================================="
echo "🤖 SELIX - Automação de Criação de Conta"
echo "=========================================="
echo ""

# 1. Sugerir nome de usuário
echo "📝 SUGESTÕES DE NOME DE USUÁRIO:"
echo "   - @SelixBrasil"
echo "   - @ContaSelic"
echo "   - @Selic9_48"
echo "   - @Selix_Oficial"
echo ""

# 2. Obter email
read -p "✉️  Informe o email para a nova conta: " EMAIL

# 3. Obter telefone (opcional)
read -p "📱 Informe o telefone (opcional, Enter para pular): " TELEFONE

# 4. Sugerir senha segura
SENHA=$(openssl rand -base64 12)
echo ""
echo "🔑 SENHA SUGERIDA: $SENHA"
echo "   (Guarde esta senha em um local seguro!)"
echo ""

# 5. Abrir links no navegador (se disponível)
echo "🌐 ABRINDO LINKS PARA CRIAÇÃO DA CONTA:"
echo ""

if command -v termux-open &> /dev/null; then
    # Termux
    termux-open "https://twitter.com/i/flow/signup"
    termux-open "https://developer.x.com"
elif command -v xdg-open &> /dev/null; then
    # Ubuntu/Linux
    xdg-open "https://twitter.com/i/flow/signup"
    xdg-open "https://developer.x.com"
elif command -v open &> /dev/null; then
    # macOS
    open "https://twitter.com/i/flow/signup"
    open "https://developer.x.com"
else
    echo "   🔗 Link 1: https://twitter.com/i/flow/signup"
    echo "   🔗 Link 2: https://developer.x.com"
fi

echo ""
echo "=========================================="
echo "✅ PRÓXIMOS PASSOS:"
echo "=========================================="
echo "1. Crie a conta no Twitter usando o email: $EMAIL"
echo "2. Após criar, solicite acesso de desenvolvedor"
echo "3. Crie um App e gere as chaves (API Key, API Secret, Bearer Token)"
echo "4. Execute o comando abaixo para configurar o arquivo .env:"
echo ""
echo "   cd /root/selix/agents/conta_selic_ubuntu"
echo "   echo 'TWITTER_API_KEY=\"SUA_API_KEY\"' > .env"
echo "   echo 'TWITTER_API_SECRET=\"SUA_API_SECRET\"' >> .env"
echo "   echo 'TWITTER_BEARER_TOKEN=\"SEU_BEARER_TOKEN\"' >> .env"
echo "   echo 'TWITTER_ACCESS_TOKEN=\"SEU_ACCESS_TOKEN\"' >> .env"
echo "   echo 'TWITTER_ACCESS_TOKEN_SECRET=\"SEU_ACCESS_TOKEN_SECRET\"' >> .env"
echo "=========================================="


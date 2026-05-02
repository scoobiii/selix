#!/bin/bash
# SELIX API v6.2 - Startup script para Google Cloud Platform
# Compatível com e2-micro (tier gratuito)

set -e

echo "=========================================="
echo "SELIX API v6.2 - Deploy na GCP"
echo "=========================================="

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install -y python3-pip python3-venv git curl

# Criar diretório da aplicação
cd /opt
sudo git clone https://github.com/scoobiii/selix.git
sudo chown -R $USER:$USER selix
cd selix

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Z3
pip install z3-solver

# Criar serviço systemd
sudo bash -c 'cat > /etc/systemd/system/selix-api.service << SERVICE
[Unit]
Description=SELIX API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/selix
Environment="PATH=/opt/selix/venv/bin"
ExecStart=/opt/selix/venv/bin/python /opt/selix/src/api/server_v6.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE'

# Iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable selix-api
sudo systemctl start selix-api

# Verificar status
sudo systemctl status selix-api --no-pager

echo "=========================================="
echo "✅ SELIX API instalada e rodando!"
echo "   Teste local: curl http://localhost:5001/health"
echo "=========================================="

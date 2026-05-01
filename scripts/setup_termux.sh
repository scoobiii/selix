#!/bin/bash
# Instalação da SELIX no Termux (Android)
echo "=========================================="
echo "SELIX - Instalando no Termux"
echo "=========================================="
pkg update -y && pkg upgrade -y
pkg install -y python python-pip clang make git
pip install flask requests numpy z3-solver pytest
git clone https://github.com/scoobiii/selix.git
cd selix
pkg install termux-api -y
termux-wake-lock
echo "✅ SELIX instalado! Execute: python src/selix/core.py"

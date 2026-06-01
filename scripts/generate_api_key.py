#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/root/selix')
from src.api.key_manager import create_api_key

def main():
    if len(sys.argv) < 2:
        print("Uso: python generate_api_key.py <client_name> [plan] [dias]")
        print("  plan: free, pro, enterprise (padrão free)")
        print("  dias: validade em dias (padrão 365)")
        sys.exit(1)
    client_name = sys.argv[1]
    plan = sys.argv[2] if len(sys.argv) > 2 else 'free'
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 365

    key_info = create_api_key(client_name, plan, days)
    print(f"✅ Chave gerada para {key_info['client_name']}")
    print(f"API Key: {key_info['api_key']}")
    print(f"Plano: {key_info['plan']}")
    print(f"Expira em: {key_info['expires_at']}")

if __name__ == "__main__":
    main()

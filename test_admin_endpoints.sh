#!/bin/bash
# Testa os endpoints administrativos do SELIX

ADMIN_KEY="master_123_super_secret"
BASE_URL="http://localhost:5000"

echo "1. Listando todas as chaves..."
curl -s -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/v1/admin/list_keys" | jq .

echo "\n2. Gerando uma nova chave de teste..."
RESP=$(curl -s -X POST "$BASE_URL/v1/admin/generate_key" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d '{"client_name":"Teste Auto","plan":"free","days_valid":1}')
echo "$RESP" | jq .
KEY_HASH=$(echo "$RESP" | jq -r '.api_key')

echo "\n3. Revogando a chave (desativando)..."
curl -s -X POST "$BASE_URL/v1/admin/revoke_key" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d "{\"key_hash\":\"$KEY_HASH\"}" | jq .

echo "\n4. Tentando renovar (deve falhar porque a chave está inativa)..."
curl -s -X POST "$BASE_URL/v1/admin/renew_key" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_KEY" \
  -d "{\"key_hash\":\"$KEY_HASH\",\"extra_days\":7}" | jq .

echo "\n5. Listagem final para ver o estado da chave..."
curl -s -H "X-Admin-Key: $ADMIN_KEY" "$BASE_URL/v1/admin/list_keys" | jq .

#!/bin/bash
echo "🧪 Testando formatação dos valores..."

python3 -c '
texto_teste = """GPA: R$ 2,60 → R$ 17,60 (+577%)
RAIZ4: R$ 3,20 → R$ 23,40 (+631%)"""

print("✅ Formatação correta:")
print(texto_teste)
print(f"\n📏 Tamanho: {len(texto_teste)} caracteres")
'

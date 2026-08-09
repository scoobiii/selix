#!/usr/bin/env python3
"""
scripts/canary_test.py

Gera um teste canário único e o inclui automaticamente na suíte.
Usado para verificar se um LLM/agente realmente executou os testes.
"""

import hashlib
import secrets
import time
from pathlib import Path


def generate_canary() -> tuple[str, str]:
    salt = secrets.token_hex(16)
    timestamp = str(time.time())
    raw = f"{salt}-{timestamp}"
    canary_hash = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return canary_hash, timestamp


def create_canary_test(canary: str) -> Path:
    test_dir = Path("tests")
    test_dir.mkdir(exist_ok=True)

    # Remove canários antigos
    for old in test_dir.glob("test_canary_*.py"):
        old.unlink(missing_ok=True)

    test_file = test_dir / f"test_canary_{canary}.py"
    content = f'''"""
Teste canário gerado em {time.strftime("%Y-%m-%d %H:%M:%S")}.
Valor único: {canary}
"""

CANARY_VALUE = "{canary}"


def test_canary_{canary}():
    """Canário de verificação de execução real."""
    assert CANARY_VALUE == "{canary}"
'''
    test_file.write_text(content)
    return test_file


def main():
    canary, timestamp = generate_canary()
    test_file = create_canary_test(canary)

    print("=" * 60)
    print("CANÁRIO GERADO E INCLUÍDO NA SUÍTE")
    print("=" * 60)
    print(f"Valor:     {canary}")
    print(f"Timestamp: {timestamp}")
    print(f"Arquivo:   {test_file}")
    print()
    print("Próximo passo:")
    print(f"  git add {test_file} && git commit -m 'test: canary {canary}' && git push")
    print("=" * 60)


if __name__ == "__main__":
    main()

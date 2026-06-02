#!/usr/bin/env python3
"""
Gera esqueletos de teste (pytest) para funções/métodos não cobertos
com base no relatório de cobertura do pytest.
Uso: python scripts/gerar_tests_nao_cobertos.py
"""

import os
import sys
import ast
import json
import subprocess
from pathlib import Path

# Configurações
REPO_ROOT = Path("/root/selix")
COVERAGE_JSON = REPO_ROOT / "coverage.json"
TEST_DIR = REPO_ROOT / "tests"

def run_coverage():
    """Executa pytest com --cov e gera relatório JSON."""
    print("📊 Executando pytest e gerando relatório de cobertura...")
    subprocess.run([
        sys.executable, "-m", "pytest", "tests/",
        "--cov=src", "--cov=confidence",
        "--cov-report=json:" + str(COVERAGE_JSON)
    ], cwd=REPO_ROOT, check=True)
    print("✅ Relatório de cobertura gerado em", COVERAGE_JSON)

def get_uncovered_functions():
    """Retorna lista de (arquivo, nome_função, linha) para funções não cobertas."""
    if not COVERAGE_JSON.exists():
        run_coverage()
    with open(COVERAGE_JSON) as f:
        data = json.load(f)

    uncovered = []
    for file_path, coverage_data in data["files"].items():
        if not file_path.startswith(str(REPO_ROOT)):
            continue
        # Verifica se o arquivo está em src/ ou confidence/
        if not (file_path.startswith(str(REPO_ROOT / "src")) or
                file_path.startswith(str(REPO_ROOT / "confidence"))):
            continue
        executed_lines = set(coverage_data.get("executed_lines", []))
        missing_lines = coverage_data.get("missing_lines", [])
        if not missing_lines:
            continue
        # Usa AST para extrair nomes de funções
        try:
            with open(file_path, "r") as f_src:
                tree = ast.parse(f_src.read())
        except:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_start = node.lineno
                func_end = node.end_lineno
                # Verifica se alguma linha da função está em missing_lines
                if any(line in missing_lines for line in range(func_start, func_end+1)):
                    uncovered.append((file_path, node.name, func_start))
    return uncovered

def generate_test_file(uncovered_list):
    """Cria um arquivo de teste para cada módulo."""
    tests_by_file = {}
    for file_path, func_name, line in uncovered_list:
        rel_path = Path(file_path).relative_to(REPO_ROOT)
        # Transforma src/selix/worker_v4.py → test_worker_v4.py
        test_file_name = "test_" + rel_path.name.replace(".py", ".py")
        test_module_path = TEST_DIR / test_file_name
        tests_by_file.setdefault(test_module_path, []).append((rel_path, func_name, line))

    for test_path, funcs in tests_by_file.items():
        if test_path.exists():
            print(f"⚠️  {test_path} já existe – pulando.")
            continue
        with open(test_path, "w") as f:
            f.write(f'"""Testes para {test_path.stem} – gerados automaticamente."""\n\n')
            f.write("import pytest\n")
            f.write("import sys\n")
            f.write("sys.path.insert(0, '/root/selix')\n\n")
            for src_path, func_name, line in funcs:
                # Importa dinamicamente o módulo
                module_path = str(src_path.with_suffix("")).replace("/", ".")
                f.write(f"from {module_path} import {func_name}\n\n")
                f.write(f"def test_{func_name}():\n")
                f.write(f'    """Teste para {func_name} (linha {line}) – implementar."""\n')
                f.write("    # TODO: implementar teste\n")
                f.write(f"    assert {func_name} is not None\n\n")
        print(f"✅ Criado: {test_path} (para {len(funcs)} funções)")

def main():
    print("🔍 Analisando cobertura...")
    uncovered = get_uncovered_functions()
    if not uncovered:
        print("🎉 Todas as funções estão cobertas por testes!")
        return
    print(f"📝 Encontradas {len(uncovered)} funções não cobertas.")
    generate_test_file(uncovered)
    print("\n✨ Esqueletos de teste criados. Execute `pytest tests/` e implemente os TODOs.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
import sys

def run_coverage():
    result = subprocess.run(
        ['coverage', 'report', '--format=json'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ Erro ao executar coverage")
        return None
    return json.loads(result.stdout)

def main():
    print("=" * 60)
    print("📊 AUDITORIA DE COBERTURA SELIX")
    print("=" * 60)
    
    data = run_coverage()
    if not data:
        return
    
    files = sorted(data['files'].items(), key=lambda x: x[1]['summary']['percent_covered'])
    
    print(f"\n📈 COBERTURA TOTAL: {data['totals']['percent_covered']:.1f}%")
    print(f"   Linhas cobertas: {data['totals']['covered_lines']}/{data['totals']['num_statements']}")
    print(f"   Arquivos: {len(files)}")
    
    print("\n📁 ARQUIVOS COM MENOR COBERTURA:")
    for filename, stats in files[:10]:
        pct = stats['summary']['percent_covered']
        if pct < 50:
            print(f"   ❌ {pct:5.1f}% - {filename}")
        elif pct < 80:
            print(f"   ⚠️  {pct:5.1f}% - {filename}")
        else:
            print(f"   ✅ {pct:5.1f}% - {filename}")
    
    print("\n📋 RECOMENDAÇÕES:")
    if data['totals']['percent_covered'] < 70:
        print("   • Cobertura abaixo do aceitável (70%)")
        print("   • Priorizar testes para arquivos com <50% cobertura")
    elif data['totals']['percent_covered'] < 85:
        print("   • Cobertura razoável, mas pode melhorar")
        print("   • Focar nos arquivos com cobertura parcial")
    else:
        print("   ✅ Cobertura excelente!")
    
    # Salvar para CI
    with open('coverage_summary.json', 'w') as f:
        json.dump({
            'total_coverage': data['totals']['percent_covered'],
            'covered_lines': data['totals']['covered_lines'],
            'total_lines': data['totals']['num_statements'],
            'timestamp': subprocess.check_output(['date', '-Iseconds']).decode().strip()
        }, f, indent=2)
    print(f"\n💾 Resumo salvo em coverage_summary.json")

if __name__ == "__main__":
    main()
